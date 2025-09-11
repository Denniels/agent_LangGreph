#!/usr/bin/env python3
"""
Test específico de las herramientas de base de datos del agente
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.tools.database_tools import DatabaseTools

async def test_agent_tools():
    """Test de las herramientas que usa el agente"""
    
    print("🔧 TEST DE HERRAMIENTAS DEL AGENTE")
    print("=" * 50)
    
    try:
        tools = DatabaseTools()
        
        # 1. Test herramienta de datos de sensores
        print("\n📊 TEST: get_sensor_data_tool")
        sensor_data = await tools.get_sensor_data_tool(limit=10)
        print(f"  ✅ Resultados: {len(sensor_data)}")
        if sensor_data:
            print(f"  📝 Primer registro: {sensor_data[0]}")
        else:
            print("  ❌ NO HAY DATOS")
        
        # 2. Test herramienta de datos recientes
        print("\n⏰ TEST: get_recent_sensor_data_tool")
        recent_data = await tools.get_recent_sensor_data_tool(minutes=10, limit=10)
        print(f"  ✅ Resultados: {len(recent_data)}")
        if recent_data:
            print(f"  📝 Primer registro: {recent_data[0]}")
        else:
            print("  ❌ NO HAY DATOS RECIENTES")
        
        # 3. Test herramienta de dispositivos
        print("\n🔌 TEST: get_devices_tool")
        devices = await tools.get_devices_tool()
        print(f"  ✅ Resultados: {len(devices)}")
        if devices:
            print(f"  📝 Primer dispositivo: {devices[0]}")
        else:
            print("  ❌ NO HAY DISPOSITIVOS")
        
        # 4. Test herramienta de datos por dispositivo específico
        print("\n📱 TEST: get_sensor_data_tool con device_id")
        device_data = await tools.get_sensor_data_tool(device_id="arduino_eth_001", limit=5)
        print(f"  ✅ Resultados: {len(device_data)}")
        if device_data:
            print(f"  📝 Primer registro: {device_data[0]}")
        else:
            print("  ❌ NO HAY DATOS DEL DISPOSITIVO")
        
        # 5. Test herramienta de alertas
        print("\n⚠️ TEST: get_alerts_tool")
        alerts = await tools.get_alerts_tool()
        print(f"  ✅ Resultados: {len(alerts)}")
        if alerts:
            print(f"  📝 Primera alerta: {alerts[0]}")
        else:
            print("  ❌ NO HAY ALERTAS")
        
        print("\n" + "=" * 50)
        print("✅ TESTS COMPLETADOS")
        
    except Exception as e:
        print(f"❌ Error en tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_tools())
