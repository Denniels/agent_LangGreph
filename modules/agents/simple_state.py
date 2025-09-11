"""
Estado simplificado para el agente IoT - Sin dependencias de LangChain
====================================================================

Estado minimalista para uso en Streamlit Cloud.
"""

from typing import Dict, Any, List, Optional, TypedDict


class SimpleIoTState(TypedDict):
    """
    Estado simplificado del agente IoT.
    
    Attributes:
        user_query: Consulta original del usuario
        query_intent: Intención detectada de la consulta
        sensor_data: Datos recolectados de sensores
        analysis_result: Resultado del análisis
        final_response: Respuesta final generada
        confidence_score: Puntuación de confianza
        error_message: Mensaje de error si ocurre alguno
    """
    user_query: str
    query_intent: Dict[str, Any]
    sensor_data: List[Dict[str, Any]]
    analysis_result: Dict[str, Any]
    final_response: str
    confidence_score: float
    error_message: Optional[str]


def create_simple_initial_state(user_query: str) -> SimpleIoTState:
    """
    Crear estado inicial simplificado.
    
    Args:
        user_query: Consulta del usuario
        
    Returns:
        Estado inicial del agente
    """
    return SimpleIoTState(
        user_query=user_query,
        query_intent={},
        sensor_data=[],
        analysis_result={},
        final_response="",
        confidence_score=0.0,
        error_message=None
    )
