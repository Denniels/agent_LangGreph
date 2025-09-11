"""
HuggingFace Integration - Reemplazo de Ollama para deployment en cloud
====================================================================

Integración con HuggingFace Inference API para usar modelos en la nube.
"""

import os
import requests
import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HuggingFaceIntegration:
    """
    Integración con HuggingFace Inference API para generar respuestas del agente IoT.
    """
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium", api_token: Optional[str] = None):
        """
        Inicializar la integración con HuggingFace.
        
        Args:
            model_name: Nombre del modelo en HuggingFace
            api_token: Token de API de HuggingFace (si no se proporciona, se busca en variables de entorno)
        """
        self.model_name = model_name
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_TOKEN")
        
        if not self.api_token:
            raise ValueError("HuggingFace API token es requerido. Configura HUGGINGFACE_API_TOKEN en variables de entorno.")
        
        # URL de la API de HuggingFace
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        
        # Headers para las requests
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Historial de conversación
        self.conversation_history = []
        
        # Configuración de modelos alternativos
        self.model_alternatives = {
            "text-generation": [
                "microsoft/DialoGPT-large",
                "microsoft/DialoGPT-medium",
                "facebook/blenderbot-400M-distill",
                "microsoft/GODEL-v1_1-base-seq2seq"
            ],
            "conversational": [
                "microsoft/DialoGPT-large",
                "facebook/blenderbot-1B-distill",
                "microsoft/GODEL-v1_1-large-seq2seq"
            ]
        }
        
        logger.info(f"HuggingFace Integration inicializada con modelo: {self.model_name}")
    
    def _create_system_prompt(self, context_data: Dict[str, Any] = None) -> str:
        """
        Crear prompt del sistema para el agente IoT.
        
        Args:
            context_data: Datos de contexto del sistema IoT
            
        Returns:
            Prompt del sistema
        """
        base_prompt = """Eres un asistente técnico especializado en sistemas IoT y análisis de datos de sensores.

INSTRUCCIONES IMPORTANTES:
- Responde ÚNICAMENTE con datos reales de sensores disponibles
- NO inventes información sobre sensores que no existen
- Proporciona respuestas técnicas precisas y profesionales
- Si no hay datos suficientes, indica claramente esa limitación

FORMATO DE RESPUESTA:
- Usa formato de informe técnico
- Incluye métricas específicas cuando estén disponibles
- Menciona la fuente de datos (API remota de Jetson)
- Proporciona recomendaciones técnicas cuando sea apropiado

"""
        
        if context_data:
            context_info = "\nCONTEXTO ACTUAL:\n"
            if "data_source" in context_data:
                context_info += f"• Fuente de datos: {context_data['data_source']}\n"
            if "timestamp" in context_data:
                context_info += f"• Última actualización: {context_data['timestamp']}\n"
            if "real_sensors" in context_data:
                context_info += f"• Sensores disponibles: {', '.join(context_data['real_sensors'])}\n"
            
            base_prompt += context_info
        
        return base_prompt
    
    async def generate_response(self, 
                              user_message: str, 
                              context_data: Dict[str, Any] = None,
                              tools_results: Dict[str, Any] = None) -> str:
        """
        Generar respuesta usando HuggingFace Inference API.
        
        Args:
            user_message: Mensaje del usuario
            context_data: Contexto del sistema IoT
            tools_results: Resultados de herramientas ejecutadas
            
        Returns:
            Respuesta generada por el modelo
        """
        try:
            logger.info(f"Generando respuesta con HuggingFace modelo: {self.model_name}")
            
            # Crear prompt mejorado con contexto
            system_prompt = self._create_system_prompt(context_data)
            enhanced_message = user_message
            
            # Añadir datos de sensores si están disponibles
            if tools_results:
                data_context = "\n\n=== DATOS DE SENSORES IoT ===\n"
                
                try:
                    # Procesar datos de sensores
                    if "sensor_data" in tools_results and tools_results["sensor_data"]:
                        sensor_data = tools_results["sensor_data"][:20]  # Limitar a 20 registros
                        data_context += f"📊 **Registros de sensores**: {len(sensor_data)}\n"
                        
                        # Agrupar por dispositivo y tipo de sensor
                        by_device = {}
                        for record in sensor_data:
                            device_id = record.get('device_id', 'unknown')
                            sensor_type = record.get('sensor_type', 'unknown')
                            value = record.get('value', 'N/A')
                            timestamp = record.get('timestamp', 'N/A')
                            
                            if device_id not in by_device:
                                by_device[device_id] = {}
                            
                            by_device[device_id][sensor_type] = {
                                'value': value,
                                'timestamp': timestamp
                            }
                        
                        # Formatear datos por dispositivo
                        for device_id, sensors in by_device.items():
                            data_context += f"\n🔌 **{device_id}**:\n"
                            for sensor_type, data in sensors.items():
                                unit = "°C" if sensor_type in ['t1', 't2', 'avg', 'ntc_entrada', 'ntc_salida'] else ""
                                data_context += f"  • {sensor_type}: {data['value']}{unit} ({data['timestamp']})\n"
                    
                    # Añadir datos formateados si están disponibles
                    if "formatted_data" in tools_results:
                        formatted = tools_results["formatted_data"]
                        if formatted and len(formatted) > 100:
                            data_context += f"\n📋 **Resumen formateado**:\n{formatted[:500]}...\n"
                    
                    data_context += "\n🔍 **IMPORTANTE**: Usa SOLO estos datos reales para tu respuesta."
                    enhanced_message += data_context
                    
                except Exception as e:
                    logger.warning(f"Error procesando datos para HuggingFace: {e}")
                    enhanced_message += f"\n\nDatos de contexto disponibles pero con errores de formato."
            
            # Preparar payload para HuggingFace
            payload = {
                "inputs": f"{system_prompt}\n\nUsuario: {enhanced_message}\n\nAsistente:",
                "parameters": {
                    "max_new_tokens": 512,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            # Hacer request a HuggingFace
            response = await asyncio.to_thread(
                requests.post,
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extraer texto generado
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    generated_text = result.get("generated_text", "")
                else:
                    generated_text = str(result)
                
                # Limpiar y formatear respuesta
                assistant_response = self._clean_response(generated_text)
                
                # Guardar en historial
                self.conversation_history.extend([
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": assistant_response}
                ])
                
                # Mantener historial limitado
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                
                logger.info("Respuesta generada exitosamente con HuggingFace")
                return assistant_response
                
            else:
                logger.error(f"Error de HuggingFace API: {response.status_code} - {response.text}")
                return self._fallback_response(user_message, tools_results)
                
        except Exception as e:
            logger.error(f"Error generando respuesta con HuggingFace: {e}")
            return self._fallback_response(user_message, tools_results)
    
    def _clean_response(self, text: str) -> str:
        """
        Limpiar y formatear la respuesta del modelo.
        
        Args:
            text: Texto generado por el modelo
            
        Returns:
            Texto limpio y formateado
        """
        if not text:
            return "No se pudo generar una respuesta adecuada."
        
        # Remover prefijos comunes
        prefixes_to_remove = [
            "Assistant:", "Asistente:", "AI:", "Bot:", 
            "Response:", "Respuesta:", "Output:"
        ]
        
        cleaned = text.strip()
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        # Asegurar que la respuesta no esté vacía
        if not cleaned or len(cleaned) < 10:
            return "Respuesta procesada desde HuggingFace. Los datos están disponibles en el contexto proporcionado."
        
        return cleaned
    
    def _fallback_response(self, user_message: str, tools_results: Dict[str, Any] = None) -> str:
        """
        Generar respuesta de fallback cuando HuggingFace falla.
        
        Args:
            user_message: Mensaje original del usuario
            tools_results: Resultados de herramientas
            
        Returns:
            Respuesta de fallback
        """
        fallback = "**Informe Técnico de Sensores IoT**\n\n"
        
        if tools_results and "sensor_data" in tools_results:
            sensor_data = tools_results["sensor_data"]
            if sensor_data:
                fallback += f"Se han procesado {len(sensor_data)} registros de sensores.\n\n"
                
                # Extraer información básica
                devices = set(record.get('device_id', 'unknown') for record in sensor_data)
                sensors = set(record.get('sensor_type', 'unknown') for record in sensor_data)
                
                fallback += f"**Dispositivos activos**: {', '.join(devices)}\n"
                fallback += f"**Tipos de sensores**: {', '.join(sensors)}\n\n"
                
                # Últimas lecturas
                if sensor_data:
                    latest = sensor_data[0]
                    fallback += f"**Última lectura**: {latest.get('sensor_type', 'N/A')} = {latest.get('value', 'N/A')} "
                    fallback += f"({latest.get('device_id', 'N/A')})\n"
                    fallback += f"**Timestamp**: {latest.get('timestamp', 'N/A')}\n\n"
            else:
                fallback += "No se encontraron datos de sensores en este momento.\n\n"
        
        fallback += "**Fuente**: API remota de Jetson via Cloudflare tunnel\n"
        fallback += f"**Consulta procesada**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return fallback
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Probar la conexión con HuggingFace API.
        
        Returns:
            Dict con resultados de la prueba
        """
        try:
            test_payload = {
                "inputs": "Hello, this is a test message.",
                "parameters": {"max_new_tokens": 50}
            }
            
            response = await asyncio.to_thread(
                requests.post,
                self.api_url,
                headers=self.headers,
                json=test_payload,
                timeout=15
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "model": self.model_name,
                    "response_time": response.elapsed.total_seconds(),
                    "message": "Conexión exitosa con HuggingFace API"
                }
            else:
                return {
                    "status": "error",
                    "error_code": response.status_code,
                    "error_message": response.text,
                    "message": "Error de conexión con HuggingFace API"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Excepción al conectar con HuggingFace API"
            }
    
    def clear_conversation_history(self):
        """Limpiar el historial de conversación."""
        self.conversation_history = []
        logger.info("Historial de conversación limpiado")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen del historial de conversación.
        
        Returns:
            Dict con resumen del historial
        """
        return {
            "total_exchanges": len(self.conversation_history) // 2,
            "model_used": self.model_name,
            "api_endpoint": self.api_url,
            "last_messages": self.conversation_history[-4:] if self.conversation_history else []
        }


# Función de utilidad para crear instancia
def create_huggingface_integration(model_name: str = "microsoft/DialoGPT-medium") -> HuggingFaceIntegration:
    """
    Crear instancia de HuggingFace Integration.
    
    Args:
        model_name: Nombre del modelo a usar
        
    Returns:
        Instancia de HuggingFaceIntegration
    """
    return HuggingFaceIntegration(model_name=model_name)


if __name__ == "__main__":
    # Prueba básica de HuggingFace Integration
    import asyncio
    
    async def test_huggingface():
        print("🧪 PRUEBA DE HUGGINGFACE INTEGRATION")
        print("=" * 50)
        
        try:
            # Crear integración (requiere HUGGINGFACE_API_TOKEN en env)
            hf = create_huggingface_integration()
            
            # Test de conexión
            print("1️⃣ Probando conexión...")
            connection_test = await hf.test_connection()
            print(f"   Status: {connection_test.get('status')}")
            print(f"   Message: {connection_test.get('message')}")
            
            if connection_test.get('status') == 'success':
                # Test de generación de respuesta
                print("\n2️⃣ Probando generación de respuesta...")
                
                test_context = {
                    "data_source": "API remota de Jetson",
                    "real_sensors": ["t1", "t2", "avg", "ntc_entrada", "ntc_salida"]
                }
                
                test_tools = {
                    "sensor_data": [
                        {
                            "device_id": "arduino_eth_001",
                            "sensor_type": "avg",
                            "value": 23.5,
                            "timestamp": "2025-09-10T16:00:00Z"
                        }
                    ]
                }
                
                response = await hf.generate_response(
                    "¿Cuál es la temperatura actual?",
                    context_data=test_context,
                    tools_results=test_tools
                )
                
                print(f"   Respuesta: {response[:200]}...")
                
            print("\n✅ Prueba completada")
            
        except Exception as e:
            print(f"❌ Error en prueba: {e}")
            print("💡 Asegúrate de configurar HUGGINGFACE_API_TOKEN en variables de entorno")
    
    asyncio.run(test_huggingface())
