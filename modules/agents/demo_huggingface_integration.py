"""
Demo HuggingFace Integration - Para pruebas sin token
====================================================

Versión demo que simula respuestas de HuggingFace para pruebas locales.
"""

import os
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DemoHuggingFaceIntegration:
    """
    Integración demo de HuggingFace que simula respuestas para pruebas.
    """
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-large"):
        """
        Inicializar la integración demo.
        
        Args:
            model_name: Nombre del modelo (solo para referencia)
        """
        self.model_name = model_name
        self.conversation_history = []
        
        logger.info(f"Demo HuggingFace Integration inicializada con modelo: {model_name}")
    
    async def generate_response(self, 
                              user_message: str, 
                              context_data: Dict[str, Any] = None,
                              tools_results: Dict[str, Any] = None) -> str:
        """
        Generar respuesta demo basada en datos de sensores.
        
        Args:
            user_message: Mensaje del usuario
            context_data: Contexto del sistema IoT
            tools_results: Resultados de herramientas ejecutadas
            
        Returns:
            Respuesta generada (demo)
        """
        try:
            logger.info("Generando respuesta demo de HuggingFace")
            
            # Respuesta base
            response = "**🤖 Informe Técnico de Sensores IoT (Demo Mode)**\n\n"
            
            # Procesar datos de sensores si están disponibles
            if tools_results and "sensor_data" in tools_results:
                sensor_data = tools_results["sensor_data"]
                
                if sensor_data:
                    response += f"📊 **Análisis de datos**: Se procesaron {len(sensor_data)} registros de sensores.\n\n"
                    
                    # Extraer información de dispositivos y sensores
                    devices = set(record.get('device_id', 'unknown') for record in sensor_data)
                    sensors = set(record.get('sensor_type', 'unknown') for record in sensor_data)
                    
                    response += f"🔌 **Dispositivos activos**: {', '.join(devices)}\n"
                    response += f"📡 **Tipos de sensores detectados**: {', '.join(sensors)}\n\n"
                    
                    # Últimas lecturas por tipo de sensor
                    response += "🌡️ **Últimas lecturas por sensor**:\n"
                    
                    sensor_readings = {}
                    for record in sensor_data:
                        sensor_type = record.get('sensor_type', 'unknown')
                        if sensor_type not in sensor_readings:
                            sensor_readings[sensor_type] = {
                                'value': record.get('value', 'N/A'),
                                'device': record.get('device_id', 'N/A'),
                                'timestamp': record.get('timestamp', 'N/A')
                            }
                    
                    for sensor_type, reading in sensor_readings.items():
                        unit = "°C" if sensor_type in ['t1', 't2', 'avg', 'ntc_entrada', 'ntc_salida'] else ""
                        response += f"• **{sensor_type}**: {reading['value']}{unit} (dispositivo: {reading['device']})\n"
                    
                    # Análisis específico según la consulta
                    user_query_lower = user_message.lower()
                    
                    if "temperatura" in user_query_lower or "temperature" in user_query_lower:
                        temp_sensors = [s for s in sensors if s in ['t1', 't2', 'avg', 'ntc_entrada', 'ntc_salida']]
                        if temp_sensors:
                            response += f"\n🔥 **Análisis de temperatura**: Se detectaron {len(temp_sensors)} sensores de temperatura activos.\n"
                            
                            # Calcular promedio si hay datos numéricos
                            temp_values = []
                            for record in sensor_data:
                                if record.get('sensor_type') in temp_sensors:
                                    try:
                                        temp_values.append(float(record.get('value', 0)))
                                    except (ValueError, TypeError):
                                        pass
                            
                            if temp_values:
                                avg_temp = sum(temp_values) / len(temp_values)
                                min_temp = min(temp_values)
                                max_temp = max(temp_values)
                                
                                response += f"• Temperatura promedio: {avg_temp:.2f}°C\n"
                                response += f"• Rango: {min_temp:.2f}°C - {max_temp:.2f}°C\n"
                    
                    elif "dispositivo" in user_query_lower or "device" in user_query_lower:
                        response += f"\n🔌 **Análisis de dispositivos**: Se encontraron {len(devices)} dispositivos únicos.\n"
                        for device in devices:
                            device_sensors = [record.get('sensor_type') for record in sensor_data if record.get('device_id') == device]
                            unique_sensors = set(device_sensors)
                            response += f"• **{device}**: {len(unique_sensors)} tipos de sensores\n"
                    
                    elif "sensor" in user_query_lower:
                        response += f"\n📡 **Análisis de sensores**: Se detectaron {len(sensors)} tipos de sensores diferentes.\n"
                        for sensor in sensors:
                            count = len([r for r in sensor_data if r.get('sensor_type') == sensor])
                            response += f"• **{sensor}**: {count} lecturas\n"
                
                else:
                    response += "⚠️ **No se encontraron datos de sensores** en este momento.\n\n"
            
            else:
                response += "📭 **Sin datos de contexto**: No se proporcionaron datos de sensores para analizar.\n\n"
            
            # Información adicional
            response += f"\n🔗 **Fuente de datos**: {context_data.get('data_source', 'API remota de Jetson') if context_data else 'No especificada'}\n"
            response += f"🕐 **Timestamp de consulta**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            response += f"🤖 **Modelo**: {self.model_name} (Demo Mode)\n"
            
            # Recomendaciones técnicas
            response += "\n💡 **Recomendaciones técnicas**:\n"
            response += "• Monitoreo continuo de temperaturas para detectar anomalías\n"
            response += "• Verificación periódica de conectividad de dispositivos\n"
            response += "• Implementación de alertas para valores fuera de rango\n"
            
            # Guardar en historial
            self.conversation_history.extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": response}
            ])
            
            # Mantener historial limitado
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            logger.info("Respuesta demo generada exitosamente")
            return response
            
        except Exception as e:
            logger.error(f"Error generando respuesta demo: {e}")
            return self._fallback_response(user_message, tools_results)
    
    def _fallback_response(self, user_message: str, tools_results: Dict[str, Any] = None) -> str:
        """
        Generar respuesta de fallback.
        
        Args:
            user_message: Mensaje original del usuario
            tools_results: Resultados de herramientas
            
        Returns:
            Respuesta de fallback
        """
        response = "**🤖 Agente IoT - Respuesta Demo**\n\n"
        response += f"📝 **Consulta procesada**: {user_message}\n\n"
        
        if tools_results and "sensor_data" in tools_results:
            sensor_data = tools_results["sensor_data"]
            response += f"📊 **Datos disponibles**: {len(sensor_data)} registros de sensores\n"
        
        response += f"🕐 **Procesado**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        response += "💡 **Nota**: Esta es una respuesta demo. Configura HUGGINGFACE_API_TOKEN para funcionalidad completa.\n"
        
        return response
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Simular test de conexión exitoso.
        
        Returns:
            Dict con resultados de la prueba (siempre exitoso en demo)
        """
        return {
            "status": "success",
            "model": self.model_name,
            "response_time": 0.1,
            "message": "Conexión demo exitosa (simulada)"
        }
    
    def clear_conversation_history(self):
        """Limpiar el historial de conversación."""
        self.conversation_history = []
        logger.info("Historial de conversación demo limpiado")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen del historial de conversación.
        
        Returns:
            Dict con resumen del historial
        """
        return {
            "total_exchanges": len(self.conversation_history) // 2,
            "model_used": f"{self.model_name} (Demo)",
            "api_endpoint": "demo://localhost",
            "last_messages": self.conversation_history[-4:] if self.conversation_history else []
        }


