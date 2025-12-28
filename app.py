from flask import Flask, render_template, request, jsonify, url_for
import pandas as pd
from src.models.data_manager import cargar_datos, obtener_analisis_jornada, obtener_patrones_la_tercera, obtener_estadisticas_generales, obtener_lista_hipodromos, calcular_precision_modelo, obtener_predicciones_historicas, detectar_patrones_futuros, obtener_ultimos_aciertos
from src.models.ai_model import configurar_gemini, get_gemini_response_stream
import os
import gc
import sys
from dotenv import load_dotenv

# --- AUTOMATION IMPORTS ---
try:
    from src.models.inference import InferencePipeline
    from src.models.train_v2 import HipicaLearner # Optional if we want to retrain
    from src.utils.migrate_to_firebase import migrate
except ImportError:
    pass # Handle gracefully if running outside context

app = Flask(__name__)

# --- SECURITY: BASIC RATE LIMITER ---
import time
from collections import defaultdict

class SimpleRateLimiter:
    def __init__(self, limit=60, window=60):
        self.limit = limit
        self.window = window
        self.requests = defaultdict(list)

    def is_allowed(self, ip):
        now = time.time()
        # Limpiar requests viejos
        self.requests[ip] = [t for t in self.requests[ip] if now - t < self.window]
        
        if len(self.requests[ip]) < self.limit:
            self.requests[ip].append(now)
            return True
        return False

# Limite: 100 peticiones por minuto por IP (Anti-Scraping básico)
limiter = SimpleRateLimiter(limit=100, window=60)

@app.before_request
def rate_limit_check():
    # Excluir estáticos para no afectar navegación normal
    if request.path.startswith('/static'):
        return
        
    ip = request.remote_addr
    if not limiter.is_allowed(ip):
        return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429
# ------------------------------------

# Configuración
load_dotenv() # Carga variables del archivo .env
configurar_gemini()

