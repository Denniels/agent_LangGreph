"""
Estado y tipos para el agente IoT con LangGraph
=============================================

Define el estado y tipos de datos utilizados en el flujo de trabajo de LangGraph.
"""

from typing import Dict, Any, List, Optional, Annotated, TypedDict
from langchain_core.messages import BaseMessage
import operator


class IoTAgentState(TypedDict):
    """
    Estado principal del agente IoT que fluye através de todos los nodos del grafo.
    
    Attributes:
        messages: Historial de mensajes de conversación
        user_query: Consulta original del usuario
        query_intent: Intención detectada de la consulta
        required_tools: Herramientas identificadas como necesarias
        tool_results: Resultados de ejecución de herramientas
        context_data: Datos contextuales recopilados
        analysis_results: Resultados de análisis de datos
        final_response: Respuesta final generada
        error_info: Información de errores si los hay
        retry_count: Contador de reintentos
        execution_metadata: Metadatos de ejecución
    """
    # Conversación
    messages: Annotated[List[BaseMessage], operator.add]
    user_query: str
    
    # Análisis de consulta
    query_intent: Optional[str]
    required_tools: List[str]
    
    # Ejecución de herramientas
    tool_results: Dict[str, Any]
    context_data: Dict[str, Any]
    
    # Datos remotos (para API de Jetson)
    raw_data: List[Dict[str, Any]]
    formatted_data: Optional[str]
    sensor_summary: Optional[Dict[str, Any]]
    data_source: Optional[str]
    data_collection_success: Optional[bool]
    data_collection_error: Optional[str]
    data_collection_timestamp: Optional[str]
    analyzed_query: Optional[Dict[str, Any]]
    
    # Análisis y procesamiento
    analysis_results: Dict[str, Any]
    
    # Respuesta
    final_response: Optional[str]
    
    # Verificación de datos (prevención de alucinaciones)
    needs_correction: bool
    correction_prompt: Optional[str]
    original_response: Optional[str]
    verification_metadata: Optional[Dict[str, Any]]
    verification_status: Optional[str]
    hallucinations_detected: Optional[List[str]]
    execution_status: Optional[str]
    
    # Control de flujo
    error_info: Optional[Dict[str, Any]]
    retry_count: int
    execution_metadata: Dict[str, Any]


class QueryIntent:
    """Constantes para tipos de intención de consulta."""
    
    SENSOR_DATA = "sensor_data"
    DEVICE_STATUS = "device_status"  
    ALERTS = "alerts"
    ANALYSIS = "analysis"
    STATISTICS = "statistics"
    ANOMALIES = "anomalies"
    REPORTS = "reports"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


class ToolType:
    """Constantes para tipos de herramientas disponibles."""
    
    # Herramientas de base de datos
    GET_SENSOR_DATA = "get_sensor_data"
    GET_DEVICES = "get_devices"
    GET_ALERTS = "get_alerts"
    GET_SENSOR_STATS = "get_sensor_stats"
    CREATE_ALERT = "create_alert"
    
    # Herramientas de análisis
    ANALYZE_TRENDS = "analyze_trends"
    DETECT_ANOMALIES = "detect_anomalies"
    CALCULATE_STATISTICS = "calculate_statistics"
    
    # Herramientas de reportes
    GENERATE_REPORT = "generate_report"
    CREATE_VISUALIZATION = "create_visualization"


class NodeNames:
    """Constantes para nombres de nodos en el grafo."""
    
    START = "start"
    QUERY_ANALYZER = "query_analyzer"
    TOOL_SELECTOR = "tool_selector"
    DATA_COLLECTOR = "data_collector"
    DATA_ANALYZER = "data_analyzer"
    RESPONSE_GENERATOR = "response_generator"
    DATA_VERIFICATION = "data_verification"
    ERROR_HANDLER = "error_handler"
    END = "end"


class ExecutionStatus:
    """Estados de ejecución de nodos."""
    
    SUCCESS = "success"
    ERROR = "error"
    RETRY = "retry"
    SKIP = "skip"
    PENDING = "pending"


def create_initial_state(user_query: str, messages: List[BaseMessage] = None) -> IoTAgentState:
    """
    Crea el estado inicial para una nueva consulta.
    
    Args:
        user_query: Consulta del usuario
        messages: Mensajes previos de la conversación
        
    Returns:
        Estado inicial del agente
    """
    return IoTAgentState(
        messages=messages or [],
        user_query=user_query,
        query_intent=None,
        required_tools=[],
        tool_results={},
        context_data={},
        raw_data=[],
        formatted_data=None,
        sensor_summary=None,
        data_source=None,
        data_collection_success=None,
        data_collection_error=None,
        data_collection_timestamp=None,
        analyzed_query=None,
        analysis_results={},
        final_response=None,
        needs_correction=False,
        correction_prompt=None,
        original_response=None,
        verification_metadata=None,
        verification_status=None,
        hallucinations_detected=None,
        execution_status=None,
        error_info=None,
        retry_count=0,
        execution_metadata={
            "start_time": None,
            "end_time": None,
            "total_duration": None,
            "nodes_executed": [],
            "tools_used": [],
            "status": ExecutionStatus.PENDING
        }
    )
