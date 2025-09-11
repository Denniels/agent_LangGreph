"""
Integración de Ollama para el agente IoT conversacional
"""

import ollama
import json
import asyncio
from typing import Dict, List, Any, Optional
from modules.utils.logger import logger
from prompts import SYSTEM_PROMPT


class OllamaLLMIntegration:
    """
    Integración de Ollama para procesamiento de lenguaje natural
    en el agente IoT conversacional.
    """
    
    def __init__(self, model_name: str = "llama3.2:latest"):
        """
        Inicializa la integración con Ollama.
        
        Args:
            model_name (str): Nombre del modelo de Ollama a usar
        """
        self.model_name = model_name
        self.client = ollama
        self.conversation_history = []
        
        logger.info(f"Inicializando integración Ollama con modelo: {model_name}")
        
    def _prepare_system_context(self, context_data: Dict[str, Any] = None) -> str:
        """
        Prepara el contexto del sistema con información actual del IoT.
        
        Args:
            context_data (Dict): Datos de contexto del sistema IoT
            
        Returns:
            str: Prompt del sistema enriquecido con contexto
        """
        base_prompt = SYSTEM_PROMPT
        
        if context_data:
            context_info = "\n\n## Contexto actual del sistema (resumen):\n"
            summary = context_data.get("data_summary", {})
            if summary:
                context_info += (
                    f"• Lecturas recientes (10m): {summary.get('total_recent_records', 'N/D')}\n"
                    f"• Lecturas ultra-recientes (2m): {summary.get('ultra_recent_records', 'N/D')}\n"
                    f"• Dispositivos activos: {summary.get('active_devices_count', 'N/D')}\n"
                    f"• Alertas activas: {summary.get('active_alerts_count', 'N/D')}\n"
                )
            else:
                if "recent_data" in context_data:
                    context_info += f"• Datos recientes: {len(context_data['recent_data'])} lecturas\n"
                if "active_devices" in context_data:
                    context_info += f"• Dispositivos activos: {len(context_data['active_devices'])}\n"
                if "alerts" in context_data:
                    context_info += f"• Alertas activas: {len(context_data['alerts'])}\n"
            if "timestamp" in context_data:
                context_info += f"• Última actualización: {context_data['timestamp']}\n"
            base_prompt += context_info
            
        return base_prompt
    
    async def generate_response(self, 
                              user_message: str, 
                              context_data: Dict[str, Any] = None,
                              tools_results: Dict[str, Any] = None) -> str:
        """
        Genera una respuesta usando Ollama basada en el mensaje del usuario
        y el contexto del sistema IoT.
        
        Args:
            user_message (str): Mensaje del usuario
            context_data (Dict): Datos de contexto del sistema
            tools_results (Dict): Resultados de las herramientas ejecutadas
            
        Returns:
            str: Respuesta generada por el modelo
        """
        try:
            # Preparar el contexto del sistema
            system_prompt = self._prepare_system_context(context_data)
            
            # Preparar el mensaje con resultados de herramientas si existen
            enhanced_message = user_message
            
            # MEJORADO: Incluir datos reales en lugar de solo conteos
            if tools_results:
                try:
                    data_context = "\n\n📊 **DATOS REALES DISPONIBLES:**\n"
                    
                    # Procesar datos de sensores
                    if "sensor_data" in tools_results and tools_results["sensor_data"]:
                        sensor_data = tools_results["sensor_data"]
                        data_context += f"🌡️ **Registros de sensores**: {len(sensor_data)} lecturas recientes\n"
                        
                        # Agregar muestra de datos más recientes por tipo de sensor
                        by_sensor = {}
                        for record in sensor_data[:20]:  # Solo los 20 más recientes
                            sensor_type = record.get('sensor_type', 'unknown')
                            if sensor_type not in by_sensor:
                                by_sensor[sensor_type] = []
                            by_sensor[sensor_type].append(record)
                        
                        for sensor_type, records in by_sensor.items():
                            latest = records[0]  # El más reciente
                            device_id = latest.get('device_id', 'N/D')
                            value = latest.get('value', 'N/D')
                            unit = latest.get('unit', '')
                            timestamp = latest.get('timestamp', 'N/D')
                            
                            data_context += f"  • {sensor_type} ({device_id}): {value} {unit} - {timestamp}\n"
                    
                    # Procesar datos de dispositivos
                    if "devices" in tools_results and tools_results["devices"]:
                        devices = tools_results["devices"]
                        data_context += f"🔌 **Dispositivos activos**: {len(devices)}\n"
                        for device in devices[:5]:  # Solo los primeros 5
                            device_id = device.get('device_id', 'N/D')
                            status = device.get('status', 'N/D')
                            last_seen = device.get('last_seen', 'N/D')
                            data_context += f"  • {device_id}: {status} - {last_seen}\n"
                    
                    data_context += "\n🔍 **INSTRUCCIONES**: Usa SOLO estos datos reales para tu respuesta. No inventes información adicional."
                    enhanced_message += data_context
                    
                except Exception as e:
                    # Fallback al resumen básico si hay error
                    recs = len(tools_results.get("sensor_data", [])) if isinstance(tools_results.get("sensor_data"), list) else "N/D"
                    devs = len(tools_results.get("devices", [])) if isinstance(tools_results.get("devices"), list) else "N/D"
                    enhanced_message += f"\n\nResumen de datos: sensores={recs}, dispositivos={devs}. Error procesando detalles: {e}"
            
            # Preparar mensajes para el modelo
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ]
            
            # Agregar historial de conversación (últimos 5 intercambios)
            for msg in self.conversation_history[-10:]:
                messages.append(msg)
            
            # Agregar mensaje actual del usuario con recordatorio de formato
            messages.append({
                "role": "user",
                "content": enhanced_message + "\n\nIMPORTANTE: Responde como informe técnico, sin código ni JSON. Si el usuario pide PDF o gráficos, describe su contenido y confirma que puedes generarlo."
            })
            
            logger.info(f"Enviando consulta a Ollama con modelo {self.model_name}")
            
            # Generar respuesta con Ollama
            response = await asyncio.to_thread(
                self.client.chat,
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2048,
                }
            )
            
            assistant_response = response['message']['content']
            
            # Guardar en historial
            self.conversation_history.extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_response}
            ])
            
            # Mantener solo los últimos 20 intercambios
            if len(self.conversation_history) > 40:
                self.conversation_history = self.conversation_history[-40:]
            
            logger.info("Respuesta generada exitosamente por Ollama")
            return assistant_response
            
        except Exception as e:
            logger.error(f"Error al generar respuesta con Ollama: {e}")
            return f"❌ Error al procesar la consulta: {str(e)}"
    
    def clear_conversation_history(self):
        """Limpia el historial de conversación."""
        self.conversation_history = []
        logger.info("Historial de conversación limpiado")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del historial de conversación.
        
        Returns:
            Dict: Resumen del historial
        """
        return {
            "total_exchanges": len(self.conversation_history) // 2,
            "model_used": self.model_name,
            "last_messages": self.conversation_history[-4:] if self.conversation_history else []
        }
    
    async def test_connection(self) -> bool:
        """
        Prueba la conexión con Ollama.
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            response = await asyncio.to_thread(
                self.client.chat,
                model=self.model_name,
                messages=[{
                    "role": "user", 
                    "content": "¡Hola! ¿Estás funcionando correctamente?"
                }]
            )
            
            logger.info("Conexión con Ollama verificada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al conectar con Ollama: {e}")
            return False
