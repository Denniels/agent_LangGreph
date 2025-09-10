"""
Agente IoT Principal con LangGraph Completo
==========================================

Agente principal que usa StateGraph de LangGraph para procesamiento avanzado.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from modules.agents.graph_builder import LangGraphBuilder
from modules.utils.logger import setup_logger
from modules.utils.config import Config

logger = setup_logger(__name__)


class IoTAgentLangGraph:
    """
    Agente IoT principal que utiliza LangGraph StateGraph para procesamiento
    estructurado con nodos especializados y flujo condicional.
    """
    
    def __init__(self):
        self.config = Config()
        self.graph_builder = LangGraphBuilder()
        self.graph = None
        self.session_history = {}
        logger.info("🤖 IoTAgentLangGraph inicializado")
    
    async def initialize(self):
        """Inicializa el agente y construye el grafo LangGraph."""
        try:
            logger.info("🔧 Inicializando agente LangGraph...")
            
            # Construir el grafo StateGraph
            self.graph = self.graph_builder.build_iot_agent_graph()
            
            logger.info("✅ Agente LangGraph inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando agente LangGraph: {e}")
            raise
    
    async def process_query(
        self, 
        user_query: str, 
        user_id: str = "default_user",
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Procesa una consulta del usuario usando el grafo LangGraph.
        
        Args:
            user_query: Consulta del usuario
            user_id: ID del usuario
            session_id: ID de sesión (opcional)
            
        Returns:
            Respuesta procesada con metadatos
        """
        try:
            if not self.graph:
                await self.initialize()
            
            # Generar thread_id único para la sesión
            thread_id = session_id or f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            logger.info(f"🔍 Procesando consulta para usuario {user_id}, sesión {thread_id}")
            logger.info(f"📝 Consulta: {user_query}")
            
            # Procesar usando LangGraph
            result = await self.graph_builder.process_query(
                user_query=user_query,
                thread_id=thread_id
            )
            
            # Agregar metadatos adicionales
            result.update({
                "user_id": user_id,
                "session_id": thread_id,
                "timestamp": datetime.now().isoformat(),
                "agent_type": "LangGraph_StateGraph"
            })
            
            # Actualizar historial de sesión
            self._update_session_history(thread_id, user_query, result)
            
            logger.info(f"✅ Consulta procesada. Status: {result.get('status', 'unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error procesando consulta: {e}")
            return {
                "response": f"Error procesando la consulta: {str(e)}",
                "status": "error",
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "error_details": str(e)
            }
    
    async def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de una sesión específica.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Lista de interacciones de la sesión
        """
        return self.session_history.get(session_id, [])
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del agente.
        
        Returns:
            Estado del agente y sus componentes
        """
        try:
            # Estado base del agente
            status = {
                "agent_initialized": self.graph is not None,
                "agent_type": "LangGraph_StateGraph",
                "active_sessions": len(self.session_history),
                "timestamp": datetime.now().isoformat()
            }
            
            # Información del grafo si está disponible
            if self.graph:
                graph_info = self.graph_builder.get_graph_visualization()
                status.update({
                    "graph_nodes": len(graph_info.get("nodes", [])),
                    "graph_edges": len(graph_info.get("edges", [])),
                    "graph_features": graph_info.get("features", [])
                })
                
                # Estadísticas de ejecución recientes
                exec_stats = self.graph_builder.get_execution_stats()
                status["last_execution"] = exec_stats.get("last_execution")
            
            return status
            
        except Exception as e:
            logger.error(f"Error obteniendo estado del agente: {e}")
            return {
                "agent_initialized": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_graph_visualization(self) -> Dict[str, Any]:
        """
        Obtiene información para visualizar el grafo LangGraph.
        
        Returns:
            Estructura del grafo para visualización
        """
        if not self.graph:
            return {"error": "Agente no inicializado"}
        
        return self.graph_builder.get_graph_visualization()
    
    async def get_available_capabilities(self) -> Dict[str, Any]:
        """
        Obtiene las capacidades disponibles del agente.
        
        Returns:
            Lista de capacidades y herramientas disponibles
        """
        return {
            "graph_features": [
                "Análisis inteligente de consultas",
                "Recopilación paralela de datos",
                "Análisis avanzado con insights",
                "Generación de respuestas contextuales",
                "Manejo robusto de errores",
                "Reintentos automáticos",
                "Persistencia de estado",
                "Flujo condicional dinámico"
            ],
            "supported_queries": [
                "Consultas de datos de sensores",
                "Estado de dispositivos IoT", 
                "Análisis de tendencias",
                "Detección de anomalías",
                "Estadísticas y métricas",
                "Alertas y notificaciones",
                "Reportes técnicos"
            ],
            "available_tools": [
                "get_sensor_data",
                "get_devices",
                "get_alerts", 
                "get_sensor_stats",
                "analyze_trends",
                "detect_anomalies",
                "calculate_statistics"
            ],
            "advanced_features": [
                "Procesamiento asíncrono",
                "Contexto persistente",
                "Ejecución paralela",
                "Recuperación de errores",
                "Análisis semántico"
            ]
        }
    
    async def reset_session(self, session_id: str) -> Dict[str, Any]:
        """
        Reinicia una sesión específica.
        
        Args:
            session_id: ID de la sesión a reiniciar
            
        Returns:
            Resultado de la operación
        """
        try:
            if session_id in self.session_history:
                del self.session_history[session_id]
            
            # Limpiar estado persistente del grafo para esta sesión
            if self.graph_builder.checkpointer:
                config = {"configurable": {"thread_id": session_id}}
                # El MemorySaver no tiene método directo para limpiar, 
                # pero se puede sobrescribir con estado vacío
                
            logger.info(f"🔄 Sesión {session_id} reiniciada")
            
            return {
                "success": True,
                "session_id": session_id,
                "message": "Sesión reiniciada exitosamente"
            }
            
        except Exception as e:
            logger.error(f"Error reiniciando sesión {session_id}: {e}")
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e)
            }
    
    def _update_session_history(
        self, 
        session_id: str, 
        user_query: str, 
        result: Dict[str, Any]
    ):
        """Actualiza el historial de la sesión."""
        
        if session_id not in self.session_history:
            self.session_history[session_id] = []
        
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "response": result.get("response", ""),
            "status": result.get("status", "unknown"),
            "query_intent": result.get("query_intent"),
            "tools_used": result.get("tools_used", []),
            "execution_metadata": result.get("execution_metadata", {})
        }
        
        self.session_history[session_id].append(interaction)
        
        # Mantener solo las últimas 50 interacciones por sesión
        if len(self.session_history[session_id]) > 50:
            self.session_history[session_id] = self.session_history[session_id][-50:]
    
    async def shutdown(self):
        """Cierra el agente y limpia recursos."""
        try:
            logger.info("🔽 Cerrando agente LangGraph...")
            
            # Limpiar historial de sesiones
            self.session_history.clear()
            
            # El grafo LangGraph no requiere cierre explícito
            self.graph = None
            
            logger.info("✅ Agente LangGraph cerrado exitosamente")
            
        except Exception as e:
            logger.error(f"Error cerrando agente: {e}")
            

# Instancia global del agente LangGraph
langgraph_agent = IoTAgentLangGraph()