# -------------------------------------------------------------------
# CRON JOB ENDPOINT (Called by Cloud Scheduler)
# -------------------------------------------------------------------
@app.route('/api/cron/update-predictions', methods=['POST'])
def cron_update():
    """
    Endpoint para actualizar predicciones diariamente.
    Ejecuta: ETL (implícito en inferencia si se requiere? No, inferencia carga DB) -> Inferencia -> Migración.
    Para producción, idealmente se debería correr ETL antes.
    
    En este diseño V2 simplificado:
    1. Ejecutamos Inferencia (Genera predicciones para carreras futuras ya en DB).
    2. Ejecutamos Migración (Sube todo a Firestore).
    """
    print("⏰ [CRON] Starting daily update...")
    start_t = time.time()
    
    try:
        # 1. Inference Pipeline
        print("   -> Running Inference...")
        pipeline = InferencePipeline()
        pipeline.run()
        
        # 2. Migration
        print("   -> Running Firestore Migration...")
        migrate()
        
        # 3. Cleanup
        del pipeline
        gc.collect()
        
        elapsed = time.time() - start_t
        msg = f"✅ Cron Job Completed in {elapsed:.2f}s"
        print(msg)
        return jsonify({'status': 'success', 'message': msg}), 200
        
    except Exception as e:
        print(f"❌ [CRON ERROR] {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/debug/firestore')
def debug_firestore():
    from src.models.data_manager import obtener_predicciones_firestore, _init_firebase_db
    import datetime
    
    status = {}
    try:
        # Check DB Init
        db = _init_firebase_db()
        status['db_initialized'] = (db is not None)
    except Exception as e:
        status['db_error'] = str(e)
        
    # Check Data
    try:
        data = obtener_predicciones_firestore("2025-01-01") # Future query
        # Try finding ANY data
        raw_docs = db.collection('predicciones').limit(5).stream()
        sample = [d.id for d in raw_docs]
        status['sample_ids'] = sample
    except Exception as e:
        status['query_error'] = str(e)
        
    return jsonify(status)

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
        # FIX: Check if keys exist before access (Full Cloud compatibility)
        if 'predicciones' in carrera and isinstance(carrera['predicciones'], pd.DataFrame):
             carrera['predicciones'] = carrera['predicciones'].to_dict('records')
        
        if 'caballos' in carrera and isinstance(carrera['caballos'], pd.DataFrame):
             carrera['caballos'] = carrera['caballos'].to_dict('records')

    # Calcular estadísticas de resumen
    total_carreras = len(analisis)
    total_caballos = sum(len(c.get('predicciones', [])) for c in analisis)
    fechas_unicas = list(set(c.get('fecha', '') for c in analisis if c.get('fecha')))
    fechas_unicas.sort(reverse=True)
    
    stats_resumen = {
        'total_carreras': total_carreras,
        'total_caballos': total_caballos,
        'fechas': fechas_unicas,
        'fecha_principal': fechas_unicas[0] if fechas_unicas else 'Sin fecha'
    }

    return render_template('program.html', analisis=analisis, hipodromo_filter=hipodromo_filter, stats=stats_resumen)

@app.route('/analisis')
def analisis():
    hipodromo_filter = request.args.get('hipodromo', 'Todos')
    patrones, last_updated = obtener_patrones_la_tercera(hipodromo_filter)
    alertas = detectar_patrones_futuros()
    return render_template('analysis.html', patrones=patrones, hipodromo_filter=hipodromo_filter, last_updated=last_updated, alertas=alertas)

@app.route('/precision')
def precision():
    """Página de precisión y transparencia del modelo"""
    from datetime import datetime, timedelta
    
    # Calcular precisión de los últimos 30 días por defecto
    fecha_fin = datetime.now().strftime('%Y-%m-%d')
    fecha_inicio_30d = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    fecha_inicio_90d = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    # Métricas generales (últimos 30 días)
    metricas_30d = calcular_precision_modelo(fecha_inicio=fecha_inicio_30d, fecha_fin=fecha_fin)
    
    # Métricas de 90 días
    metricas_90d = calcular_precision_modelo(fecha_inicio=fecha_inicio_90d, fecha_fin=fecha_fin)
    
    # Métricas históricas completas
    metricas_all = calcular_precision_modelo()
    
    # Obtener ACIERTOS recientes para mostrar confianza (Match Result vs Prediccion)
    predicciones_recientes = obtener_ultimos_aciertos(dias=30)
    
    return render_template('precision.html',
                         metricas_30d=metricas_30d,
                         metricas_90d=metricas_90d,
                         metricas_all=metricas_all,
                         predicciones_recientes=predicciones_recientes)

@app.route('/politica-de-privacidad')
def politica_privacidad():
    return render_template('privacy_policy.html')

@app.route('/terminos-y-condiciones')
def terminos():
    return render_template('terms.html')

@app.route('/quienes-somos')
def quienes_somos():
    return render_template('about.html')

@app.route('/blog')
def blog_index():
    return render_template('blog_index.html')

@app.route('/blog/metodologia-precision')
def blog_article_precision():
    return render_template('blog/article_precision.html')

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

@app.route('/robots.txt')
def robots_txt():
    """Servir robots.txt para SEO"""
    from flask import send_from_directory
    return send_from_directory('static', 'robots.txt')

@app.route('/ads.txt')
def ads_txt():
    """Servir ads.txt para AdSense"""
    from flask import send_from_directory
    return send_from_directory('static', 'ads.txt')

@app.route('/sitemap.xml')
def sitemap_xml():
    """Generar sitemap.xml dinámico para SEO"""
    from flask import Response
    from datetime import datetime
    
    # URLs estáticas
    pages = []
    
    # Página principal
    pages.append({
        'loc': url_for('home', _external=True),
        'lastmod': datetime.now().strftime('%Y-%m-%d'),
        'changefreq': 'daily',
        'priority': '1.0'
    })
    
    # Páginas de programa
    hipodromos = obtener_lista_hipodromos()
    for hipodromo in hipodromos:
        pages.append({
            'loc': url_for('programa', hipodromo=hipodromo, _external=True),
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'daily',
            'priority': '0.9'
        })
    
    # Programa general
    pages.append({
        'loc': url_for('programa', _external=True),
        'lastmod': datetime.now().strftime('%Y-%m-%d'),
        'changefreq': 'daily',
        'priority': '0.9'
    })
    
    # Estadísticas
    pages.append({
        'loc': url_for('estadisticas', _external=True),
        'lastmod': datetime.now().strftime('%Y-%m-%d'),
        'changefreq': 'weekly',
        'priority': '0.7'
    })
    
    # Análisis
    pages.append({
        'loc': url_for('analisis', _external=True),
        'lastmod': datetime.now().strftime('%Y-%m-%d'),
        'changefreq': 'daily',
        'priority': '0.8'
    })

    # Páginas Estáticas (Legales y Blog)
    static_pages = ['politica_privacidad', 'terminos', 'quienes_somos', 'blog_index']
    for p in static_pages:
        pages.append({
            'loc': url_for(p, _external=True),
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.5'
        })
    
    # Generar XML
    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for page in pages:
        sitemap_xml += '  <url>\n'
        sitemap_xml += f'    <loc>{page["loc"]}</loc>\n'
        sitemap_xml += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
        sitemap_xml += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        sitemap_xml += f'    <priority>{page["priority"]}</priority>\n'
        sitemap_xml += '  </url>\n'
    
    sitemap_xml += '</urlset>'
    
    return Response(sitemap_xml, mimetype='application/xml')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
