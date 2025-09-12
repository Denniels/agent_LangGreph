"""
Cloud IoT Agent - Versión para despliegue en Streamlit Cloud con HuggingFace
===========================================================================

Agente IoT optimizado para cloud usando HuggingFace en lugar de Ollama.
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import streamlit as st

# Imports del proyecto
from modules.agents.groq_integration import GroqIntegration
from modules.tools.jetson_api_connector import JetsonAPIConnector
from modules.agents.langgraph_state import IoTAgentState, create_initial_state

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)

class CloudIoTAgent:
    """
    Agente IoT para cloud que usa Groq en lugar de Ollama/HuggingFace.
    Optimizado para despliegue en Streamlit Cloud.
    """
    
    def __init__(self, 
                 groq_model: str = "llama-3.1-8b-instant",
                 jetson_api_url: str = None):
        """
        Inicializar Cloud IoT Agent.
        
        Args:
            groq_model: Modelo de Groq a usar (gratuito)
            jetson_api_url: URL de la API de Jetson
        """
        self.groq_model = groq_model
        self.jetson_api_url = jetson_api_url or os.getenv(
            "JETSON_API_URL", 
            "https://dpi-opportunity-hybrid-manufacturer.trycloudflare.com"
        )
        
        # Inicializar componentes
        self.groq_integration = None
        self.jetson_connector = None
        self.graph = None
        self.memory = MemorySaver()
        
        # Estado del agente
        self.is_initialized = False
        self.last_health_check = None
        
        logger.info(f"Cloud IoT Agent creado con modelo: {groq_model}")
    
    async def initialize(self) -> bool:
        """
        Inicializar componentes del agente de forma asíncrona.
        
        Returns:
            True si la inicialización fue exitosa
        """
        try:
            logger.info("🚀 Inicializando Cloud IoT Agent...")
            
            # 1. Inicializar Groq Integration
            groq_api_key = os.getenv("GROQ_API_KEY")
            
            if groq_api_key == "demo_mode" or not groq_api_key or groq_api_key.startswith("demo"):
                # Usar modo demo
                self.groq_integration = GroqIntegration()  # Sin API key = modo fallback
                logger.info("🎭 Usando Groq en modo DEMO")
            else:
                # Usar Groq real
                self.groq_integration = GroqIntegration(api_key=groq_api_key)
            
            # 2. Inicializar Jetson API Connector
            self.jetson_connector = JetsonAPIConnector(base_url=self.jetson_api_url)
            
            # 3. Probar conexiones
            groq_test = self.groq_integration.test_connection()
            jetson_test = self.jetson_connector.get_health_status() if self.jetson_connector else {"status": "not_configured"}
            
            if not groq_test.get('success', False):
                logger.warning(f"Groq API no disponible: {groq_test}. Usando modo fallback.")
                # Continuar en modo fallback
            
            if not jetson_test.get('status') == 'healthy':
                logger.warning(f"Jetson API no disponible: {jetson_test}")
                # Continuar sin Jetson (modo demo)
            
            # 4. Construir graph
            self._build_graph()
            
            self.is_initialized = True
            self.last_health_check = datetime.now()
            
            logger.info("✅ Cloud IoT Agent inicializado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando Cloud IoT Agent: {e}")
            # Continuar en modo fallback
            self.groq_integration = GroqIntegration()  # Sin API key
            self._build_graph()
            self.is_initialized = True
            logger.info("⚠️ Cloud IoT Agent inicializado en modo fallback")
            return True
    
    def _build_graph(self):
        """Construir el graph de LangGraph para cloud."""
        
        # Crear StateGraph
        workflow = StateGraph(IoTAgentState)
        
        # Agregar nodos
        workflow.add_node("query_analyzer", self._query_analyzer_node)
        workflow.add_node("remote_data_collector", self._remote_data_collector_node)
        workflow.add_node("data_analyzer", self._data_analyzer_node)
        workflow.add_node("response_generator", self._response_generator_node)
        workflow.add_node("data_verification", self._data_verification_node)
        
        # Configurar flujo
        workflow.set_entry_point("query_analyzer")
        
        # Edges del flujo
        workflow.add_edge("query_analyzer", "remote_data_collector")
        workflow.add_edge("remote_data_collector", "data_analyzer")
        workflow.add_edge("data_analyzer", "response_generator")
        workflow.add_edge("response_generator", "data_verification")
        workflow.add_edge("data_verification", END)
        
        # Compilar graph
        self.graph = workflow.compile(checkpointer=self.memory)
        
        logger.info("📊 Graph de LangGraph construido para cloud")
    
    async def _query_analyzer_node(self, state: IoTAgentState) -> IoTAgentState:
        """
        Nodo para analizar la consulta del usuario.
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado
        """
        try:
            logger.info("🔍 Ejecutando query_analyzer_node (Cloud)")
            
            user_query = state["user_query"]
            
            # Análisis simple de la consulta
            analysis = {
                "intent": "sensor_data_query",
                "requires_data": True,
                "sensors_mentioned": [],
                "devices_mentioned": [],
                "timestamp": datetime.now().isoformat()
            }
            
            # Detectar sensores mencionados
            sensor_keywords = ["temperatura", "temperature", "sensor", "calor", "grados"]
            if any(keyword in user_query.lower() for keyword in sensor_keywords):
                analysis["sensors_mentioned"] = ["temperature"]
            
            # Detectar dispositivos mencionados
            device_keywords = ["arduino", "esp32", "dispositivo", "device"]
            for keyword in device_keywords:
                if keyword in user_query.lower():
                    analysis["devices_mentioned"].append(keyword)
            
            # Actualizar estado
            state["query_analysis"] = analysis
            state["execution_status"] = "query_analyzed"
            
            logger.info(f"   ✅ Consulta analizada: {analysis['intent']}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en query_analyzer_node: {e}")
            state["execution_status"] = "error"
            state["error_details"] = str(e)
            return state
    
    async def _remote_data_collector_node(self, state: IoTAgentState) -> IoTAgentState:
        """
        Nodo para recolectar datos remotos via Jetson API.
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado
        """
        try:
            logger.info("📡 Ejecutando remote_data_collector_node (Cloud)")
            
            # Verificar si Jetson está disponible
            if not self.jetson_connector:
                logger.error("🚨 Jetson connector no disponible")
                jetson_status = self._check_jetson_api_status()
                state["raw_data"] = []
                state["execution_status"] = "jetson_api_offline"
                state["error"] = jetson_status
                return state
            
            # Obtener datos de Jetson
            devices_result = self.jetson_connector.get_devices()
            
            if devices_result:
                all_data = []
                
                # Recolectar datos de cada dispositivo
                for device in devices_result[:2]:  # Limitar a 2 dispositivos para cloud
                    device_id = device.get("device_id")
                    if device_id:
                        device_data = self.jetson_connector.get_sensor_data(
                            device_id=device_id,
                            limit=20  # Menos datos para cloud
                        )
                        
                        if device_data:
                            all_data.extend(device_data)
                
                state["raw_data"] = all_data
                state["execution_status"] = "remote_data_collected"
                
                logger.info(f"   ✅ Datos remotos recolectados: {len(all_data)} registros")
            else:
                logger.error("🚨 Error obteniendo dispositivos desde Jetson API")
                jetson_status = self._check_jetson_api_status()
                state["raw_data"] = []
                state["execution_status"] = "jetson_api_error"
                state["error"] = jetson_status
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en remote_data_collector_node: {e}")
            jetson_status = self._check_jetson_api_status()
            state["raw_data"] = []
            state["execution_status"] = "jetson_connection_error"
            state["error"] = jetson_status
            state["exception"] = str(e)
            return state
    
    async def _data_analyzer_node(self, state: IoTAgentState) -> IoTAgentState:
        """
        Nodo para analizar los datos recolectados.
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado
        """
        try:
            logger.info("📊 Ejecutando data_analyzer_node (Cloud)")
            
            raw_data = state.get("raw_data", [])
            
            # Verificar si hay datos disponibles
            if not raw_data:
                logger.warning("🚨 No hay datos para analizar")
                
                # Si hay información de error de Jetson, incluirla
                if "error" in state:
                    error_info = state["error"]
                    state["formatted_data"] = f"""
