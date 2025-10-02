#!/usr/bin/env python3
"""
Test completo del agente con la corrección
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.agents.cloud_iot_agent import CloudIoTAgent

async def test_agent_data_collection():
    """Probar que el agente puede obtener datos"""
    print("=== TEST COMPLETO DEL AGENTE CON CORRECION ===")
    print()
    
    try:
        # Crear agente
        print("1. Creando agente...")
        agent = CloudIoTAgent()
        print("   ✅ Agente creado")
        print()
        
        # Inicializar
        print("2. Inicializando agente...")
        await agent.initialize()
        print("   ✅ Agente inicializado")
        print()
        
        # Verificar conector Jetson
        print("3. Verificando conector Jetson...")
        if agent.jetson_connector:
            print("   ✅ Jetson connector disponible")
            
            # Probar get_devices
            devices = agent.jetson_connector.get_devices()
            print(f"   📱 Dispositivos encontrados: {len(devices)}")
            for device in devices:
                print(f"      - {device['device_id']}: {device['status']}")
            
            # Probar get_sensor_data
            if devices:
                device_id = devices[0]['device_id']
                sensor_data = agent.jetson_connector.get_sensor_data(device_id=device_id, limit=3)
                print(f"   📊 Datos de {device_id}: {len(sensor_data)} registros")
                if sensor_data:
                    print(f"      Último valor: {sensor_data[0]['sensor_type']} = {sensor_data[0]['value']}")
        else:
            print("   ❌ Jetson connector no disponible")
        print()
        
        # Probar consulta simple
        print("4. Probando consulta simple al agente...")
        query = "¿Qué dispositivos están conectados?"
        
        result = await agent.process_query(query)
        print(f"   Consulta: {query}")
        print(f"   Respuesta: {result[:200]}...")
        
        if "esp32" in result.lower() or "arduino" in result.lower():
            print("   ✅ Agente reconoce dispositivos")
        else:
            print("   ⚠️ Agente no menciona dispositivos específicos")
        
        print()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agent_data_collection())