# Función de utilidad para crear instancia demo
def create_demo_huggingface_integration(model_name: str = "microsoft/DialoGPT-large") -> DemoHuggingFaceIntegration:
    """
    Crear instancia demo de HuggingFace Integration.
    
    Args:
        model_name: Nombre del modelo a simular
        
    Returns:
        Instancia de DemoHuggingFaceIntegration
    """
    return DemoHuggingFaceIntegration(model_name=model_name)


if __name__ == "__main__":
    # Prueba básica de Demo HuggingFace Integration
    import asyncio
    
    async def test_demo_huggingface():
        print("🧪 PRUEBA DE DEMO HUGGINGFACE INTEGRATION")
        print("=" * 50)
        
        try:
            # Crear integración demo
            hf = create_demo_huggingface_integration()
            
            # Test de conexión
            print("1️⃣ Probando conexión demo...")
            connection_test = await hf.test_connection()
            print(f"   Status: {connection_test.get('status')}")
            print(f"   Message: {connection_test.get('message')}")
            
            # Test de generación de respuesta
            print("\n2️⃣ Probando generación de respuesta demo...")
            
            test_context = {
                "data_source": "API demo de Jetson",
                "real_sensors": ["t1", "t2", "avg", "ntc_entrada", "ntc_salida"]
            }
            
            test_tools = {
                "sensor_data": [
                    {
                        "device_id": "arduino_eth_001",
                        "sensor_type": "avg",
                        "value": 23.5,
                        "timestamp": "2025-09-10T16:00:00Z"
                    },
                    {
                        "device_id": "esp32_wifi_001",
                        "sensor_type": "t1",
                        "value": 24.1,
                        "timestamp": "2025-09-10T16:00:05Z"
                    }
                ]
            }
            
            response = await hf.generate_response(
                "¿Cuál es la temperatura actual de los sensores?",
                context_data=test_context,
                tools_results=test_tools
            )
            
            print(f"   Respuesta generada: {len(response)} caracteres")
            print(f"   Muestra:\n{response[:300]}...")
            
            print("\n✅ Prueba demo completada exitosamente")
            
        except Exception as e:
            print(f"❌ Error en prueba demo: {e}")
    
    asyncio.run(test_demo_huggingface())
