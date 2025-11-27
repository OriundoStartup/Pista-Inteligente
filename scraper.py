import pandas as pd
import random
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time
import sqlite3


def generar_datos_simulados(dias_atras=90):
    """Genera un DataFrame con datos simulados de carreras hípicas.

    Args:
        dias_atras (int): Número de días hacia atrás para generar datos.

    Returns:
        pd.DataFrame: DataFrame con columnas ['fecha', 'hipodromo', 'nro_carrera', 'llegada_str']
    """
    datos = []
    fecha_actual = datetime.now()
    hipodromos = ['Club Hípico', 'Hipódromo Chile']

    for i in range(dias_atras):
        fecha = fecha_actual - timedelta(days=i)
        fecha_str = fecha.strftime('%Y-%m-%d')
        for hipodromo in hipodromos:
            if random.random() > 0.3:  # 70% de probabilidad de tener carreras
                for carrera in range(1, 11):
                    llegada = random.sample(range(1, 16), 3)
                    llegada_str = "-".join(map(str, llegada))
                    datos.append({
                        'fecha': fecha_str,
                        'hipodromo': hipodromo,
                        'nro_carrera': carrera,
                        'llegada_str': llegada_str,
                        'primero': llegada[0],
                        'segundo': llegada[1],
                        'tercero': llegada[2]
                    })
    df = pd.DataFrame(datos)
    # Inyección de patrón repetido para prueba
    print("Inyectando patrón de prueba '3-7-10'...")
    if len(df) > 0:
        df.at[0, 'llegada_str'] = '3-7-10'
        df.at[0, 'primero'] = 3
        df.at[0, 'segundo'] = 7
        df.at[0, 'tercero'] = 10
    if len(df) > 1:
        df.at[len(df) - 1, 'llegada_str'] = '3-7-10'
        df.at[len(df) - 1, 'primero'] = 3
        df.at[len(df) - 1, 'segundo'] = 7
        df.at[len(df) - 1, 'tercero'] = 10
    return df


