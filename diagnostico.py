import requests
from bs4 import BeautifulSoup

print("Prueba 1: Hipódromo Chile")
print("=" * 60)

url = "https://www.hipodromo.cl/carreras-proximos-programas"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status code: {response.status_code}")
    print(f"Content length: {len(response.content)}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Buscar h3 con fecha
    fecha_elem = soup.find('h3', class_='text-center')
    print(f"Elemento de fecha encontrado: {fecha_elem is not None}")
    if fecha_elem:
        print(f"Texto de fecha: {fecha_elem.get_text(strip=True)}")
    
    # Buscar todas las h3
    all_h3 = soup.find_all('h3')
    print(f"\nTotal de elementos h3: {len(all_h3)}")
    for i, h3 in enumerate(all_h3[:5]):
        print(f"  H3 {i+1}: {h3.get_text(strip=True)[:100]}")
    
    # Buscar tablas
    tablas = soup.find_all('table', class_='table')
    print(f"\nTotal de tablas con clase 'table': {len(tablas)}")
    
    # Buscar cualquier tabla
    all_tables = soup.find_all('table')
    print(f"Total de tablas: {len(all_tables)}")
    
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Prueba 2: Club Hípico")
print("=" * 60)

from datetime import date, timedelta
fecha_prueba = date.today() + timedelta(days=1)
fecha_str = fecha_prueba.strftime('%Y-%m-%d')

url_ch = f"https://www.clubhipico.cl/carreras/programa-y-resultados/?fecha={fecha_str}&carrera=1"
print(f"URL: {url_ch}")

try:
    response = requests.get(url_ch, headers=headers, timeout=10)
    print(f"Status code: {response.status_code}")
    print(f"Content length: {len(response.content)}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Buscar tablas
    all_tables = soup.find_all('table')
    print(f"Total de tablas: {len(all_tables)}")
    
    # Buscar filas con números
    all_rows = soup.find_all('tr')
    print(f"Total de filas (tr): {len(all_rows)}")
    
    numeros_encontrados = []
    for row in all_rows[:10]:
        cols = row.find_all(['td', 'th'])
        if cols:
            primer_col = cols[0].get_text(strip=True)
            if primer_col.isdigit():
                numeros_encontrados.append(primer_col)
    
    print(f"Números encontrados en primeras 10 filas: {numeros_encontrados}")
    
except Exception as e:
    print(f"Error: {e}")
