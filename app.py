from flask import Flask, render_template, request, jsonify
import pandas as pd
from src.models.data_manager import cargar_datos, obtener_analisis_jornada, obtener_patrones_la_tercera, obtener_estadisticas_generales, obtener_lista_hipodromos
from src.models.ai_model import configurar_gemini, get_gemini_response_stream
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Configuración
load_dotenv() # Carga variables del archivo .env
configurar_gemini()

@app.context_processor
def inject_global_vars():
    return dict(
        site_name="Pista Inteligente",
        hipodromos=obtener_lista_hipodromos()
    )

@app.route('/')
def home():
    # Obtener estadisticas (ahora retorna un diccionario)
    data = obtener_estadisticas_generales()
    
    # Adaptar para el template home existente (si lo requiere separado)
    # Asumimos que home.html usa stats, top_ganadores, top_jinetes
    # Pero las listas ya vienen como dicts en 'jinetes', 'caballos'
    
    return render_template('home.html', 
                           stats=data, 
                           top_ganadores=data.get('caballos', []), 
                           top_jinetes=data.get('jinetes', []))

@app.route('/estadisticas')
def estadisticas():
    stats = obtener_estadisticas_generales()
    return render_template('estadisticas.html', stats=stats)

@app.route('/programa')
def programa():
    hipodromo_filter = request.args.get('hipodromo', 'Todos')
    analisis = obtener_analisis_jornada()
    
    if hipodromo_filter != 'Todos':
        analisis = [a for a in analisis if a['hipodromo'] == hipodromo_filter]
        
    # Pre-procesar DataFrames de predicciones para que sean fáciles de renderizar
    for carrera in analisis:
        if isinstance(carrera['predicciones'], pd.DataFrame):
             carrera['predicciones'] = carrera['predicciones'].to_dict('records')
        if isinstance(carrera['caballos'], pd.DataFrame):
             carrera['caballos'] = carrera['caballos'].to_dict('records')

    return render_template('program.html', analisis=analisis, hipodromo_filter=hipodromo_filter)

@app.route('/analisis')
def analisis():
    hipodromo_filter = request.args.get('hipodromo', 'Todos')
    patrones = obtener_patrones_la_tercera(hipodromo_filter)
    return render_template('analysis.html', patrones=patrones, hipodromo_filter=hipodromo_filter)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'response': 'Por favor escribe un mensaje.'})
    
    # Obtener respuesta completa (no streaming para simplificar frontend por ahora)
    full_response = ""
    try:
        for chunk in get_gemini_response_stream(user_message):
            full_response += chunk
    except Exception as e:
        full_response = "Lo siento, tuve un problema procesando tu solicitud."
        
    return jsonify({'response': full_response})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
