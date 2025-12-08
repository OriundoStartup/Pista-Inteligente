"""
BOT PISTA INTELIGENTE - VERSIÓN OPTIMIZADA V3.2
================================================
Bot de scraping optimizado con VENTANAS DE TIEMPO + DESCARGA DE PDFs:

RESULTADOS (Pasado):
- Solo últimos 30 días desde fecha actual
- Break inmediato si encuentra fecha más antigua
- Ignora fechas futuras (errores de datos)

PROGRAMAS (Futuro):
- Solo fechas >= hoy
- Ordenados de más cercano a más lejano
- Limitado a las próximas 3 jornadas
- Archivos con fechas en el nombre
- ✨ NUEVO: Descarga automática de PDFs

HIPÓDROMOS:
- HC: Hipódromo Chile (resultados + programas + PDFs)
- CHS: Club Hípico de Santiago (resultados + programas + PDFs)

Autor: Oriundo Startup Chile
Fecha: 30/11/2025
Versión: 3.2
"""

import os
import re
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

@dataclass
class BotConfig:
    """Configuración del bot con ventanas de tiempo"""
    headless: bool = False
    page_timeout: int = 30
    element_timeout: int = 15
    delay_between_pages: float = 2.0
    output_dir: str = "exports"
    html_dump_dir: str = "html_dumps"
    pdf_dir: str = "pdfs_programas"  # ✨ NUEVO: Directorio para PDFs
    
    # === VENTANAS DE TIEMPO ===
    resultados_dias_atras: int = 30
    programas_max_jornadas: int = 3
    programas_dias_adelante: int = 30
    
    # === DESCARGA DE PDFs ===
    descargar_pdfs: bool = True  # ✨ NUEVO: Activar descarga de PDFs
    pdf_timeout: int = 30  # Timeout para descarga de PDFs


@dataclass
class Hipodromo:
    codigo: str
    nombre: str
    resultados_url: str
    programas_url: str
    base_url: str = ""  # ✨ NUEVO: URL base para construir links completos


# Configuración de hipódromos
HIPODROMOS = {
    'HC': Hipodromo(
        codigo='HC',
        nombre='Hipódromo Chile',
        resultados_url='https://hipodromo.cl/carreras-ultimos-resultados',
        programas_url='https://hipodromo.cl/carreras-proximos-programas',
        base_url='https://hipodromo.cl',
    ),
    'CHS': Hipodromo(
        codigo='CHS',
        nombre='Club Hípico de Santiago',
        resultados_url='https://www.clubhipico.cl/carreras/resultados/',
        programas_url='https://www.clubhipico.cl/carreras/programa/',
        base_url='https://www.clubhipico.cl',
    ),
}


# ============================================================================
# LOGGER
# ============================================================================

def setup_logger() -> logging.Logger:
    os.makedirs("logs", exist_ok=True)
    
    logger = logging.getLogger("PistaBotV3")
    logger.setLevel(logging.DEBUG)
    
    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%H:%M:%S')
        
        log_file = f"logs/pista_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger


# ============================================================================
# UTILIDADES DE FECHA
# ============================================================================

class FechaUtils:
    """Utilidades para manejo de fechas y ventanas de tiempo"""
    
    MESES = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    
    @staticmethod
    def hoy() -> datetime:
        """Retorna fecha actual sin hora"""
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def parse_fecha(texto: str) -> Optional[datetime]:
        """
        Parsea fecha desde varios formatos:
        - "2025-11-29" (ISO)
        - "29 de Noviembre del año 2025" (texto largo)
        - "Sábado 29 de Noviembre del año 2025"
        - "29/11/2025"
        - "29-11-2025"
        """
        if not texto:
            return None
        
        texto = texto.strip()
        
        # Formato ISO: YYYY-MM-DD
        try:
            return datetime.strptime(texto, '%Y-%m-%d')
        except ValueError:
            pass
        
        # Formato DD/MM/YYYY
        try:
            return datetime.strptime(texto, '%d/%m/%Y')
        except ValueError:
            pass
        
        # Formato DD-MM-YYYY
        try:
            return datetime.strptime(texto, '%d-%m-%Y')
        except ValueError:
            pass
        
        # Formato texto: "29 de Noviembre del año 2025"
        match = re.search(r'(\d{1,2})\s+de\s+(\w+)\s+(?:del?\s+año\s+)?(\d{4})', texto, re.IGNORECASE)
        if match:
            dia = int(match.group(1))
            mes_nombre = match.group(2).lower()
            ano = int(match.group(3))
            mes = FechaUtils.MESES.get(mes_nombre)
            if mes:
                try:
                    return datetime(ano, mes, dia)
                except ValueError:
                    pass
        
        # Formato corto: "29 Noviembre 2025" o "Noviembre 29, 2025"
        match = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})', texto, re.IGNORECASE)
        if match:
            dia = int(match.group(1))
            mes_nombre = match.group(2).lower()
            ano = int(match.group(3))
            mes = FechaUtils.MESES.get(mes_nombre)
            if mes:
                try:
                    return datetime(ano, mes, dia)
                except ValueError:
                    pass
        
        return None
    
    @staticmethod
    def fecha_en_rango_resultados(fecha: datetime, dias_atras: int = 30) -> str:
        """Verifica si fecha está en rango válido para resultados"""
        hoy = FechaUtils.hoy()
        limite_inferior = hoy - timedelta(days=dias_atras)
        
        if fecha > hoy:
            return 'futura'
        elif fecha < limite_inferior:
            return 'antigua'
        else:
            return 'valida'
    
    @staticmethod
    def fecha_en_rango_programas(fecha: datetime, dias_adelante: int = 30) -> str:
        """Verifica si fecha está en rango válido para programas"""
        hoy = FechaUtils.hoy()
        limite_superior = hoy + timedelta(days=dias_adelante)
        
        if fecha < hoy:
            return 'pasada'
        elif fecha > limite_superior:
            return 'muy_lejana'
        else:
            return 'valida'
    
    @staticmethod
    def formato_fecha(fecha: datetime) -> str:
        """Formatea fecha a ISO"""
        return fecha.strftime('%Y-%m-%d')
    
    @staticmethod
    def formato_fecha_corto(fecha: datetime) -> str:
        """Formatea fecha corta para nombres de archivo"""
        return fecha.strftime('%Y%m%d')
    
    @staticmethod
    def rango_fechas_str(fechas: List[str]) -> str:
        """
        Genera string con rango de fechas para nombre de archivo.
        Ej: "20251201_20251210" o "20251201" si es una sola fecha
        """
        if not fechas:
            return datetime.now().strftime('%Y%m%d')
        
        # Parsear todas las fechas
        fechas_dt = []
        for f in fechas:
            dt = FechaUtils.parse_fecha(f)
            if dt:
                fechas_dt.append(dt)
        
        if not fechas_dt:
            return datetime.now().strftime('%Y%m%d')
        
        fecha_min = min(fechas_dt)
        fecha_max = max(fechas_dt)
        
        if fecha_min == fecha_max:
            return FechaUtils.formato_fecha_corto(fecha_min)
        else:
            return f"{FechaUtils.formato_fecha_corto(fecha_min)}_a_{FechaUtils.formato_fecha_corto(fecha_max)}"


# ============================================================================
# BOT OPTIMIZADO V3.2 CON DESCARGA DE PDFs
# ============================================================================

