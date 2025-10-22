#!/usr/bin/env python3
"""
Ejemplo de Migración al Nuevo Sistema de URLs
==============================================

Este archivo muestra cómo migrar el código existente para usar el nuevo
sistema de gestión de URLs de Cloudflare automático.

ANTES (URLs hardcodeadas):
--------------------------
base_url = "https://replica-subscriber-permission-restricted.trycloudflare.com"

DESPUÉS (URLs automáticas):
---------------------------
from modules.utils.jetson_url_config import JETSON_API_URL
base_url = JETSON_API_URL

Autor: IoT Agent System
Fecha: 22 de octubre de 2025
"""

# ============================================================================
# MÉTODO 1: IMPORTAR URL CONSTANTE (MÁS SIMPLE)
# ============================================================================

# ✅ NUEVO - Recomendado para la mayoría de casos
from modules.utils.jetson_url_config import JETSON_API_URL

# Usar directamente
api_base_url = JETSON_API_URL
print(f"URL desde constante: {api_base_url}")

# ============================================================================
# MÉTODO 2: IMPORTAR FUNCIÓN (MÁS DINÁMICO)
# ============================================================================

# ✅ NUEVO - Para casos que necesitan URL siempre fresca
from modules.utils.jetson_url_config import get_current_jetson_url

# Obtener URL dinámica
dynamic_url = get_current_jetson_url()
print(f"URL dinámica: {dynamic_url}")

# ============================================================================
# MÉTODO 3: USAR EL MANAGER DIRECTAMENTE (AVANZADO)
# ============================================================================

# ✅ NUEVO - Para control total
from modules.utils.cloudflare_url_manager import get_cloudflare_url_manager

manager = get_cloudflare_url_manager()
advanced_url = manager.get_url_with_fallback()
print(f"URL desde manager: {advanced_url}")

# Verificar estado del manager
status = manager.get_status()
print(f"Estado del cache: {status['cache_valid']}")

# ============================================================================
# EJEMPLO PRÁCTICO: MIGRAR UN CONECTOR EXISTENTE
# ============================================================================

import requests
from typing import Dict, Any

class JetsonConnectorMigrado:
    """Ejemplo de cómo migrar un conector existente."""
    
    def __init__(self):
        # ❌ ANTES: URL hardcodeada
        # self.base_url = "https://replica-subscriber-permission-restricted.trycloudflare.com"
        
        # ✅ DESPUÉS: URL automática
        from modules.utils.jetson_url_config import JETSON_API_URL
        self.base_url = JETSON_API_URL
        
        print(f"🔧 Conector inicializado con URL: {self.base_url}")
    
    def get_data(self) -> Dict[str, Any]:
        """Obtener datos de la API."""
        try:
            response = requests.get(f"{self.base_url}/data", timeout=30)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en request: {e}")
            
            # ✅ NUEVO: Auto-recuperación cuando falla la URL
            from modules.utils.jetson_url_config import refresh_jetson_url
            
            print("🔄 Intentando actualizar URL...")
            new_url = refresh_jetson_url()
            self.base_url = new_url
            
            # Reintentar con nueva URL
            try:
                response = requests.get(f"{self.base_url}/data", timeout=30)
                response.raise_for_status()
                return response.json()
            except Exception as retry_error:
                print(f"❌ Error persistente: {retry_error}")
                raise
    
    def validate_connection(self) -> bool:
        """Validar que la conexión funcione."""
        # ✅ NUEVO: Usar función de validación integrada
        from modules.utils.jetson_url_config import validate_jetson_url
        return validate_jetson_url(self.base_url)

# ============================================================================
# EJEMPLO PRÁCTICO: MIGRAR UNA APP STREAMLIT
# ============================================================================

