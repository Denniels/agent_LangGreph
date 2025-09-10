"""
Constructor de Gráficos LangGraph COMPLETO
=========================================

Implementación completa del StateGraph usando LangGraph para el agente IoT.
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from modules.agents.langgraph_state import (
    IoTAgentState, NodeNames, ExecutionStatus, create_initial_state
)
from modules.agents.langgraph_nodes import LangGraphNodes
from modules.utils.logger import setup_logger

logger = setup_logger(__name__)


class LangGraphBuilder:
    """
    Constructor completo de gráficos LangGraph para el agente IoT.
    Implementa StateGraph con nodos especializados y flujo condicional.
    """
    
    def __init__(self):
        self.nodes = LangGraphNodes()
        self.graph = None
        self.checkpointer = MemorySaver()
        logger.info("🔧 LangGraphBuilder inicializado")
    
    def build_iot_agent_graph(self) -> StateGraph:
        """
        Construye el grafo completo del agente IoT con nodos especializados.
        
        Returns:
            StateGraph configurado y compilado
        """
        logger.info("🏗️ Construyendo StateGraph del agente IoT")
        
        # Crear el grafo con el estado
        workflow = StateGraph(IoTAgentState)
        
        # Agregar nodos especializados
        workflow.add_node(NodeNames.QUERY_ANALYZER, self.nodes.query_analyzer_node)
        workflow.add_node(NodeNames.DATA_COLLECTOR, self.nodes.data_collector_node)
        workflow.add_node(NodeNames.DATA_ANALYZER, self.nodes.data_analyzer_node)
        workflow.add_node(NodeNames.RESPONSE_GENERATOR, self.nodes.response_generator_node)
        workflow.add_node(NodeNames.ERROR_HANDLER, self.nodes.error_handler_node)
        
        # Configurar punto de entrada
        workflow.set_entry_point(NodeNames.QUERY_ANALYZER)
        
        # Definir flujo principal
        workflow.add_edge(NodeNames.QUERY_ANALYZER, NodeNames.DATA_COLLECTOR)
        workflow.add_edge(NodeNames.DATA_COLLECTOR, NodeNames.DATA_ANALYZER)
        workflow.add_edge(NodeNames.DATA_ANALYZER, NodeNames.RESPONSE_GENERATOR)
        
        # Flujo condicional desde response_generator
        workflow.add_conditional_edges(
            NodeNames.RESPONSE_GENERATOR,
            self._should_end_or_handle_error,
            {
                "end": END,
                "error": NodeNames.ERROR_HANDLER
            }
        )
        
        # Flujo condicional desde error_handler
        workflow.add_conditional_edges(
            NodeNames.ERROR_HANDLER,
            self._should_retry_or_end,
            {
                "retry": NodeNames.QUERY_ANALYZER,
                "end": END
            }
        )
        
        # Compilar el grafo con checkpointer para persistencia
        self.graph = workflow.compile(checkpointer=self.checkpointer)
        
        logger.info("✅ StateGraph compilado exitosamente")
        return self.graph
    
    async def process_query(self, user_query: str, thread_id: str = "default") -> Dict[str, Any]:
        """
        Procesa una consulta del usuario usando el grafo LangGraph.
        
        Args:
            user_query: Consulta del usuario
            thread_id: ID del hilo de conversación
            
        Returns:
            Resultado del procesamiento con respuesta final
        """
        try:
            logger.info(f"🚀 Procesando consulta: {user_query}")
            
            # Crear estado inicial
            initial_state = create_initial_state(
                user_query=user_query,
                messages=[HumanMessage(content=user_query)]
            )
            
            # Configurar thread para persistencia
            config = {"configurable": {"thread_id": thread_id}}
            
            # Ejecutar el grafo
            final_state = None
            async for state in self.graph.astream(initial_state, config=config):
                final_state = state
                
                # Log del progreso
                if "execution_metadata" in state and "nodes_executed" in state["execution_metadata"]:
                    nodes = state["execution_metadata"]["nodes_executed"]
                    if nodes:
                        logger.info(f"📍 Nodo ejecutado: {nodes[-1]}")
            
            # Extraer resultado final
            if final_state:
                response = final_state.get("final_response", "No se pudo generar respuesta")
                status = final_state.get("execution_metadata", {}).get("status", ExecutionStatus.ERROR)
                
                result = {
                    "response": response,
                    "status": status,
                    "execution_metadata": final_state.get("execution_metadata", {}),
                    "query_intent": final_state.get("query_intent"),
                    "tools_used": final_state.get("execution_metadata", {}).get("tools_used", [])
                }
                
                logger.info(f"✅ Consulta procesada exitosamente. Status: {status}")
                return result
            
            else:
                logger.error("❌ No se obtuvo estado final del grafo")
                return {
                    "response": "Error interno procesando la consulta",
                    "status": ExecutionStatus.ERROR,
                    "execution_metadata": {}
                }
                
        except Exception as e:
            logger.error(f"❌ Error crítico procesando consulta: {e}")
            return {
                "response": f"Error procesando consulta: {str(e)}",
                "status": ExecutionStatus.ERROR,
                "execution_metadata": {"error": str(e)}
            }
    
    def get_graph_visualization(self) -> Dict[str, Any]:
        """
        Obtiene información para visualizar el grafo.
        
        Returns:
            Estructura del grafo para visualización
        """
        if not self.graph:
            return {"error": "Grafo no construido"}
        
        nodes_info = [
            {
                "id": NodeNames.QUERY_ANALYZER,
                "label": "Analizador de Consultas",
                "description": "Analiza intención y determina herramientas",
                "type": "analyzer"
            },
            {
                "id": NodeNames.DATA_COLLECTOR,
                "label": "Recopilador de Datos", 
                "description": "Ejecuta herramientas y recopila datos",
                "type": "collector"
            },
            {
                "id": NodeNames.DATA_ANALYZER,
                "label": "Analizador de Datos",
                "description": "Analiza datos y extrae insights",
                "type": "analyzer"
            },
            {
                "id": NodeNames.RESPONSE_GENERATOR,
                "label": "Generador de Respuestas",
                "description": "Genera respuesta final usando LLM",
                "type": "generator"
            },
            {
                "id": NodeNames.ERROR_HANDLER,
                "label": "Manejador de Errores",
                "description": "Maneja errores y reintentos",
                "type": "handler"
            }
        ]
        
        edges_info = [
            {"from": NodeNames.QUERY_ANALYZER, "to": NodeNames.DATA_COLLECTOR, "type": "sequential"},
            {"from": NodeNames.DATA_COLLECTOR, "to": NodeNames.DATA_ANALYZER, "type": "sequential"},
            {"from": NodeNames.DATA_ANALYZER, "to": NodeNames.RESPONSE_GENERATOR, "type": "sequential"},
            {"from": NodeNames.RESPONSE_GENERATOR, "to": "END", "type": "conditional"},
            {"from": NodeNames.RESPONSE_GENERATOR, "to": NodeNames.ERROR_HANDLER, "type": "conditional"},
            {"from": NodeNames.ERROR_HANDLER, "to": NodeNames.QUERY_ANALYZER, "type": "retry"},
            {"from": NodeNames.ERROR_HANDLER, "to": "END", "type": "conditional"}
        ]
        
        return {
            "nodes": nodes_info,
            "edges": edges_info,
            "entry_point": NodeNames.QUERY_ANALYZER,
            "features": [
                "Flujo condicional",
                "Manejo de errores",
                "Reintentos automáticos",
                "Persistencia de estado",
                "Ejecución paralela de herramientas"
            ]
        }
    
    def get_execution_stats(self, thread_id: str = "default") -> Dict[str, Any]:
        """
        Obtiene estadísticas de ejecución del grafo.
        
        Args:
            thread_id: ID del hilo de conversación
            
        Returns:
            Estadísticas de ejecución
        """
        try:
            config = {"configurable": {"thread_id": thread_id}}
            
            # Intentar obtener el último estado
            checkpoint = self.checkpointer.get(config)
            if checkpoint and checkpoint.values:
                metadata = checkpoint.values.get("execution_metadata", {})
                
                return {
                    "last_execution": {
                        "nodes_executed": metadata.get("nodes_executed", []),
                        "tools_used": metadata.get("tools_used", []),
                        "status": metadata.get("status", "unknown"),
                        "duration": metadata.get("total_duration", 0),
                        "start_time": metadata.get("start_time"),
                        "end_time": metadata.get("end_time")
                    },
                    "graph_ready": True
                }
            
            return {"graph_ready": True, "last_execution": None}
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"graph_ready": False, "error": str(e)}
    
    # Métodos auxiliares para flujo condicional
    
    def _should_end_or_handle_error(self, state: IoTAgentState) -> str:
        """Determina si terminar o manejar errores después de generar respuesta."""
        
        if state.get("error_info") is not None:
            return "error"
        
        if state.get("final_response") is not None:
            return "end"
        
        return "error"  # Por defecto, manejar como error
    
    def _should_retry_or_end(self, state: IoTAgentState) -> str:
        """Determina si reintentar o terminar después del manejo de errores."""
        
        retry_count = state.get("retry_count", 0)
        
        if retry_count < 2 and state.get("error_info") is None:
            return "retry"
        
        return "end"
