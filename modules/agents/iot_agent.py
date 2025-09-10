"""
Agente IoT Principal
===================

Agente conversacional principal que maneja las interacciones con el sistema IoT.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from modules.tools.database_tools import DatabaseTools
from modules.tools.analysis_tools import AnalysisTools
from modules.agents.ollama_integration import OllamaLLMIntegration
from modules.utils.logger import logger

logger


class IoTAgent:
    """
    Agente conversacional para el sistema IoT.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=0.1,
            api_key=Config.OPENAI_API_KEY
        )
        self.db_tools = DatabaseTools()
        self.analysis_tools = AnalysisTools()
        self.conversation_history: List[BaseMessage] = []
        self._setup_system_prompt()
    
    def _setup_system_prompt(self):
        """Configura el prompt del sistema para el agente."""
        system_prompt = """
        Eres un asistente especializado en sistemas IoT (Internet de las Cosas). Tu función es ayudar a los usuarios a:

        1. **Consultar datos de sensores**: Puedes obtener y analizar datos de diferentes tipos de sensores
        2. **Monitorear dispositivos**: Revisar el estado de dispositivos IoT conectados
        3. **Gestionar alertas**: Consultar alertas activas y crear nuevas cuando sea necesario
        4. **Analizar tendencias**: Identificar patrones y tendencias en los datos
        5. **Detectar anomalías**: Encontrar valores inusuales que requieren atención
        6. **Generar reportes**: Crear resúmenes del estado del sistema

        **Herramientas disponibles:**
        - get_sensor_data: Obtener datos de sensores
        - get_devices: Listar dispositivos activos
        - get_alerts: Consultar alertas del sistema
        - create_alert: Crear nueva alerta
        - analyze_trends: Analizar tendencias en los datos
        - detect_anomalies: Detectar valores anómalos
        - generate_report: Generar reporte resumen

        **Instrucciones:**
        - Proporciona respuestas claras y precisas
        - Usa datos reales del sistema cuando estén disponibles
        - Sugiere acciones cuando detectes problemas
        - Explica los términos técnicos cuando sea necesario
        - Mantén un tono profesional pero amigable

        Cuando no sepas algo específico sobre el sistema, consulta los datos disponibles antes de responder.
        """
        
        self.conversation_history = [SystemMessage(content=system_prompt)]
    
    async def process_message(self, user_message: str) -> str:
        """
        Procesa un mensaje del usuario y retorna una respuesta.
        
        Args:
            user_message: Mensaje del usuario
            
        Returns:
            Respuesta del agente
        """
        try:
            # Agregar mensaje del usuario al historial
            self.conversation_history.append(HumanMessage(content=user_message))
            
            # Determinar qué herramientas usar basado en el mensaje
            tools_to_use = self._determine_tools(user_message)
            
            # Recopilar datos si es necesario
            context_data = await self._gather_context_data(tools_to_use, user_message)
            
            # Crear mensaje enriquecido con contexto
            enriched_message = self._create_enriched_message(user_message, context_data)
            
            # Generar respuesta usando el LLM
            response = await self._generate_response(enriched_message)
            
            # Agregar respuesta al historial
            self.conversation_history.append(AIMessage(content=response))
            
            logger.info(f"Mensaje procesado exitosamente")
            return response
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            return "Lo siento, ocurrió un error al procesar tu solicitud. Por favor, inténtalo de nuevo."
    
    def _determine_tools(self, message: str) -> List[str]:
        """
        Determina qué herramientas usar basado en el mensaje del usuario.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            Lista de herramientas a usar
        """
        message_lower = message.lower()
        tools = []
        
        # Palabras clave para determinar herramientas
        if any(word in message_lower for word in ['sensor', 'dato', 'lectura', 'medición']):
            tools.append('sensor_data')
        
        if any(word in message_lower for word in ['dispositivo', 'device', 'equipo']):
            tools.append('devices')
        
        if any(word in message_lower for word in ['alerta', 'alert', 'alarma', 'problema']):
            tools.append('alerts')
        
        if any(word in message_lower for word in ['tendencia', 'trend', 'análisis', 'patrón']):
            tools.append('analysis')
        
        if any(word in message_lower for word in ['anomalía', 'anomaly', 'inusual', 'extraño']):
            tools.append('anomalies')
        
        if any(word in message_lower for word in ['reporte', 'report', 'resumen', 'estado']):
            tools.append('report')
        
        # Si no se detecta ninguna herramienta específica, usar datos básicos
        if not tools:
            tools = ['sensor_data', 'devices', 'alerts']
        
        return tools
    
    async def _gather_context_data(self, tools: List[str], message: str) -> Dict[str, Any]:
        """
        Recopila datos de contexto usando las herramientas determinadas.
        
        Args:
            tools: Lista de herramientas a usar
            message: Mensaje original del usuario
            
        Returns:
            Diccionario con datos de contexto
        """
        context = {}
        
        try:
            if 'sensor_data' in tools:
                context['sensor_data'] = await self.db_tools.get_sensor_data_tool(limit=20)
            
            if 'devices' in tools:
                context['devices'] = await self.db_tools.get_devices_tool()
            
            if 'alerts' in tools:
                context['alerts'] = await self.db_tools.get_alerts_tool()
            
            if 'analysis' in tools and 'sensor_data' in context:
                context['trends_analysis'] = self.analysis_tools.analyze_sensor_trends(
                    context['sensor_data']
                )
            
            if 'anomalies' in tools and 'sensor_data' in context:
                context['anomalies'] = self.analysis_tools.detect_anomalies(
                    context['sensor_data']
                )
            
            if 'report' in tools:
                sensor_data = context.get('sensor_data', await self.db_tools.get_sensor_data_tool())
                alerts = context.get('alerts', await self.db_tools.get_alerts_tool())
                context['system_report'] = self.analysis_tools.generate_summary_report(
                    sensor_data, alerts
                )
        
        except Exception as e:
            logger.error(f"Error recopilando datos de contexto: {e}")
            context['error'] = str(e)
        
        return context
    
    def _create_enriched_message(self, original_message: str, context_data: Dict[str, Any]) -> str:
        """
        Crea un mensaje enriquecido con datos de contexto.
        
        Args:
            original_message: Mensaje original del usuario
            context_data: Datos de contexto recopilados
            
        Returns:
            Mensaje enriquecido
        """
        enriched_parts = [f"Pregunta del usuario: {original_message}"]
        
        if context_data.get('sensor_data'):
            enriched_parts.append(f"Datos de sensores recientes: {len(context_data['sensor_data'])} lecturas disponibles")
        
        if context_data.get('devices'):
            enriched_parts.append(f"Dispositivos activos: {len(context_data['devices'])} dispositivos")
        
        if context_data.get('alerts'):
            enriched_parts.append(f"Alertas activas: {len(context_data['alerts'])} alertas")
        
        if context_data.get('trends_analysis'):
            enriched_parts.append("Análisis de tendencias disponible")
        
        if context_data.get('anomalies'):
            enriched_parts.append(f"Anomalías detectadas: {len(context_data['anomalies'])}")
        
        if context_data.get('system_report'):
            enriched_parts.append("Reporte del sistema disponible")
        
        # Agregar datos específicos si están disponibles
        for key, value in context_data.items():
            if key not in ['error'] and value:
                enriched_parts.append(f"\\n{key}: {str(value)[:500]}...")
        
        return "\\n".join(enriched_parts)
    
    async def _generate_response(self, enriched_message: str) -> str:
        """
        Genera una respuesta usando el LLM.
        
        Args:
            enriched_message: Mensaje enriquecido con contexto
            
        Returns:
            Respuesta generada
        """
        try:
            # Usar solo los últimos 10 mensajes para no exceder límites
            recent_history = self.conversation_history[-10:]
            recent_history.append(HumanMessage(content=enriched_message))
            
            response = await self.llm.ainvoke(recent_history)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return "Lo siento, no pude generar una respuesta en este momento."
    
    def clear_history(self):
        """Limpia el historial de conversación, manteniendo solo el prompt del sistema."""
        self._setup_system_prompt()
        logger.info("Historial de conversación limpiado")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Retorna un resumen de la conversación actual.
        
        Returns:
            Resumen de la conversación
        """
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": len([msg for msg in self.conversation_history if isinstance(msg, HumanMessage)]),
            "assistant_messages": len([msg for msg in self.conversation_history if isinstance(msg, AIMessage)]),
            "last_interaction": self.conversation_history[-1].content[:100] + "..." if self.conversation_history else None
        }
