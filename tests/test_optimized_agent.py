#!/usr/bin/env python3
"""
Prueba del Agente IoT Optimizado
===============================

Script para probar las mejoras en acceso a datos en tiempo real
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.agents.iot_agent_ollama import IoTAgent


async def test_optimized_agent():
    """Prueba el agente con datos optimizados"""
    
    print("🚀 PRUEBA DEL AGENTE IoT OPTIMIZADO")
    print("=" * 60)
    
    # Inicializar agente
    print("\n1️⃣ Inicializando agente...")
    agent = IoTAgent()
    
    # Probar recopilación de contexto
    print("\n2️⃣ Probando recopilación de contexto optimizada...")
    tools = ['sensor_data', 'devices', 'alerts']
    context = await agent._gather_context_data(tools)
    
    print(f"📊 Resumen de datos:")
    if 'data_summary' in context:
        summary = context['data_summary']
        print(f"   - Registros recientes: {summary['total_recent_records']}")
        print(f"   - Registros ultra-recientes: {summary['ultra_recent_records']}")
        print(f"   - Dispositivos activos: {summary['active_devices_count']}")
        print(f"   - Alertas activas: {summary['active_alerts_count']}")
    
    # Mostrar algunos datos recientes
    if 'ultra_recent_data' in context and context['ultra_recent_data']:
        print(f"\n📋 Últimos 5 registros ultra-recientes:")
        for i, record in enumerate(context['ultra_recent_data'][:5]):
            print(f"   {i+1}. {record['device_id']} - {record['sensor_type']}: {record['value']} @ {record['timestamp']}")
    
    # Probar consulta al agente
    print("\n3️⃣ Probando consulta al agente...")
    test_query = "¿Cuál es el estado actual de los sensores en tiempo real?"
    
    print(f"🔍 Consulta: {test_query}")
    print(f"⏰ Hora: {datetime.now()}")
    
    try:
        response = await agent.process_message(test_query)
        print(f"\n🤖 Respuesta del agente:")
        print(f"{response}")
        
    except Exception as e:
        print(f"❌ Error en la consulta: {e}")
    
    print("\n" + "=" * 60)
    print("✅ PRUEBA COMPLETADA")


if __name__ == "__main__":
    asyncio.run(test_optimized_agent())
