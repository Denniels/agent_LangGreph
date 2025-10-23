#!/usr/bin/env python3
"""
Dashboard URL Extractor - Extrae URL de Cloudflare desde el dashboard
==================================================================

Sistema simple que consulta el dashboard de Streamlit para obtener la URL
actual de Cloudflare mediante scraping o requests directo.

Compatible con Streamlit Cloud y sin dependencias complejas.
"""

import requests
import re
import json
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class DashboardURLExtractor:
    """
    Extractor que obtiene la URL actual desde el dashboard de Streamlit.
    """
    
    def __init__(self):
        self.dashboard_url = "https://iotapp-jvwtoekeo73ruxn9mdhfnc.streamlit.app"
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos
        self.timeout = 30
    
    def _is_cache_valid(self) -> bool:
        """Verificar si el cache es válido."""
        if 'url' not in self.cache or 'timestamp' not in self.cache:
            return False
        
        cache_age = datetime.now() - self.cache['timestamp']
        return cache_age < timedelta(seconds=self.cache_ttl)
    
    def extract_url_from_dashboard(self) -> Optional[str]:
        """
        Extraer URL de Cloudflare desde el dashboard mediante scraping.
        
        Returns:
            URL actual de Cloudflare o None si falla
        """
        try:
            logger.info(f"🔍 Consultando dashboard: {self.dashboard_url}")
            
            # Headers para simular navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(
                self.dashboard_url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            response.raise_for_status()
            content = response.text
            
            # Buscar patrones de URL de Cloudflare en el contenido
            cloudflare_patterns = [
                r'https://[\w\-]+\.trycloudflare\.com',
                r'"(https://[\w\-]+\.trycloudflare\.com)"',
                r"'(https://[\w\-]+\.trycloudflare\.com)'",
                r'API conectada:.*?(https://[\w\-]+\.trycloudflare\.com)',
                r'URL.*?conectada.*?(https://[\w\-]+\.trycloudflare\.com)',
            ]
            
            found_urls = set()
            for pattern in cloudflare_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Limpiar la URL (en caso de que esté en un grupo de captura)
                    url = match if isinstance(match, str) else match[0]
                    url = url.strip('"\'')
                    
                    if url.startswith('https://') and '.trycloudflare.com' in url:
                        found_urls.add(url)
            
            if found_urls:
                # Tomar la primera URL encontrada (o la más común)
                current_url = list(found_urls)[0]
                logger.info(f"✅ URL extraída del dashboard: {current_url}")
                
                # Verificar que la URL funcione
                if self._test_url(current_url):
                    # Actualizar cache
                    self.cache = {
                        'url': current_url,
                        'timestamp': datetime.now(),
                        'source': 'dashboard_scraping'
                    }
                    return current_url
                else:
                    logger.warning(f"⚠️ URL extraída no responde: {current_url}")
            
            logger.warning("⚠️ No se encontraron URLs válidas en el dashboard")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo URL del dashboard: {e}")
            return None
    
    def _test_url(self, url: str) -> bool:
        """Probar si una URL responde correctamente."""
        try:
            response = requests.get(f"{url}/health", timeout=15)
            return response.status_code == 200
        except:
            return False
    
    def get_current_url(self, force_refresh: bool = False) -> Optional[str]:
        """
        Obtener URL actual con cache.
        
        Args:
            force_refresh: Forzar actualización
            
        Returns:
            URL actual de Cloudflare
        """
        if not force_refresh and self._is_cache_valid():
            logger.debug(f"💨 Usando URL desde cache: {self.cache['url']}")
            return self.cache['url']
        
        return self.extract_url_from_dashboard()
    
    def get_url_with_fallback(self) -> str:
        """
        Obtener URL con fallback garantizado.
        
        Returns:
            URL de Cloudflare (nunca None)
        """
        url = self.get_current_url()
        
        if url:
            return url
        
        # Fallback a URL conocida más reciente
        fallback = "https://reflect-wed-governmental-fisher.trycloudflare.com"
        logger.warning(f"🆘 Usando URL de fallback: {fallback}")
        return fallback


# Instancia global
_extractor = None

def get_jetson_url_from_dashboard() -> str:
    """
    Función principal para obtener URL desde el dashboard.
    
    Returns:
        URL actual de Cloudflare
    """
    global _extractor
    if _extractor is None:
        _extractor = DashboardURLExtractor()
    
    return _extractor.get_url_with_fallback()


if __name__ == "__main__":
    # Test del extractor
    print("🧪 PRUEBA DEL DASHBOARD URL EXTRACTOR")
    print("=" * 50)
    
    extractor = DashboardURLExtractor()
    
    print(f"🔍 Extrayendo URL del dashboard...")
    url = extractor.get_current_url()
    
    if url:
        print(f"✅ URL obtenida: {url}")
        
        # Probar conectividad
        if extractor._test_url(url):
            print(f"✅ URL responde correctamente")
        else:
            print(f"❌ URL no responde")
    else:
        print(f"❌ No se pudo obtener URL")
    
    print(f"\n🔄 URL con fallback: {extractor.get_url_with_fallback()}")