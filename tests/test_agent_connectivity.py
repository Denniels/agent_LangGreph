#!/usr/bin/env python3
"""
Test específico para verificar conectividad del agente IoT
"""

import sys
import os

# Agregar path del proyecto
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

def test_agent_connectivity():
    print("🔍 PROBANDO CONECTIVIDAD DEL AGENTE IoT")
    print("=" * 50)
    
    try:
        # Importar el agente
        from modules.agents.cloud_iot_agent import CloudIoTAgent
        import asyncio
        print("✅ Agente importado correctamente")
        
        # Crear instancia
        agent = CloudIoTAgent()
        print("✅ Agente instanciado correctamente")
        
        # INICIALIZAR EL AGENTE (esto es clave!)
        async def init_and_test():
            await agent.initialize()
            print("✅ Agente inicializado correctamente")
            
            # Probar conexión directa con el conector
            if hasattr(agent, 'jetson_connector') and agent.jetson_connector:
                print("✅ Agente tiene jetson_connector activo")
                
                # Probar obtener dispositivos
                try:
                    devices = agent.jetson_connector.get_devices()
                    print(f"✅ Dispositivos obtenidos: {len(devices)} dispositivos")
                    for device in devices:
                        print(f"   - {device.get('device_id')}: {device.get('status')}")
                except Exception as e:
                    print(f"❌ Error obteniendo dispositivos: {e}")
                    
                # Probar obtener datos
                try:
                    data = agent.jetson_connector.get_sensor_data(limit=5)
                    print(f"✅ Datos obtenidos: {len(data)} registros")
                    if data:
                        print(f"   - Último registro: {data[0].get('device_id')} - {data[0].get('sensor_type')}")
                except Exception as e:
                    print(f"❌ Error obteniendo datos: {e}")
            else:
                print("❌ Agente NO tiene jetson_connector activo")
                
            # Probar consulta simple
            try:
                response = await agent.process_query("lista los dispositivos disponibles")
                print("✅ Consulta procesada correctamente")
                print(f"Respuesta (primeros 200 chars): {response[:200]}...")
            except Exception as e:
                print(f"❌ Error procesando consulta: {e}")
                import traceback
                traceback.print_exc()
        
        # Ejecutar test asíncrono
        asyncio.run(init_and_test())
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent_connectivity()