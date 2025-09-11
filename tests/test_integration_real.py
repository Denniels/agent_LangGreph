#!/usr/bin/env python3
"""
Test paso a paso del agente completo para identificar dónde falla
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.agents.graph_builder import LangGraphBuilder

async def test_agent_step_by_step():
    """Test detallado paso a paso del agente"""
    
    print("🧪 TEST PASO A PASO DEL AGENTE COMPLETO")
    print("=" * 60)
    
    try:
        builder = LangGraphBuilder()
        graph = builder.build_iot_agent_graph()
        print("✅ Grafo construido exitosamente")
        
        # Test con una consulta simple de temperatura
        query = "¿Cuál es la temperatura actual?"
        print(f"\n🔍 CONSULTA: {query}")
        print("-" * 40)
        
        result = await builder.process_query(query)
        
        print(f"\n📊 RESULTADO COMPLETO:")
        print(f"  Status: {result['status']}")
        print(f"  Response length: {len(result.get('response', ''))}")
        print(f"  Query intent: {result.get('query_intent')}")
        print(f"  Tools used: {result.get('tools_used', [])}")
        
        if 'execution_metadata' in result:
            metadata = result['execution_metadata']
            print(f"  Nodes executed: {metadata.get('nodes_executed', [])}")
            print(f"  Duration: {metadata.get('total_duration')} seconds")
        
        print(f"\n📝 RESPUESTA:")
        print(result.get('response', 'Sin respuesta'))
        
        # Verificar si el agente realmente obtuvo datos
        print(f"\n🔍 ANÁLISIS DETALLADO:")
        
        # Ver si hay tool_results en metadata
        if 'execution_metadata' in result:
            print("  Metadata disponible ✅")
        else:
            print("  ❌ No hay metadata de ejecución")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_step_by_step())