def obtener_resultados_hipodromo(url_base, fecha, hipodromo_nombre):
    """Obtiene los resultados de un hipódromo para una fecha específica.
    Busca tablas HTML y extrae posibles llegadas.
    """
    resultados = []
    url = f"{url_base}?fecha={fecha}"
    print(f"Consultando {hipodromo_nombre}: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        time.sleep(random.uniform(1, 3))
        if response.status_code != 200:
            print(f"  -> Error {response.status_code} al acceder a la URL.")
            return []
        soup = BeautifulSoup(response.content, 'html.parser')
        tablas = soup.find_all('table')
        if not tablas:
            # No hay tablas, probablemente no hay resultados para esta fecha
            return []
        carrera_count = 1
        for tabla in tablas:
            rows = tabla.find_all('tr')
            if not rows:
                continue
            posibles_caballos = []
            for row in rows:
                cols = row.find_all(['td', 'th'])
                for col in cols:
                    txt = col.get_text(strip=True)
                    if txt.isdigit() and 1 <= int(txt) <= 20:
                        posibles_caballos.append(int(txt))
            if len(posibles_caballos) >= 3:
                llegada = posibles_caballos[:3]
                llegada_str = "-".join(map(str, llegada))
                resultados.append({
                    'fecha': fecha,
                    'hipodromo': hipodromo_nombre,
                    'nro_carrera': carrera_count,
                    'llegada_str': llegada_str,
                    'primero': llegada[0],
                    'segundo': llegada[1],
                    'tercero': llegada[2]
                })
                carrera_count += 1
        return resultados
    except Exception as e:
        print(f"  -> Excepción al scrapear: {e}")
        return []


def obtener_datos_reales(dias_atras=30):
    """Obtiene datos reales iterando por fechas y hipódromos.
    """
    datos_totales = []
    fecha_actual = datetime.now()
    urls = {
        'Club Hípico': 'https://www.clubhipico.cl/resultados',
        'Hipódromo Chile': 'https://www.hipodromo.cl/carreras-ultimos-resultados'
    }
    print(f"Iniciando scraping real para los últimos {dias_atras} días...")
    for i in range(dias_atras):
        fecha = fecha_actual - timedelta(days=i)
        fecha_str = fecha.strftime('%Y-%m-%d')
        for hipodromo, url in urls.items():
            resultados = obtener_resultados_hipodromo(url, fecha_str, hipodromo)
            datos_totales.extend(resultados)
    return pd.DataFrame(datos_totales)


def obtener_programa_proxima_jornada():
    """Obtiene el programa de la próxima jornada de carreras de ambos hipódromos.
    
    Extrae:
    - Fecha de la jornada
    - Hipódromo
    - Número de carrera
    - Lista de caballos participantes (números)
    
    Returns:
        pd.DataFrame: DataFrame con las columnas mencionadas
    """
    from datetime import datetime, date, timedelta
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    
    programa_total = []
    
    # Configurar Selenium en modo headless
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # 1. Scraping Hipódromo Chile
        print("Obteniendo programa de Hipódromo Chile...")
        try:
            url_proximos = "https://www.hipodromo.cl/carreras-proximos-programas"
            driver.get(url_proximos)
            time.sleep(3)  # Esperar a que cargue la página
            
            # Buscar la fecha de la próxima jornada
            try:
                fecha_elem = driver.find_element(By.CSS_SELECTOR, 'h3.text-center')
                fecha_text = fecha_elem.text
                print(f"  Fecha encontrada: {fecha_text}")
                
                # Convertir fecha a formato YYYY-MM-DD
                parts = fecha_text.split()
                if len(parts) >= 5:
                    dia = parts[1]
                    mes_str = parts[3]
                    año = parts[4]
                    
                    meses = {
                        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                        'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                        'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
                    }
                    mes = meses.get(mes_str.lower(), '01')
                    fecha_str = f"{año}-{mes}-{dia.zfill(2)}"
                else:
                    fecha_str = datetime.now().strftime('%Y-%m-%d')
            except:
                fecha_str = datetime.now().strftime('%Y-%m-%d')
            
            # Buscar enlaces a programas de carreras
            try:
                enlaces_programa = driver.find_elements(By.LINK_TEXT, "Programa")
                print(f"  Encontrados {len(enlaces_programa)} enlaces de programa")
                
                for i, enlace in enumerate(enlaces_programa[:12], 1):  # Máximo 12 carreras
                    try:
                        url_carrera = enlace.get_attribute('href')
                        if url_carrera and 'carreras-programa-ver' in url_carrera:
                            # Abrir en nueva ventana
                            driver.execute_script(f"window.open('{url_carrera}', '_blank');")
                            driver.switch_to.window(driver.window_handles[-1])
                            time.sleep(2)
                            
                            # Buscar números de caballos en la tabla
                            caballos = []
                            try:
                                rows = driver.find_elements(By.CSS_SELECTOR, 'table.table tbody tr')
                                for row in rows:
                                    try:
                                        cols = row.find_elements(By.TAG_NAME, 'td')
                                        if cols:
                                            numero_text = cols[0].text.strip()
                                            if numero_text.isdigit():
                                                caballos.append(int(numero_text))
                                    except:
                                        continue
                            except:
                                pass
                            
                            if caballos:
                                programa_total.append({
                                    'fecha': fecha_str,
                                    'hipodromo': 'Hipódromo Chile',
                                    'nro_carrera': i,
                                    'caballos': ','.join(map(str, caballos))
                                })
                                print(f"  -> Carrera {i}: {len(caballos)} caballos")
                            
                            # Cerrar ventana y volver a la principal
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                            time.sleep(1)
                    except Exception as e:
                        print(f"  -> Error en carrera {i}: {e}")
                        # Asegurarse de volver a la ventana principal
                        if len(driver.window_handles) > 1:
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                        continue
                        
            except Exception as e:
                print(f"  Error al buscar enlaces de programa: {e}")
                
        except Exception as e:
            print(f"Error al obtener programa de Hipódromo Chile: {e}")
        
        # 2. Scraping Club Hípico
        print("\nObteniendo programa de Club Hípico...")
        try:
            fecha_prueba = date.today() + timedelta(days=1)
            fecha_str_ch = fecha_prueba.strftime('%Y-%m-%d')
            
            for nro_carrera in range(1, 15):  # Probar hasta 14 carreras
                try:
                    url_carrera_ch = f"https://www.clubhipico.cl/carreras/programa-y-resultados/?fecha={fecha_str_ch}&carrera={nro_carrera}"
                    driver.get(url_carrera_ch)
                    time.sleep(2)
                    
                    # Buscar tabla de participantes
                    caballos = []
                    try:
                        rows = driver.find_elements(By.CSS_SELECTOR, 'table tr')
                        for row in rows:
                            try:
                                cols = row.find_elements(By.TAG_NAME, 'td')
                                if not cols:
                                    cols = row.find_elements(By.TAG_NAME, 'th')
                                if cols:
                                    primer_col = cols[0].text.strip()
                                    if primer_col.isdigit() and 1 <= int(primer_col) <= 20:
                                        caballos.append(int(primer_col))
                            except:
                                continue
                    except:
                        pass
                    
                    # Eliminar duplicados manteniendo orden
                    caballos_unicos = []
                    for c in caballos:
                        if c not in caballos_unicos:
                            caballos_unicos.append(c)
                    caballos = caballos_unicos
                    
                    if caballos:
                        programa_total.append({
                            'fecha': fecha_str_ch,
                            'hipodromo': 'Club Hípico',
                            'nro_carrera': nro_carrera,
                            'caballos': ','.join(map(str, caballos))
                        })
                        print(f"  -> Carrera {nro_carrera}: {len(caballos)} caballos")
                    else:
                        # Si no hay caballos, probablemente no hay más carreras
                        break
                        
                except Exception as e:
                    print(f"  -> Error en carrera {nro_carrera}: {e}")
                    break
                    
        except Exception as e:
            print(f"Error al obtener programa de Club Hípico: {e}")
        
        driver.quit()
        
    except Exception as e:
        print(f"Error al inicializar Selenium: {e}")
        print("NOTA: Asegúrate de tener ChromeDriver instalado y en el PATH")
    
    # Convertir a DataFrame
    df_programa = pd.DataFrame(programa_total)
    print(f"\n✅ Total de carreras encontradas: {len(df_programa)}")
    return df_programa



def guardar_datos_en_db(df, nombre_db='hipica_data.db'):
    """Guarda el DataFrame en una base de datos SQLite.
    Evita duplicados verificando si la fecha y hipódromo ya existen.
    """
    if df.empty:
        print("DataFrame vacío, nada que guardar.")
        return
    try:
        conn = sqlite3.connect(nombre_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resultados (
                fecha TEXT,
                hipodromo TEXT,
                nro_carrera INTEGER,
                llegada_str TEXT,
                primero INTEGER,
                segundo INTEGER,
                tercero INTEGER
            )
        ''')
        conn.commit()
        combinaciones_nuevas = df[['fecha', 'hipodromo']].drop_duplicates()
        datos_a_insertar = pd.DataFrame()
        for _, row in combinaciones_nuevas.iterrows():
            fecha = row['fecha']
            hipodromo = row['hipodromo']
            cursor.execute("SELECT COUNT(*) FROM resultados WHERE fecha = ? AND hipodromo = ?", (fecha, hipodromo))
            count = cursor.fetchone()[0]
            if count == 0:
                filtro = (df['fecha'] == fecha) & (df['hipodromo'] == hipodromo)
                datos_a_insertar = pd.concat([datos_a_insertar, df[filtro]])
            else:
                print(f"  -> Datos para {fecha} en {hipodromo} ya existen en DB. Saltando.")
        if not datos_a_insertar.empty:
            print(f"Insertando {len(datos_a_insertar)} nuevos registros en {nombre_db}...")
            datos_a_insertar.to_sql('resultados', conn, if_exists='append', index=False)
        else:
            print("No hay nuevos datos para insertar.")
        conn.close()
    except Exception as e:
        print(f"Error al guardar en base de datos: {e}")


def guardar_programa_en_db(df, nombre_db='hipica_data.db'):
    """Guarda el programa de carreras en la base de datos.
    Actualiza la tabla programa_carreras cada vez que se ejecuta,
    eliminando datos antiguos y reemplazándolos con los nuevos.
    
    Args:
        df: DataFrame con el programa de carreras
        nombre_db: Nombre del archivo de base de datos
    """
    if df.empty:
        print("DataFrame vacío, nada que guardar.")
        return
    
    try:
        conn = sqlite3.connect(nombre_db)
        cursor = conn.cursor()
        
        # Crear tabla si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS programa_carreras (
                fecha TEXT,
                hipodromo TEXT,
                nro_carrera INTEGER,
                caballos TEXT
            )
        ''')
        conn.commit()
        
        # Limpiar la tabla antes de insertar nuevos datos (actualización completa)
        cursor.execute('DELETE FROM programa_carreras')
        print("Limpiando datos antiguos de programa_carreras...")
        
        # Insertar nuevos datos
        print(f"Insertando {len(df)} registros en programa_carreras...")
        df.to_sql('programa_carreras', conn, if_exists='append', index=False)
        
        conn.commit()
        conn.close()
        print("✅ Programa guardado exitosamente en la base de datos.")
        
    except Exception as e:
        print(f"Error al guardar programa en base de datos: {e}")



if __name__ == "__main__":
    # 1) Generar y guardar datos simulados
    df_sim = generar_datos_simulados(5)
    guardar_datos_en_db(df_sim)
    print("✅ Datos simulados guardados en la base de datos.")

    # 2) Probar scraping real para tres fechas (ayer, hoy, mañana)
    from datetime import date, timedelta
    fechas_prueba = [date.today() - timedelta(days=1), date.today(), date.today() + timedelta(days=1)]
    resultados_reales = []
    for f in fechas_prueba:
        fecha_str = f.strftime('%Y-%m-%d')
        for hipodromo, url in {
            'Club Hípico': 'https://www.clubhipico.cl/resultados',
            'Hipódromo Chile': 'https://www.hipodromo.cl/carreras-ultimos-resultados'
        }.items():
            res = obtener_resultados_hipodromo(url, fecha_str, hipodromo)
            resultados_reales.extend(res)
    df_real = pd.DataFrame(resultados_reales)
    if not df_real.empty:
        guardar_datos_en_db(df_real)
        print(f"✅ Se guardaron {len(df_real)} registros reales en la DB.")
    else:
        print("ℹ️ No se obtuvieron datos reales para las fechas de prueba (posiblemente fechas sin carreras).")

    # 3) Obtener programa de próxima jornada
    print("\n" + "="*60)
    print("OBTENIENDO PROGRAMA DE PRÓXIMA JORNADA")
    print("="*60)
    df_programa = obtener_programa_proxima_jornada()
    if not df_programa.empty:
        guardar_programa_en_db(df_programa)
        print(f"\n✅ Se guardaron {len(df_programa)} carreras del programa en la DB.")
        print("\nPrimeras filas del programa:")
        print(df_programa.head(10))
    else:
        print("ℹ️ No se pudo obtener el programa de la próxima jornada.")

    # 4) Mostrar resumen rápido de la DB
    print("\n" + "="*60)
    print("RESUMEN DE LA BASE DE DATOS")
    print("="*60)
    conn = sqlite3.connect('hipica_data.db')
    total_resultados = pd.read_sql('SELECT COUNT(*) as cnt FROM resultados', conn)['cnt'][0]
    print(f"📊 Total de resultados históricos: {total_resultados}")
    
    # Mostrar resumen del programa
    try:
        total_programa = pd.read_sql('SELECT COUNT(*) as cnt FROM programa_carreras', conn)['cnt'][0]
        print(f"📅 Total de carreras en el programa: {total_programa}")
        
        # Mostrar detalle por hipódromo
        resumen = pd.read_sql('''
            SELECT hipodromo, fecha, COUNT(*) as num_carreras 
            FROM programa_carreras 
            GROUP BY hipodromo, fecha
        ''', conn)
        if not resumen.empty:
            print("\nDetalle del programa por hipódromo:")
            print(resumen.to_string(index=False))
    except Exception as e:
        print(f"No hay datos de programa aún: {e}")
    
    conn.close()

