#!/usr/bin/env python3
"""
Cloudflare URL Manager - Sistema Robusto de Gestión de URLs
===========================================================

Gestor centralizado que maneja automáticamente los cambios de URL de Cloudflare,
consulta el endpoint /cf_url para obtener la URL actual, y proporciona fallbacks
robustos cuando la URL cambia.

Características:
- Auto-detección de cambios de URL
- Cache inteligente con TTL
- Fallback a URLs conocidas
- Thread-safe para aplicaciones concurrent
- Logging detallado para debugging
- Compatible con Streamlit Cloud

Autor: IoT Agent System
Fecha: 22 de octubre de 2025
"""

import requests
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import logging
import os
from pathlib import Path

# Configurar logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | CloudflareURLManager | %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class CloudflareURLManager:
    """
    Gestor robusto y thread-safe para URLs de Cloudflare que cambian dinámicamente.
    
    Este manager:
    1. Consulta automáticamente el endpoint /cf_url para obtener la URL actual
    2. Mantiene un cache con TTL para optimizar rendimiento  
    3. Proporciona fallback a URLs conocidas cuando sea necesario
    4. Auto-detecta cambios y actualiza la configuración
    5. Es thread-safe para aplicaciones concurrentes
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern para asegurar una sola instancia global."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar el manager con configuración por defecto."""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self._url_cache = None
        self._cache_timestamp = None
        self._cache_ttl = 300  # 5 minutos de cache
        self._request_timeout = 15
        self._max_retries = 3
        
        # URLs fallback en orden de prioridad
        self._fallback_urls = [
            "https://replica-subscriber-permission-restricted.trycloudflare.com",  # Nueva URL
            "https://replica-subscriber-permission-restricted.trycloudflare.com",          # URL anterior
        ]
        
        # Archivo de configuración para persistir estado
        self._config_file = Path("cloudflare_url_config.json")
        
        # Cargar configuración guardada
        self._load_config()
        
        logger.info("🌟 CloudflareURLManager inicializado")
    
    def _load_config(self) -> None:
        """Cargar configuración guardada desde archivo."""
        try:
            if self._config_file.exists():
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                self._url_cache = config.get('active_url')
                
                # Cargar timestamp si existe
                if config.get('cache_timestamp'):
                    self._cache_timestamp = datetime.fromisoformat(config['cache_timestamp'])
                
                # Actualizar fallback URLs si hay nuevas en config
                if config.get('fallback_urls'):
                    self._fallback_urls = config['fallback_urls']
                
                logger.info(f"📁 Configuración cargada: {self._url_cache}")
                
        except Exception as e:
            logger.warning(f"⚠️ No se pudo cargar configuración: {e}")
            # Usar configuración por defecto
            self._url_cache = None
            self._cache_timestamp = None
    
    def _save_config(self) -> None:
        """Guardar configuración actual en archivo."""
        try:
            config = {
                'active_url': self._url_cache,
                'cache_timestamp': self._cache_timestamp.isoformat() if self._cache_timestamp else None,
                'fallback_urls': self._fallback_urls,
                'last_updated': datetime.now().isoformat(),
                'manager_version': '1.0.0'
            }
            
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            logger.debug("💾 Configuración guardada")
            
        except Exception as e:
            logger.warning(f"⚠️ No se pudo guardar configuración: {e}")
    
    def _is_cache_valid(self) -> bool:
        """Verificar si el cache actual sigue siendo válido."""
        if not self._url_cache or not self._cache_timestamp:
            return False
            
        return datetime.now() - self._cache_timestamp < timedelta(seconds=self._cache_ttl)
    
    def _test_url_connectivity(self, url: str) -> bool:
        """
        Probar conectividad básica a una URL.
        
        Args:
            url: URL a probar
            
        Returns:
            True si la URL responde correctamente
        """
        try:
            # Probar endpoint básico de salud
            response = requests.get(
                f"{url}/health", 
                timeout=self._request_timeout,
                headers={'User-Agent': 'CloudflareURLManager/1.0'}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.debug(f"🔍 URL {url} no responde: {e}")
            return False
    
    def _fetch_current_url_from_api(self, base_url: str) -> Optional[str]:
        """
        Obtener la URL actual desde el endpoint /cf_url.
        
        Args:
            base_url: URL base para consultar el endpoint
            
        Returns:
            URL actual de Cloudflare o None si falla
        """
        try:
            response = requests.get(
                f"{base_url}/cf_url",
                timeout=self._request_timeout,
                headers={'User-Agent': 'CloudflareURLManager/1.0'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extraer URL del response según formato esperado
                if isinstance(data, dict):
                    # Formato: {"success": true, "cf_url": "https://..."}
                    if data.get('cf_url'):
                        return data['cf_url']
                    # Formato: {"data": {"cf_url": "https://..."}}
                    elif data.get('data', {}).get('cf_url'):
                        return data['data']['cf_url']
                
                logger.warning(f"⚠️ Formato inesperado en /cf_url: {data}")
                
        except Exception as e:
            logger.debug(f"🔍 Error consultando /cf_url en {base_url}: {e}")
            
        return None
    
    def _discover_active_url(self) -> Optional[str]:
        """
        Descubrir la URL activa probando las URLs fallback y consultando /cf_url.
        
        Returns:
            URL activa encontrada o None
        """
        logger.info("🔍 Descubriendo URL activa de Cloudflare...")
        
        # Primero probar URLs fallback para encontrar una que responda
        for url in self._fallback_urls:
            logger.debug(f"🧪 Probando URL: {url}")
            
            if self._test_url_connectivity(url):
                logger.info(f"✅ URL respondiendo: {url}")
                
                # Intentar obtener la URL actual desde esta URL que responde
                current_url = self._fetch_current_url_from_api(url)
                
                if current_url and current_url != url:
                    # La API reporta una URL diferente - usar la reportada
                    logger.info(f"🔄 API reporta URL diferente: {current_url}")
                    
                    # Verificar que la nueva URL también funcione
                    if self._test_url_connectivity(current_url):
                        logger.info(f"✅ Nueva URL verificada: {current_url}")
                        return current_url
                    else:
                        logger.warning(f"⚠️ Nueva URL no responde, usando fallback: {url}")
                        return url
                else:
                    # La URL responde y es la misma que reporta - usar esta
                    return url
        
        logger.error("❌ No se encontró ninguna URL funcional")
        return None
    
    def get_current_url(self, force_refresh: bool = False) -> Optional[str]:
        """
        Obtener la URL actual de Cloudflare.
        
        Args:
            force_refresh: Forzar actualización ignorando cache
            
        Returns:
            URL actual de Cloudflare o None si no está disponible
        """
        with self._lock:
            # Usar cache si es válido y no se fuerza refresh
            if not force_refresh and self._is_cache_valid():
                logger.debug(f"💨 Usando URL desde cache: {self._url_cache}")
                return self._url_cache
            
            # Necesitamos actualizar la URL
            logger.info("🔄 Actualizando URL de Cloudflare...")
            
            # Descubrir URL activa
            active_url = self._discover_active_url()
            
            if active_url:
                # Actualizar cache
                old_url = self._url_cache
                self._url_cache = active_url
                self._cache_timestamp = datetime.now()
                
                # Guardar configuración
                self._save_config()
                
                if old_url != active_url:
                    logger.info(f"🔄 URL cambió: {old_url} → {active_url}")
                else:
                    logger.info(f"✅ URL confirmada: {active_url}")
                
                return active_url
            
            else:
                logger.error("❌ No se pudo determinar URL activa")
                
                # Como último recurso, usar la primera URL fallback
                if self._fallback_urls:
                    fallback_url = self._fallback_urls[0]
                    logger.warning(f"🆘 Usando URL de emergencia: {fallback_url}")
                    return fallback_url
                
                return None
    
    def get_url_with_fallback(self) -> str:
        """
        Obtener URL con garantía de fallback.
        
        Returns:
            URL de Cloudflare (nunca None)
        """
        url = self.get_current_url()
        
        if url:
            return url
        
        # Fallback de emergencia
        emergency_url = "https://replica-subscriber-permission-restricted.trycloudflare.com"
        logger.warning(f"🆘 Usando URL de emergencia: {emergency_url}")
        return emergency_url
    
    def invalidate_cache(self) -> None:
        """Invalidar cache para forzar actualización en siguiente consulta."""
        with self._lock:
            self._cache_timestamp = None
            logger.info("🗑️ Cache invalidado")
    
    def add_fallback_url(self, url: str) -> None:
        """
        Agregar nueva URL a la lista de fallback.
        
        Args:
            url: Nueva URL a agregar
        """
        if url not in self._fallback_urls:
            self._fallback_urls.insert(0, url)  # Agregar al inicio (mayor prioridad)
            self._save_config()
            logger.info(f"➕ Nueva URL fallback agregada: {url}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtener estado actual del manager.
        
        Returns:
            Diccionario con información de estado
        """
        return {
            'current_url': self._url_cache,
            'cache_valid': self._is_cache_valid(),
            'cache_age_seconds': (
                (datetime.now() - self._cache_timestamp).total_seconds() 
                if self._cache_timestamp else None
            ),
            'fallback_urls': self._fallback_urls,
            'config_file_exists': self._config_file.exists(),
            'last_check': self._cache_timestamp.isoformat() if self._cache_timestamp else None
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Realizar verificación completa de salud del sistema.
        
        Returns:
            Reporte de salud completo
        """
        logger.info("🏥 Iniciando verificación de salud...")
        
        current_url = self.get_current_url()
        status = self.get_status()
        
        # Probar conectividad actual
        connectivity_ok = False
        if current_url:
            connectivity_ok = self._test_url_connectivity(current_url)
        
        # Probar todas las URLs fallback
        fallback_status = {}
        for url in self._fallback_urls:
            fallback_status[url] = self._test_url_connectivity(url)
        
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_health': 'healthy' if connectivity_ok else 'unhealthy',
            'current_url': current_url,
            'current_url_working': connectivity_ok,
            'fallback_urls_status': fallback_status,
            'cache_status': status,
            'recommendations': []
        }
        
        # Generar recomendaciones
        if not connectivity_ok:
            health_report['recommendations'].append("URL actual no responde - considerar invalidar cache")
        
        working_fallbacks = [url for url, working in fallback_status.items() if working]
        if len(working_fallbacks) == 0:
            health_report['recommendations'].append("CRÍTICO: Ninguna URL fallback funciona")
        elif len(working_fallbacks) == 1:
            health_report['recommendations'].append("Solo una URL fallback funciona - agregar más URLs")
        
        logger.info(f"🏥 Salud general: {health_report['overall_health']}")
        return health_report


# Instancia global singleton
_url_manager = None

def get_cloudflare_url_manager() -> CloudflareURLManager:
    """
    Obtener instancia singleton del manager.
    
    Returns:
        Instancia de CloudflareURLManager
    """
    global _url_manager
    if _url_manager is None:
        _url_manager = CloudflareURLManager()
    return _url_manager


def get_jetson_url() -> str:
    """
    Función de conveniencia para obtener la URL actual de Jetson/Cloudflare.
    
    Esta función es el punto de entrada principal que deben usar todos los
    módulos del proyecto en lugar de hardcodear URLs.
    
    Returns:
        URL actual de Cloudflare (nunca None)
    """
    manager = get_cloudflare_url_manager()
    return manager.get_url_with_fallback()


def get_jetson_url_for_env() -> str:
    """
    Obtener URL para variables de entorno, con respeto a JETSON_API_URL si existe.
    
    Returns:
        URL para usar en variables de entorno
    """
    # Respetar variable de entorno si está configurada explícitamente
    env_url = os.getenv('JETSON_API_URL')
    if env_url and env_url.strip():
        logger.info(f"🔧 Usando URL desde variable de entorno: {env_url}")
        return env_url.strip()
    
    # Caso contrario, usar el manager
    return get_jetson_url()


def force_url_refresh() -> str:
    """
    Forzar actualización de URL ignorando cache.
    
    Returns:
        Nueva URL obtenida
    """
    manager = get_cloudflare_url_manager()
    return manager.get_current_url(force_refresh=True) or manager.get_url_with_fallback()


def add_new_cloudflare_url(url: str) -> None:
    """
    Agregar nueva URL de Cloudflare cuando se detecte un cambio.
    
    Args:
        url: Nueva URL de Cloudflare
    """
    manager = get_cloudflare_url_manager()
    manager.add_fallback_url(url)
    manager.invalidate_cache()  # Forzar re-evaluación
    logger.info(f"🔄 Nueva URL agregada y cache invalidado: {url}")


if __name__ == "__main__":
    # Script de prueba cuando se ejecuta directamente
    print("🧪 PRUEBA DEL CLOUDFLARE URL MANAGER")
    print("=" * 50)
    
    manager = get_cloudflare_url_manager()
    
    # Mostrar estado inicial
    print(f"\n📊 Estado inicial:")
    status = manager.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Obtener URL actual
    print(f"\n🌐 URL actual: {get_jetson_url()}")
    
    # Realizar verificación de salud
    print(f"\n🏥 Verificación de salud:")
    health = manager.health_check()
    print(f"  Estado general: {health['overall_health']}")
    print(f"  URL actual funciona: {health['current_url_working']}")
    
    if health['recommendations']:
        print(f"  Recomendaciones:")
        for rec in health['recommendations']:
            print(f"    - {rec}")
    
    print(f"\n✅ Prueba completada")