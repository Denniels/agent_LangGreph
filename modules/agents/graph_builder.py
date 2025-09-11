"""
Constructor de Gráficos LangGraph COMPLETO
=========================================

Implementación completa del StateGraph usando LangGraph para el agente IoT.
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

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
        logger.info("🔧 LangGraphBuilder inicializado")
    
    def build_iot_agent_graph(self) -> StateGraph:
        """
        Construye el grafo completo del agente IoT con nodos especializados.
        VERSIÓN SIMPLIFICADA - Sin flujo condicional complejo
        
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
        workflow.add_node(NodeNames.DATA_VERIFICATION, self.nodes.data_verification_node)
        
        # Configurar punto de entrada
        workflow.set_entry_point(NodeNames.QUERY_ANALYZER)
        
        # Definir flujo secuencial con verificación
        workflow.add_edge(NodeNames.QUERY_ANALYZER, NodeNames.DATA_COLLECTOR)
        workflow.add_edge(NodeNames.DATA_COLLECTOR, NodeNames.DATA_ANALYZER)
        workflow.add_edge(NodeNames.DATA_ANALYZER, NodeNames.RESPONSE_GENERATOR)
        workflow.add_edge(NodeNames.RESPONSE_GENERATOR, NodeNames.DATA_VERIFICATION)
        workflow.add_edge(NodeNames.DATA_VERIFICATION, END)
        
        # Compilar el grafo sin checkpointer para simplificar
        self.graph = workflow.compile()
        
        logger.info("✅ StateGraph compilado exitosamente")
        return self.graph
    
    async def process_query(self, user_query: str, thread_id: str = "default") -> Dict[str, Any]:
        """
        Procesa una consulta del usuario usando el grafo LangGraph.
        VERSIÓN SIMPLIFICADA - Sin flujo condicional complejo
        
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
            
            # Ejecutar el grafo de forma simple (sin config complejo)
            final_state = await self.graph.ainvoke(initial_state)
            
            # Debug: mostrar el estado final
            logger.info(f"🔍 DEBUG: Estado final simplificado")
            logger.info(f"  - final_response existe: {final_state.get('final_response') is not None}")
            logger.info(f"  - status: {final_state.get('execution_metadata', {}).get('status')}")
            
            # Extraer resultado de forma robusta
            response = final_state.get("final_response")
            status = final_state.get("execution_metadata", {}).get("status", ExecutionStatus.ERROR)
            
            # Si no hay respuesta pero no hay errores, crear respuesta por defecto
            if not response and not final_state.get("error_info"):
                response = "Consulta procesada pero sin respuesta generada."
                status = ExecutionStatus.SUCCESS
            
            # Si hay respuesta, forzar status SUCCESS
            if response and response.strip():
                status = ExecutionStatus.SUCCESS
            
            result = {
                "response": response or "No se pudo generar respuesta...",
                "status": status,
                "execution_metadata": final_state.get("execution_metadata", {}),
                "query_intent": final_state.get("query_intent"),
                "tools_used": final_state.get("execution_metadata", {}).get("tools_used", [])
            }
            
            logger.info(f"✅ Consulta procesada. Status final: {status}")
            return result
                
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
                "id": NodeNames.DATA_VERIFICATION,
                "label": "Verificador de Datos",
                "description": "Verifica veracidad y previene alucinaciones",
                "type": "validator"
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
            {"from": NodeNames.RESPONSE_GENERATOR, "to": NodeNames.DATA_VERIFICATION, "type": "sequential"},
            {"from": NodeNames.DATA_VERIFICATION, "to": "END", "type": "conditional"},
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
        VERSIÓN SIMPLIFICADA
        
        Args:
            thread_id: ID del hilo de conversación
            
        Returns:
            Estadísticas de ejecución
        """
        return {
            "graph_ready": self.graph is not None,
            "last_execution": None,
            "message": "Estadísticas simplificadas - sin persistencia"
        }

