#!/usr/bin/env python3
"""
Prueba específica del flujo de datos en Remote IoT Agent
Depurar por qué los datos no se transfieren entre nodos
"""

import sys
import os
import asyncio
from datetime import datetime

# Añadir el directorio padre al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from modules.agents.remote_iot_agent import RemoteIoTAgent

async def debug_data_flow():
    """Depurar el flujo de datos paso a paso"""
    print("🔍 DEPURACIÓN DEL FLUJO DE DATOS")
    print("=" * 50)
    
    # Crear agente
    agent = RemoteIoTAgent()
    
    # Configurar para una sola consulta de prueba
    query = "¿Cuál es la temperatura actual?"
    thread_id = "debug_test"
    
    print(f"📝 Consulta: {query}")
    print(f"🔧 Thread ID: {thread_id}")
    
    # Crear estado inicial manualmente
    from modules.agents.langgraph_state import create_initial_state
    initial_state = create_initial_state(query)
    initial_state["execution_metadata"]["start_time"] = datetime.now()
    
    print(f"\n🎯 Estado inicial:")
    print(f"  - Query: {initial_state.get('user_query')}")
    print(f"  - Raw data: {len(initial_state.get('raw_data', []))}")
    
    # Configuración del thread
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"\n🔄 Ejecutando grafo paso a paso...")
    
    step_count = 0
    async for output in agent.app.astream(initial_state, config):
        step_count += 1
        for node_name, node_output in output.items():
            print(f"\n📋 PASO {step_count}: {node_name}")
            print(f"  - Raw data: {len(node_output.get('raw_data', []))}")
            print(f"  - Formatted data presente: {'formatted_data' in node_output}")
            print(f"  - Data source: {node_output.get('data_source', 'N/A')}")
            print(f"  - Error info: {node_output.get('error_info', 'None')}")
            
            # Mostrar muestra de datos si existen
            raw_data = node_output.get('raw_data', [])
            if raw_data:
                print(f"  - Muestra de datos: {raw_data[0]}")
            
            # Si es el nodo de data_collector, mostrar más detalles
            if node_name == "data_collector":
                print(f"  - Collection success: {node_output.get('data_collection_success', 'N/A')}")
                print(f"  - Collection error: {node_output.get('data_collection_error', 'None')}")
                formatted = node_output.get('formatted_data', '')
                print(f"  - Formatted data length: {len(formatted)}")
                if formatted:
                    print(f"  - Formatted preview: {formatted[:200]}...")
            
            final_state = node_output
    
    print(f"\n📊 ESTADO FINAL:")
    print(f"  - Raw data: {len(final_state.get('raw_data', []))}")
    print(f"  - Final response presente: {'final_response' in final_state}")
    print(f"  - Verification status: {final_state.get('verification_status', 'unknown')}")
    
    if final_state.get('raw_data'):
        print(f"  - Tipos de sensores detectados:")
        sensor_types = set()
        for record in final_state.get('raw_data', []):
            sensor_type = record.get('sensor_type')
            if sensor_type:
                sensor_types.add(sensor_type)
        print(f"    {sensor_types}")
    
    print(f"\n✅ Depuración completada")
    return final_state

if __name__ == "__main__":
    asyncio.run(debug_data_flow())