🚨 ERROR: No se pudieron obtener datos de sensores

{error_info.get('message', 'Error desconocido')}

📋 INSTRUCCIONES PARA RESOLVER:
"""
                    for instruction in error_info.get('instructions', []):
                        state["formatted_data"] += f"\n{instruction}"
                else:
                    state["formatted_data"] = """
🚨 ERROR: No hay datos de sensores disponibles

La API de la Jetson no está respondiendo. Por favor:

🔧 Verificar que la Jetson esté encendida y conectada a la red
📡 Confirmar que los servicios systemd estén ejecutándose:
   sudo systemctl status iot-api-service
   sudo systemctl status sensor-collector-service
🌐 Verificar conectividad de red desde la Jetson
📋 Revisar logs del sistema: journalctl -u iot-api-service -f
🔄 Reiniciar servicios si es necesario: sudo systemctl restart iot-api-service
"""
                
                state["sensor_summary"] = {}
                state["analysis"] = {"error": "no_data_available"}
                return state
            
            # Análisis optimizado para cloud
            analysis = {
                "total_records": len(raw_data),
                "devices": set(),
                "sensors": set(),
                "latest_readings": {},
                "timestamp_range": {"start": None, "end": None}
            }
            
            # Procesar datos (máximo 50 registros para cloud)
            processed_data = raw_data[:50] if len(raw_data) > 50 else raw_data
            
            for record in processed_data:
                device_id = record.get("device_id", "unknown")
                sensor_type = record.get("sensor_type", "unknown")
                value = record.get("value")
                timestamp = record.get("timestamp")
                
                analysis["devices"].add(device_id)
                analysis["sensors"].add(sensor_type)
                
                # Última lectura por sensor
                if sensor_type not in analysis["latest_readings"]:
                    analysis["latest_readings"][sensor_type] = {
                        "value": value,
                        "device": device_id,
                        "timestamp": timestamp
                    }
            
            # Convertir sets a listas para serialización
            analysis["devices"] = list(analysis["devices"])
            analysis["sensors"] = list(analysis["sensors"])
            
            # Formatear datos para el modelo
            formatted_data = self._format_data_for_model(processed_data, analysis)
            
            state["formatted_data"] = formatted_data
            state["sensor_summary"] = analysis
            state["execution_status"] = "data_analyzed"
            
            logger.info(f"   ✅ Datos analizados: {len(processed_data)} registros, {len(analysis['sensors'])} tipos de sensores")
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en data_analyzer_node: {e}")
            state["execution_status"] = "error"
            state["error_details"] = str(e)
            return state
    
    async def _response_generator_node(self, state: IoTAgentState) -> IoTAgentState:
        """
        Nodo para generar respuesta usando Groq.
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado
        """
        try:
            logger.info("🤖 Ejecutando response_generator_node (Cloud con Groq)")
            
            user_query = state["user_query"]
            formatted_data = state.get("formatted_data", "")
            
            # Crear prompt para Groq
            prompt = f"""
            Eres un asistente experto en análisis de datos de sensores IoT.
            
            CONSULTA DEL USUARIO: {user_query}
            
            DATOS DE SENSORES DISPONIBLES:
            {formatted_data}
            
            Proporciona un análisis claro y profesional basado ÚNICAMENTE en los datos mostrados.
            NO inventes datos que no están presentes.
            """
            
            # Generar respuesta con Groq
            response = self.groq_integration.generate_response(prompt, model=self.groq_model)
            
            state["final_response"] = response
            state["execution_status"] = "response_generated"
            
            logger.info("   ✅ Respuesta generada con Groq")
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en response_generator_node: {e}")
            # Respuesta de fallback
            state["final_response"] = self._generate_fallback_response(state)
            state["execution_status"] = "fallback_response"
            return state
    
    async def _data_verification_node(self, state: IoTAgentState) -> IoTAgentState:
        """
        Nodo para verificar la respuesta y detectar alucinaciones.
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado
        """
        try:
            logger.info("🔍 Ejecutando data_verification_node (Cloud)")
            
            response = state.get("final_response", "")
            real_sensors = state.get("sensor_summary", {}).get("sensors", [])
            
            # Verificación simple de alucinaciones
            verification = {
                "status": "verified",
                "hallucinations_detected": [],
                "confidence": 0.9,
                "timestamp": datetime.now().isoformat()
            }
            
            # Detectar sensores mencionados que no existen
            problematic_sensors = ["humidity", "humedad", "pressure", "presión"]
            for sensor in problematic_sensors:
                if sensor.lower() in response.lower() and sensor not in real_sensors:
                    verification["hallucinations_detected"].append(f"Sensor inexistente: {sensor}")
                    verification["confidence"] -= 0.2
            
            # Ajustar status basado en confianza
            if verification["confidence"] < 0.5:
                verification["status"] = "needs_review"
            elif verification["confidence"] < 0.8:
                verification["status"] = "caution"
            
            state["verification_status"] = verification
            state["execution_status"] = "verification_complete"
            
            logger.info(f"   ✅ Verificación completada: {verification['status']}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en data_verification_node: {e}")
            state["verification_status"] = {"status": "error", "error": str(e)}
            state["execution_status"] = "verification_error"
            return state
    
    async def process_query(self, user_query: str, thread_id: str = "cloud-session") -> Dict[str, Any]:
        """
        Procesar consulta del usuario usando el agente cloud.
        
        Args:
            user_query: Consulta del usuario
            thread_id: ID del hilo de conversación
            
        Returns:
            Dict con la respuesta procesada
        """
        try:
            if not self.is_initialized:
                await self.initialize()
            
            logger.info(f"🔄 Procesando consulta cloud: {user_query[:100]}...")
            
            # Crear estado inicial
            initial_state = create_initial_state(user_query)
            
            # Ejecutar graph
            config = {"configurable": {"thread_id": thread_id}}
            
            result = await self.graph.ainvoke(initial_state, config=config)
            
            # Formatear respuesta
            response = {
                "success": True,
                "response": result.get("final_response", "No se pudo generar respuesta"),
                "execution_status": result.get("execution_status", "unknown"),
                "verification": result.get("verification_status", {}),
                "data_summary": {
                    "total_records": len(result.get("raw_data", [])),
                    "sensors": result.get("sensor_summary", {}).get("sensors", []),
                    "devices": result.get("sensor_summary", {}).get("devices", [])
                },
                "timestamp": datetime.now().isoformat(),
                "model_used": self.groq_model
            }
            
            logger.info("✅ Consulta cloud procesada exitosamente")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error procesando consulta cloud: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "Error procesando la consulta. Por favor intenta nuevamente.",
                "timestamp": datetime.now().isoformat()
            }
    
    def _check_jetson_api_status(self) -> Dict[str, Any]:
        """
        Verificar el estado de la API de Jetson.
        
        Returns:
            Diccionario con el estado de la API
        """
        try:
            # Aquí iría la verificación real de la API de Jetson
            # Por ejemplo: response = requests.get(f"{JETSON_API_URL}/health", timeout=5)
            
            return {
                "status": "offline",
                "error": "API_JETSON_OFFLINE",
                "message": "La API de la Jetson no está disponible",
                "instructions": [
                    "🔧 Verificar que la Jetson esté encendida y conectada a la red",
                    "📡 Confirmar que los servicios systemd estén ejecutándose:",
                    "   sudo systemctl status iot-api-service",
                    "   sudo systemctl status sensor-collector-service", 
                    "🌐 Verificar conectividad de red desde la Jetson",
                    "📋 Revisar logs del sistema: journalctl -u iot-api-service -f",
                    "🔄 Reiniciar servicios si es necesario: sudo systemctl restart iot-api-service"
                ]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": "CONNECTION_ERROR", 
                "message": f"Error al verificar API de Jetson: {str(e)}",
                "instructions": [
                    "🚨 Error de conexión con la Jetson",
                    "🔌 Verificar cables de red y alimentación",
                    "📡 Confirmar IP de la Jetson en la red local",
                    "🔧 Revisar configuración de firewall en la Jetson"
                ]
            }
    
    def _format_data_for_model(self, data: List[Dict], analysis: Dict) -> str:
        """
        Formatear datos para el modelo HuggingFace.
        
        Args:
            data: Datos de sensores
            analysis: Análisis de datos
            
        Returns:
            Datos formateados como string
        """
        formatted = f"=== DATOS DE SENSORES IoT ===\n"
        formatted += f"Total de registros: {analysis['total_records']}\n"
        formatted += f"Dispositivos: {', '.join(analysis['devices'])}\n"
        formatted += f"Sensores: {', '.join(analysis['sensors'])}\n\n"
        
        # Últimas lecturas por sensor
        formatted += "ÚLTIMAS LECTURAS:\n"
        for sensor, reading in analysis.get("latest_readings", {}).items():
            unit = "°C" if sensor in ['t1', 't2', 'avg', 'ntc_entrada', 'ntc_salida'] else ""
            formatted += f"• {sensor}: {reading['value']}{unit} ({reading['device']})\n"
        
        return formatted
    
    def _generate_fallback_response(self, state: IoTAgentState) -> str:
        """
        Generar respuesta de fallback cuando HuggingFace falla.
        
        Args:
            state: Estado actual
            
        Returns:
            Respuesta de fallback
        """
        response = "**Informe de Sensores IoT - Cloud Agent**\n\n"
        
        sensor_summary = state.get("sensor_summary", {})
        total_records = sensor_summary.get("total_records", 0)
        
        if total_records > 0:
            response += f"Se procesaron {total_records} registros de sensores.\n\n"
            
            sensors = sensor_summary.get("sensors", [])
            devices = sensor_summary.get("devices", [])
            
            response += f"**Dispositivos activos**: {', '.join(devices)}\n"
            response += f"**Tipos de sensores**: {', '.join(sensors)}\n\n"
            
            latest_readings = sensor_summary.get("latest_readings", {})
            if latest_readings:
                response += "**Últimas lecturas**:\n"
                for sensor, reading in latest_readings.items():
                    unit = "°C" if sensor in ['t1', 't2', 'avg', 'ntc_entrada', 'ntc_salida'] else ""
                    response += f"• {sensor}: {reading['value']}{unit}\n"
        else:
            response += "No hay datos de sensores disponibles en este momento.\n"
        
        response += f"\n**Generado por**: Cloud IoT Agent con Groq\n"
        response += f"**Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return response
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verificar estado de salud del agente cloud.
        
        Returns:
            Dict con estado de salud
        """
        try:
            health = {
                "agent_status": "healthy" if self.is_initialized else "not_initialized",
                "groq_status": "unknown",
                "jetson_status": "unknown",
                "last_check": datetime.now().isoformat()
            }
            
            if self.is_initialized:
                # Test Groq
                groq_test = self.groq_integration.test_connection()
                health["groq_status"] = "success" if groq_test.get("success") else "fallback"
                
                # Test Jetson (opcional)
                if self.jetson_connector:
                    jetson_test = self.jetson_connector.get_health_status()
                    health["jetson_status"] = jetson_test.get("status", "error")
                else:
                    health["jetson_status"] = "not_configured"
            
            health["overall_status"] = "healthy" if all([
                health["agent_status"] == "healthy",
                health["groq_status"] in ["success", "fallback"]  # Fallback también es válido
            ]) else "degraded"
            
            return health
            
        except Exception as e:
            return {
                "overall_status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Función de utilidad para crear instancia cloud
def create_cloud_iot_agent(groq_model: str = "llama-3.1-8b-instant") -> CloudIoTAgent:
    """
    Crear instancia de Cloud IoT Agent.
    
    Args:
        groq_model: Modelo de Groq a usar (gratuito)
        
    Returns:
        Instancia de CloudIoTAgent
    """
    return CloudIoTAgent(groq_model=groq_model)


if __name__ == "__main__":
    # Prueba del Cloud IoT Agent
    import asyncio
    
    async def test_cloud_agent():
        print("🧪 PRUEBA DE CLOUD IOT AGENT")
        print("=" * 50)
        
        try:
            # Crear agente cloud
            agent = create_cloud_iot_agent()
            
            # Health check
            print("1️⃣ Health check...")
            health = await agent.health_check()
            print(f"   Status: {health.get('overall_status')}")
            
            # Procesar consulta de prueba
            print("\n2️⃣ Procesando consulta de prueba...")
            response = await agent.process_query("¿Cuál es la temperatura actual?")
            
            print(f"   Success: {response.get('success')}")
            print(f"   Response: {response.get('response', '')[:200]}...")
            print(f"   Model: {response.get('model_used')}")
            
            print("\n✅ Prueba cloud completada")
            
        except Exception as e:
            print(f"❌ Error en prueba cloud: {e}")
            print("💡 Configura GROQ_API_KEY para usar Groq API completa (opcional)")
            print("💡 Sin API key, el agente funciona en modo fallback")
    
    asyncio.run(test_cloud_agent())
