"""
Nodos para el grafo LangGraph del agente IoT
===========================================

Implementa todos los nodos de procesamiento para el flujo de trabajo del agente.
"""

import time
import asyncio
from typing import Dict, Any, List
from datetime import datetime

from modules.agents.langgraph_state import (
    IoTAgentState, QueryIntent, ToolType, ExecutionStatus
)
from modules.tools.database_tools import (
    get_sensor_data, get_devices, get_alerts, get_sensor_stats_tool,
    create_alert
)
from modules.tools.analysis_tools import (
    analyze_trends, detect_anomalies, calculate_statistics
)
from modules.agents.ollama_integration import OllamaLLM
from modules.utils.logger import setup_logger

logger = setup_logger(__name__)


class LangGraphNodes:
    """Nodos de procesamiento para el grafo LangGraph del agente IoT."""
    
    def __init__(self):
        self.ollama = OllamaLLM()
        
    async def query_analyzer_node(self, state: IoTAgentState) -> IoTAgentState:
        """
        Analiza la consulta del usuario para determinar intención y herramientas necesarias.
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado con intención y herramientas identificadas
        """
        try:
            logger.info(f"🔍 Analizando consulta: {state['user_query']}")
            
            # Marcar inicio del nodo
            state["execution_metadata"]["start_time"] = datetime.now()
            state["execution_metadata"]["nodes_executed"].append("query_analyzer")
            
            query = state["user_query"].lower()
            
            # Detectar intención basada en palabras clave
            intent = self._detect_query_intent(query)
            required_tools = self._determine_required_tools(intent, query)
            
            # Actualizar estado
            state["query_intent"] = intent
            state["required_tools"] = required_tools
            
            logger.info(f"✅ Intención detectada: {intent}")
            logger.info(f"🛠️ Herramientas requeridas: {required_tools}")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en query_analyzer_node: {e}")
            state["error_info"] = {
                "node": "query_analyzer",
                "error": str(e),
                "timestamp": datetime.now()
            }
            return state
    
    async def data_collector_node(self, state: IoTAgentState) -> IoTAgentState:
        """
        Recopila datos ejecutando las herramientas identificadas.
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado con resultados de herramientas
        """
        try:
            logger.info(f"📥 Recopilando datos con herramientas: {state['required_tools']}")
            
            state["execution_metadata"]["nodes_executed"].append("data_collector")
            tool_results = {}
            
            # Ejecutar herramientas en paralelo cuando sea posible
            for tool_name in state["required_tools"]:
                try:
                    result = await self._execute_tool(tool_name, state)
                    tool_results[tool_name] = result
                    state["execution_metadata"]["tools_used"].append(tool_name)
                    logger.info(f"✅ Herramienta {tool_name} ejecutada exitosamente")
                    
                except Exception as e:
                    logger.error(f"❌ Error ejecutando {tool_name}: {e}")
                    tool_results[tool_name] = {"error": str(e)}
            
            state["tool_results"] = tool_results
            
            # Procesar resultados para contexto
            context_data = self._process_tool_results(tool_results)
            state["context_data"] = context_data
            
            logger.info(f"📊 Datos recopilados: {len(tool_results)} herramientas")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en data_collector_node: {e}")
            state["error_info"] = {
                "node": "data_collector", 
                "error": str(e),
                "timestamp": datetime.now()
            }
            return state
    
    async def data_analyzer_node(self, state: IoTAgentState) -> IoTAgentState:
        """
        Analiza los datos recopilados para extraer insights.
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado con resultados de análisis
        """
        try:
            logger.info("🔬 Analizando datos recopilados")
            
            state["execution_metadata"]["nodes_executed"].append("data_analyzer")
            
            analysis_results = {}
            
            # Análisis basado en la intención
            if state["query_intent"] == QueryIntent.ANALYSIS:
                analysis_results["trends"] = await self._analyze_trends(state["context_data"])
                analysis_results["anomalies"] = await self._detect_anomalies(state["context_data"])
            
            elif state["query_intent"] == QueryIntent.STATISTICS:
                analysis_results["statistics"] = await self._calculate_statistics(state["context_data"])
            
            # Análisis general siempre aplicado
            analysis_results["summary"] = self._generate_data_summary(state["context_data"])
            analysis_results["recommendations"] = self._generate_recommendations(state["context_data"])
            
            state["analysis_results"] = analysis_results
            
            logger.info(f"📈 Análisis completado: {len(analysis_results)} componentes")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en data_analyzer_node: {e}")
            state["error_info"] = {
                "node": "data_analyzer",
                "error": str(e), 
                "timestamp": datetime.now()
            }
            return state
    
    async def response_generator_node(self, state: IoTAgentState) -> IoTAgentState:
        """
        Genera la respuesta final usando LLM con todos los datos contextuales.
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado con respuesta final
        """
        try:
            logger.info("📝 Generando respuesta final")
            
            state["execution_metadata"]["nodes_executed"].append("response_generator")
            
            # Preparar contexto completo para el LLM
            context = self._prepare_llm_context(state)
            
            # Generar respuesta usando Ollama
            response = await self.ollama.generate_response(
                user_query=state["user_query"],
                context=context
            )
            
            state["final_response"] = response
            state["execution_metadata"]["status"] = ExecutionStatus.SUCCESS
            state["execution_metadata"]["end_time"] = datetime.now()
            
            # Calcular duración total
            if state["execution_metadata"]["start_time"]:
                duration = state["execution_metadata"]["end_time"] - state["execution_metadata"]["start_time"]
                state["execution_metadata"]["total_duration"] = duration.total_seconds()
            
            logger.info("✅ Respuesta generada exitosamente")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en response_generator_node: {e}")
            state["error_info"] = {
                "node": "response_generator",
                "error": str(e),
                "timestamp": datetime.now()
            }
            state["execution_metadata"]["status"] = ExecutionStatus.ERROR
            return state
    
    async def error_handler_node(self, state: IoTAgentState) -> IoTAgentState:
        """
        Maneja errores y determina si reintentar o generar respuesta de error.
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado con manejo de errores
        """
        try:
            logger.warning("⚠️ Manejando error en el flujo")
            
            state["execution_metadata"]["nodes_executed"].append("error_handler")
            
            # Verificar si se puede reintentar
            if state["retry_count"] < 2:  # Máximo 2 reintentos
                state["retry_count"] += 1
                logger.info(f"🔄 Reintentando operación (intento {state['retry_count']})")
                
                # Limpiar error para reintento
                state["error_info"] = None
                return state
            
            # Generar respuesta de error amigable
            error_response = self._generate_error_response(state["error_info"])
            state["final_response"] = error_response
            state["execution_metadata"]["status"] = ExecutionStatus.ERROR
            
            logger.info("❌ Error manejado, respuesta de error generada")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Error crítico en error_handler_node: {e}")
            state["final_response"] = "Lo siento, ha ocurrido un error inesperado. Por favor, inténtelo nuevamente."
            state["execution_metadata"]["status"] = ExecutionStatus.ERROR
            return state
    
    # Métodos auxiliares
    
    def _detect_query_intent(self, query: str) -> str:
        """Detecta la intención de la consulta basada en palabras clave."""
        
        intent_keywords = {
            QueryIntent.SENSOR_DATA: ["sensor", "datos", "medición", "temperatura", "humedad", "valor"],
            QueryIntent.DEVICE_STATUS: ["dispositivo", "estado", "conexión", "activo", "online"],
            QueryIntent.ALERTS: ["alerta", "alarma", "notificación", "problema", "crítico"],
            QueryIntent.ANALYSIS: ["análisis", "tendencia", "patrón", "evolución", "comportamiento"],
            QueryIntent.STATISTICS: ["estadísticas", "promedio", "máximo", "mínimo", "total", "contar"],
            QueryIntent.ANOMALIES: ["anomalía", "anormal", "extraño", "inusual", "outlier"],
            QueryIntent.REPORTS: ["reporte", "informe", "resumen", "documento"]
        }
        
        for intent, keywords in intent_keywords.items():
            if any(keyword in query for keyword in keywords):
                return intent
        
        return QueryIntent.UNKNOWN
    
    def _determine_required_tools(self, intent: str, query: str) -> List[str]:
        """Determina qué herramientas son necesarias según la intención."""
        
        tools_mapping = {
            QueryIntent.SENSOR_DATA: [ToolType.GET_SENSOR_DATA],
            QueryIntent.DEVICE_STATUS: [ToolType.GET_DEVICES], 
            QueryIntent.ALERTS: [ToolType.GET_ALERTS],
            QueryIntent.ANALYSIS: [ToolType.GET_SENSOR_DATA, ToolType.ANALYZE_TRENDS],
            QueryIntent.STATISTICS: [ToolType.GET_SENSOR_STATS, ToolType.CALCULATE_STATISTICS],
            QueryIntent.ANOMALIES: [ToolType.GET_SENSOR_DATA, ToolType.DETECT_ANOMALIES],
            QueryIntent.REPORTS: [ToolType.GET_SENSOR_STATS, ToolType.GET_DEVICES]
        }
        
        # Herramientas adicionales basadas en palabras clave
        additional_tools = []
        if "contar" in query or "cuántos" in query or "total" in query:
            additional_tools.append(ToolType.GET_SENSOR_STATS)
        
        if "dispositivo" in query:
            additional_tools.append(ToolType.GET_DEVICES)
        
        base_tools = tools_mapping.get(intent, [ToolType.GET_SENSOR_DATA])
        return list(set(base_tools + additional_tools))
    
    async def _execute_tool(self, tool_name: str, state: IoTAgentState) -> Dict[str, Any]:
        """Ejecuta una herramienta específica."""
        
        try:
            if tool_name == ToolType.GET_SENSOR_DATA:
                return await get_sensor_data(limit=100)
            
            elif tool_name == ToolType.GET_DEVICES:
                return await get_devices()
            
            elif tool_name == ToolType.GET_ALERTS:
                return await get_alerts()
            
            elif tool_name == ToolType.GET_SENSOR_STATS:
                return await get_sensor_stats_tool()
            
            elif tool_name == ToolType.ANALYZE_TRENDS:
                return await analyze_trends(state["context_data"])
            
            elif tool_name == ToolType.DETECT_ANOMALIES:
                return await detect_anomalies(state["context_data"])
            
            elif tool_name == ToolType.CALCULATE_STATISTICS:
                return await calculate_statistics(state["context_data"])
            
            else:
                logger.warning(f"⚠️ Herramienta desconocida: {tool_name}")
                return {"error": f"Herramienta no encontrada: {tool_name}"}
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando herramienta {tool_name}: {e}")
            raise
    
    def _process_tool_results(self, tool_results: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa los resultados de las herramientas para contexto."""
        
        context = {}
        
        for tool_name, result in tool_results.items():
            if "error" not in result:
                context[tool_name] = result
        
        return context
    
    async def _analyze_trends(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza tendencias en los datos."""
        return await analyze_trends(context_data)
    
    async def _detect_anomalies(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta anomalías en los datos."""
        return await detect_anomalies(context_data)
    
    async def _calculate_statistics(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula estadísticas de los datos."""
        return await calculate_statistics(context_data)
    
    def _generate_data_summary(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un resumen de los datos."""
        
        summary = {
            "total_data_sources": len(context_data),
            "available_tools": list(context_data.keys()),
            "timestamp": datetime.now().isoformat()
        }
        
        # Agregar información específica si está disponible
        if ToolType.GET_SENSOR_DATA in context_data:
            sensor_data = context_data[ToolType.GET_SENSOR_DATA]
            if isinstance(sensor_data, list):
                summary["sensor_records"] = len(sensor_data)
        
        if ToolType.GET_DEVICES in context_data:
            devices_data = context_data[ToolType.GET_DEVICES]
            if isinstance(devices_data, list):
                summary["total_devices"] = len(devices_data)
        
        return summary
    
    def _generate_recommendations(self, context_data: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en los datos."""
        
        recommendations = []
        
        # Recomendaciones basadas en datos disponibles
        if ToolType.GET_SENSOR_DATA in context_data:
            recommendations.append("Considera establecer alertas automáticas para valores críticos")
        
        if ToolType.GET_DEVICES in context_data:
            recommendations.append("Revisa periódicamente el estado de conexión de dispositivos")
        
        recommendations.append("Mantén un monitoreo continuo de las métricas clave")
        
        return recommendations
    
    def _prepare_llm_context(self, state: IoTAgentState) -> Dict[str, Any]:
        """Prepara el contexto completo para el LLM."""
        
        return {
            "query_intent": state["query_intent"],
            "tool_results": state["tool_results"],
            "context_data": state["context_data"],
            "analysis_results": state["analysis_results"],
            "execution_metadata": state["execution_metadata"]
        }
    
    def _generate_error_response(self, error_info: Dict[str, Any]) -> str:
        """Genera una respuesta amigable para errores."""
        
        if not error_info:
            return "Ha ocurrido un error inesperado. Por favor, inténtelo nuevamente."
        
        node = error_info.get("node", "desconocido")
        error_msg = error_info.get("error", "Error no especificado")
        
        friendly_responses = {
            "query_analyzer": "No pude analizar correctamente su consulta. Por favor, intente reformularla.",
            "data_collector": "Hubo un problema recopilando los datos solicitados. Verifique la conexión a la base de datos.",
            "data_analyzer": "No pude completar el análisis de los datos. Los datos pueden estar incompletos.",
            "response_generator": "Hubo un problema generando la respuesta. Por favor, inténtelo nuevamente."
        }
        
        return friendly_responses.get(node, f"Error en {node}: {error_msg}")
