#!/usr/bin/env python3
"""
Test del sistema mejorado con verificación de datos
Prueba el nuevo nodo de verificación que previene alucinaciones
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.agents.graph_builder import LangGraphBuilder
from modules.utils.logger import setup_logger

logger = setup_logger(__name__)

async def test_improved_agent():
    """Prueba el agente mejorado con verificación de datos"""
    
    print("🧪 PRUEBA DEL AGENTE MEJORADO CON VERIFICACIÓN")
    print("=" * 60)
    
    try:
        # Crear el builder del grafo
        builder = LangGraphBuilder()
        
        # Construir el grafo con el nuevo nodo de verificación
        graph = builder.build_iot_agent_graph()
        print("✅ Grafo construido con nodo de verificación")
        
        # Pruebas diseñadas para activar alucinaciones
        test_queries = [
            "¿Cuál es la humedad actual en la oficina?",  # Debería detectar que no tenemos humedad
            "Analiza la temperatura y humedad de hoy",     # Debería corregir la parte de humedad
            "Dame un reporte de temperatura, presión y luz", # Debería corregir presión
            "¿Hay movimiento en la entrada?",              # Debería decir que no tenemos sensores de movimiento
            "Muestra solo los datos de temperatura"        # Esta debería pasar sin problemas
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 PRUEBA {i}: {query}")
            print("-" * 50)
            
            try:
                result = await builder.process_query(query)
                
                print(f"📊 **Status**: {result['status']}")
                print(f"📝 **Respuesta**:")
                print(result['response'])
                
                # Mostrar metadata de verificación si existe
                if 'execution_metadata' in result:
                    metadata = result['execution_metadata']
                    if 'nodes_executed' in metadata:
                        print(f"🔧 **Nodos ejecutados**: {metadata['nodes_executed']}")
                
                print(f"🎯 **Herramientas usadas**: {result.get('tools_used', [])}")
                
            except Exception as e:
                print(f"❌ Error en prueba {i}: {e}")
            
            print()
        
        print("✅ TODAS LAS PRUEBAS COMPLETADAS")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_improved_agent())
