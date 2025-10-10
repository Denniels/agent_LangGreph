"""
Test final del sistema completo IoT Agent con datos reales
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.agents.cloud_iot_agent import CloudIoTAgent
import asyncio
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sistema_completo():
    """
    Test del sistema completo con el agente corregido
    """
    print("🚀 Test Sistema IoT Completo")
    print("=" * 50)
    
    try:
        # Crear agente principal
        agent = CloudIoTAgent()
        print("✅ CloudIoTAgent creado exitosamente")
        
        # Test 1: Consulta sobre estado del sistema
        print("\n📊 Test 1: Estado del sistema")
        query = "¿Cuál es el estado actual del sistema IoT?"
        
        response = agent.process_query_sync(query)
        print(f"Consulta: {query}")
        print(f"Respuesta:")
        print(response)
        
        # Verificar que la respuesta contiene dispositivos reales
        if 'arduino_eth_001' in response and 'esp32_wifi_001' in response:
            print("✅ Respuesta contiene dispositivos reales")
        else:
            print("⚠️ Respuesta no contiene dispositivos reales específicos")
        
        # Test 2: Consulta específica sobre sensores
        print("\n🔬 Test 2: Información de sensores")
        query2 = "¿Qué sensores están disponibles y cuáles son sus últimas lecturas?"
        
        response2 = agent.process_query_sync(query2)
        print(f"Consulta: {query2}")
        print(f"Respuesta:")
        print(response2)
        
        # Test 3: Solicitar reporte
        print("\n📋 Test 3: Generar reporte")
        query3 = "Genera un reporte del estado actual del sistema IoT"
        
        response3 = agent.process_query_sync(query3)
        print(f"Consulta: {query3}")
        print(f"Respuesta (primeros 500 caracteres):")
        print(response3[:500] + "..." if len(response3) > 500 else response3)
        
        print("\n🎉 Test sistema completo finalizado")
        return True
        
    except Exception as e:
        print(f"❌ Error en test sistema completo: {e}")
        logger.exception("Error detallado:")
        return False

if __name__ == "__main__":
    test_sistema_completo()