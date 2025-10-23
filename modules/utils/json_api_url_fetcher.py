#!/usr/bin/env python3
"""
JSON API URL Fetcher - Obtiene URL desde endpoint JSON del dashboard
================================================================

Sistema robusto que consulta un endpoint JSON simple del dashboard
para obtener la URL actual de Cloudflare.

Requiere agregar un endpoint JSON al dashboard, pero es más confiable
que el scraping y más simple que GitHub Actions.
"""

import requests
import json
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class JSONAPIURLFetcher:
    """
    Fetcher que obtiene URL desde endpoint JSON del dashboard.
    """
    
    def __init__(self):
        # Endpoints posibles del dashboard
        self.base_dashboard_url = "https://iotapp-jvwtoekeo73ruxn9mdhfnc.streamlit.app"
        self.api_endpoints = [
            f"{self.base_dashboard_url}/api/current-url",  # Endpoint ideal
            f"{self.base_dashboard_url}/current-url.json", # Archivo JSON estático
            f"{self.base_dashboard_url}/status.json",      # Status con URL
        ]
        
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos
        self.timeout = 15
        self.max_retries = 3
    
    def _is_cache_valid(self) -> bool:
        """Verificar si el cache es válido."""
        if 'url' not in self.cache or 'timestamp' not in self.cache:
            return False
        
        cache_age = datetime.now() - self.cache['timestamp']
        return cache_age < timedelta(seconds=self.cache_ttl)
    
    def fetch_url_from_json_api(self) -> Optional[str]:
        """
        Obtener URL desde endpoint JSON del dashboard.
        
        Returns:
            URL actual de Cloudflare o None si falla
        """
        for endpoint in self.api_endpoints:
            try:
                logger.info(f"🔍 Consultando endpoint JSON: {endpoint}")
                
                response = requests.get(
                    endpoint,
                    timeout=self.timeout,
                    headers={
                        'Accept': 'application/json',
                        'User-Agent': 'IoT-Agent-URLFetcher/1.0'
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Buscar URL en diferentes formatos de respuesta
                    url_candidates = [
                        data.get('current_url'),
                        data.get('cloudflare_url'),
                        data.get('jetson_url'),
                        data.get('api_url'),
                        data.get('url'),
                        data.get('data', {}).get('current_url'),
                        data.get('data', {}).get('url'),
                    ]
                    
                    for url in url_candidates:
                        if url and isinstance(url, str) and '.trycloudflare.com' in url:
                            logger.info(f"✅ URL obtenida desde JSON: {url}")
                            
                            # Verificar que la URL funcione
                            if self._test_url(url):
                                # Actualizar cache
                                self.cache = {
                                    'url': url,
                                    'timestamp': datetime.now(),
                                    'source': f'json_api_{endpoint}'
                                }
                                return url
                            else:
                                logger.warning(f"⚠️ URL desde JSON no responde: {url}")
                
            except requests.exceptions.RequestException as e:
                logger.debug(f"🔍 Endpoint {endpoint} no disponible: {e}")
            except json.JSONDecodeError as e:
                logger.debug(f"🔍 Respuesta no es JSON válido en {endpoint}: {e}")
            except Exception as e:
                logger.warning(f"⚠️ Error consultando {endpoint}: {e}")
        
        logger.warning("⚠️ No se pudo obtener URL desde ningún endpoint JSON")
        return None
    
    def _test_url(self, url: str) -> bool:
        """Probar si una URL responde correctamente."""
        try:
            response = requests.get(f"{url}/health", timeout=10)
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
        
        return self.fetch_url_from_json_api()
    
    def get_url_with_fallback(self) -> str:
        """
        Obtener URL con fallback garantizado.
        
        Returns:
            URL de Cloudflare (nunca None)
        """
        url = self.get_current_url()
        
        if url:
            return url
        
        # Fallback a URL más reciente conocida
        fallback = "https://reflect-wed-governmental-fisher.trycloudflare.com"
        logger.warning(f"🆘 Usando URL de fallback: {fallback}")
        return fallback


# Instancia global
_json_fetcher = None

def get_jetson_url_from_json_api() -> str:
    """
    Función principal para obtener URL desde API JSON.
    
    Returns:
        URL actual de Cloudflare
    """
    global _json_fetcher
    if _json_fetcher is None:
        _json_fetcher = JSONAPIURLFetcher()
    
    return _json_fetcher.get_url_with_fallback()


if __name__ == "__main__":
    # Test del fetcher
    print("🧪 PRUEBA DEL JSON API URL FETCHER")
    print("=" * 50)
    
    fetcher = JSONAPIURLFetcher()
    
    print(f"🔍 Obteniendo URL desde API JSON...")
    url = fetcher.get_current_url()
    
    if url:
        print(f"✅ URL obtenida: {url}")
        
        # Probar conectividad
        if fetcher._test_url(url):
            print(f"✅ URL responde correctamente")
        else:
            print(f"❌ URL no responde")
    else:
        print(f"❌ No se pudo obtener URL desde JSON API")
    
    print(f"\n🔄 URL con fallback: {fetcher.get_url_with_fallback()}")