class PistaInteligenteBot:
    """Bot optimizado para scraping de hipódromos chilenos con filtros de tiempo y descarga de PDFs"""
    
    def __init__(self, config: BotConfig = None):
        self.config = config or BotConfig()
        self.logger = setup_logger()
        self.driver = None
        self._init_driver()
        
        # Crear directorios
        os.makedirs(self.config.output_dir, exist_ok=True)
        os.makedirs(self.config.html_dump_dir, exist_ok=True)
        os.makedirs(self.config.pdf_dir, exist_ok=True)  # ✨ NUEVO
        
        # Estadísticas de filtrado
        self.stats = {
            'procesados': 0,
            'filtrados_antiguos': 0,
            'filtrados_futuros': 0,
            'errores_fecha': 0,
            'pdfs_descargados': 0,  # ✨ NUEVO
            'pdfs_fallidos': 0,  # ✨ NUEVO
        }
        
        # Lista de PDFs descargados
        self.pdfs_descargados = []  # ✨ NUEVO
    
    def _init_driver(self):
        self.logger.info("🚀 Inicializando navegador...")
        
        options = Options()
        if self.config.headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(self.config.page_timeout)
        self.logger.info("✅ Navegador listo")
    
    def _reset_stats(self):
        """Reinicia estadísticas de filtrado"""
        self.stats = {
            'procesados': 0,
            'filtrados_antiguos': 0,
            'filtrados_futuros': 0,
            'errores_fecha': 0,
            'pdfs_descargados': 0,
            'pdfs_fallidos': 0,
        }
    
    def _get_html(self, url: str, wait_selector: str = None) -> str:
        """Obtiene el HTML de una página con espera inteligente"""
        try:
            self.logger.info(f"   🌐 Cargando: {url}")
            self.driver.get(url)
            time.sleep(2)
            
            if wait_selector:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
                    )
                except TimeoutException:
                    self.logger.warning(f"   ⚠️ Timeout esperando {wait_selector}")
            
            time.sleep(self.config.delay_between_pages)
            return self.driver.page_source
            
        except Exception as e:
            self.logger.error(f"   ❌ Error cargando {url}: {e}")
            return ""
    
    def _save_html(self, html: str, filename: str):
        """Guarda HTML para debugging"""
        path = os.path.join(self.config.html_dump_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        self.logger.debug(f"   📄 HTML guardado: {path}")
    
    # ========================================================================
    # ✨ NUEVO: MÉTODOS PARA DESCARGA DE PDFs
    # ========================================================================
    
    def _descargar_pdf(self, url: str, nombre_archivo: str, hipodromo: str) -> Optional[str]:
        """
        Descarga un PDF desde una URL.
        
        Args:
            url: URL del PDF
            nombre_archivo: Nombre para guardar el archivo
            hipodromo: Código del hipódromo (HC o CHS)
            
        Returns:
            Path del archivo descargado o None si falló
        """
        try:
            # Crear subdirectorio por hipódromo
            subdir = os.path.join(self.config.pdf_dir, hipodromo)
            os.makedirs(subdir, exist_ok=True)
            
            # Sanitizar nombre de archivo
            nombre_limpio = re.sub(r'[^\w\-_\.]', '_', nombre_archivo)
            if not nombre_limpio.endswith('.pdf'):
                nombre_limpio += '.pdf'
            
            filepath = os.path.join(subdir, nombre_limpio)
            
            # Verificar si ya existe
            if os.path.exists(filepath):
                self.logger.info(f"   📄 PDF ya existe: {nombre_limpio}")
                return filepath
            
            self.logger.info(f"   📥 Descargando PDF: {nombre_limpio}")
            self.logger.debug(f"      URL: {url}")
            
            # Headers para simular navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/pdf,*/*',
                'Accept-Language': 'es-CL,es;q=0.9,en;q=0.8',
                'Referer': HIPODROMOS[hipodromo].base_url,
            }
            
            response = requests.get(
                url, 
                headers=headers, 
                timeout=self.config.pdf_timeout,
                stream=True
            )
            response.raise_for_status()
            
            # Verificar que es un PDF
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' not in content_type.lower() and not url.lower().endswith('.pdf'):
                self.logger.warning(f"   ⚠️ No parece ser un PDF: {content_type}")
            
            # Guardar el archivo
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verificar tamaño
            size = os.path.getsize(filepath)
            if size < 1000:  # Menos de 1KB probablemente no es válido
                self.logger.warning(f"   ⚠️ PDF muy pequeño ({size} bytes), puede estar corrupto")
                os.remove(filepath)
                self.stats['pdfs_fallidos'] += 1
                return None
            
            size_kb = size / 1024
            self.logger.info(f"   ✅ PDF descargado: {nombre_limpio} ({size_kb:.1f} KB)")
            self.stats['pdfs_descargados'] += 1
            self.pdfs_descargados.append({
                'archivo': nombre_limpio,
                'path': filepath,
                'url': url,
                'hipodromo': hipodromo,
                'size_kb': round(size_kb, 1)
            })
            
            return filepath
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"   ❌ Error descargando PDF: {e}")
            self.stats['pdfs_fallidos'] += 1
            return None
        except Exception as e:
            self.logger.error(f"   ❌ Error inesperado descargando PDF: {e}")
            self.stats['pdfs_fallidos'] += 1
            return None
    
    def _buscar_links_pdf(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """
        Busca todos los links a PDFs en una página.
        
        Returns:
            Lista de diccionarios con info de cada PDF encontrado
        """
        pdfs = []
        
        # Buscar links que terminan en .pdf
        for link in soup.select('a[href$=".pdf"], a[href*=".pdf"]'):
            href = link.get('href', '')
            if not href:
                continue
            
            # Construir URL completa
            if href.startswith('http'):
                url = href
            elif href.startswith('//'):
                url = 'https:' + href
            elif href.startswith('/'):
                url = urljoin(base_url, href)
            else:
                url = urljoin(base_url, href)
            
            # Obtener texto del link
            texto = link.get_text(strip=True) or 'programa'
            
            pdfs.append({
                'url': url,
                'texto': texto,
                'href_original': href
            })
        
        # Buscar links con texto que mencione "programa" o "pdf"
        for link in soup.select('a'):
            texto = link.get_text(strip=True).lower()
            href = link.get('href', '')
            
            if not href:
                continue
            
            # Ya procesado como .pdf
            if href.endswith('.pdf'):
                continue
            
            # Buscar por texto relevante
            if any(palabra in texto for palabra in ['programa', 'pdf', 'descargar', 'download', 'ver programa']):
                if href.startswith('http'):
                    url = href
                elif href.startswith('/'):
                    url = urljoin(base_url, href)
                else:
                    url = urljoin(base_url, href)
                
                pdfs.append({
                    'url': url,
                    'texto': link.get_text(strip=True),
                    'href_original': href,
                    'es_link_texto': True
                })
        
        # Buscar en onclick o data attributes
        for elem in soup.select('[onclick*="pdf"], [data-pdf], [data-url*="pdf"]'):
            onclick = elem.get('onclick', '')
            data_pdf = elem.get('data-pdf', '') or elem.get('data-url', '')
            
            url = None
            if data_pdf:
                url = data_pdf if data_pdf.startswith('http') else urljoin(base_url, data_pdf)
            elif onclick:
                match = re.search(r"['\"]([^'\"]*\.pdf[^'\"]*)['\"]", onclick)
                if match:
                    url = match.group(1)
                    url = url if url.startswith('http') else urljoin(base_url, url)
            
            if url:
                pdfs.append({
                    'url': url,
                    'texto': elem.get_text(strip=True) or 'programa',
                    'es_onclick': True
                })
        
        # Eliminar duplicados por URL
        urls_vistas = set()
        pdfs_unicos = []
        for pdf in pdfs:
            if pdf['url'] not in urls_vistas:
                urls_vistas.add(pdf['url'])
                pdfs_unicos.append(pdf)
        
        return pdfs_unicos
    
    def _extraer_fecha_de_texto(self, texto: str) -> Optional[str]:
        """Extrae fecha de un texto para nombrar el PDF"""
        fecha_dt = FechaUtils.parse_fecha(texto)
        if fecha_dt:
            return FechaUtils.formato_fecha_corto(fecha_dt)
        return None
    
    # ========================================================================
    # HIPÓDROMO CHILE - RESULTADOS
    # ========================================================================
    
    def obtener_resultados_hipodromo_chile(self) -> List[Dict]:
        """Extrae resultados del Hipódromo Chile con ventana de tiempo."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 HIPÓDROMO CHILE - RESULTADOS")
        self.logger.info(f"   📅 Ventana: últimos {self.config.resultados_dias_atras} días")
        self.logger.info("=" * 60)
        
        self._reset_stats()
        hipo = HIPODROMOS['HC']
        
        fecha_hoy = FechaUtils.hoy()
        fecha_limite = fecha_hoy - timedelta(days=self.config.resultados_dias_atras)
        self.logger.info(f"   📆 Rango válido: {FechaUtils.formato_fecha(fecha_limite)} → {FechaUtils.formato_fecha(fecha_hoy)}")
        
        html = self._get_html(hipo.resultados_url, 'table.table-hover')
        
        if not html:
            return []
        
        self._save_html(html, 'HC_resultados_v3.html')
        soup = BeautifulSoup(html, 'lxml')
        resultados = []
        
        titulo = soup.select_one('h1.tituloshome')
        reunion_info = titulo.get_text(strip=True) if titulo else "Sin información"
        self.logger.info(f"   📅 Reunión: {reunion_info}")
        
        fecha_reunion_dt = FechaUtils.parse_fecha(reunion_info)
        
        if fecha_reunion_dt:
            estado_fecha = FechaUtils.fecha_en_rango_resultados(
                fecha_reunion_dt, 
                self.config.resultados_dias_atras
            )
            
            if estado_fecha == 'futura':
                self.logger.warning(f"   ⚠️ Fecha futura detectada: {fecha_reunion_dt}")
                self.stats['filtrados_futuros'] += 1
                
            elif estado_fecha == 'antigua':
                self.logger.info(f"   ⏭️ Reunión fuera de rango (>{self.config.resultados_dias_atras} días)")
                self.stats['filtrados_antiguos'] += 1
                self._mostrar_stats_filtrado()
                return []
        
        fecha_reunion = FechaUtils.formato_fecha(fecha_reunion_dt) if fecha_reunion_dt else datetime.now().strftime('%Y-%m-%d')
        
        tabla = soup.select_one('table.table-hover.table-condensed')
        if not tabla:
            tabla = soup.select_one('table.table-hover')
        
        if not tabla:
            self.logger.warning("   ⚠️ No se encontró tabla de resultados")
            return []
        
        tbodies = tabla.select('tbody')
        self.logger.info(f"   📋 Carreras encontradas: {len(tbodies)}")
        
        for tbody in tbodies:
            rows = tbody.select('tr')
            for row in rows:
                carrera_data = self._parse_fila_hc(row, fecha_reunion, reunion_info)
                if carrera_data:
                    resultados.extend(carrera_data)
                    self.stats['procesados'] += len(carrera_data)
        
        carreras_unicas = len(set(r['carrera'] for r in resultados if 'carrera' in r))
        self.logger.info(f"   ✅ Carreras procesadas: {carreras_unicas}")
        self.logger.info(f"   ✅ Registros totales: {len(resultados)}")
        
        self._mostrar_stats_filtrado()
        
        return resultados
    
    def _parse_fila_hc(self, row, fecha_reunion: str, reunion_info: str) -> List[Dict]:
        """Parsea una fila de resultados del Hipódromo Chile"""
        resultados = []
        cells = row.select('td')
        
        if len(cells) < 6:
            return []
        
        num_text = cells[0].get_text(strip=True).replace('ª', '').strip()
        if not num_text.isdigit():
            return []
        
        num_carrera = int(num_text)
        hora = cells[1].get_text(strip=True) if len(cells) > 1 else ""
        
        distancia = ""
        dist_cell = row.select_one('td.visible-lg')
        if dist_cell:
            dist_text = dist_cell.get_text(strip=True)
            dist_match = re.search(r'(\d+)', dist_text)
            if dist_match:
                distancia = dist_match.group(1)
        
        tipo = ""
        grado = ""
        for cell in cells[3:6]:
            text = cell.get_text(strip=True)
            if text in ['Hd', 'Cd', 'Cl']:
                tipo = text
            elif text in ['G1', 'G2', 'G3', 'ClCd']:
                grado = text
        
        cond_cell = row.select_one('td.condicion')
        condicion = cond_cell.get_text(strip=True) if cond_cell else ""
        
        ejemplares = row.select('.vue-comp-menu-ejemplar a')
        
        for i, ejemplar in enumerate(ejemplares[:3]):
            title = ejemplar.get('title', '')
            nombre_match = re.search(r'Ejemplar:\s*(.+)', title)
            nombre = nombre_match.group(1).strip() if nombre_match else ejemplar.get_text(strip=True)
            
            padre = ""
            ano_nacimiento = ""
            parent_font = ejemplar.find_parent('font')
            if parent_font:
                text = parent_font.get_text()
                padre_match = re.search(r'\((\d+),\s*([^)]+)\)', text)
                if padre_match:
                    ano_nacimiento = padre_match.group(1)
                    padre = padre_match.group(2).strip()
            
            resultado = {
                'hipodromo': 'Hipódromo Chile',
                'codigo_hipodromo': 'HC',
                'fecha': fecha_reunion,
                'reunion': reunion_info,
                'carrera': num_carrera,
                'hora': hora,
                'distancia': distancia,
                'tipo': tipo,
                'grado': grado,
                'condicion': condicion,
                'posicion': i + 1,
                'caballo': nombre,
                'ano_nacimiento': ano_nacimiento,
                'padre': padre,
            }
            resultados.append(resultado)
        
        return resultados
    
    # ========================================================================
    # CLUB HÍPICO DE SANTIAGO - RESULTADOS
    # ========================================================================
    
    def obtener_resultados_club_hipico(self, fecha: str = None) -> List[Dict]:
        """Extrae resultados del Club Hípico de Santiago con ventana de tiempo."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 CLUB HÍPICO DE SANTIAGO - RESULTADOS")
        self.logger.info(f"   📅 Ventana: últimos {self.config.resultados_dias_atras} días")
        self.logger.info("=" * 60)
        
        self._reset_stats()
        hipo = HIPODROMOS['CHS']
        
        fecha_hoy = FechaUtils.hoy()
        fecha_limite = fecha_hoy - timedelta(days=self.config.resultados_dias_atras)
        self.logger.info(f"   📆 Rango válido: {FechaUtils.formato_fecha(fecha_limite)} → {FechaUtils.formato_fecha(fecha_hoy)}")
        
        url = hipo.resultados_url
        if fecha:
            url = f"{url}?fecha={fecha}"
        
        html = self._get_html(url, 'table.b-table')
        
        if not html:
            return []
        
        self._save_html(html, 'CHS_resultados_v3.html')
        soup = BeautifulSoup(html, 'lxml')
        resultados = []
        
        tablas = soup.select('table.b-table')
        self.logger.info(f"   📋 Tablas encontradas: {len(tablas)}")
        
        for tabla in tablas:
            rows = tabla.select('tbody.r-title-12 tr')
            
            for row in rows:
                cells = row.select('td')
                if len(cells) < 10:
                    continue
                
                resultado = self._parse_fila_chs_con_filtro(cells, fecha_limite, fecha_hoy)
                
                if resultado:
                    if resultado.get('_estado_fecha') == 'valida':
                        del resultado['_estado_fecha']
                        resultados.append(resultado)
                        self.stats['procesados'] += 1
                    elif resultado.get('_estado_fecha') == 'antigua':
                        self.stats['filtrados_antiguos'] += 1
                    elif resultado.get('_estado_fecha') == 'futura':
                        self.stats['filtrados_futuros'] += 1
        
        self.logger.info(f"   ✅ Registros en rango: {len(resultados)}")
        self._mostrar_stats_filtrado()
        
        return resultados
    
    def _parse_fila_chs_con_filtro(self, cells, fecha_limite: datetime, fecha_hoy: datetime) -> Optional[Dict]:
        """Parsea una fila de CHS con validación de fecha"""
        try:
            fecha_cell = cells[0]
            fecha_link = fecha_cell.select_one('a')
            if fecha_link:
                fecha_text = fecha_link.get_text(strip=True)
                href = fecha_link.get('href', '')
                carrera_match = re.search(r'carrera=(\d+)', href)
                num_carrera = int(carrera_match.group(1)) if carrera_match else 0
            else:
                fecha_text = fecha_cell.get_text(strip=True)
                num_carrera = 0
            
            fecha_dt = FechaUtils.parse_fecha(fecha_text)
            estado_fecha = 'valida'
            
            if fecha_dt:
                if fecha_dt > fecha_hoy:
                    estado_fecha = 'futura'
                elif fecha_dt < fecha_limite:
                    estado_fecha = 'antigua'
            else:
                self.stats['errores_fecha'] += 1
            
            posicion = cells[2].get_text(strip=True)
            peso_fs = cells[3].get_text(strip=True)
            
            jinete_peso = cells[4].get_text(strip=True)
            jinete_match = re.match(r'([A-Z\.\s]+)\s*/\s*(\d+)\s*Kg', jinete_peso)
            if jinete_match:
                jinete = jinete_match.group(1).strip()
                peso_jinete = jinete_match.group(2)
            else:
                jinete = jinete_peso
                peso_jinete = ""
            
            distancia = cells[5].get_text(strip=True)
            
            ganador_cell = cells[6]
            ganador_link = ganador_cell.select_one('a')
            if ganador_link:
                ganador = ganador_link.get_text(strip=True)
                href = ganador_link.get('href', '')
                rut_match = re.search(r'fs_rut=(\d+)', href)
                ganador_rut = rut_match.group(1) if rut_match else ""
            else:
                ganador = ganador_cell.get_text(strip=True)
                ganador_rut = ""
            
            indice = cells[7].get_text(strip=True)
            dividendo = cells[8].get_text(strip=True)
            tiempo = cells[9].get_text(strip=True)
            
            pres_cell = cells[1]
            pista_img = pres_cell.select_one('img.img-pista-mini')
            pista = ""
            if pista_img:
                src = pista_img.get('src', '')
                if 'a-' in src:
                    pista = "Arena"
                elif 'p-' in src:
                    pista = "Pasto"
            
            mandil = ""
            mandil_label = pres_cell.select_one('label.mini-mandil')
            if mandil_label:
                mandil = mandil_label.get_text(strip=True)
            
            es_ganador = 'bg-secondary' in (cells[0].parent.get('class', []) if cells[0].parent else [])
            
            return {
                '_estado_fecha': estado_fecha,
                'hipodromo': 'Club Hípico de Santiago',
                'codigo_hipodromo': 'CHS',
                'fecha': fecha_text,
                'carrera': num_carrera,
                'posicion': posicion,
                'peso_fs': peso_fs,
                'jinete': jinete,
                'peso_jinete': peso_jinete,
                'distancia_cpos': distancia,
                'ganador': ganador,
                'ganador_rut': ganador_rut,
                'indice': indice,
                'dividendo': dividendo,
                'tiempo': tiempo,
                'pista': pista,
                'mandil': mandil,
                'es_victoria': es_ganador,
            }
            
        except Exception as e:
            self.logger.debug(f"   Error parseando fila CHS: {e}")
            return None
    
    # ========================================================================
    # HIPÓDROMO CHILE - PROGRAMAS + PDFs
    # ========================================================================
    
    def obtener_programas_hipodromo_chile(self) -> Tuple[List[Dict], List[str]]:
        """
        Extrae programas del Hipódromo Chile y descarga PDFs.
        
        Returns:
            Tuple[List[Dict], List[str]]: (programas, fechas_procesadas)
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("🔮 HIPÓDROMO CHILE - PROGRAMAS")
        self.logger.info(f"   📅 Límite: próximas {self.config.programas_max_jornadas} jornadas")
        if self.config.descargar_pdfs:
            self.logger.info("   📥 Descarga de PDFs: ACTIVADA")
        self.logger.info("=" * 60)
        
        self._reset_stats()
        hipo = HIPODROMOS['HC']
        fecha_hoy = FechaUtils.hoy()
        
        html = self._get_html(hipo.programas_url, 'table.table-hover')
        
        if not html:
            return [], []
        
        self._save_html(html, 'HC_programas_v3.html')
        soup = BeautifulSoup(html, 'lxml')
        
        # ✨ NUEVO: Buscar y descargar PDFs
        if self.config.descargar_pdfs:
            self._descargar_pdfs_hipodromo_chile(soup, hipo)
        
        # Extraer fechas de programas
        fechas_encontradas = self._extraer_fechas_programas_hc(soup)
        
        if not fechas_encontradas:
            self.logger.warning("   ⚠️ No se encontraron fechas de programas")
            return [], []
        
        self.logger.info(f"   📋 Fechas encontradas: {len(fechas_encontradas)}")
        
        # Filtrar solo fechas futuras
        fechas_futuras = []
        for fecha_dt, info in fechas_encontradas:
            if fecha_dt >= fecha_hoy:
                fechas_futuras.append((fecha_dt, info))
                self.logger.debug(f"      ✓ {FechaUtils.formato_fecha(fecha_dt)} (futura)")
            else:
                self.stats['filtrados_antiguos'] += 1
                self.logger.debug(f"      ✗ {FechaUtils.formato_fecha(fecha_dt)} (pasada)")
        
        if not fechas_futuras:
            self.logger.warning("   ⚠️ No hay programas futuros disponibles")
            self._mostrar_stats_filtrado()
            return [], []
        
        # Ordenar por cercanía
        fechas_futuras.sort(key=lambda x: x[0])
        
        self.logger.info(f"   ✅ Fechas futuras válidas: {len(fechas_futuras)}")
        for fecha_dt, _ in fechas_futuras:
            dias_hasta = (fecha_dt - fecha_hoy).days
            self.logger.info(f"      📅 {FechaUtils.formato_fecha(fecha_dt)} (en {dias_hasta} días)")
        
        # Seleccionar TOP N jornadas
        fechas_seleccionadas = fechas_futuras[:self.config.programas_max_jornadas]
        
        self.logger.info(f"\n   🎯 Procesando TOP {len(fechas_seleccionadas)} jornadas:")
        
        todos_programas = []
        fechas_procesadas = []
        
        for i, (fecha_dt, info) in enumerate(fechas_seleccionadas, 1):
            fecha_str = FechaUtils.formato_fecha(fecha_dt)
            fechas_procesadas.append(fecha_str)
            self.logger.info(f"\n   [{i}/{len(fechas_seleccionadas)}] 📅 {fecha_str}")
            
            programas_fecha = self._extraer_programas_fecha_hc(soup, fecha_dt, info)
            
            if programas_fecha:
                todos_programas.extend(programas_fecha)
                self.stats['procesados'] += len(programas_fecha)
                self.logger.info(f"       ✅ {len(programas_fecha)} carreras extraídas")
            else:
                self.logger.warning(f"       ⚠️ Sin carreras para esta fecha")
        
        self.logger.info(f"\n   ✅ Total programas: {len(todos_programas)}")
        self._mostrar_stats_filtrado()
        
        return todos_programas, fechas_procesadas
    
    def _descargar_pdfs_hipodromo_chile(self, soup: BeautifulSoup, hipo: Hipodromo):
        """Busca y descarga PDFs del Hipódromo Chile"""
        self.logger.info("\n   📥 BUSCANDO PDFs EN HIPÓDROMO CHILE...")
        
        # Buscar PDFs en la página
        pdfs = self._buscar_links_pdf(soup, hipo.base_url)
        
        if not pdfs:
            self.logger.info("   ℹ️ No se encontraron links directos a PDFs")
            # Buscar botones específicos de HC
            self._buscar_pdfs_especificos_hc(soup, hipo)
            return
        
        self.logger.info(f"   📄 PDFs encontrados: {len(pdfs)}")
        
        for pdf_info in pdfs:
            # Determinar nombre del archivo
            texto = pdf_info.get('texto', 'programa')
            fecha_str = self._extraer_fecha_de_texto(texto)
            
            if fecha_str:
                nombre = f"HC_programa_{fecha_str}"
            else:
                nombre = f"HC_programa_{texto[:30]}"
            
            self._descargar_pdf(pdf_info['url'], nombre, 'HC')
    
    def _buscar_pdfs_especificos_hc(self, soup: BeautifulSoup, hipo: Hipodromo):
        """Busca PDFs en elementos específicos de Hipódromo Chile"""
        # Buscar botones con clase btn que tengan links a programas
        botones = soup.select('a.btn, button.btn, .btn-programa, .descargar-programa')
        
        for boton in botones:
            href = boton.get('href', '')
            onclick = boton.get('onclick', '')
            texto = boton.get_text(strip=True).lower()
            
            if 'programa' in texto or 'pdf' in texto or 'descargar' in texto:
                url = None
                
                if href and href != '#':
                    url = href if href.startswith('http') else urljoin(hipo.base_url, href)
                elif onclick:
                    match = re.search(r"['\"]([^'\"]+)['\"]", onclick)
                    if match:
                        url = match.group(1)
                        url = url if url.startswith('http') else urljoin(hipo.base_url, url)
                
                if url:
                    nombre = f"HC_programa_{datetime.now().strftime('%Y%m%d')}"
                    self._descargar_pdf(url, nombre, 'HC')
        
        # Buscar en iframes o embeds
        iframes = soup.select('iframe[src*="pdf"], embed[src*="pdf"]')
        for iframe in iframes:
            src = iframe.get('src', '')
            if src:
                url = src if src.startswith('http') else urljoin(hipo.base_url, src)
                nombre = f"HC_programa_embed_{datetime.now().strftime('%Y%m%d')}"
                self._descargar_pdf(url, nombre, 'HC')
    
    def _extraer_fechas_programas_hc(self, soup: BeautifulSoup) -> List[Tuple[datetime, Dict]]:
        """Extrae todas las fechas de programas de HC"""
        fechas = []
        
        titulos = soup.select('h1.tituloshome')
        for titulo in titulos:
            texto = titulo.get_text(strip=True)
            fecha_dt = FechaUtils.parse_fecha(texto)
            if fecha_dt:
                fechas.append((fecha_dt, {'titulo': texto, 'elemento': titulo}))
        
        # Eliminar duplicados
        fechas_unicas = []
        fechas_vistas = set()
        for fecha_dt, info in fechas:
            fecha_str = FechaUtils.formato_fecha(fecha_dt)
            if fecha_str not in fechas_vistas:
                fechas_vistas.add(fecha_str)
                fechas_unicas.append((fecha_dt, info))
        
        return fechas_unicas
    
    def _extraer_programas_fecha_hc(self, soup: BeautifulSoup, fecha: datetime, info: Dict) -> List[Dict]:
        """Extrae programas de una fecha específica de HC"""
        programas = []
        fecha_str = FechaUtils.formato_fecha(fecha)
        reunion_info = info.get('titulo', '')
        
        tabla = soup.select_one('table.table-hover')
        if not tabla:
            return []
        
        tbodies = tabla.select('tbody')
        
        for tbody in tbodies:
            rows = tbody.select('tr')
            for row in rows:
                programa = self._parse_fila_programa_hc(row, fecha_str, reunion_info)
                if programa:
                    programas.append(programa)
        
        return programas
    
    def _parse_fila_programa_hc(self, row, fecha: str, reunion_info: str) -> Optional[Dict]:
        """Parsea una fila de programa de HC"""
        cells = row.select('td')
        if len(cells) < 5:
            return None
        
        num_text = cells[0].get_text(strip=True).replace('ª', '').strip()
        if not num_text.isdigit():
            return None
        
        num_carrera = int(num_text)
        hora = cells[1].get_text(strip=True) if len(cells) > 1 else ""
        
        distancia = ""
        dist_cell = row.select_one('td.visible-lg')
        if dist_cell:
            dist_text = dist_cell.get_text(strip=True)
            dist_match = re.search(r'(\d+)', dist_text)
            if dist_match:
                distancia = dist_match.group(1)
        
        cond_cell = row.select_one('td.condicion')
        condicion = cond_cell.get_text(strip=True) if cond_cell else ""
        
        return {
            'hipodromo': 'Hipódromo Chile',
            'codigo_hipodromo': 'HC',
            'fecha': fecha,
            'reunion': reunion_info,
            'carrera': num_carrera,
            'hora': hora,
            'distancia': distancia,
            'condicion': condicion,
        }
    
    # ========================================================================
    # CLUB HÍPICO DE SANTIAGO - PROGRAMAS + PDFs
    # ========================================================================
    
    def obtener_programas_club_hipico(self) -> Tuple[List[Dict], List[str]]:
        """
        Extrae programas del Club Hípico de Santiago y descarga PDFs.
        
        Returns:
            Tuple[List[Dict], List[str]]: (programas, fechas_procesadas)
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("🔮 CLUB HÍPICO DE SANTIAGO - PROGRAMAS")
        self.logger.info(f"   📅 Límite: próximas {self.config.programas_max_jornadas} jornadas")
        if self.config.descargar_pdfs:
            self.logger.info("   📥 Descarga de PDFs: ACTIVADA")
        self.logger.info("=" * 60)
        
        self._reset_stats()
        hipo = HIPODROMOS['CHS']
        fecha_hoy = FechaUtils.hoy()
        
        html = self._get_html(hipo.programas_url, 'table')
        
        if not html:
            return [], []
        
        self._save_html(html, 'CHS_programas_v3.html')
        soup = BeautifulSoup(html, 'lxml')
        
        # ✨ NUEVO: Buscar y descargar PDFs
        if self.config.descargar_pdfs:
            self._descargar_pdfs_club_hipico(soup, hipo)
        
        # === PASO 1: Identificar todas las fechas disponibles ===
        fechas_encontradas = self._extraer_fechas_programas_chs(soup)
        
        if not fechas_encontradas:
            self.logger.warning("   ⚠️ No se encontraron fechas de programas")
            # Intentar extraer de la página actual
            return self._extraer_programa_actual_chs(soup)
        
        self.logger.info(f"   📋 Fechas encontradas: {len(fechas_encontradas)}")
        
        # === PASO 2: Filtrar solo fechas FUTURAS ===
        fechas_futuras = []
        for fecha_dt, info in fechas_encontradas:
            if fecha_dt >= fecha_hoy:
                fechas_futuras.append((fecha_dt, info))
                dias_hasta = (fecha_dt - fecha_hoy).days
                self.logger.info(f"      ✓ {FechaUtils.formato_fecha(fecha_dt)} (en {dias_hasta} días)")
            else:
                self.stats['filtrados_antiguos'] += 1
                self.logger.debug(f"      ✗ {FechaUtils.formato_fecha(fecha_dt)} (pasada)")
        
        if not fechas_futuras:
            self.logger.warning("   ⚠️ No hay programas futuros disponibles")
            self._mostrar_stats_filtrado()
            return [], []
        
        # === PASO 3: Ordenar de más cercana a más lejana ===
        fechas_futuras.sort(key=lambda x: x[0])
        
        self.logger.info(f"\n   ✅ Fechas futuras válidas: {len(fechas_futuras)}")
        
        # === PASO 4: Seleccionar TOP N jornadas ===
        fechas_seleccionadas = fechas_futuras[:self.config.programas_max_jornadas]
        
        self.logger.info(f"   🎯 Procesando TOP {len(fechas_seleccionadas)} jornadas:")
        
        # === PASO 5: Scrapear cada jornada seleccionada ===
        todos_programas = []
        fechas_procesadas = []
        
        for i, (fecha_dt, info) in enumerate(fechas_seleccionadas, 1):
            fecha_str = FechaUtils.formato_fecha(fecha_dt)
            fechas_procesadas.append(fecha_str)
            
            self.logger.info(f"\n   [{i}/{len(fechas_seleccionadas)}] 📅 {fecha_str}")
            
            # Cargar página de la fecha específica si tiene URL
            if info.get('url'):
                html_fecha = self._get_html(info['url'], 'table')
                if html_fecha:
                    soup_fecha = BeautifulSoup(html_fecha, 'lxml')
                    
                    # ✨ Buscar PDFs en la página de la fecha específica
                    if self.config.descargar_pdfs:
                        self._descargar_pdfs_club_hipico(soup_fecha, hipo, fecha_str)
                    
                    programas_fecha = self._extraer_carreras_programa_chs(soup_fecha, fecha_str)
                else:
                    programas_fecha = []
            else:
                programas_fecha = self._extraer_carreras_programa_chs(soup, fecha_str)
            
            if programas_fecha:
                todos_programas.extend(programas_fecha)
                self.stats['procesados'] += len(programas_fecha)
                self.logger.info(f"       ✅ {len(programas_fecha)} carreras extraídas")
            else:
                self.logger.warning(f"       ⚠️ Sin carreras para esta fecha")
        
        self.logger.info(f"\n   ✅ Total programas CHS: {len(todos_programas)}")
        self._mostrar_stats_filtrado()
        
        return todos_programas, fechas_procesadas
    
    def _descargar_pdfs_club_hipico(self, soup: BeautifulSoup, hipo: Hipodromo, fecha_str: str = None):
        """Busca y descarga PDFs del Club Hípico de Santiago"""
        self.logger.info("\n   📥 BUSCANDO PDFs EN CLUB HÍPICO...")
        
        # Buscar PDFs generales
        pdfs = self._buscar_links_pdf(soup, hipo.base_url)
        
        # Buscar links específicos de CHS
        self._buscar_pdfs_especificos_chs(soup, hipo, pdfs)
        
        if not pdfs:
            self.logger.info("   ℹ️ No se encontraron PDFs en esta página")
            return
        
        self.logger.info(f"   📄 PDFs encontrados: {len(pdfs)}")
        
        for pdf_info in pdfs:
            # Determinar nombre del archivo
            texto = pdf_info.get('texto', 'programa')
            
            # Usar fecha proporcionada o extraer del texto
            if fecha_str:
                fecha_archivo = fecha_str.replace('-', '')
            else:
                fecha_archivo = self._extraer_fecha_de_texto(texto) or datetime.now().strftime('%Y%m%d')
            
            # Determinar tipo de documento
            texto_lower = texto.lower()
            if 'oficial' in texto_lower:
                tipo = 'oficial'
            elif 'recorrido' in texto_lower:
                tipo = 'recorrido'
            elif 'partidor' in texto_lower or 'partida' in texto_lower:
                tipo = 'partidores'
            else:
                tipo = 'programa'
            
            nombre = f"CHS_{tipo}_{fecha_archivo}"
            self._descargar_pdf(pdf_info['url'], nombre, 'CHS')
    
    def _buscar_pdfs_especificos_chs(self, soup: BeautifulSoup, hipo: Hipodromo, pdfs: List[Dict]):
        """Busca PDFs en elementos específicos del Club Hípico"""
        # Buscar en la sección de descargas
        secciones_descarga = soup.select('.descargas, .downloads, .programa-pdf, .documentos')
        
        for seccion in secciones_descarga:
            links = seccion.select('a')
            for link in links:
                href = link.get('href', '')
                if href and '.pdf' in href.lower():
                    url = href if href.startswith('http') else urljoin(hipo.base_url, href)
                    pdfs.append({
                        'url': url,
                        'texto': link.get_text(strip=True) or 'documento',
                        'seccion': 'descargas'
                    })
        
        # Buscar botones con iconos de PDF
        botones_pdf = soup.select('a[href*="pdf"], button[onclick*="pdf"], .btn-pdf, .pdf-link')
        
        for boton in botones_pdf:
            href = boton.get('href', '')
            onclick = boton.get('onclick', '')
            
            url = None
            if href and 'pdf' in href.lower():
                url = href if href.startswith('http') else urljoin(hipo.base_url, href)
            elif onclick:
                match = re.search(r"['\"]([^'\"]*pdf[^'\"]*)['\"]", onclick, re.IGNORECASE)
                if match:
                    url = match.group(1)
                    url = url if url.startswith('http') else urljoin(hipo.base_url, url)
            
            if url and url not in [p['url'] for p in pdfs]:
                pdfs.append({
                    'url': url,
                    'texto': boton.get_text(strip=True) or 'documento',
                    'es_boton': True
                })
        
        # Buscar en data attributes
        elementos_data = soup.select('[data-pdf-url], [data-href*="pdf"]')
        for elem in elementos_data:
            url = elem.get('data-pdf-url') or elem.get('data-href')
            if url:
                url = url if url.startswith('http') else urljoin(hipo.base_url, url)
                if url not in [p['url'] for p in pdfs]:
                    pdfs.append({
                        'url': url,
                        'texto': elem.get_text(strip=True) or 'documento',
                        'es_data_attr': True
                    })
    
    def _extraer_fechas_programas_chs(self, soup: BeautifulSoup) -> List[Tuple[datetime, Dict]]:
        """Extrae todas las fechas de programas disponibles en CHS"""
        fechas = []
        
        # Buscar en títulos y encabezados
        for selector in ['h1', 'h2', 'h3', '.titulo', '.fecha-reunion', '.date-title']:
            elementos = soup.select(selector)
            for elem in elementos:
                texto = elem.get_text(strip=True)
                fecha_dt = FechaUtils.parse_fecha(texto)
                if fecha_dt:
                    fechas.append((fecha_dt, {'titulo': texto, 'elemento': elem}))
        
        # Buscar links que contengan fechas en href o texto
        links = soup.select('a[href*="fecha"], a[href*="date"], a[href*="programa"]')
        for link in links:
            texto = link.get_text(strip=True)
            href = link.get('href', '')
            
            # Intentar parsear del texto
            fecha_dt = FechaUtils.parse_fecha(texto)
            if fecha_dt:
                full_url = href if href.startswith('http') else urljoin(HIPODROMOS['CHS'].base_url, href)
                fechas.append((fecha_dt, {'titulo': texto, 'url': full_url}))
                continue
            
            # Intentar parsear del href
            fecha_match = re.search(r'fecha=(\d{4}-\d{2}-\d{2})', href)
            if fecha_match:
                fecha_dt = FechaUtils.parse_fecha(fecha_match.group(1))
                if fecha_dt:
                    full_url = href if href.startswith('http') else urljoin(HIPODROMOS['CHS'].base_url, href)
                    fechas.append((fecha_dt, {'titulo': texto, 'url': full_url}))
        
        # Buscar en selectores/dropdowns de fecha
        selects = soup.select('select[name*="fecha"], select.fecha-select')
        for select in selects:
            options = select.select('option')
            for opt in options:
                valor = opt.get('value', '')
                fecha_dt = FechaUtils.parse_fecha(valor)
                if fecha_dt:
                    fechas.append((fecha_dt, {'titulo': opt.get_text(strip=True), 'value': valor}))
        
        # Eliminar duplicados
        fechas_unicas = []
        fechas_vistas = set()
        for fecha_dt, info in fechas:
            fecha_str = FechaUtils.formato_fecha(fecha_dt)
            if fecha_str not in fechas_vistas:
                fechas_vistas.add(fecha_str)
                fechas_unicas.append((fecha_dt, info))
        
        return fechas_unicas
    
    def _extraer_programa_actual_chs(self, soup: BeautifulSoup) -> Tuple[List[Dict], List[str]]:
        """Extrae el programa de la página actual de CHS cuando no hay lista de fechas"""
        self.logger.info("   ℹ️ Extrayendo programa de página actual...")
        
        fecha_hoy = FechaUtils.formato_fecha(FechaUtils.hoy())
        
        # Buscar fecha en la página
        fecha_encontrada = None
        for selector in ['h1', 'h2', '.titulo', '.fecha']:
            elem = soup.select_one(selector)
            if elem:
                fecha_dt = FechaUtils.parse_fecha(elem.get_text())
                if fecha_dt:
                    fecha_encontrada = FechaUtils.formato_fecha(fecha_dt)
                    break
        
        if not fecha_encontrada:
            fecha_encontrada = fecha_hoy
        
        programas = self._extraer_carreras_programa_chs(soup, fecha_encontrada)
        
        fechas_procesadas = [fecha_encontrada] if programas else []
        
        return programas, fechas_procesadas
    
    def _extraer_carreras_programa_chs(self, soup: BeautifulSoup, fecha: str) -> List[Dict]:
        """Extrae las carreras de un programa de CHS"""
        programas = []
        
        # Buscar tablas de programa
        tablas = soup.select('table.b-table, table.table, table.programa')
        
        for tabla in tablas:
            rows = tabla.select('tbody tr, tr')
            
            for row in rows:
                cells = row.select('td')
                if len(cells) < 3:
                    continue
                
                programa = self._parse_fila_programa_chs(cells, fecha)
                if programa:
                    programas.append(programa)
        
        # Si no encontró en tablas, buscar en otros formatos
        if not programas:
            carreras_divs = soup.select('.carrera, .race-card, [class*="carrera"]')
            for i, div in enumerate(carreras_divs, 1):
                programa = {
                    'hipodromo': 'Club Hípico de Santiago',
                    'codigo_hipodromo': 'CHS',
                    'fecha': fecha,
                    'carrera': i,
                    'hora': '',
                    'distancia': '',
                    'condicion': '',
                    'descripcion': div.get_text(strip=True)[:100]
                }
                programas.append(programa)
        
        return programas
    
    def _parse_fila_programa_chs(self, cells, fecha: str) -> Optional[Dict]:
        """Parsea una fila de programa de CHS"""
        try:
            num_carrera = 0
            hora = ""
            distancia = ""
            condicion = ""
            
            num_text = cells[0].get_text(strip=True)
            num_match = re.search(r'(\d+)', num_text)
            if num_match:
                num_carrera = int(num_match.group(1))
            else:
                return None
            
            for cell in cells:
                text = cell.get_text(strip=True)
                hora_match = re.search(r'(\d{1,2}:\d{2})', text)
                if hora_match:
                    hora = hora_match.group(1)
                    break
            
            for cell in cells:
                text = cell.get_text(strip=True)
                dist_match = re.search(r'(\d{3,4})\s*m', text, re.IGNORECASE)
                if dist_match:
                    distancia = dist_match.group(1)
                    break
            
            for cell in cells:
                text = cell.get_text(strip=True).lower()
                if any(c in text for c in ['3a', 'h3', 'm3', 'handicap', 'condicional']):
                    condicion = cell.get_text(strip=True)
                    break
            
            return {
                'hipodromo': 'Club Hípico de Santiago',
                'codigo_hipodromo': 'CHS',
                'fecha': fecha,
                'carrera': num_carrera,
                'hora': hora,
                'distancia': distancia,
                'condicion': condicion,
            }
            
        except Exception as e:
            self.logger.debug(f"   Error parseando programa CHS: {e}")
            return None
    
    # ========================================================================
    # ESTADÍSTICAS Y UTILIDADES
    # ========================================================================
    
    def _mostrar_stats_filtrado(self):
        """Muestra estadísticas del filtrado"""
        self.logger.info("\n   📊 ESTADÍSTICAS DE FILTRADO:")
        self.logger.info(f"      ✅ Procesados:        {self.stats['procesados']}")
        self.logger.info(f"      ⏮️  Filtrados antiguos: {self.stats['filtrados_antiguos']}")
        self.logger.info(f"      ⏭️  Filtrados futuros:  {self.stats['filtrados_futuros']}")
        if self.stats['errores_fecha'] > 0:
            self.logger.info(f"      ⚠️  Errores de fecha:  {self.stats['errores_fecha']}")
        
        # ✨ NUEVO: Stats de PDFs
        if self.config.descargar_pdfs:
            self.logger.info(f"\n   📥 ESTADÍSTICAS DE PDFs:")
            self.logger.info(f"      ✅ Descargados: {self.stats['pdfs_descargados']}")
            self.logger.info(f"      ❌ Fallidos:    {self.stats['pdfs_fallidos']}")
    
    def mostrar_resumen_pdfs(self):
        """Muestra resumen de PDFs descargados"""
        if not self.pdfs_descargados:
            self.logger.info("\n   ℹ️ No se descargaron PDFs en esta sesión")
            return
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📥 RESUMEN DE PDFs DESCARGADOS")
        self.logger.info("=" * 60)
        
        total_size = sum(p['size_kb'] for p in self.pdfs_descargados)
        
        # Agrupar por hipódromo
        por_hipodromo = {}
        for pdf in self.pdfs_descargados:
            hip = pdf['hipodromo']
            if hip not in por_hipodromo:
                por_hipodromo[hip] = []
            por_hipodromo[hip].append(pdf)
        
        for hip, pdfs in por_hipodromo.items():
            self.logger.info(f"\n   📁 {HIPODROMOS[hip].nombre}:")
            for pdf in pdfs:
                self.logger.info(f"      📄 {pdf['archivo']} ({pdf['size_kb']} KB)")
        
        self.logger.info(f"\n   📊 Total: {len(self.pdfs_descargados)} PDFs ({total_size:.1f} KB)")
        self.logger.info(f"   📂 Ubicación: {os.path.abspath(self.config.pdf_dir)}")
    
    # ========================================================================
    # MÉTODOS DE CONVENIENCIA
    # ========================================================================
    
    def obtener_todos_resultados(self) -> Tuple[List[Dict], List[Dict]]:
        """Obtiene resultados de ambos hipódromos"""
        self.logger.info("\n" + "=" * 70)
        self.logger.info(f"📊 OBTENIENDO TODOS LOS RESULTADOS (últimos {self.config.resultados_dias_atras} días)")
        self.logger.info("=" * 70)
        
        resultados_hc = self.obtener_resultados_hipodromo_chile()
        resultados_chs = self.obtener_resultados_club_hipico()
        
        return resultados_hc, resultados_chs
    
    def obtener_todos_programas(self) -> Tuple[List[Dict], List[Dict], Dict[str, List[str]]]:
        """
        Obtiene programas de ambos hipódromos y descarga PDFs.
        
        Returns:
            Tuple: (programas_hc, programas_chs, fechas_dict)
        """
        self.logger.info("\n" + "=" * 70)
        self.logger.info(f"🔮 OBTENIENDO TODOS LOS PROGRAMAS (próximas {self.config.programas_max_jornadas} jornadas)")
        if self.config.descargar_pdfs:
            self.logger.info("📥 DESCARGA DE PDFs: ACTIVADA")
        self.logger.info("=" * 70)
        
        # Limpiar lista de PDFs
        self.pdfs_descargados = []
        
        prog_hc, fechas_hc = self.obtener_programas_hipodromo_chile()
        prog_chs, fechas_chs = self.obtener_programas_club_hipico()
        
        fechas_dict = {
            'HC': fechas_hc,
            'CHS': fechas_chs
        }
        
        # Mostrar resumen de PDFs
        if self.config.descargar_pdfs:
            self.mostrar_resumen_pdfs()
        
        return prog_hc, prog_chs, fechas_dict
    
    # ========================================================================
    # EXPORTACIÓN
    # ========================================================================
    
    def exportar_csv(self, datos: List[Dict], nombre_base: str, incluir_fechas: bool = True) -> str:
        """Exporta datos a CSV con fechas en el nombre del archivo"""
        if not datos:
            self.logger.warning("⚠️ No hay datos para exportar")
            return ""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if incluir_fechas and 'fecha' in datos[0]:
            fechas = [d['fecha'] for d in datos if d.get('fecha')]
            rango_fechas = FechaUtils.rango_fechas_str(fechas)
            filename = f"{nombre_base}_{rango_fechas}_{timestamp}.csv"
        else:
            filename = f"{nombre_base}_{timestamp}.csv"
        
        path = os.path.join(self.config.output_dir, filename)
        
        df = pd.DataFrame(datos)
        df.to_csv(path, index=False, encoding='utf-8-sig')
        
        self.logger.info(f"📁 Exportado: {path}")
        
        if 'fecha' in datos[0]:
            fechas_unicas = sorted(set(d['fecha'] for d in datos if d.get('fecha')))
            self.logger.info(f"   📅 Fechas incluidas: {', '.join(fechas_unicas)}")
        
        return path
    
    def exportar_excel(self, datos_hc: List[Dict] = None, datos_chs: List[Dict] = None,
                       programas_hc: List[Dict] = None, programas_chs: List[Dict] = None,
                       fechas_programas: Dict[str, List[str]] = None) -> str:
        """Exporta a Excel con múltiples hojas"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        todas_fechas = []
        if fechas_programas:
            for fechas in fechas_programas.values():
                todas_fechas.extend(fechas)
        
        if todas_fechas:
            rango = FechaUtils.rango_fechas_str(todas_fechas)
            filename = f"pista_inteligente_programas_{rango}_{timestamp}.xlsx"
        else:
            filename = f"pista_inteligente_{timestamp}.xlsx"
        
        path = os.path.join(self.config.output_dir, filename)
        
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            if datos_hc:
                df = pd.DataFrame(datos_hc)
                df.to_excel(writer, sheet_name='HC_Resultados', index=False)
            
            if datos_chs:
                df = pd.DataFrame(datos_chs)
                df.to_excel(writer, sheet_name='CHS_Resultados', index=False)
            
            if programas_hc:
                df = pd.DataFrame(programas_hc)
                df.to_excel(writer, sheet_name='HC_Programas', index=False)
            
            if programas_chs:
                df = pd.DataFrame(programas_chs)
                df.to_excel(writer, sheet_name='CHS_Programas', index=False)
            
            # ✨ NUEVO: Hoja de PDFs descargados
            if self.pdfs_descargados:
                df_pdfs = pd.DataFrame(self.pdfs_descargados)
                df_pdfs.to_excel(writer, sheet_name='PDFs_Descargados', index=False)
            
            # Hoja de resumen
            resumen_data = {
                'Métrica': [
                    'Fecha de extracción',
                    'Ventana resultados (días)',
                    'Límite programas (jornadas)',
                    'Total HC Resultados',
                    'Total CHS Resultados',
                    'Total HC Programas',
                    'Total CHS Programas',
                    'PDFs descargados',
                ],
                'Valor': [
                    datetime.now().strftime('%Y-%m-%d %H:%M'),
                    self.config.resultados_dias_atras,
                    self.config.programas_max_jornadas,
                    len(datos_hc) if datos_hc else 0,
                    len(datos_chs) if datos_chs else 0,
                    len(programas_hc) if programas_hc else 0,
                    len(programas_chs) if programas_chs else 0,
                    len(self.pdfs_descargados),
                ]
            }
            
            if fechas_programas:
                for hip, fechas in fechas_programas.items():
                    if fechas:
                        resumen_data['Métrica'].append(f'Fechas programas {hip}')
                        resumen_data['Valor'].append(', '.join(fechas))
            
            df_resumen = pd.DataFrame(resumen_data)
            df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
        
        self.logger.info(f"📁 Excel exportado: {path}")
        
        return path
    
    def close(self):
        if self.driver:
            self.driver.quit()
        self.logger.info("🔒 Bot cerrado")
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


# ============================================================================
# INTERFAZ DE LÍNEA DE COMANDOS
# ============================================================================

def mostrar_menu():
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   🏇  PISTA INTELIGENTE - BOT OPTIMIZADO V3.2                            ║
║                                                                           ║
║   "A cobrar los que saben"                                                ║
║                                                                           ║
║   ⏰ FILTROS DE TIEMPO:                                                   ║
║   • Resultados: últimos 30 días (con BREAK si más antiguo)                ║
║   • Programas: próximas 3 jornadas (ordenadas por cercanía)               ║
║                                                                           ║
║   ✨ NUEVO EN V3.2:                                                       ║
║   • Descarga automática de PDFs de programas                              ║
║   • PDFs organizados por hipódromo y fecha                                ║
║                                                                           ║
║   Hipódromos: HC (Hipódromo Chile) | CHS (Club Hípico Santiago)           ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("""
═══════════════════════════════════════════════════════════════════════════
                           📊 RESULTADOS
