"""
Constructor de Gráficos LangGraph
=================================

Construye gráficos de flujo usando LangGraph para el agente IoT.
"""

from typing import Dict, Any, List, TypedDict, Optional
from modules.utils.logger import setup_logger

logger = setup_logger(__name__)


class AgentState(TypedDict):
    """Estado del agente durante la ejecución."""
    messages: List[Dict[str, Any]]
    current_step: str
    context_data: Dict[str, Any]
    user_query: str
    final_response: Optional[str]


class GraphBuilder:
    """
    Constructor de gráficos LangGraph para el agente IoT.
    Versión simplificada para evitar dependencias circulares.
    """
    
    def __init__(self):
        self.graph_structure = None
        logger.info("GraphBuilder inicializado")
    
    def build_conversation_graph(self) -> Dict[str, Any]:
        """
        Construye un gráfico de conversación básico.
        
        Returns:
            Estructura del gráfico
        """
        graph_structure = {
            "nodes": [
                {"id": "start", "type": "entry", "description": "Punto de entrada"},
                {"id": "analyze", "type": "processing", "description": "Análisis de consulta"},
                {"id": "gather_data", "type": "action", "description": "Recopilación de datos"},
                {"id": "process", "type": "processing", "description": "Procesamiento"},
                {"id": "respond", "type": "output", "description": "Generación de respuesta"}
            ],
            "edges": [
                {"from": "start", "to": "analyze"},
                {"from": "analyze", "to": "gather_data"},
                {"from": "gather_data", "to": "process"},
                {"from": "process", "to": "respond"}
            ]
        }
        
        self.graph_structure = graph_structure
        logger.info("Gráfico de conversación construido")
        return graph_structure
    
    def get_available_tools(self) -> List[str]:
        """
        Obtiene la lista de herramientas disponibles.
        
        Returns:
            Lista de nombres de herramientas
        """
        return [
            "get_sensor_data",
            "get_devices", 
            "get_alerts",
            "create_alert",
            "analyze_trends",
            "detect_anomalies",
            "generate_report"
        ]
    
    def determine_workflow_path(self, user_query: str) -> List[str]:
        """
        Determina el camino del flujo de trabajo basado en la consulta.
        
        Args:
            user_query: Consulta del usuario
            
        Returns:
            Lista de pasos del flujo
        """
        query_lower = user_query.lower()
        
        # Flujo básico por defecto
        workflow_path = ["start", "analyze", "gather_data", "process", "respond"]
        
        # Personalizar flujo según la consulta
        if any(word in query_lower for word in ["rápido", "quick", "simple"]):
            # Flujo simplificado
            workflow_path = ["start", "analyze", "respond"]
        elif any(word in query_lower for word in ["detallado", "completo", "análisis"]):
            # Flujo completo con análisis adicional
            workflow_path.extend(["analyze_deeper", "validate"])
        
        logger.debug(f"Camino del flujo determinado: {workflow_path}")
        return workflow_path
    
    def get_graph_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del gráfico.
        
        Returns:
            Estado del gráfico
        """
        return {
            "graph_built": self.graph_structure is not None,
            "node_count": len(self.graph_structure["nodes"]) if self.graph_structure else 0,
            "edge_count": len(self.graph_structure["edges"]) if self.graph_structure else 0,
            "available_tools": len(self.get_available_tools())
        }
