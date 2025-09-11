"""
Módulos del Agente Conversacional IoT
====================================

Este paquete contiene todos los módulos necesarios para el funcionamiento
del agente conversacional IoT basado en LangGraph.

Módulos disponibles:
- database: Conectores y modelos de base de datos
- agents: Agentes de conversación y procesamiento
- tools: Herramientas para el agente
- utils: Utilidades generales
"""

__version__ = "1.0.0"
__author__ = "Tu Nombre"

"""
Módulos del Agente Conversacional IoT
====================================

Este paquete contiene todos los módulos necesarios para el funcionamiento
del agente conversacional IoT basado en LangGraph.

Módulos disponibles:
- agents: Agentes de conversación y procesamiento
- tools: Herramientas para el agente
- utils: Utilidades generales
"""

__version__ = "1.0.0"
__author__ = "Tu Nombre"

# Importaciones solo para cloud (sin base de datos)
try:
    from .utils import setup_logger
except ImportError:
    # Fallback si utils no está disponible
    def setup_logger(*args, **kwargs):
        import logging
        return logging.getLogger(__name__)

__all__ = [
    "setup_logger"
]
