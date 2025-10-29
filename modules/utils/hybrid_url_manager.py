#!/usr/bin/env python3
"""
Hybrid URL Manager - Sistema híbrido robusto de obtención de URLs
===============================================================

Combina múltiples métodos para obtener la URL actual de Cloudflare:
1. Cache local inteligente
2. API JSON del dashboard (si está disponible)
3. Scraping del dashboard como fallback
4. URLs hardcodeadas como último recurso

Optimizado para Streamlit Cloud con mínimas dependencias.
"""

import requests
import re
import json
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import threading
import os

logger = logging.getLogger(__name__)

class HybridURLManager:
    """
    Manager híbrido que combina múltiples estrategias para obtener la URL actual.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        
        # Configuración
        self.dashboard_url = "https://iotapp-jvwtoekeo73ruxn9mdhfnc.streamlit.app"
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos
        self.timeout = 20
        
        # URLs conocidas en orden de prioridad (más reciente primero)
        self.known_urls = [
            "https://along-critical-decorative-physics.trycloudflare.com",  # URL ACTUAL NUEVA
            "https://roof-imposed-noticed-fire.trycloudflare.com",  # URL anterior
            "https://returned-convenience-tower-switched.trycloudflare.com",  # URL anterior
            "https://reflect-wed-governmental-fisher.trycloudflare.com",  # URL más antigua
        ]
        
        # Estrategias en orden de preferencia
        self.strategies = [
            self._get_from_cache,
            self._get_from_json_api,
            self._get_from_dashboard_scraping,
            self._get_from_known_urls,
            self._get_emergency_fallback
        ]
        
        logger.info("🌟 HybridURLManager inicializado")
    
    def _is_cache_valid(self) -> bool:
        """Verificar si el cache es válido."""
        if 'url' not in self.cache or 'timestamp' not in self.cache:
            return False
        
        cache_age = datetime.now() - self.cache['timestamp']
        return cache_age < timedelta(seconds=self.cache_ttl)
    
    def _update_cache(self, url: str, source: str):
        """Actualizar cache con nueva URL."""
        self.cache = {
            'url': url,
            'timestamp': datetime.now(),
            'source': source
        }
        logger.info(f"💾 Cache actualizado: {url} (fuente: {source})")
    
    def _test_url(self, url: str) -> bool:
        """Probar si una URL responde correctamente."""
        try:
            response = requests.get(f"{url}/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def _get_from_cache(self) -> Optional[str]:
        """Estrategia 1: Obtener desde cache."""
        if self._is_cache_valid():
            url = self.cache['url']
            logger.debug(f"💨 URL desde cache: {url}")
            return url
        return None
    
    def _get_from_json_api(self) -> Optional[str]:
        """Estrategia 2: Obtener desde API JSON del dashboard."""
        try:
            endpoints = [
                f"{self.dashboard_url}/api/current-url",
                f"{self.dashboard_url}/current-url.json",
                f"{self.dashboard_url}/status.json",
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=15, headers={
                        'Accept': 'application/json',
                        'User-Agent': 'HybridURLManager/1.0'
                    })
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Buscar URL en el JSON
                        url_fields = ['current_url', 'cloudflare_url', 'jetson_url', 'api_url', 'url']
                        for field in url_fields:
                            url = data.get(field) or data.get('data', {}).get(field)
                            if url and '.trycloudflare.com' in url:
                                if self._test_url(url):
                                    self._update_cache(url, f'json_api_{endpoint}')
                                    return url
                
                except (requests.RequestException, json.JSONDecodeError):
                    continue
                    
        except Exception as e:
            logger.debug(f"🔍 Error en JSON API: {e}")
        
        return None
    
    def _get_from_dashboard_scraping(self) -> Optional[str]:
        """Estrategia 3: Scraping del dashboard."""
        try:
            logger.info(f"🔍 Haciendo scraping del dashboard...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            response = requests.get(self.dashboard_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Buscar URLs de Cloudflare en el contenido
            patterns = [
                r'https://[\w\-]+\.trycloudflare\.com',
                r'API conectada:.*?(https://[\w\-]+\.trycloudflare\.com)',
                r'Conectando.*?(https://[\w\-]+\.trycloudflare\.com)',
            ]
            
            found_urls = set()
            for pattern in patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    url = match if isinstance(match, str) else match[0]
                    url = url.strip('"\'')
                    if url.startswith('https://') and '.trycloudflare.com' in url:
                        found_urls.add(url)
            
            # Probar URLs encontradas
            for url in found_urls:
                if self._test_url(url):
                    self._update_cache(url, 'dashboard_scraping')
                    return url
                    
        except Exception as e:
            logger.debug(f"🔍 Error en scraping: {e}")
        
        return None
    
    def _get_from_known_urls(self) -> Optional[str]:
        """Estrategia 4: Probar URLs conocidas."""
        logger.info("🔍 Probando URLs conocidas...")
        
        for url in self.known_urls:
            if self._test_url(url):
                logger.info(f"✅ URL conocida funciona: {url}")
                self._update_cache(url, 'known_urls')
                return url
        
        return None
    
    def _get_emergency_fallback(self) -> str:
        """Estrategia 5: Fallback de emergencia."""
        emergency_url = self.known_urls[0] if self.known_urls else "https://reflect-wed-governmental-fisher.trycloudflare.com"
        logger.warning(f"🆘 Usando URL de emergencia: {emergency_url}")
        return emergency_url
    
    def get_current_url(self, force_refresh: bool = False) -> str:
        """
        Obtener URL actual usando todas las estrategias disponibles.
        
        Args:
            force_refresh: Forzar actualización ignorando cache
            
        Returns:
            URL actual de Cloudflare (nunca None)
        """
        if force_refresh:
            self.cache = {}  # Limpiar cache
        
        for i, strategy in enumerate(self.strategies, 1):
            try:
                url = strategy()
                if url:
                    logger.debug(f"✅ Estrategia {i} exitosa: {strategy.__name__}")
                    return url
            except Exception as e:
                logger.debug(f"⚠️ Estrategia {i} falló ({strategy.__name__}): {e}")
        
        # Esto nunca debería llegar aquí debido al fallback de emergencia
        return self._get_emergency_fallback()
    
    def add_known_url(self, url: str):
        """Agregar nueva URL conocida."""
        if url not in self.known_urls:
            self.known_urls.insert(0, url)  # Agregar al inicio (mayor prioridad)
            logger.info(f"➕ Nueva URL conocida agregada: {url}")
    
    def get_status(self) -> Dict:
        """Obtener estado del manager."""
        return {
            'current_url': self.cache.get('url'),
            'cache_valid': self._is_cache_valid(),
            'cache_source': self.cache.get('source'),
            'cache_age': (datetime.now() - self.cache['timestamp']).total_seconds() if self.cache.get('timestamp') else None,
            'known_urls': self.known_urls,
            'dashboard_url': self.dashboard_url
        }


# Instancia global
_hybrid_manager = None

def get_jetson_url_hybrid() -> str:
    """
    Función principal para obtener URL usando el sistema híbrido.
    
    Returns:
        URL actual de Cloudflare
    """
    global _hybrid_manager
    if _hybrid_manager is None:
        _hybrid_manager = HybridURLManager()
    
    return _hybrid_manager.get_current_url()


def force_url_refresh_hybrid() -> str:
    """Forzar actualización de URL."""
    global _hybrid_manager
    if _hybrid_manager is None:
        _hybrid_manager = HybridURLManager()
    
    return _hybrid_manager.get_current_url(force_refresh=True)


if __name__ == "__main__":
    # Test del manager híbrido
    print("🧪 PRUEBA DEL HYBRID URL MANAGER")
    print("=" * 50)
    
    manager = HybridURLManager()
    
    print(f"🔍 Obteniendo URL con sistema híbrido...")
    url = manager.get_current_url()
    
    print(f"✅ URL obtenida: {url}")
    
    # Mostrar estado
    status = manager.get_status()
    print(f"\n📊 Estado del manager:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Test de actualización forzada
    print(f"\n🔄 Probando actualización forzada...")
    url_fresh = manager.get_current_url(force_refresh=True)
    print(f"✅ URL actualizada: {url_fresh}")