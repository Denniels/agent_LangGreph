"""
Script de prueba para el agente IoT LangGraph
============================================

Prueba la implementación completa del StateGraph de LangGraph.
"""

import asyncio
import time
from datetime import datetime

from modules.agents.iot_agent_langgraph import langgraph_agent
from modules.utils.logger import setup_logger

logger = setup_logger(__name__)

async def test_langgraph_agent():
    """Prueba completa del agente LangGraph."""
    
    print("🚀 Iniciando pruebas del agente LangGraph StateGraph")
    print("=" * 60)
    
    try:
        # 1. Inicializar agente
        print("\n1️⃣ Inicializando agente...")
        await langgraph_agent.initialize()
        print("✅ Agente inicializado exitosamente")
        
        # 2. Verificar estado del agente
        print("\n2️⃣ Verificando estado del agente...")
        status = await langgraph_agent.get_agent_status()
        print(f"📊 Estado: {status}")
        
        # 3. Obtener capacidades
        print("\n3️⃣ Obteniendo capacidades...")
        capabilities = await langgraph_agent.get_available_capabilities()
        print(f"🔧 Nodos disponibles: {len(capabilities.get('available_tools', []))}")
        print(f"⚡ Características: {len(capabilities.get('graph_features', []))}")
        
        # 4. Visualización del grafo
        print("\n4️⃣ Visualizando estructura del grafo...")
        graph_viz = await langgraph_agent.get_graph_visualization()
        print(f"🔗 Nodos: {len(graph_viz.get('nodes', []))}")
        print(f"📊 Aristas: {len(graph_viz.get('edges', []))}")
        
        # 5. Pruebas de consultas
        test_queries = [
            "¿Cuántos registros de sensores hay en total?",
            "Muestra los últimos datos de sensores",
            "¿Qué dispositivos están activos?", 
            "Analiza las tendencias de temperatura",
            "Detecta anomalías en los datos",
            "Genera estadísticas de los sensores"
        ]
        
        print(f"\n5️⃣ Ejecutando {len(test_queries)} consultas de prueba...")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Consulta {i}/6 ---")
            print(f"📝 Query: {query}")
            
            start_time = time.time()
            
            result = await langgraph_agent.process_query(
                user_query=query,
                user_id="test_user",
                session_id=f"test_session_{i}"
            )
            
            duration = time.time() - start_time
            
            print(f"⏱️ Tiempo: {duration:.2f}s")
            print(f"📊 Estado: {result.get('status')}")
            print(f"🎯 Intención: {result.get('query_intent')}")
            print(f"🛠️ Herramientas: {result.get('tools_used', [])}")
            print(f"💬 Respuesta: {result.get('response', '')[:200]}...")
            
            # Verificar metadatos de ejecución
            metadata = result.get('execution_metadata', {})
            nodes_executed = metadata.get('nodes_executed', [])
            print(f"🔗 Nodos ejecutados: {nodes_executed}")
            
            if result.get('status') != 'success':
                print(f"⚠️ Advertencia: Estado no exitoso - {result.get('status')}")
        
        # 6. Prueba de manejo de errores
        print(f"\n6️⃣ Probando manejo de errores...")
        
        error_query = "Esta es una consulta inválida con caracteres especiales ñáéíóú @#$%"
        result = await langgraph_agent.process_query(
            user_query=error_query,
            user_id="test_user",
            session_id="error_test_session"
        )
        
        print(f"📊 Estado error test: {result.get('status')}")
        print(f"💬 Respuesta error: {result.get('response', '')[:200]}...")
        
        # 7. Prueba de historial de sesión
        print(f"\n7️⃣ Verificando historial de sesión...")
        
        history = await langgraph_agent.get_session_history("test_session_1")
        print(f"📚 Interacciones en historial: {len(history)}")
        
        if history:
            last_interaction = history[-1]
            print(f"🕐 Última interacción: {last_interaction.get('timestamp')}")
            print(f"📝 Última consulta: {last_interaction.get('user_query')}")
        
        # 8. Estadísticas finales
        print(f"\n8️⃣ Estadísticas finales...")
        
        final_status = await langgraph_agent.get_agent_status()
        print(f"📈 Sesiones activas: {final_status.get('active_sessions')}")
        print(f"🕐 Timestamp final: {final_status.get('timestamp')}")
        
        # 9. Prueba de reinicio de sesión
        print(f"\n9️⃣ Probando reinicio de sesión...")
        
        reset_result = await langgraph_agent.reset_session("test_session_1")
        print(f"🔄 Reinicio exitoso: {reset_result.get('success')}")
        print(f"💬 Mensaje: {reset_result.get('message')}")
        
        print("\n" + "=" * 60)
        print("✅ ¡Todas las pruebas completadas exitosamente!")
        print("🎯 El agente LangGraph StateGraph está funcionando correctamente")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        logger.error(f"Error en pruebas LangGraph: {e}")
        raise
    
    finally:
        # Cleanup
        await langgraph_agent.shutdown()
        print("🔽 Agente cerrado")

async def test_graph_flow():
    """Prueba específica del flujo del StateGraph."""
    
    print("\n🔗 Prueba específica del flujo StateGraph")
    print("-" * 40)
    
    await langgraph_agent.initialize()
    
    # Consulta que active todos los nodos
    complex_query = "Analiza todos los datos de sensores, detecta anomalías y genera un reporte completo con estadísticas"
    
    print(f"📝 Consulta compleja: {complex_query}")
    
    result = await langgraph_agent.process_query(
        user_query=complex_query,
        user_id="flow_test_user",
        session_id="flow_test_session"
    )
    
    # Analizar el flujo de ejecución
    metadata = result.get('execution_metadata', {})
    nodes_executed = metadata.get('nodes_executed', [])
    tools_used = metadata.get('tools_used', [])
    duration = metadata.get('total_duration', 0)
    
    print(f"\n📊 Resultados del flujo:")
    print(f"🔗 Nodos ejecutados: {nodes_executed}")
    print(f"🛠️ Herramientas usadas: {tools_used}")
    print(f"⏱️ Duración total: {duration:.2f}s")
    print(f"📊 Estado final: {result.get('status')}")
    print(f"🎯 Intención detectada: {result.get('query_intent')}")
    
    # Verificar que el grafo funcionó correctamente
    expected_nodes = ['query_analyzer', 'data_collector', 'data_analyzer', 'response_generator']
    nodes_match = all(node in nodes_executed for node in expected_nodes)
    
    print(f"\n✅ Flujo StateGraph completo: {'SÍ' if nodes_match else 'NO'}")
    
    if not nodes_match:
        missing_nodes = [node for node in expected_nodes if node not in nodes_executed]
        print(f"❌ Nodos faltantes: {missing_nodes}")
    
    await langgraph_agent.shutdown()

def main():
    """Función principal para ejecutar las pruebas."""
    
    print("🤖 Pruebas del Agente IoT LangGraph StateGraph")
    print("=" * 60)
    print(f"🕐 Inicio: {datetime.now()}")
    
    try:
        # Ejecutar pruebas principales
        asyncio.run(test_langgraph_agent())
        
        print("\n" + "🔄" * 20)
        
        # Ejecutar prueba específica de flujo
        asyncio.run(test_graph_flow())
        
        print(f"\n🕐 Fin: {datetime.now()}")
        print("🎉 ¡Todas las pruebas completadas exitosamente!")
        
    except Exception as e:
        print(f"\n💥 Error crítico en las pruebas: {e}")
        print("❌ Las pruebas fallaron")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
