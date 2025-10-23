#!/usr/bin/env python3
"""
Smart Dashboard URL Extractor - Extractor Inteligente de URLs
==========================================================

Herramienta inteligente que puede extraer la URL actual de Cloudflare
desde el dashboard de Streamlit usando múltiples métodos:

1. Scraping directo del HTML
2. Esperar a que se cargue el contenido dinámico
3. Buscar patrones específicos de la aplicación
4. Validar conectividad de URLs encontradas
"""

import requests
import re
import time
import logging
from typing import Optional, List, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class SmartDashboardURLExtractor:
    """
    Extractor inteligente que puede encontrar URLs de Cloudflare
    en el dashboard incluso cuando se cargan dinámicamente.
    """
    
    def __init__(self, dashboard_url: str = "https://iotapp-jvwtoekeo73ruxn9mdhfnc.streamlit.app"):
        self.dashboard_url = dashboard_url
        self.timeout = 30
        self.retry_delay = 2
        self.max_retries = 3
    
    def extract_urls_from_html(self, html_content: str) -> List[str]:
        """
        Extraer URLs de Cloudflare del contenido HTML.
        
        Args:
            html_content: Contenido HTML de la página
            
        Returns:
            Lista de URLs encontradas
        """
        patterns = [
            # Patrones específicos para nuestra aplicación
            r'URL pública detectada.*?(https://[\w\-]+\.trycloudflare\.com)',
            r'API conectada.*?(https://[\w\-]+\.trycloudflare\.com)',
            r'Jetson URL.*?(https://[\w\-]+\.trycloudflare\.com)',
            
            # Patrones generales
            r'https://[\w\-]+\.trycloudflare\.com(?:/[^\s"\'<>]*)?',
            r'"(https://[\w\-]+\.trycloudflare\.com)"',
            r"'(https://[\w\-]+\.trycloudflare\.com)'",
            r'>(https://[\w\-]+\.trycloudflare\.com)<',
            r'\b(https://[\w\-]+\.trycloudflare\.com)\b',
        ]
        
        found_urls = set()
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            for match in matches:
                # Limpiar la URL
                url = match if isinstance(match, str) else match[0] if match else None
                if url and '.trycloudflare.com' in url:
                    # Limpiar caracteres extraños
                    url = re.sub(r'[<>"\'`]', '', url.strip())
                    # Asegurar que tenga protocolo
                    if not url.startswith('http'):
                        url = 'https://' + url
                    found_urls.add(url)
        
        return list(found_urls)
    
    def test_url_connectivity(self, url: str) -> Tuple[bool, dict]:
        """
        Probar si una URL responde correctamente.
        
        Args:
            url: URL a probar
            
        Returns:
            Tupla (funciona, metadata)
        """
        try:
            response = requests.get(
                f"{url}/health",
                timeout=10,
                allow_redirects=True,
                headers={'User-Agent': 'SmartDashboardExtractor/1.0'}
            )
            
            metadata = {
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'headers': dict(response.headers),
                'url_tested': f"{url}/health"
            }
            
            return response.status_code == 200, metadata
            
        except Exception as e:
            metadata = {
                'error': str(e),
                'url_tested': f"{url}/health"
            }
            return False, metadata
    
    def scrape_dashboard_with_retry(self) -> Tuple[Optional[str], dict]:
        """
        Hacer scraping del dashboard con reintentos y validación.
        
        Returns:
            Tupla (url_encontrada, metadata)
        """
        metadata = {
            'attempts': 0,
            'errors': [],
            'html_length': 0,
            'urls_found': [],
            'working_urls': []
        }
        
        for attempt in range(self.max_retries):
            metadata['attempts'] += 1
            
            try:
                logger.info(f"🔍 Intento {attempt + 1}/{self.max_retries}: Scraping dashboard...")
                
                # Headers más realistas
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
                
                response = requests.get(
                    self.dashboard_url,
                    headers=headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}"
                    metadata['errors'].append(error_msg)
                    logger.warning(f"  ⚠️ {error_msg}")
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return None, metadata
                
                html_content = response.text
                metadata['html_length'] = len(html_content)
                logger.debug(f"  📄 HTML obtenido: {len(html_content)} caracteres")
                
                # Extraer URLs
                found_urls = self.extract_urls_from_html(html_content)
                metadata['urls_found'] = found_urls
                
                if not found_urls:
                    error_msg = "No se encontraron URLs en el HTML"
                    metadata['errors'].append(error_msg)
                    logger.warning(f"  ⚠️ {error_msg}")
                    
                    # Si es el primer intento, esperar y reintentar
                    # (puede que la página aún se esté cargando)
                    if attempt < self.max_retries - 1:
                        logger.info(f"  ⏳ Esperando {self.retry_delay}s para que se cargue el contenido dinámico...")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return None, metadata
                
                logger.info(f"  🎯 URLs encontradas: {found_urls}")
                
                # Probar conectividad de cada URL
                for url in found_urls:
                    logger.debug(f"  🔍 Probando: {url}")
                    is_working, test_metadata = self.test_url_connectivity(url)
                    
                    if is_working:
                        logger.info(f"  ✅ URL funcional: {url}")
                        metadata['working_urls'].append({
                            'url': url,
                            'test_metadata': test_metadata
                        })
                        # Retornar la primera URL que funcione
                        return url, metadata
                    else:
                        logger.debug(f"  ❌ URL no funciona: {url} - {test_metadata.get('error', 'No response')}")
                
                # Si llegamos aquí, encontramos URLs pero ninguna funciona
                error_msg = f"Se encontraron {len(found_urls)} URLs pero ninguna responde"
                metadata['errors'].append(error_msg)
                logger.warning(f"  ⚠️ {error_msg}")
                
                # Esperar antes del siguiente intento
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                
            except Exception as e:
                error_msg = f"Error en intento {attempt + 1}: {str(e)}"
                metadata['errors'].append(error_msg)
                logger.error(f"  ❌ {error_msg}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        return None, metadata
    
    def get_current_url(self) -> Tuple[Optional[str], dict]:
        """
        Obtener la URL actual con metadata completa.
        
        Returns:
            Tupla (url, metadata)
        """
        logger.info(f"🚀 Iniciando extracción inteligente de URL desde: {self.dashboard_url}")
        
        start_time = time.time()
        url, metadata = self.scrape_dashboard_with_retry()
        
        metadata.update({
            'dashboard_url': self.dashboard_url,
            'total_time': time.time() - start_time,
            'timestamp': datetime.now().isoformat(),
            'success': url is not None
        })
        
        if url:
            logger.info(f"✅ URL extraída exitosamente: {url}")
        else:
            logger.error(f"❌ No se pudo extraer URL después de {metadata['attempts']} intentos")
        
        return url, metadata
    
    def save_extraction_report(self, url: Optional[str], metadata: dict, filename: str = None):
        """
        Guardar reporte detallado de la extracción.
        
        Args:
            url: URL extraída (puede ser None)
            metadata: Metadata de la extracción
            filename: Nombre del archivo (opcional)
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"url_extraction_report_{timestamp}.json"
        
        report = {
            'extraction_result': {
                'url': url,
                'success': url is not None,
                'timestamp': metadata.get('timestamp')
            },
            'metadata': metadata,
            'dashboard_url': self.dashboard_url,
            'extractor_config': {
                'timeout': self.timeout,
                'max_retries': self.max_retries,
                'retry_delay': self.retry_delay
            }
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"📋 Reporte guardado en: {filename}")
        except Exception as e:
            logger.error(f"❌ Error guardando reporte: {e}")


def extract_current_jetson_url() -> Optional[str]:
    """
    Función principal para extraer la URL actual del Jetson.
    
    Returns:
        URL actual o None si no se puede extraer
    """
    extractor = SmartDashboardURLExtractor()
    url, metadata = extractor.get_current_url()
    
    # Guardar reporte si hay errores
    if not url or metadata.get('errors'):
        extractor.save_extraction_report(url, metadata)
    
    return url


if __name__ == "__main__":
    print("🚀 SMART DASHBOARD URL EXTRACTOR")
    print("=" * 50)
    
    extractor = SmartDashboardURLExtractor()
    url, metadata = extractor.get_current_url()
    
    print(f"\n📊 RESULTADOS:")
    print(f"  URL extraída: {url or 'None'}")
    print(f"  Éxito: {'✅' if url else '❌'}")
    print(f"  Intentos: {metadata.get('attempts', 0)}")
    print(f"  Tiempo total: {metadata.get('total_time', 0):.2f}s")
    print(f"  URLs encontradas: {len(metadata.get('urls_found', []))}")
    print(f"  URLs funcionales: {len(metadata.get('working_urls', []))}")
    
    if metadata.get('errors'):
        print(f"\n❌ ERRORES:")
        for error in metadata['errors']:
            print(f"  - {error}")
    
    if url:
        print(f"\n✅ URL RECOMENDADA: {url}")
    else:
        print(f"\n❌ NO SE PUDO EXTRAER URL")
        print(f"💡 Sugerencias:")
        print(f"  - Verificar que el dashboard esté funcionando")
        print(f"  - Asegurar que la aplicación muestre la URL correctamente")
        print(f"  - Revisar conectividad de red")
    
    # Guardar reporte detallado
    extractor.save_extraction_report(url, metadata)
    print(f"\n📋 Reporte detallado guardado")