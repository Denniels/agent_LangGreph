#!/usr/bin/env python3
"""
Smart IoT App URL Scraper - Detección Inteligente desde la App IoT
================================================================

Sistema que extrae la URL actual de Cloudflare directamente desde
la aplicación IoT de Streamlit que SIEMPRE tiene la información actualizada.

URL objetivo: https://iotapp-jvwtoekeo73ruxn9mdhfnc.streamlit.app/

ESTRATEGIAS DE DETECCIÓN:
1. 🌐 HTML Scraping directo del contenido
2. 🔍 Búsqueda de patrones específicos de Cloudflare
3. 📱 Simulación de navegador para contenido dinámico
4. 🎯 Extracción desde elementos específicos del sidebar

Compatible con GitHub Actions y ejecución local.
"""

import requests
import re
import time
import logging
from datetime import datetime
from typing import Optional, List, Dict
from urllib.parse import urljoin
import json

logger = logging.getLogger(__name__)

class SmartIoTAppScraper:
    """
    Scraper inteligente para extraer URL de Cloudflare desde la app IoT.
    """
    
    def __init__(self):
        self.iot_app_url = "https://iotapp-jvwtoekeo73ruxn9mdhfnc.streamlit.app/"
        self.timeout = 30
        self.max_retries = 3
        self.retry_delay = 2
        
        # Headers para simular navegador real
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Patrones específicos para buscar URLs de Cloudflare
        self.cloudflare_patterns = [
            # Patrones para URLs de Cloudflare
            r'https://[\w\-]+\.trycloudflare\.com',
            r'"(https://[\w\-]+\.trycloudflare\.com)"',
            r"'(https://[\w\-]+\.trycloudflare\.com)'",
            
            # Patrones específicos del contexto de la app
            r'URL pública detectada:.*?(https://[\w\-]+\.trycloudflare\.com)',
            r'API conectada:.*?(https://[\w\-]+\.trycloudflare\.com)',
            r'Jetson URL:.*?(https://[\w\-]+\.trycloudflare\.com)',
            
            # Patrones para el sidebar (según las capturas)
            r'🔗 Jetson URL:.*?(https://[\w\-]+\.trycloudflare\.com)',
            r'Configuración.*?URL.*?(https://[\w\-]+\.trycloudflare\.com)',
        ]
    
    def scrape_iot_app_content(self) -> Optional[str]:
        """
        Obtener contenido HTML de la aplicación IoT.
        
        Returns:
            Contenido HTML o None si falla
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🌐 Accediendo a la app IoT (intento {attempt + 1}/{self.max_retries})...")
                
                response = requests.get(
                    self.iot_app_url,
                    headers=self.headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                response.raise_for_status()
                
                logger.info(f"✅ Respuesta obtenida: {response.status_code}, {len(response.text)} caracteres")
                return response.text
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ Intento {attempt + 1} falló: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"❌ Falló después de {self.max_retries} intentos")
        
        return None
    
    def extract_cloudflare_urls_from_content(self, content: str) -> List[str]:
        """
        Extraer URLs de Cloudflare del contenido HTML.
        
        Args:
            content: Contenido HTML
            
        Returns:
            Lista de URLs encontradas
        """
        found_urls = set()
        
        for pattern in self.cloudflare_patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    # Limpiar la URL
                    if isinstance(match, tuple):
                        url = match[0] if match else None
                    else:
                        url = match
                    
                    if url:
                        # Limpiar caracteres no deseados
                        url = url.strip(' \'"<>[](){}')
                        
                        # Validar que sea una URL de Cloudflare válida
                        if (url.startswith('https://') and 
                            '.trycloudflare.com' in url and
                            len(url.split('/')[-1].split('.')[0]) > 10):  # Nombre suficientemente largo
                            found_urls.add(url)
                            logger.debug(f"🔍 URL encontrada con patrón '{pattern}': {url}")
                
            except Exception as e:
                logger.debug(f"Error con patrón '{pattern}': {e}")
                continue
        
        return list(found_urls)
    
    def validate_url(self, url: str) -> bool:
        """
        Validar que una URL de Cloudflare funcione.
        
        Args:
            url: URL a validar
            
        Returns:
            True si la URL responde correctamente
        """
        try:
            # Probar endpoint de salud
            health_url = f"{url.rstrip('/')}/health"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ URL válida: {url}")
                return True
            else:
                logger.debug(f"🟡 URL responde pero con código {response.status_code}: {url}")
                return False
                
        except Exception as e:
            logger.debug(f"❌ URL no válida {url}: {e}")
            return False
    
    def detect_current_cloudflare_url(self) -> Optional[str]:
        """
        Detectar la URL actual de Cloudflare desde la app IoT.
        
        Returns:
            URL actual de Cloudflare o None si no se puede detectar
        """
        logger.info("🚀 Iniciando detección de URL desde la app IoT...")
        
        # Paso 1: Obtener contenido de la app
        content = self.scrape_iot_app_content()
        if not content:
            logger.error("❌ No se pudo obtener contenido de la app IoT")
            return None
        
        # Paso 2: Extraer URLs candidatas
        candidate_urls = self.extract_cloudflare_urls_from_content(content)
        
        if not candidate_urls:
            logger.warning("⚠️ No se encontraron URLs de Cloudflare en el contenido")
            logger.debug(f"Contenido (primeros 500 chars): {content[:500]}")
            return None
        
        logger.info(f"🔍 URLs candidatas encontradas: {candidate_urls}")
        
        # Paso 3: Validar URLs
        valid_urls = []
        for url in candidate_urls:
            if self.validate_url(url):
                valid_urls.append(url)
        
        if not valid_urls:
            logger.warning("⚠️ Ninguna URL candidata es válida")
            return None
        
        # Paso 4: Retornar la primera URL válida
        selected_url = valid_urls[0]
        logger.info(f"🎯 URL seleccionada: {selected_url}")
        
        return selected_url
    
    def detect_with_detailed_report(self) -> Dict:
        """
        Detectar URL con reporte detallado.
        
        Returns:
            Diccionario con resultados detallados
        """
        start_time = time.time()
        
        result = {
            'success': False,
            'url': None,
            'timestamp': datetime.now().isoformat(),
            'execution_time': 0,
            'details': {
                'content_obtained': False,
                'content_length': 0,
                'urls_found': 0,
                'valid_urls': 0,
                'errors': []
            }
        }
        
        try:
            # Obtener contenido
            content = self.scrape_iot_app_content()
            
            if content:
                result['details']['content_obtained'] = True
                result['details']['content_length'] = len(content)
                
                # Extraer URLs
                candidate_urls = self.extract_cloudflare_urls_from_content(content)
                result['details']['urls_found'] = len(candidate_urls)
                
                # Validar URLs
                valid_urls = []
                for url in candidate_urls:
                    if self.validate_url(url):
                        valid_urls.append(url)
                
                result['details']['valid_urls'] = len(valid_urls)
                
                if valid_urls:
                    result['success'] = True
                    result['url'] = valid_urls[0]
                else:
                    result['details']['errors'].append("No se encontraron URLs válidas")
            else:
                result['details']['errors'].append("No se pudo obtener contenido de la app")
                
        except Exception as e:
            result['details']['errors'].append(str(e))
        
        result['execution_time'] = time.time() - start_time
        return result


def detect_cloudflare_url_from_iot_app() -> Optional[str]:
    """
    Función principal para detectar URL desde la app IoT.
    
    Returns:
        URL actual de Cloudflare o None
    """
    scraper = SmartIoTAppScraper()
    return scraper.detect_current_cloudflare_url()


def get_detailed_detection_report() -> Dict:
    """
    Obtener reporte detallado de la detección.
    
    Returns:
        Diccionario con resultados detallados
    """
    scraper = SmartIoTAppScraper()
    return scraper.detect_with_detailed_report()


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s'
    )
    
    print("🚀 SMART IOT APP URL SCRAPER")
    print("=" * 50)
    
    # Ejecutar detección con reporte detallado
    report = get_detailed_detection_report()
    
    print(f"\n📊 RESULTADOS:")
    print(f"  ✅ Éxito: {report['success']}")
    print(f"  🌐 URL detectada: {report['url']}")
    print(f"  ⏱️ Tiempo de ejecución: {report['execution_time']:.2f}s")
    print(f"  📄 Contenido obtenido: {report['details']['content_obtained']}")
    print(f"  📏 Tamaño contenido: {report['details']['content_length']} chars")
    print(f"  🔍 URLs encontradas: {report['details']['urls_found']}")
    print(f"  ✅ URLs válidas: {report['details']['valid_urls']}")
    
    if report['details']['errors']:
        print(f"  ❌ Errores: {report['details']['errors']}")
    
    if report['success']:
        print(f"\n🎉 ¡URL detectada exitosamente!")
        print(f"   📍 {report['url']}")
    else:
        print(f"\n⚠️ No se pudo detectar la URL automáticamente")
        print(f"   💡 Verifica que la app IoT esté funcionando correctamente")
    
    print(f"\n📅 Timestamp: {report['timestamp']}")