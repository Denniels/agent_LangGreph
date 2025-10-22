#!/usr/bin/env python3
"""
Jetson API URL Configuration - Wrapper Inteligente
==================================================

Este módulo proporciona un wrapper inteligente para reemplazar todas las
URLs hardcodeadas de Cloudflare en el proyecto, sin necesidad de modificar
cada archivo individual.

Utiliza el CloudflareURLManager para obtener automáticamente la URL actual
y proporciona compatibilidad hacia atrás con el código existente.

Uso:
    # En lugar de:
    # base_url = "https://replica-subscriber-permission-restricted.trycloudflare.com"
    
    # Usar:
    from modules.utils.jetson_url_config import JETSON_API_URL
    base_url = JETSON_API_URL

Autor: IoT Agent System  
Fecha: 22 de octubre de 2025
"""

import os
import logging
from typing import Optional

# Importar el manager de URLs
try:
    from .cloudflare_url_manager import (
        get_jetson_url, 
        get_jetson_url_for_env,
        get_cloudflare_url_manager,
        force_url_refresh,
        add_new_cloudflare_url
    )
except ImportError:
    # Fallback en caso de que no se pueda importar
    def get_jetson_url() -> str:
        return os.getenv('JETSON_API_URL', 'https://replica-subscriber-permission-restricted.trycloudflare.com')
    
    def get_jetson_url_for_env() -> str:
        return get_jetson_url()
    
    def force_url_refresh() -> str:
        return get_jetson_url()
    
    def add_new_cloudflare_url(url: str) -> None:
        pass
    
    def get_cloudflare_url_manager():
        return None

# Configurar logging
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURACIÓN PRINCIPAL - PUNTO DE ENTRADA ÚNICO
# ============================================================================

# URL principal que se actualizará automáticamente
JETSON_API_URL = get_jetson_url_for_env()

# URLs alternativas para compatibilidad
JETSON_URL = JETSON_API_URL
API_BASE_URL = JETSON_API_URL
BASE_URL = JETSON_API_URL

# Configuración adicional
JETSON_API_TIMEOUT = int(os.getenv('JETSON_API_TIMEOUT', '30'))
JETSON_API_RETRIES = int(os.getenv('JETSON_API_RETRIES', '3'))

# ============================================================================
# FUNCIONES DE CONVENIENCIA
# ============================================================================

def get_current_jetson_url() -> str:
    """
    Obtener la URL actual de Jetson/Cloudflare.
    
    Esta función siempre devuelve la URL más actualizada,
    consultando el manager si es necesario.
    
    Returns:
        URL actual de Cloudflare
    """
    return get_jetson_url()


def refresh_jetson_url() -> str:
    """
    Forzar actualización de la URL de Jetson/Cloudflare.
    
    Útil cuando se detecta que la URL actual no funciona.
    
    Returns:
        Nueva URL obtenida
    """
    global JETSON_API_URL, JETSON_URL, API_BASE_URL, BASE_URL
    
    new_url = force_url_refresh()
    
    # Actualizar todas las variables globales
    JETSON_API_URL = new_url
    JETSON_URL = new_url
    API_BASE_URL = new_url
    BASE_URL = new_url
    
    logger.info(f"🔄 URLs actualizadas globalmente: {new_url}")
    return new_url


def register_new_jetson_url(url: str) -> None:
    """
    Registrar una nueva URL de Jetson/Cloudflare.
    
    Args:
        url: Nueva URL descubierta
    """
    add_new_cloudflare_url(url)
    # Actualizar automáticamente las variables globales
    refresh_jetson_url()


def get_jetson_config() -> dict:
    """
    Obtener configuración completa de Jetson API.
    
    Returns:
        Diccionario con toda la configuración
    """
    return {
        'url': JETSON_API_URL,
        'timeout': JETSON_API_TIMEOUT,
        'retries': JETSON_API_RETRIES,
        'manager_available': get_cloudflare_url_manager() is not None
    }


def validate_jetson_url(url: Optional[str] = None) -> bool:
    """
    Validar que una URL de Jetson funcione correctamente.
    
    Args:  
        url: URL a validar (si None, usa la actual)
        
    Returns:
        True si la URL funciona
    """
    if url is None:
        url = JETSON_API_URL
    
    try:
        import requests
        response = requests.get(f"{url}/health", timeout=10)
        return response.status_code == 200
    except Exception:
        return False


# ============================================================================
# COMPATIBILIDAD CON CÓDIGO EXISTENTE  
# ============================================================================

# Para archivos que buscan estas variables específicas
CLOUDFLARE_URL = JETSON_API_URL
JETSON_BASE_URL = JETSON_API_URL
IOT_API_URL = JETSON_API_URL

# Para Streamlit y otras apps
STREAMLIT_JETSON_URL = JETSON_API_URL

# Para tests
TEST_API_URL = JETSON_API_URL

# ============================================================================
# AUTO-INICIALIZACIÓN
# ============================================================================

def _initialize_config():
    """Inicializar configuración al importar el módulo."""
    try:
        # Verificar que la URL actual funcione
        if not validate_jetson_url():
            logger.warning("⚠️ URL actual no responde, intentando actualizar...")
            refresh_jetson_url()
        else:
            logger.info(f"✅ URL validada: {JETSON_API_URL}")
            
    except Exception as e:
        logger.warning(f"⚠️ Error en inicialización: {e}")

# Ejecutar inicialización al importar
_initialize_config()

# ============================================================================
# INFORMACIÓN DEL MÓDULO
# ============================================================================

__version__ = "1.0.0"
__author__ = "IoT Agent System"
__description__ = "Wrapper inteligente para gestión automática de URLs de Cloudflare"

if __name__ == "__main__":
    # Script de prueba
    print("🧪 PRUEBA DE JETSON URL CONFIG")
    print("=" * 40)
    
    print(f"URL actual: {JETSON_API_URL}")
    print(f"Timeout: {JETSON_API_TIMEOUT}s")
    print(f"Reintentos: {JETSON_API_RETRIES}")
    
    config = get_jetson_config()
    print(f"\nConfiguración completa:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print(f"\nValidación URL: {validate_jetson_url()}")
    
    if get_cloudflare_url_manager():
        manager = get_cloudflare_url_manager()
        status = manager.get_status()
        print(f"\nEstado del manager:")
        for key, value in status.items():
            print(f"  {key}: {value}")