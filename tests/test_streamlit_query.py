#!/usr/bin/env python3
"""
Test específico del mensaje de Streamlit
=======================================

Reproduce exactamente la consulta que aparece en la imagen de Streamlit
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.agents.iot_agent_ollama import IoTAgent
from modules.tools.database_tools import DatabaseTools


async def test_streamlit_query():
    """Test específico para reproducir el problema de Streamlit"""
    
    print("🔍 TEST: Reproduciendo problema de Streamlit")
    print("=" * 60)
    
    # 1. Probar DatabaseTools directamente
    print("\n1️⃣ Probando DatabaseTools directamente...")
    db_tools = DatabaseTools()
    
    sensor_data = await db_tools.get_sensor_data_tool(limit=5)
    devices = await db_tools.get_devices_tool()
    alerts = await db_tools.get_alerts_tool()
    
    print(f"📊 sensor_data: {len(sensor_data)} registros")
    print(f"📱 devices: {len(devices)} dispositivos") 
    print(f"🚨 alerts: {len(alerts)} alertas")
    
    if sensor_data:
        print("\n🔍 Primer registro de sensor_data:")
        for key, value in sensor_data[0].items():
            print(f"   {key}: {value}")
    else:
        print("❌ sensor_data está vacío!")
    
    # 2. Probar el contexto que usa el agente
    print("\n2️⃣ Probando contexto del agente...")
    agent = IoTAgent()
    
    # Simular _gather_context_data
    tools_to_use = ['sensor_data', 'devices', 'alerts']
    context = await agent._gather_context_data(tools_to_use)
    
    print(f"📋 Contexto generado:")
    print(f"   timestamp: {context.get('timestamp')}")
    print(f"   tools_requested: {context.get('tools_requested')}")
    print(f"   recent_data: {len(context.get('recent_data', []))} registros")
    print(f"   active_devices: {len(context.get('active_devices', []))} dispositivos")
    print(f"   alerts: {len(context.get('alerts', []))} alertas")
    
    if context.get('recent_data'):
        print("\n🔍 Primer registro en contexto:")
        for key, value in context['recent_data'][0].items():
            print(f"   {key}: {value}")
    
    # 3. Simular exactamente lo que hace Ollama
    print("\n3️⃣ Simulando prompt para Ollama...")
    
    # Crear el prompt que se envía a Ollama
    prompt_data = {
        "user_message": "¿Cuál es el estado actual de los sensores?",
        "context_data": context,
        "tools_results": {}
    }
    
    print(f"\n📝 Datos que se envían a Ollama:")
    print(f"   user_message: {prompt_data['user_message']}")
    print(f"   context_data tiene: {list(context.keys())}")
    
    # Mostrar datos específicos que Ollama está viendo
    recent_data = context.get('recent_data', [])
    if recent_data:
        print(f"\n📊 Datos de sensores que ve Ollama:")
        for i, data in enumerate(recent_data[:3]):
            print(f"   Registro {i+1}:")
            print(f"     device_id: {data.get('device_id')}")
            print(f"     sensor_type: {data.get('sensor_type')}")
            print(f"     value: {data.get('value')}")
            print(f"     timestamp: {data.get('timestamp')}")
    else:
        print("❌ Ollama está viendo sensor_data vacío!")
    
    # 4. Test de respuesta completa
    print("\n4️⃣ Test de respuesta completa del agente...")
    
    response = await agent.process_message("¿Cuál es el estado actual de los sensores?")
    
    print(f"\n🤖 Respuesta del agente:")
    print("-" * 40)
    print(response[:500] + "..." if len(response) > 500 else response)
    print("-" * 40)
    
    print("\n✅ TEST COMPLETADO")


if __name__ == "__main__":
    asyncio.run(test_streamlit_query())
