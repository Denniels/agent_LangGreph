"""
Test para verificar que el DirectAPIAgent corregido obtiene datos reales de dispositivos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import json
from modules.agents.direct_api_agent import create_direct_api_agent

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_api_agent_corrected():
    """
    Test para verificar que el DirectAPIAgent corregido funciona correctamente
    """
    print("🔬 Test DirectAPIAgent Corregido")
    print("=" * 50)
    
    # URL actual que funciona
    api_url = "https://replica-subscriber-permission-restricted.trycloudflare.com"
    
    try:
        # Crear agente
        agent = create_direct_api_agent(api_url)
        print(f"✅ Agente creado con URL: {api_url}")
        
        # Test 1: Obtener dispositivos
        print("\n📱 Test 1: Obtener dispositivos")
        devices = agent.get_devices_direct()
        print(f"Dispositivos encontrados: {len(devices)}")
        
        if devices:
            for i, device in enumerate(devices):
                device_id = device.get('device_id', 'Sin ID')
                status = device.get('status', 'Sin estado')
                print(f"  {i+1}. {device_id} - {status}")
                
                # Verificar que son dispositivos reales, no claves JSON
                expected_devices = ['arduino_eth_001', 'esp32_wifi_001']
                if device_id in expected_devices:
                    print(f"    ✅ {device_id} es un dispositivo real")
                else:
                    print(f"    ❌ {device_id} no parece ser un dispositivo válido")
        else:
            print("❌ No se encontraron dispositivos")
            return False
        
        # Test 2: Obtener datos de sensores para un dispositivo
        print("\n🔬 Test 2: Obtener datos de sensores")
        if devices:
            # Probar con ambos dispositivos
            for device in devices:
                device_id = device.get('device_id')
                sensor_data = agent.get_sensor_data_direct(device_id, limit=10)
                print(f"Datos de sensores para {device_id}: {len(sensor_data)} registros")
                
                if sensor_data and isinstance(sensor_data, list) and len(sensor_data) > 0:
                    # Mostrar primeros registros
                    for i, record in enumerate(sensor_data[:3]):
                        timestamp = record.get('timestamp', 'Sin timestamp')
                        sensor_type = record.get('sensor_type', 'Sin tipo')
                        value = record.get('value', 'Sin valor')
                        print(f"  {i+1}. {timestamp} - {sensor_type}: {value}")
                    break  # Si encontramos datos, salir del loop
                else:
                    print(f"⚠️ {device_id}: Sin datos de sensores o acceso temporal bloqueado")
        
        # Test 3: Obtener todos los datos recientes
        print("\n📊 Test 3: Obtener todos los datos recientes")
        all_data = agent.get_all_recent_data()
        print(f"Estado: {all_data.get('status', 'Sin estado')}")
        print(f"Dispositivos activos: {all_data.get('active_devices', 0)}")
        print(f"Registros totales: {all_data.get('total_records', 0)}")
        
        # Test 4: Formatear respuesta para el agente
        print("\n💬 Test 4: Formatear respuesta para el agente")
        formatted_response = agent.format_for_analysis("Estado del sistema IoT")
        print("Respuesta formateada (primeros 500 caracteres):")
        print(formatted_response[:500] + "..." if len(formatted_response) > 500 else formatted_response)
        
        # Verificar que la respuesta contiene dispositivos reales
        if 'arduino_eth_001' in formatted_response and 'esp32_wifi_001' in formatted_response:
            print("✅ La respuesta contiene dispositivos reales")
        else:
            print("❌ La respuesta NO contiene dispositivos reales")
            return False
        
        print("\n🎉 Todos los tests pasaron exitosamente!")
        print("✅ DirectAPIAgent corregido está funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        logger.exception("Error detallado:")
        return False

if __name__ == "__main__":
    test_direct_api_agent_corrected()