def ejemplo_streamlit_migration():
    """Ejemplo de cómo migrar una app Streamlit."""
    
    # ❌ ANTES: URLs hardcodeadas en múltiples lugares
    # JETSON_API_URL = "https://replica-subscriber-permission-restricted.trycloudflare.com"
    # API_BASE_URL = "https://replica-subscriber-permission-restricted.trycloudflare.com"
    
    # ✅ DESPUÉS: Una sola importación
    from modules.utils.jetson_url_config import (
        JETSON_API_URL, 
        get_jetson_config,
        validate_jetson_url
    )
    
    # Obtener configuración completa
    config = get_jetson_config()
    print(f"Configuración Streamlit:")
    print(f"  URL: {config['url']}")
    print(f"  Timeout: {config['timeout']}s")
    print(f"  Retries: {config['retries']}")
    
    # Validar antes de usar
    if validate_jetson_url():
        print("✅ URL validada, ready para Streamlit")
        return JETSON_API_URL
    else:
        print("❌ URL no válida, iniciando recuperación...")
        from modules.utils.jetson_url_config import refresh_jetson_url
        return refresh_jetson_url()

# ============================================================================
# EJEMPLO PRÁCTICO: MIGRAR TESTS
# ============================================================================

def ejemplo_test_migration():
    """Ejemplo de cómo migrar tests existentes."""
    
    # ❌ ANTES: URL fija en tests
    # API_BASE_URL = "https://replica-subscriber-permission-restricted.trycloudflare.com"
    
    # ✅ DESPUÉS: URL dinámica en tests
    from modules.utils.jetson_url_config import get_current_jetson_url
    
    def test_api_connectivity():
        """Test que siempre usa la URL correcta."""
        current_url = get_current_jetson_url()
        
        response = requests.get(f"{current_url}/health", timeout=10)
        assert response.status_code == 200, f"API no responde en {current_url}"
        
        print(f"✅ Test passed con URL: {current_url}")
    
    # Ejecutar test
    test_api_connectivity()

# ============================================================================
# EJEMPLO PRÁCTICO: MONITOREO Y NOTIFICACIONES
# ============================================================================

def ejemplo_monitoring():
    """Ejemplo de monitoreo de cambios de URL."""
    
    from modules.utils.cloudflare_url_manager import get_cloudflare_url_manager
    
    manager = get_cloudflare_url_manager()
    
    # Obtener reporte de salud
    health = manager.health_check()
    
    print(f"\n🏥 REPORTE DE SALUD:")
    print(f"Estado general: {health['overall_health']}")
    print(f"URL actual: {health['current_url']}")
    print(f"URL funciona: {health['current_url_working']}")
    
    if health['recommendations']:
        print("📋 Recomendaciones:")
        for rec in health['recommendations']:
            print(f"  - {rec}")
    
    # Simular detección de nueva URL
    if not health['current_url_working']:
        print("\n🚨 URL actual no funciona, buscando alternativa...")
        
        # Forzar búsqueda de nueva URL
        new_url = manager.get_current_url(force_refresh=True)
        print(f"🔄 Nueva URL encontrada: {new_url}")

# ============================================================================
# FUNCIÓN PRINCIPAL PARA DEMOSTRACIÓN
# ============================================================================

def main():
    """Ejecutar todos los ejemplos de migración."""
    
    print("🚀 EJEMPLOS DE MIGRACIÓN AL NUEVO SISTEMA")
    print("=" * 50)
    
    print("\n1️⃣ Conector migrado:")
    connector = JetsonConnectorMigrado()
    print(f"   Conexión válida: {connector.validate_connection()}")
    
    print("\n2️⃣ Configuración Streamlit:")
    streamlit_url = ejemplo_streamlit_migration()
    print(f"   URL para Streamlit: {streamlit_url}")
    
    print("\n3️⃣ Test migrado:")
    ejemplo_test_migration()
    
    print("\n4️⃣ Monitoreo:")
    ejemplo_monitoring()
    
    print("\n✅ Todos los ejemplos completados")

if __name__ == "__main__":
    main()