"""
Remote IoT Agent - Versión completa para API de Jetson
====================================================

Agente IoT completo que usa la API remota de Jetson en lugar de base de datos local.
"""

import sys
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Añadir el directorio padre al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

from modules.agents.langgraph_state import (
    IoTAgentState, QueryIntent, ToolType, ExecutionStatus, NodeNames, create_initial_state
)
from modules.agents.remote_langgraph_nodes import RemoteLangGraphNodes
from modules.utils.logger import setup_logger

logger = setup_logger(__name__)


class RemoteIoTAgent:
    """
    Agente IoT que utiliza LangGraph con conexión remota a API de Jetson.
    """
    
    def __init__(self):
        """Inicializar el agente remoto."""
        logger.info("🚀 Inicializando Remote IoT Agent")
        
        self.nodes = RemoteLangGraphNodes()
        self.graph = None
        self.app = None
        self.memory = MemorySaver()
        
        self._build_graph()
        logger.info("✅ Remote IoT Agent inicializado")
    
    def _build_graph(self):
        """Construir el grafo de LangGraph."""
        logger.info("🔧 Construyendo grafo remoto de LangGraph")
        
        # Crear el grafo
        workflow = StateGraph(IoTAgentState)
        
        # Añadir nodos
        workflow.add_node(NodeNames.QUERY_ANALYZER, self.nodes.query_analyzer_node)
        workflow.add_node(NodeNames.DATA_COLLECTOR, self.nodes.remote_data_collector_node)
        workflow.add_node(NodeNames.DATA_ANALYZER, self.nodes.data_analyzer_node)
        workflow.add_node(NodeNames.RESPONSE_GENERATOR, self.nodes.response_generator_node)
        workflow.add_node(NodeNames.DATA_VERIFICATION, self.nodes.data_verification_node)
        
        # Definir flujo del grafo
        workflow.add_edge(START, NodeNames.QUERY_ANALYZER)
        workflow.add_edge(NodeNames.QUERY_ANALYZER, NodeNames.DATA_COLLECTOR)
        workflow.add_edge(NodeNames.DATA_COLLECTOR, NodeNames.DATA_ANALYZER)
        workflow.add_edge(NodeNames.DATA_ANALYZER, NodeNames.RESPONSE_GENERATOR)
        workflow.add_edge(NodeNames.RESPONSE_GENERATOR, NodeNames.DATA_VERIFICATION)
        workflow.add_edge(NodeNames.DATA_VERIFICATION, END)
        
        # Compilar el grafo
        self.app = workflow.compile(checkpointer=self.memory)
        
        logger.info("✅ Grafo remoto construido exitosamente")
    
    async def process_query(self, user_query: str, thread_id: str = "default") -> Dict[str, Any]:
        """
        Procesar una consulta del usuario usando el grafo remoto.
        
        Args:
            user_query: Consulta del usuario
            thread_id: ID del hilo de conversación
            
        Returns:
            Dict con la respuesta y metadatos
        """
        try:
            logger.info(f"🔍 Procesando consulta remota: {user_query}")
            start_time = datetime.now()
            
            # Crear estado inicial
            initial_state = create_initial_state(user_query)
            initial_state["execution_metadata"]["start_time"] = start_time
            
            # Configuración del thread
            config = {"configurable": {"thread_id": thread_id}}
            
            # Ejecutar el grafo
            final_state = None
            async for output in self.app.astream(initial_state, config):
                for node_name, node_output in output.items():
                    logger.info(f"📋 Ejecutado nodo: {node_name}")
                    final_state = node_output
            
            # Calcular tiempo de ejecución
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Preparar respuesta
            response = {
                "success": True,
                "query": user_query,
                "response": final_state.get("final_response", "No se pudo generar respuesta"),
                "execution_time": execution_time,
                "data_source": final_state.get("data_source", "unknown"),
                "records_processed": len(final_state.get("raw_data", [])),
                "nodes_executed": final_state.get("execution_metadata", {}).get("nodes_executed", []),
                "verification_status": final_state.get("verification_status", "unknown"),
                "timestamp": end_time.isoformat()
            }
            
            # Añadir información de verificación si hay correcciones
            if final_state.get("verification_status") == "corrected":
                response["hallucinations_detected"] = final_state.get("hallucinations_detected", [])
                response["correction_applied"] = True
            
            # Añadir información de error si existe
            if final_state.get("error_info"):
                response["warnings"] = [final_state["error_info"]]
            
            logger.info(f"✅ Consulta procesada en {execution_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error procesando consulta: {e}")
            return {
                "success": False,
                "query": user_query,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_graph_visualization(self) -> str:
        """
        Obtener representación visual del grafo.
        
        Returns:
            String con la estructura del grafo
        """
        return """
🔄 REMOTE IOT AGENT FLOW:
========================

START
  ↓
🔍 Query Analyzer
  │ • Analiza intención del usuario
  │ • Detecta tipo de datos requeridos
  ↓
📡 Remote Data Collector  
  │ • Conecta a API de Jetson
  │ • Obtiene datos en tiempo real
  │ • Formatea para LLM
  ↓
🔬 Data Analyzer
  │ • Analiza datos obtenidos
  │ • Genera estadísticas/tendencias
  ↓
🤖 Response Generator
  │ • Genera respuesta con Ollama
  │ • Integra datos y análisis
  ↓
✅ Data Verification
  │ • Previene alucinaciones
  │ • Corrige respuestas si necesario
  ↓
END

📊 DATA SOURCE: Jetson API (Cloudflare Tunnel)
🌐 REMOTE SENSORS: Arduino ETH + ESP32 WiFi
        """
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verificar estado de salud del agente y conexiones remotas.
        
        Returns:
            Dict con estado de salud
        """
        try:
            logger.info("💓 Verificando salud del agente remoto")
            
            # Verificar conexión a API de Jetson
            health = self.nodes.remote_collector.check_api_health()
            
            # Verificar Ollama
            ollama_status = "unknown"
            try:
                # Test simple de Ollama
                test_response = await self.nodes.ollama.generate_response({
                    'query': 'test',
                    'sensor_data': 'test data',
                    'analysis': {}
                })
                ollama_status = "healthy" if test_response else "unhealthy"
            except Exception:
                ollama_status = "unhealthy"
            
            return {
                "agent_status": "healthy",
                "jetson_api": health.get("status", "unknown"),
                "ollama_llm": ollama_status,
                "graph_ready": self.app is not None,
                "timestamp": datetime.now().isoformat(),
                "api_details": health
            }
            
        except Exception as e:
            logger.error(f"❌ Error en health check: {e}")
            return {
                "agent_status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Función de utilidad para crear instancia global
def create_remote_agent() -> RemoteIoTAgent:
    """Crear instancia del agente remoto."""
    return RemoteIoTAgent()


async def main():
    """Función principal para pruebas."""
    print("🚀 PRUEBA DEL REMOTE IOT AGENT COMPLETO")
    print("=" * 60)
    
    # Crear agente
    agent = create_remote_agent()
    
    # Mostrar estructura del grafo
    print(agent.get_graph_visualization())
    
    # Health check
    print("💓 VERIFICANDO SALUD DEL SISTEMA...")
    health = await agent.health_check()
    print(f"   Estado del agente: {health.get('agent_status')}")
    print(f"   API de Jetson: {health.get('jetson_api')}")
    print(f"   LLM Ollama: {health.get('ollama_llm')}")
    print(f"   Grafo listo: {health.get('graph_ready')}")
    
    # Pruebas de consultas
    test_queries = [
        "¿Cuál es la temperatura actual?",
        "Muéstrame los datos del Arduino",
        "¿Cómo están los sensores del ESP32?",
        "Dame un análisis de las temperaturas"
    ]
    
    print("\n🧪 PROBANDO CONSULTAS...")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}️⃣ CONSULTA: {query}")
        print("-" * 40)
        
        response = await agent.process_query(query, thread_id=f"test_{i}")
        
        if response.get("success"):
            print(f"✅ Respuesta generada en {response.get('execution_time', 0):.2f}s")
            print(f"📊 Registros procesados: {response.get('records_processed', 0)}")
            print(f"🔄 Nodos ejecutados: {len(response.get('nodes_executed', []))}")
            print(f"✅ Verificación: {response.get('verification_status', 'unknown')}")
            print(f"📝 Respuesta: {response.get('response', 'N/A')[:200]}...")
        else:
            print(f"❌ Error: {response.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("✅ PRUEBAS COMPLETADAS")
    print("🚀 Remote IoT Agent listo para producción!")


if __name__ == "__main__":
    asyncio.run(main())