═══════════════════════════════════════════════════════════════════════════
  1. Resultados HC  (últimos 30 días)
  2. Resultados CHS (últimos 30 días)
  3. Resultados TODOS (HC + CHS)

═══════════════════════════════════════════════════════════════════════════
                           🔮 PROGRAMAS + PDFs
═══════════════════════════════════════════════════════════════════════════
  4. Programas HC  (próximas 3 jornadas + PDFs)
  5. Programas CHS (próximas 3 jornadas + PDFs)
  6. Programas TODOS (HC + CHS + PDFs)

═══════════════════════════════════════════════════════════════════════════
                           📦 COMPLETO
═══════════════════════════════════════════════════════════════════════════
  7. TODO (Resultados + Programas + PDFs de ambos hipódromos)

═══════════════════════════════════════════════════════════════════════════
  C. Configurar ventanas de tiempo
  P. Activar/Desactivar descarga de PDFs
  0. Salir
═══════════════════════════════════════════════════════════════════════════
    """)
    return input("Selecciona opción: ").strip().upper()


def configurar_ventanas():
    """Permite configurar las ventanas de tiempo"""
    print("\n⚙️ CONFIGURACIÓN DE VENTANAS DE TIEMPO")
    print("-" * 50)
    
    try:
        dias_resultados = input("Días hacia atrás para resultados [30]: ").strip()
        dias_resultados = int(dias_resultados) if dias_resultados else 30
        
        jornadas_programas = input("Máximo jornadas futuras para programas [3]: ").strip()
        jornadas_programas = int(jornadas_programas) if jornadas_programas else 3
        
        return BotConfig(
            resultados_dias_atras=dias_resultados,
            programas_max_jornadas=jornadas_programas
        )
    except ValueError:
        print("⚠️ Valor inválido, usando configuración por defecto")
        return BotConfig()


def mostrar_resumen_fechas(datos: List[Dict], titulo: str):
    """Muestra resumen con fechas de los datos"""
    if not datos:
        return
    
    print(f"\n📊 {titulo}")
    print("-" * 50)
    
    df = pd.DataFrame(datos)
    print(f"   Total registros: {len(df)}")
    
    if 'fecha' in df.columns:
        fechas_unicas = sorted(df['fecha'].unique())
        print(f"   Fechas ({len(fechas_unicas)}):")
        for f in fechas_unicas:
            count = len(df[df['fecha'] == f])
            print(f"      📅 {f}: {count} registros")
    
    if 'carrera' in df.columns:
        carreras = df['carrera'].nunique()
        print(f"   Carreras únicas: {carreras}")


def main():
    config = BotConfig(headless=False, descargar_pdfs=True)
    
    while True:
        opcion = mostrar_menu()
        
        if opcion == '0':
            print("\n👋 ¡Hasta pronto! Que ganen los que saben 🏇")
            break
        
        if opcion == 'C':
            config = configurar_ventanas()
            print(f"\n✅ Configuración actualizada:")
            print(f"   • Resultados: últimos {config.resultados_dias_atras} días")
            print(f"   • Programas: próximas {config.programas_max_jornadas} jornadas")
            input("\nPresiona Enter para continuar...")
            continue
        
        if opcion == 'P':
            config.descargar_pdfs = not config.descargar_pdfs
            estado = "ACTIVADA" if config.descargar_pdfs else "DESACTIVADA"
            print(f"\n📥 Descarga de PDFs: {estado}")
            input("\nPresiona Enter para continuar...")
            continue
        
        with PistaInteligenteBot(config) as bot:
            
            # === RESULTADOS ===
            if opcion == '1':
                resultados = bot.obtener_resultados_hipodromo_chile()
                if resultados:
                    bot.exportar_csv(resultados, "HC_resultados")
                    mostrar_resumen_fechas(resultados, "HIPÓDROMO CHILE - RESULTADOS")
            
            elif opcion == '2':
                resultados = bot.obtener_resultados_club_hipico()
                if resultados:
                    bot.exportar_csv(resultados, "CHS_resultados")
                    mostrar_resumen_fechas(resultados, "CLUB HÍPICO - RESULTADOS")
            
            elif opcion == '3':
                res_hc, res_chs = bot.obtener_todos_resultados()
                
                if res_hc:
                    bot.exportar_csv(res_hc, "HC_resultados")
                    mostrar_resumen_fechas(res_hc, "HIPÓDROMO CHILE - RESULTADOS")
                
                if res_chs:
                    bot.exportar_csv(res_chs, "CHS_resultados")
                    mostrar_resumen_fechas(res_chs, "CLUB HÍPICO - RESULTADOS")
                
                if res_hc or res_chs:
                    bot.exportar_excel(datos_hc=res_hc, datos_chs=res_chs)
            
            # === PROGRAMAS + PDFs ===
            elif opcion == '4':
                programas, fechas = bot.obtener_programas_hipodromo_chile()
                if programas:
                    bot.exportar_csv(programas, "HC_programas")
                    mostrar_resumen_fechas(programas, "HIPÓDROMO CHILE - PROGRAMAS")
                    print(f"\n   🎯 Jornadas procesadas: {', '.join(fechas)}")
                bot.mostrar_resumen_pdfs()
            
            elif opcion == '5':
                programas, fechas = bot.obtener_programas_club_hipico()
                if programas:
                    bot.exportar_csv(programas, "CHS_programas")
                    mostrar_resumen_fechas(programas, "CLUB HÍPICO - PROGRAMAS")
                    print(f"\n   🎯 Jornadas procesadas: {', '.join(fechas)}")
                bot.mostrar_resumen_pdfs()
            
            elif opcion == '6':
                prog_hc, prog_chs, fechas_dict = bot.obtener_todos_programas()
                
                if prog_hc:
                    bot.exportar_csv(prog_hc, "HC_programas")
                    mostrar_resumen_fechas(prog_hc, "HIPÓDROMO CHILE - PROGRAMAS")
                
                if prog_chs:
                    bot.exportar_csv(prog_chs, "CHS_programas")
                    mostrar_resumen_fechas(prog_chs, "CLUB HÍPICO - PROGRAMAS")
                
                if prog_hc or prog_chs:
                    bot.exportar_excel(programas_hc=prog_hc, programas_chs=prog_chs,
                                      fechas_programas=fechas_dict)
                
                print("\n" + "=" * 60)
                print("📅 RESUMEN DE JORNADAS PROCESADAS:")
                for hip, fechas in fechas_dict.items():
                    if fechas:
                        print(f"   {hip}: {', '.join(fechas)}")
            
            # === TODO ===
            elif opcion == '7':
                print("\n🚀 Ejecutando extracción completa...")
                
                # Resultados
                res_hc, res_chs = bot.obtener_todos_resultados()
                
                # Programas + PDFs
                prog_hc, prog_chs, fechas_dict = bot.obtener_todos_programas()
                
                # Exportar CSVs individuales
                if res_hc:
                    bot.exportar_csv(res_hc, "HC_resultados")
                if res_chs:
                    bot.exportar_csv(res_chs, "CHS_resultados")
                if prog_hc:
                    bot.exportar_csv(prog_hc, "HC_programas")
                if prog_chs:
                    bot.exportar_csv(prog_chs, "CHS_programas")
                
                # Exportar Excel consolidado
                bot.exportar_excel(
                    datos_hc=res_hc,
                    datos_chs=res_chs,
                    programas_hc=prog_hc,
                    programas_chs=prog_chs,
                    fechas_programas=fechas_dict
                )
                
                print("\n" + "=" * 70)
                print("✅ EXTRACCIÓN COMPLETA FINALIZADA")
                print("=" * 70)
                print(f"   📊 Resultados HC:  {len(res_hc) if res_hc else 0} registros")
                print(f"   📊 Resultados CHS: {len(res_chs) if res_chs else 0} registros")
                print(f"   🔮 Programas HC:   {len(prog_hc) if prog_hc else 0} registros")
                print(f"   🔮 Programas CHS:  {len(prog_chs) if prog_chs else 0} registros")
                print(f"   📥 PDFs descargados: {len(bot.pdfs_descargados)}")
                print("\n   📅 JORNADAS PROGRAMADAS:")
                for hip, fechas in fechas_dict.items():
                    if fechas:
                        print(f"      {hip}: {', '.join(fechas)}")
            
            else:
                print("\n⚠️ Opción no válida")
        
        input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    main()