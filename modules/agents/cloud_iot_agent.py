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
from modules.utils.usage_tracker import usage_tracker

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)

# Import del motor de visualización
try:
    from modules.utils.visualization_engine import create_visualization_engine
    VISUALIZATION_AVAILABLE = True
    logger.info("🎨 Motor de visualización cargado exitosamente")
except ImportError as e:
    VISUALIZATION_AVAILABLE = False
    logger.warning(f"⚠️ Motor de visualización no disponible: {e}")

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
            "https://couples-mario-repository-alive.trycloudflare.com"
        )
        
        # Inicializar componentes
        self.groq_integration = None
        self.jetson_connector = None
        self.graph = None
        self.memory = MemorySaver()
        
        # Motor de visualización (inicialización con fallback)
        self.visualization_engine = None
        try:
            from modules.utils.visualization_engine import IoTVisualizationEngine
            self.visualization_engine = IoTVisualizationEngine()
            logger.info("✅ Motor de visualización inicializado")
        except ImportError as e:
            logger.warning(f"Motor de visualización no disponible: {e}")
        except Exception as e:
            logger.error(f"Error inicializando motor de visualización: {e}")
        
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
            
            # Detectar tipos de consultas específicas
            user_query = state.get("user_query", "").lower()
            request_specific_count = False
            request_per_device = False
            request_by_time = False
            requested_count = 10  # Default
            time_value = 0
            time_unit = ""
            
            # Buscar números específicos en la consulta
            import re
            from datetime import datetime, timedelta
            
            numbers = re.findall(r'\d+', user_query)
            
            # DETECCIÓN DE CONSULTAS POR TIEMPO
            time_keywords = ["minuto", "minutos", "hora", "horas", "min", "hrs"]
            if numbers and ("últimos" in user_query or "ultimos" in user_query):
                # Verificar si es consulta por tiempo
                for keyword in time_keywords:
                    if keyword in user_query:
                        request_by_time = True
                        time_value = int(numbers[0])
                        time_unit = keyword
                        logger.info(f"   ⏰ Consulta por TIEMPO detectada: últimos {time_value} {time_unit}")
                        break
                
                # Si no es por tiempo, es por cantidad de registros
                if not request_by_time:
                    request_specific_count = True
                    requested_count = min(int(numbers[0]), 50)  # Máximo 50 para cloud
                    
                    # Detectar si pide registros POR DISPOSITIVO
                    if "cada dispositivo" in user_query or "por dispositivo" in user_query:
                        request_per_device = True
                        logger.info(f"   📋 Consulta específica detectada: últimos {requested_count} registros POR DISPOSITIVO")
                    else:
                        logger.info(f"   📋 Consulta específica detectada: últimos {requested_count} registros TOTAL")
            
            # Procesar datos según el tipo de consulta
            if request_by_time:
                # CONSULTAS POR TIEMPO - Filtrar por ventana temporal
                from datetime import datetime, timedelta
                import dateutil.parser
                
                # Calcular tiempo límite
                now = datetime.now()
                if time_unit in ["minuto", "minutos", "min"]:
                    time_limit = now - timedelta(minutes=time_value)
                elif time_unit in ["hora", "horas", "hrs"]:
                    time_limit = now - timedelta(hours=time_value)
                else:
                    time_limit = now - timedelta(minutes=time_value)  # Default a minutos
                
                logger.info(f"   ⏰ Filtrando datos desde: {time_limit.strftime('%H:%M:%S')}")
                
                # Filtrar datos por tiempo para TODOS los dispositivos
                processed_data = []
                devices_found = set(record.get("device_id") for record in raw_data)
                total_in_timeframe = 0
                
                for device_id in devices_found:
                    device_records = [r for r in raw_data if r.get("device_id") == device_id]
                    device_time_filtered = []
                    
                    for record in device_records:
                        try:
                            # Parsear timestamp del registro
                            timestamp_str = record.get("timestamp", "")
                            if timestamp_str:
                                # Intentar parsear diferentes formatos de timestamp
                                try:
                                    record_time = dateutil.parser.parse(timestamp_str)
                                    # Convertir a naive datetime si tiene timezone info
                                    if record_time.tzinfo is not None:
                                        record_time = record_time.replace(tzinfo=None)
                                except:
                                    # Fallback: asumir formato ISO básico
                                    record_time = datetime.fromisoformat(timestamp_str.replace('Z', '').split('+')[0].split('-03:00')[0])
                                
                                # Verificar si está en el rango de tiempo
                                if record_time >= time_limit:
                                    device_time_filtered.append(record)
                        except Exception as e:
                            logger.warning(f"   ⚠️ Error parseando timestamp {timestamp_str}: {e}")
                            # Si no se puede parsear, incluir el registro (mejor incluir que excluir)
                            device_time_filtered.append(record)
                    
                    processed_data.extend(device_time_filtered)
                    total_in_timeframe += len(device_time_filtered)
                    logger.info(f"   📱 {device_id}: {len(device_time_filtered)} registros en últimos {time_value} {time_unit}")
                
                logger.info(f"   📊 Procesando {len(processed_data)} registros por TIEMPO ({len(devices_found)} dispositivos)")
                
            elif request_specific_count and request_per_device:
                # Para consultas de "X registros por dispositivo", distribuir equitativamente
                processed_data = []
                devices_found = set(record.get("device_id") for record in raw_data)
                
                for device_id in devices_found:
                    device_records = [r for r in raw_data if r.get("device_id") == device_id]
                    device_limited = device_records[:requested_count]
                    processed_data.extend(device_limited)
                    logger.info(f"   📱 {device_id}: {len(device_limited)} registros incluidos")
                
                logger.info(f"   📊 Procesando {len(processed_data)} registros específicos ({len(devices_found)} dispositivos)")
            elif request_specific_count:
                # Para consultas específicas totales, tomar exactamente la cantidad solicitada
                processed_data = raw_data[:requested_count]
                logger.info(f"   📊 Procesando {len(processed_data)} registros específicos TOTAL")
            else:
                # Para análisis general, limitar a 50 registros para cloud
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
            is_direct_query = any(keyword in state["user_query"].lower() for keyword in 
                                  ["últimos", "ultimos", "listar", "mostrar", "dame", "dime"])
            
            # Información adicional para el formateo
            query_info = {
                "is_time_query": request_by_time,
                "time_value": time_value if request_by_time else None,
                "time_unit": time_unit if request_by_time else None,
                "is_per_device": request_per_device,
                "is_count_query": request_specific_count
            }
            
            formatted_data = self._format_data_for_model(processed_data, analysis, is_direct_query, query_info)
            
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
            
            # 1. Verificar límites de uso antes de hacer la consulta
            can_make_request, usage_message = usage_tracker.check_can_make_request(self.groq_model)
            
            if not can_make_request:
                logger.warning(f"⚠️ Límite de uso alcanzado: {usage_message}")
                state["final_response"] = f"""
🚨 **LÍMITE DE USO DIARIO ALCANZADO**

{usage_message}

📊 **Información del límite**:
- Los límites se resetean automáticamente cada día
- Modelo actual: {self.groq_model}

🔄 **Alternativas**:
- Esperar al reseteo diario (medianoche UTC)
- Continuar mañana cuando se renueven los límites
- Contactar al administrador si necesitas más consultas

💡 **Información**: Este sistema de control nos ayuda a mantener el servicio gratuito y disponible para todos los usuarios.
"""
                state["execution_status"] = "usage_limit_reached"
                state["usage_info"] = usage_tracker.get_usage_info(self.groq_model)
                return state
            
            # Mostrar información de uso actual si hay advertencia
            if "warning" in usage_message.lower() or "crítico" in usage_message.lower():
                logger.info(f"📊 {usage_message}")
            
            user_query = state["user_query"]
            formatted_data = state.get("formatted_data", "")
            
            # DETECTAR TIPO DE CONSULTA PARA RESPUESTA APROPIADA
            query_lower = user_query.lower()
            
            # Palabras clave para consultas DIRECTAS/ESPECÍFICAS
            direct_keywords = [
                "últimos", "ultimos", "listar", "mostrar", "dame", "dime",
                "cuáles son", "cuales son", "qué datos", "que datos",
                "registros de", "valores de", "lecturas de", "datos de"
            ]
            
            # Palabras clave para consultas ANALÍTICAS
            analytical_keywords = [
                "analiza", "analizar", "tendencia", "patrón", "patron",
                "interpreta", "evalúa", "evalua", "reporte", "informe",
                "comportamiento", "variabilidad", "estabilidad"
            ]
            
            is_direct_query = any(keyword in query_lower for keyword in direct_keywords)
            is_analytical_query = any(keyword in query_lower for keyword in analytical_keywords)
            
            # Crear prompt adaptativo basado en el tipo de consulta
            if is_direct_query and not is_analytical_query:
                # CONSULTA DIRECTA - Respuesta específica y concisa
                prompt = f"""
                CONSULTA DIRECTA DEL USUARIO: {user_query}
                
                INSTRUCCIONES ESPECÍFICAS:
                - El usuario hace una consulta DIRECTA y ESPECÍFICA
                - RESPONDE EXACTAMENTE lo que pide, sin análisis extenso
                - USA formato de LISTA cuando sea apropiado
                - SÉ CONCISO pero completo
                - NO uses secciones de análisis técnico extenso
                
                DATOS DISPONIBLES:
                {formatted_data}
                
                EJEMPLOS DE RESPUESTA APROPIADA:
                - Si pide "últimos 10 registros": Lista exactamente 10 registros
                - Si pide "temperatura actual": Muestra valores actuales de temperatura
                - Si pide "qué sensores hay": Lista los sensores disponibles
                
                RESPONDE DIRECTAMENTE lo solicitado:
                """
            else:
                # CONSULTA ANALÍTICA - Análisis completo con secciones técnicas
                prompt = f"""
                Eres un asistente experto en análisis de datos de sensores IoT.
                
                CONFIGURACIÓN REAL DE DISPOSITIVOS (IMPORTANTE - SEGUIR EXACTAMENTE):
                
                🔧 ARDUINO ETHERNET (arduino_eth_001):
                - IP: 192.168.0.106
                - SENSORES DISPONIBLES: t1, t2, avg (SOLO temperaturas)
                - NO TIENE: LDR, sensor de luz, luminosidad, fotoresistor
                
                📡 ESP32 WIFI (esp32_wifi_001):
                - IP: 192.168.0.105  
                - SENSORES DISPONIBLES: ntc_entrada, ntc_salida (temperaturas) + ldr (sensor de luz)
                - SÍ TIENE: Sensores de temperatura Y sensor LDR para luminosidad
                
                CONSULTA DEL USUARIO: {user_query}
                
                DATOS REALES DE SENSORES:
                {formatted_data}
                
                REGLAS DE ANÁLISIS (CUMPLIR ESTRICTAMENTE):
                1. ✅ INCLUIR datos de LDR SOLO si se refiere a ESP32 WiFi
                2. ❌ NUNCA mencionar LDR para Arduino Ethernet (no existe)
                3. ✅ Arduino Ethernet SOLO tiene temperaturas (t1, t2, avg)
                4. ✅ ESP32 WiFi tiene temperaturas (ntc_entrada, ntc_salida) Y ldr
                5. 📊 Analiza TODOS los sensores disponibles del dispositivo consultado
                6. 🚫 NO inventes sensores que no existen en la configuración
                7. 📍 Especifica claramente qué dispositivo tiene qué sensores
                
                EJEMPLO DE RESPUESTA CORRECTA:
                - "El ESP32 WiFi muestra temperaturas de 25°C y 26°C en ntc_entrada y ntc_salida, además de 450 unidades en el sensor LDR"
                - "El Arduino Ethernet registra 24°C en t1, 25°C en t2, con promedio de 24.5°C (no tiene sensor LDR)"
                
                Analiza los datos reales disponibles siguiendo estas reglas exactas.
                """
            
            # 2. EVALUAR NECESIDAD DE VISUALIZACIÓN
            chart_paths = []
            visualization_info = ""
            
            if self.visualization_engine and formatted_data:
                try:
                    # Analizar si se necesitan gráficos
                    should_generate = self.visualization_engine.should_generate_charts(
                        user_query, 
                        formatted_data
                    )
                    
                    if should_generate:
                        logger.info("📊 Generando visualizaciones para consulta avanzada...")
                        
                        # Usar raw_data en lugar de formatted_data para los gráficos
                        raw_data = state.get("raw_data", [])
                        
                        if raw_data:
                            # Generar gráficos apropiados
                            chart_paths = self.visualization_engine.generate_charts(
                                raw_data,
                                user_query
                            )
                            
                            if chart_paths:
                                chart_names = [path.split('\\')[-1] for path in chart_paths]
                                visualization_info = f"""

📊 **GRÁFICOS GENERADOS**: {', '.join(chart_names)}
                                
Los gráficos han sido guardados y están disponibles para análisis visual de los datos.
"""
                                logger.info(f"✅ Generados {len(chart_paths)} gráficos: {chart_names}")
                        else:
                            logger.warning("No hay datos raw disponibles para generar gráficos")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error generando visualizaciones: {e}")
            
            # 3. Generar respuesta con Groq
            response = self.groq_integration.generate_response(prompt, model=self.groq_model)
            
            # 4. Integrar información de visualización con la respuesta
            final_response = response + visualization_info
            
            # 5. Registrar uso de la consulta (estimar tokens basado en longitud)
            estimated_tokens = len(prompt) // 4 + len(response) // 4  # Estimación aproximada
            usage_info = usage_tracker.track_request(self.groq_model, estimated_tokens)
            
            # 6. Agregar información de uso a la respuesta si está cerca del límite
            usage_footer = ""
            if usage_info["status"] in ["warning", "critical"]:
                remaining_percentage = 100 - usage_info["requests_percentage"]
                usage_footer = f"""

---
📊 **Uso de API**: {usage_info['requests_used']}/{usage_info['requests_limit']} consultas ({remaining_percentage:.1f}% disponible)
"""
            
            state["final_response"] = final_response + usage_footer
            state["execution_status"] = "response_generated"
            state["usage_info"] = usage_info
            state["chart_paths"] = chart_paths  # Incluir rutas de gráficos en el estado
            
            logger.info(f"   ✅ Respuesta generada con Groq - Uso: {usage_info['requests_used']}/{usage_info['requests_limit']}")
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
                "chart_paths": result.get("chart_paths", []),
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
    
    def _format_data_for_model(self, data: List[Dict], analysis: Dict, is_direct_query: bool = False, query_info: Dict = None) -> str:
        """
        Formatear datos para el modelo con configuración específica de dispositivos.
        
        Args:
            data: Datos de sensores
            analysis: Análisis de datos
            is_direct_query: Si es una consulta directa que requiere lista de datos
            query_info: Información adicional sobre el tipo de consulta
            
        Returns:
            Datos formateados como string con configuración detallada
        """
        if query_info is None:
            query_info = {}
        if is_direct_query:
            # FORMATO DIRECTO - Para consultas específicas como "últimos 10 registros" o "últimos X minutos"
            
            # Título adaptativo según el tipo de consulta
            if query_info.get("is_time_query", False):
                time_value = query_info.get("time_value", "X")
                time_unit = query_info.get("time_unit", "tiempo")
                formatted = f"=== REGISTROS DE LOS ÚLTIMOS {time_value} {time_unit.upper()} ===\n"
            elif query_info.get("is_count_query", False):
                formatted = f"=== LISTA DE REGISTROS SOLICITADOS ===\n"
            else:
                formatted = f"=== REGISTROS DE SENSORES ===\n"
            
            formatted += f"Total encontrado: {len(data)} registros\n\n"
            
            # Agrupar por dispositivo para mejor legibilidad
            by_device = {}
            for record in data:
                device_id = record.get("device_id", "unknown")
                if device_id not in by_device:
                    by_device[device_id] = []
                by_device[device_id].append(record)
            
            # Siempre mostrar agrupado por dispositivo para consultas de tiempo
            if len(by_device) > 1 or query_info.get("is_time_query", False):
                for device_id, device_records in by_device.items():
                    formatted += f"📱 DISPOSITIVO: {device_id} ({len(device_records)} registros)\n"
                    
                    for i, record in enumerate(device_records[:15], 1):  # Máximo 15 por dispositivo
                        sensor_type = record.get("sensor_type", "unknown")
                        value = record.get("value", "N/A")
                        timestamp = record.get("timestamp", "unknown")
                        unit = record.get("unit", "")
                        
                        # Determinar unidad apropiada
                        if not unit:
                            if sensor_type in ['t1', 't2', 'avg', 'temperature_1', 'temperature_2', 'temperature_avg', 'ntc_entrada', 'ntc_salida']:
                                unit = "°C"
                            elif sensor_type == 'ldr':
                                unit = " (unidades de luz)"
                        
                        formatted += f"   {i}. {sensor_type}: {value}{unit} ({timestamp})\n"
                    
                    if len(device_records) > 15:
                        formatted += f"   ... y {len(device_records) - 15} registros más de este dispositivo.\n"
                    formatted += "\n"
            else:
                # Un solo dispositivo, formato simple
                for i, record in enumerate(data[:20], 1):  # Máximo 20 para no saturar
                    device_id = record.get("device_id", "unknown")
                    sensor_type = record.get("sensor_type", "unknown")
                    value = record.get("value", "N/A")
                    timestamp = record.get("timestamp", "unknown")
                    unit = record.get("unit", "")
                    
                    # Determinar unidad apropiada
                    if not unit:
                        if sensor_type in ['t1', 't2', 'avg', 'temperature_1', 'temperature_2', 'temperature_avg', 'ntc_entrada', 'ntc_salida']:
                            unit = "°C"
                        elif sensor_type == 'ldr':
                            unit = " (unidades de luz)"
                    
                    formatted += f"{i}. {device_id} - {sensor_type}: {value}{unit} ({timestamp})\n"
                
                if len(data) > 20:
                    formatted += f"\n... y {len(data) - 20} registros más disponibles.\n"
            
            return formatted
        
        else:
            # FORMATO ANALÍTICO - Para análisis completo
            formatted = f"=== CONFIGURACIÓN REAL DE DISPOSITIVOS ===\n"
            
            # Configuración específica para evitar alucinaciones
            formatted += "🔧 ARDUINO ETHERNET (arduino_eth_001):\n"
            formatted += "   - IP: 192.168.0.106\n"
            formatted += "   - SENSORES: SOLO t1, t2, avg (temperaturas únicamente)\n"
            formatted += "   - NO TIENE: LDR, sensor de luz, luminosidad\n\n"
            
            formatted += "📡 ESP32 WIFI (esp32_wifi_001):\n"
            formatted += "   - IP: 192.168.0.105\n"
            formatted += "   - SENSORES: ntc_entrada, ntc_salida (temperaturas) + ldr (luz)\n\n"
            
            formatted += f"=== DATOS ACTUALES ===\n"
            formatted += f"Total de registros: {analysis['total_records']}\n"
            formatted += f"Dispositivos activos: {', '.join(analysis['devices'])}\n"
            formatted += f"Sensores disponibles: {', '.join(analysis['sensors'])}\n\n"
            
            # Últimas lecturas organizadas por dispositivo
            formatted += "ÚLTIMAS LECTURAS POR DISPOSITIVO:\n"
            latest_readings = analysis.get("latest_readings", {})
            
            # Agrupar por dispositivo
            by_device = {}
            for sensor, reading in latest_readings.items():
                device = reading['device']
                if device not in by_device:
                    by_device[device] = []
                by_device[device].append((sensor, reading))
            
            for device, sensors in by_device.items():
                formatted += f"\n{device}:\n"
                for sensor, reading in sensors:
                    unit = "°C" if sensor in ['t1', 't2', 'avg', 'ntc_entrada', 'ntc_salida'] else ""
                    formatted += f"   • {sensor}: {reading['value']}{unit}\n"
            
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
        Verificar estado de salud del agente cloud incluyendo uso de API.
        
        Returns:
            Dict con estado de salud y uso de API
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
                
                # Agregar información de uso de API
                usage_info = usage_tracker.get_usage_info(self.groq_model)
                health["api_usage"] = {
                    "model": self.groq_model,
                    "model_description": usage_info.get("model_description", "Desconocido"),
                    "requests_used": usage_info.get("requests_used", 0),
                    "requests_limit": usage_info.get("requests_limit", 0),
                    "requests_remaining": usage_info.get("requests_remaining", 0),
                    "tokens_used": usage_info.get("tokens_used", 0),
                    "tokens_limit": usage_info.get("tokens_limit", 0),
                    "tokens_remaining": usage_info.get("tokens_remaining", 0),
                    "usage_percentage": usage_info.get("requests_percentage", 0),
                    "status": usage_info.get("status", "unknown"),
                    "can_make_request": usage_info.get("can_make_request", True),
                    "daily_reset_date": usage_info.get("date", "unknown")
                }
            
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
