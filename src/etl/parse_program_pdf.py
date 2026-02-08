"""
Parser de PDF de Programa de Carreras - Formato Club Hípico v2
Extrae datos estructurados incluyendo Jinete y Preparador.
"""
import pdfplumber
import pandas as pd
import re
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_program_pdf(pdf_path, output_csv=None):
    """
    Parsea un PDF de programa de carreras y extrae datos completos.
    """
    logger.info(f"📄 Parseando: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"No existe: {pdf_path}")
    
    pdf = pdfplumber.open(pdf_path)
    logger.info(f"   Páginas: {len(pdf.pages)}")
    
    all_text = ""
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            all_text += text + "\n\n"
    
    # Detectar fecha del programa
    fecha_match = re.search(r'(\d{1,2})\s*(ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|JULIO|AGOSTO|SEPTIEMBRE|OCTUBRE|NOVIEMBRE|DICIEMBRE)\s*(\d{4})', all_text, re.IGNORECASE)
    if fecha_match:
        dia = fecha_match.group(1)
        mes_text = fecha_match.group(2).upper()
        year = fecha_match.group(3)
        meses = {'ENERO': 1, 'FEBRERO': 2, 'MARZO': 3, 'ABRIL': 4, 'MAYO': 5, 'JUNIO': 6,
                 'JULIO': 7, 'AGOSTO': 8, 'SEPTIEMBRE': 9, 'OCTUBRE': 10, 'NOVIEMBRE': 11, 'DICIEMBRE': 12}
        mes = meses.get(mes_text, 1)
        fecha_programa = f"{year}-{mes:02d}-{int(dia):02d}"
    else:
        fecha_programa = datetime.now().strftime("%Y-%m-%d")
    
    logger.info(f"   Fecha: {fecha_programa}")
    
    # Detectar hipódromo
    if "CLUB HIPICO DE SANTIAGO" in all_text.upper():
        hipodromo = "Club Hípico de Santiago"
    elif "HIPODROMO CHILE" in all_text.upper():
        hipodromo = "Hipódromo Chile"
    elif "VALPARAISO" in all_text.upper():
        hipodromo = "Valparaíso Sporting"
    elif "CONCEPCION" in all_text.upper():
        hipodromo = "Club Hípico de Concepción"
    else:
        hipodromo = "Club Hípico de Santiago"
    
    logger.info(f"   Hipódromo: {hipodromo}")
    
    # Extraer carreras usando patrón mejorado
    carreras = []
    
    lines = all_text.split('\n')
    current_carrera_num = 0
    current_hora = ""
    current_premio = ""
    current_distancia = 1000
    current_superficie = "Arena"
    
    for i, line in enumerate(lines):
        # Detectar nueva carrera (patrón: "13:00 APROX. Pr. SHAADIR")
        carrera_header = re.search(r'(\d{1,2}:\d{2})\s*APROX\.?\s*Pr\.\s*([A-ZÁÉÍÓÚÑ\s\']+)', line, re.IGNORECASE)
        if carrera_header:
            current_hora = carrera_header.group(1)
            current_premio = carrera_header.group(2).strip()
            current_carrera_num += 1
            continue
        
        # Detectar distancia (patrón: "1000 MTS" o "1 1000 MTS")
        dist_match = re.search(r'\b(\d{3,4})\s*MTS', line)
        if dist_match:
            current_distancia = int(dist_match.group(1))
            if "PASTO" in line.upper() or "CESPED" in line.upper():
                current_superficie = "Pasto"
            else:
                current_superficie = "Arena"
            continue
        
        # Patrón para participante:
        # NUMERO CABALLO - PADRILLO PESO EDAD JINETE PREPARADOR ...
        # Ejemplo: "1 PASAPALABRA - Bad Daddy 57 9 V. Miranda F. Gonzalez S. 1 14cP 7cA 3cP..."
        participante_match = re.match(
            r'^(\d{1,2})\s+'                           # Número
            r'([A-ZÁÉÍÓÚÑ\s\'\(\)]+?)\s*-\s*'          # Caballo (hasta el guión)
            r'([A-Za-záéíóúñ\s\(\)]+?)\s+'             # Padrillo
            r'(\d{2,3})\s+'                            # Peso
            r'(\d{1,2})\s*'                            # Edad/Kilos extra
            r'([A-Za-záéíóúñ\.\s]+?)\s+'               # Jinete (hasta 2 palabras con puntos)
            r'([A-Za-záéíóúñ\.\s]+?)\s+'               # Preparador (siguientes palabras)
            r'(\d+)',                                  # Siguiente número (llegadas)
            line
        )
        
        if participante_match:
            numero = int(participante_match.group(1))
            caballo = participante_match.group(2).strip()
            padrillo = participante_match.group(3).strip()
            peso = int(participante_match.group(4))
            # grupo 5 es edad
            rest = participante_match.group(6) + " " + participante_match.group(7)
            
            # Separar jinete y preparador (heurística: buscar el punto seguido de espacio y mayúscula)
            # Ejemplos: "V. Miranda F. Gonzalez S." -> Jinete: V. Miranda, Prep: F. Gonzalez S.
            jinete, preparador = extract_jinete_preparador(rest)
            
            if caballo and len(caballo) > 2:
                carreras.append({
                    'fecha': fecha_programa,
                    'hipodromo': hipodromo,
                    'nro_carrera': current_carrera_num,
                    'hora': current_hora,
                    'premio': current_premio,
                    'distancia': current_distancia,
                    'superficie': current_superficie,
                    'numero': numero,
                    'caballo': clean_name(caballo),
                    'padrillo': clean_name(padrillo),
                    'peso': peso,
                    'jinete': jinete,
                    'preparador': preparador
                })
        else:
            # Patrón alternativo más simple
            alt_match = re.match(
                r'^(\d{1,2})\s+'                        # Número
                r'([A-ZÁÉÍÓÚÑ\s\'\(\)]+?)\s*-\s*'       # Caballo
                r'([A-Za-záéíóúñ\s\(\)]+?)\s*'          # Padrillo
                r'(\d{2,3})',                           # Peso
                line
            )
            if alt_match:
                numero = int(alt_match.group(1))
                caballo = alt_match.group(2).strip()
                padrillo = alt_match.group(3).strip()
                peso = int(alt_match.group(4))
                
                # Buscar jinete y preparador en el resto de la línea
                rest = line[alt_match.end():]
                jinete, preparador = extract_jinete_preparador(rest)
                
                if caballo and len(caballo) > 2:
                    carreras.append({
                        'fecha': fecha_programa,
                        'hipodromo': hipodromo,
                        'nro_carrera': current_carrera_num if current_carrera_num > 0 else 1,
                        'hora': current_hora,
                        'premio': current_premio,
                        'distancia': current_distancia,
                        'superficie': current_superficie,
                        'numero': numero,
                        'caballo': clean_name(caballo),
                        'padrillo': clean_name(padrillo),
                        'peso': peso,
                        'jinete': jinete,
                        'preparador': preparador
                    })
    
    pdf.close()
    
    # Crear DataFrame
    df = pd.DataFrame(carreras)
    logger.info(f"   Registros extraídos: {len(df)}")
    
    # Contar jinetes y preparadores encontrados
    jinetes_found = df['jinete'].apply(lambda x: len(x) > 1).sum()
    preps_found = df['preparador'].apply(lambda x: len(x) > 1).sum()
    logger.info(f"   Con Jinete: {jinetes_found}, Con Preparador: {preps_found}")
    
    # Guardar CSV
    if output_csv is None:
        base = os.path.splitext(os.path.basename(pdf_path))[0]
        output_csv = f"exports/PROGRAMA_{hipodromo.replace(' ', '_')[:10]}_{fecha_programa}.csv"
    
    df.to_csv(output_csv, index=False, encoding='utf-8')
    logger.info(f"✅ Guardado: {output_csv}")
    
    return df, output_csv


def clean_name(name):
    """Limpia un nombre removiendo caracteres extra"""
    if not name:
        return ""
    name = re.sub(r'\s+', ' ', name)
    name = name.strip()
    # Truncar a 30 caracteres
    return name[:30]


def extract_jinete_preparador(text):
    """
    Extrae jinete y preparador de un texto como "V. Miranda F. Gonzalez S."
    Limpia datos extra como llegadas, fechas, etc.
    """
    text = text.strip()
    if not text:
        return "", ""
    
    # Primero limpiar: remover todo después de números de llegadas (ej: "1 14cP 7cA")
    # Patrón: números seguidos de letras minúsculas (posiciones de carrera)
    clean = re.sub(r'\s+\d+\s*\d*[cChHpP]+[A-Za-z]*.*$', '', text)
    clean = re.sub(r'\s+\d{2}/\d{2}.*$', '', clean)  # Fechas DD/MM
    clean = re.sub(r'\s+\d{1,2}\s+(cpos|cp|1/2|3/4).*$', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\s+\d+\.\d+.*$', '', clean)  # Tiempos como 0:58.49
    clean = clean.strip()
    
    if not clean:
        return "", ""
    
    # Dividir por espacios
    parts = clean.split()
    if len(parts) < 2:
        return clean, ""
    
    # Buscar el segundo "punto" que indica inicio del preparador
    # Formato típico: "V. Miranda F. Gonzalez S."
    punto_count = 0
    split_idx = 0
    
    for i, p in enumerate(parts):
        if p.endswith('.') or '.' in p:
            punto_count += 1
            if punto_count == 2 and i > 0:
                split_idx = i
                break
    
    if split_idx > 0:
        jinete = ' '.join(parts[:split_idx])
        preparador = ' '.join(parts[split_idx:])
    else:
        # Si no hay segundo punto, tomar primeras 2 palabras como jinete
        mid = min(2, len(parts) - 1)
        jinete = ' '.join(parts[:mid]) if mid > 0 else parts[0]
        preparador = ' '.join(parts[mid:]) if mid < len(parts) else ""
    
    # Limpiar caracteres extra
    jinete = re.sub(r'[0-9]+$', '', jinete).strip()
    preparador = re.sub(r'[0-9]+$', '', preparador).strip()
    
    # Truncar a longitud razonable
    jinete = jinete[:25]
    preparador = preparador[:25]
    
    return jinete, preparador


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Buscar PDFs en exports
        pdf_path = None
        for f in os.listdir('exports'):
            if f.endswith('.pdf'):
                pdf_path = f'exports/{f}'
                break
    
    if pdf_path:
        try:
            df, csv_path = parse_program_pdf(pdf_path)
            print(f"\n✅ Extraídos {len(df)} registros")
            print(f"   Archivo: {csv_path}")
            print(f"\nMuestra (primeros 10):")
            cols = ['nro_carrera', 'numero', 'caballo', 'padrillo', 'peso', 'jinete', 'preparador']
            print(df[cols].head(10).to_string(index=False))
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("No se encontró ningún PDF en exports/")
