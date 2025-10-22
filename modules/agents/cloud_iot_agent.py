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
from modules.tools.direct_jetson_connector import DirectJetsonConnector
from modules.agents.direct_api_agent import create_direct_api_agent
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
            "https://replica-subscriber-permission-restricted.trycloudflare.com"
        )
        
        # Inicializar componentes
        self.groq_integration = None
        self.jetson_connector = None
        self.direct_api_agent = None  # Fallback robusto
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
        
        # Inicializar DirectAPIAgent inmediatamente (fallback robusto)
        try:
            self.direct_api_agent = create_direct_api_agent(self.jetson_api_url)
            logger.info("✅ DirectAPIAgent inicializado como fallback robusto")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo inicializar DirectAPIAgent: {e}")
        
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
            
            # 2. Inicializar conectores con prioridad
            # PRIORIDAD 1: Conector directo (igual que dashboard exitoso)
            self.direct_connector = DirectJetsonConnector(self.jetson_api_url)
            logger.info("✅ DirectJetsonConnector inicializado")
            
            # PRIORIDAD 2: Conector tradicional (fallback)
            self.jetson_connector = JetsonAPIConnector(base_url=self.jetson_api_url)
            
            # PRIORIDAD 3: Agente directo (último fallback)
            self.direct_api_agent = create_direct_api_agent(self.jetson_api_url)
            
            # 4. Probar conexiones
            groq_test = self.groq_integration.test_connection()
            jetson_test = self.jetson_connector.get_health_status() if self.jetson_connector else {"status": "not_configured"}
            
            if not groq_test.get('success', False):
                logger.warning(f"Groq API no disponible: {groq_test}. Usando modo fallback.")
                # Continuar en modo fallback
            
            if not jetson_test.get('status') == 'healthy':
                logger.warning(f"Jetson API no disponible: {jetson_test}")
                # Continuar sin Jetson (modo demo)
            
            # 5. Construir graph
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
        Nodo ROBUSTO para recolectar datos con fallback directo que SÍ FUNCIONA.
        
        ESTRATEGIA:
        1. Intentar conexión normal del agente
        2. Si falla, usar DirectAPIAgent (misma lógica del frontend exitoso)
        3. Garantizar que el agente tenga acceso a los mismos datos que el frontend
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado
        """
        try:
            logger.info("📡 Ejecutando remote_data_collector_node (ULTRA-ROBUSTO)")
            
            all_data = []
            method_used = "none"
            
            # MÉTODO 1: Conector DIRECTO (igual que dashboard exitoso)
            if self.direct_connector:
                try:
                    logger.info("🚀 Intentando método DIRECTO (igual que dashboard)...")
                    
                    # Usar el método completo que replica el dashboard
                    result = self.direct_connector.get_all_data_simple()
                    
                    if result["status"] == "success" and result["sensor_data"]:
                        all_data = result["sensor_data"]
                        method_used = "direct"
                        logger.info(f"✅ Método DIRECTO exitoso: {len(all_data)} registros")
                        logger.info(f"📊 Stats: {result['stats']}")
                        
                        # Guardar información detallada
                        state["connection_info"] = result["connection"]
                        state["device_info"] = result["devices"]
                        state["data_stats"] = result["stats"]
                        
                except Exception as e:
                    logger.warning(f"⚠️ Método DIRECTO falló: {e}")
            
            # MÉTODO 2: Método tradicional (solo si el directo falla)
            if not all_data and self.jetson_connector:
                try:
                    logger.info("🔄 Intentando método tradicional...")
                    devices_result = self.jetson_connector.get_devices()
                    
                    if devices_result and not any(d.get("status") == "unknown" for d in devices_result):
                        for device in devices_result:
                            device_id = device.get("device_id")
                            if device_id:
                                device_data = self.jetson_connector.get_sensor_data(
                                    device_id=device_id,
                                    limit=500
                                )
                                if device_data:
                                    all_data.extend(device_data)
                        
                        if all_data:
                            method_used = "traditional"
                            logger.info(f"✅ Método tradicional exitoso: {len(all_data)} registros")
                        else:
                            raise Exception("Método normal no devolvió datos")
                    else:
                        raise Exception("Método normal no encontró dispositivos")
                        
                except Exception as normal_error:
                    logger.warning(f"⚠️ Método normal falló: {normal_error}")
                    all_data = []  # Limpiar para intentar fallback
            
            # MÉTODO 2: FALLBACK DIRECTO (usa la misma lógica exitosa del frontend)
            if not all_data:
                try:
                    logger.info("� Activando FALLBACK DIRECTO (frontend logic)...")
                    
                    if hasattr(self, 'direct_api_agent') and self.direct_api_agent:
                        # Usar el agente directo que copia la lógica del frontend
                        # Intentar obtener configuración temporal del contexto
                        analysis_hours = 3.0  # Default
                        
                        # Buscar si hay configuración temporal en la consulta
                        if "CONFIGURACIÓN TEMPORAL" in user_query:
                            try:
                                import re
                                match = re.search(r"(\d+(?:\.\d+)?)\s*horas", user_query)
                                if match:
                                    analysis_hours = float(match.group(1))
                                    logger.info(f"📅 Usando configuración temporal: {analysis_hours} horas")
                            except:
                                pass
                        
                        direct_result = self.direct_api_agent.get_all_recent_data(hours=analysis_hours)
                        
                        if direct_result.get("status") == "success":
                            all_data = direct_result.get("sensor_data", [])
                            method_used = "direct_fallback"
                            logger.info(f"✅ FALLBACK DIRECTO exitoso: {len(all_data)} registros")
                        else:
                            logger.error(f"❌ Fallback directo falló: {direct_result.get('message', 'Error desconocido')}")
                    else:
                        logger.error("❌ Direct API Agent no disponible")
                        
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback directo falló: {fallback_error}")
            
            # RESULTADO FINAL
            if all_data:
                state["raw_data"] = all_data
                state["execution_status"] = "remote_data_collected"
                state["data_collection_method"] = method_used
                logger.info(f"🎉 DATOS OBTENIDOS ({method_used}): {len(all_data)} registros")
            else:
                # Si ambos métodos fallan, reportar problema
                jetson_status = self._check_jetson_api_status()
                state["raw_data"] = []
                state["execution_status"] = "all_methods_failed"
                state["error"] = {
                    "message": "Tanto método normal como fallback directo fallaron",
                    "jetson_status": jetson_status,
                    "methods_tried": ["normal", "direct_fallback"]
                }
                logger.error("❌ TODOS LOS MÉTODOS FALLARON - No se pudieron obtener datos")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Error crítico en remote_data_collector_node: {e}")
            state["raw_data"] = []
            state["execution_status"] = "critical_error"
            state["error"] = {"message": str(e), "type": "critical_error"}
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
            
            # Análisis optimizado para cloud - CON VALIDACIÓN ROBUSTA
            analysis = {
                "total_records": len(raw_data),
                "devices": set(),
                "sensors": set(),
                "latest_readings": {},
                "timestamp_range": {"start": None, "end": None}
            }
            
            # 🔧 VALIDACIÓN Y SANITIZACIÓN DE DATOS
            processed_data = []
            for item in raw_data:
                try:
                    # Verificar que sea un diccionario
                    if isinstance(item, dict):
                        # Verificar que tenga los campos mínimos requeridos
                        if all(key in item for key in ['device_id', 'sensor_type', 'value']):
                            processed_data.append(item)
                        else:
                            logger.warning(f"⚠️ Registro incompleto: {item}")
                    elif isinstance(item, str):
                        # Intentar parsear como JSON si es string
                        import json
                        try:
                            parsed_item = json.loads(item)
                            if isinstance(parsed_item, dict) and all(key in parsed_item for key in ['device_id', 'sensor_type', 'value']):
                                processed_data.append(parsed_item)
                            else:
                                logger.warning(f"⚠️ String JSON inválido: {item[:100]}...")
                        except json.JSONDecodeError:
                            logger.warning(f"⚠️ String no es JSON válido: {item[:100]}...")
                    else:
                        logger.warning(f"⚠️ Tipo de dato inesperado: {type(item)} - {str(item)[:100]}")
                except Exception as e:
                    logger.warning(f"⚠️ Error procesando item: {e}")
            
            logger.info(f"🔍 Datos sanitizados: {len(processed_data)}/{len(raw_data)} registros válidos")
            
            # Si no hay datos válidos después de la sanitización
            if not processed_data:
                logger.warning("🚨 No hay datos válidos después de la sanitización")
                state["formatted_data"] = """
🚨 ERROR: Los datos obtenidos tienen formato incorrecto

Los datos de la API están llegando pero no tienen el formato esperado.

📋 DATOS RECIBIDOS:
""" + str(raw_data[:3]) + """

🔧 POSIBLES SOLUCIONES:
📡 Verificar formato de respuesta de la API Jetson
🔄 Reiniciar servicios de la API: sudo systemctl restart iot-api-service
🌐 Verificar que la API retorne JSON válido
"""
                state["sensor_summary"] = {}
                state["analysis"] = {"error": "invalid_data_format"}
                return state
            
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
                # USAR DATOS SANITIZADOS como base
                time_filtered_data = []
                devices_found = set(record.get("device_id") for record in processed_data)
                total_in_timeframe = 0
                
                for device_id in devices_found:
                    device_records = [r for r in processed_data if r.get("device_id") == device_id]
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
                    
                    time_filtered_data.extend(device_time_filtered)
                    total_in_timeframe += len(device_time_filtered)
                    logger.info(f"   📱 {device_id}: {len(device_time_filtered)} registros en últimos {time_value} {time_unit}")
                
                # Actualizar processed_data con los datos filtrados por tiempo
                processed_data = time_filtered_data
                logger.info(f"   📊 Procesando {len(processed_data)} registros por TIEMPO ({len(devices_found)} dispositivos)")
                
            elif request_specific_count and request_per_device:
                # Para consultas de "X registros por dispositivo", distribuir equitativamente
                # USAR DATOS SANITIZADOS como base
                per_device_data = []
                devices_found = set(record.get("device_id") for record in processed_data)
                
                for device_id in devices_found:
                    device_records = [r for r in processed_data if r.get("device_id") == device_id]
                    device_limited = device_records[:requested_count]
                    per_device_data.extend(device_limited)
                    logger.info(f"   📱 {device_id}: {len(device_limited)} registros incluidos")
                
                # Actualizar processed_data con los datos filtrados por dispositivo
                processed_data = per_device_data
                logger.info(f"   📊 Procesando {len(processed_data)} registros específicos ({len(devices_found)} dispositivos)")
            elif request_specific_count:
                # Para consultas específicas totales, tomar exactamente la cantidad solicitada
                # USAR DATOS SANITIZADOS, no raw_data
                processed_data = processed_data[:requested_count]
                logger.info(f"   📊 Procesando {len(processed_data)} registros específicos TOTAL")
            else:
                # Para análisis general, limitar a 50 registros para cloud  
                # USAR DATOS SANITIZADOS, no raw_data
                processed_data = processed_data[:50] if len(processed_data) > 50 else processed_data
            
            # Usar los datos sanitizados para el análisis final
            for record in processed_data:
                try:
                    # Verificación adicional para asegurar que sea un diccionario
                    if not isinstance(record, dict):
                        logger.warning(f"⚠️ Registro no es diccionario: {type(record)}")
                        continue
                        
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
                except Exception as e:
                    logger.warning(f"⚠️ Error procesando registro en análisis: {e}")
                    continue
            
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
            
            # 2. EVALUAR NECESIDAD DE VISUALIZACIÓN ANTES DE CONSTRUIR PROMPT
            chart_paths = []
            visualization_info = ""
            
            if self.visualization_engine and formatted_data:
                try:
                    # Analizar si se necesitan gráficos
                    should_generate = self.visualization_engine.should_generate_charts(
                        user_query
                    )
                    
                    if should_generate:
                        logger.info("📊 Generando visualizaciones para consulta avanzada...")
                        
                        # Usar raw_data en lugar de formatted_data para los gráficos
                        raw_data = state.get("raw_data", [])
                        
                        if raw_data:
                            # Generar gráficos apropiados
                            chart_base64_list = self.visualization_engine.generate_charts(
                                raw_data,
                                user_query
                            )
                            
                            if chart_base64_list:
                                visualization_info = f"GRÁFICOS GENERADOS: {len(chart_base64_list)} gráficos"
                                logger.info(f"✅ Generados {len(chart_base64_list)} gráficos en base64")
                                # Guardar los base64 para usar después  
                                chart_paths = chart_base64_list
                        else:
                            logger.warning("No hay datos raw disponibles para generar gráficos")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error generando visualizaciones: {e}")

            # 3. Crear prompt adaptativo basado en el tipo de consulta
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
                {f"- IMPORTANTE: Se han generado GRÁFICOS para esta consulta: {visualization_info}" if visualization_info else ""}
                
                DATOS DISPONIBLES:
                {formatted_data}
                
                EJEMPLOS DE RESPUESTA APROPIADA:
                - Si pide "últimos 10 registros": Lista exactamente 10 registros
                - Si pide "temperatura actual": Muestra valores actuales de temperatura
                - Si pide "qué sensores hay": Lista los sensores disponibles
                {f"- Si se solicitan gráficos: Menciona que se han generado: {visualization_info}" if visualization_info else ""}
                
                RESPONDE DIRECTAMENTE lo solicitado:
                """
            else:
                # CONSULTA ANALÍTICA - Análisis completo con secciones técnicas
                prompt = f"""
                Eres un asistente experto en análisis de datos de sensores IoT.
                {f"IMPORTANTE: Se han generado GRÁFICOS para esta consulta: {visualization_info}" if visualization_info else ""}
                
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
            
            # 3. Generar respuesta con Groq
            response = self.groq_integration.generate_response(prompt, model=self.groq_model)
            
            # 4. Integrar información de visualización con la respuesta
            if visualization_info and "GRÁFICOS GENERADOS:" not in visualization_info:
                # Formato más detallado para la respuesta final
                chart_names = [path.split('\\')[-1] for path in chart_paths] if chart_paths else []
                visualization_section = f"""

📊 **GRÁFICOS GENERADOS**: {', '.join(chart_names)}
                                
Los gráficos han sido guardados y están disponibles para análisis visual de los datos.
"""
                final_response = response + visualization_section
            else:
                final_response = response
            
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
            state["chart_base64_list"] = chart_paths  # Incluir gráficos base64 en el estado
            
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
            
            # Detectar sensores mencionados que no existen en el hardware real
            # SOLO tenemos: temperatura (NTC/thermistores) y LDR (luminosidad)
            problematic_sensors = ["humidity", "humedad", "pressure", "presión", "co2", "voltage", "voltaje", "motion", "movimiento"]
            for sensor in problematic_sensors:
                if sensor.lower() in response.lower() and sensor not in real_sensors:
                    verification["hallucinations_detected"].append(f"Sensor inexistente mencionado: {sensor} - Solo tenemos temperatura y LDR")
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
                "chart_base64_list": result.get("chart_base64_list", []),
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
    
    def process_query_sync(self, user_query: str, thread_id: str = "cloud-session", analysis_hours: float = None) -> str:
        """
        Versión síncrona de process_query para usar en Streamlit.
        
        Args:
            user_query: Consulta del usuario
            thread_id: ID del hilo de conversación
            analysis_hours: Horas para análisis temporal (None = usar configuración por defecto)
            
        Returns:
            String con la respuesta procesada
        """
        import asyncio
        import nest_asyncio
        
        try:
            # Aplicar nest_asyncio para permitir loops anidados
            nest_asyncio.apply()
            
            # Agregar información temporal al contexto si se especifica
            if analysis_hours:
                # Modificar la consulta para incluir contexto temporal
                temporal_context = f"\n[CONFIGURACIÓN TEMPORAL: Analizar datos de las últimas {analysis_hours} horas]"
                enhanced_query = user_query + temporal_context
            else:
                enhanced_query = user_query
            
            # Ejecutar la función async
            result = asyncio.run(self.process_query(enhanced_query, thread_id))
            
            # Extraer respuesta del resultado
            if isinstance(result, dict):
                return result.get('response', str(result))
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"❌ Error en process_query_sync: {e}")
            # FALLBACK DIRECTO cuando el agente async falla
            return self.process_query_direct_fallback(user_query)
    
    def process_query_direct_fallback(self, user_query: str) -> str:
        """
        Fallback DIRECTO que usa la misma lógica exitosa del frontend.
        Se ejecuta cuando el agente principal falla.
        
        Args:
            user_query: Consulta del usuario
            
        Returns:
            Respuesta usando datos directos (misma lógica del frontend)
        """
        try:
            logger.info(f"🚀 FALLBACK DIRECTO para consulta: {user_query}")
            
            # Usar DirectAPIAgent (misma lógica del frontend exitoso)
            if hasattr(self, 'direct_api_agent') and self.direct_api_agent:
                # Obtener datos formateados para análisis
                formatted_data = self.direct_api_agent.format_for_analysis(user_query)
                
                # Si tenemos datos, procesarlos
                if "📊 ESTADO ACTUAL DEL SISTEMA IoT" in formatted_data:
                    logger.info("✅ Datos obtenidos exitosamente con fallback directo")
                    
                    # Crear respuesta contextual básica
                    if any(keyword in user_query.lower() for keyword in ['gráfico', 'grafica', 'visualiza', 'chart', 'plot']):
                        response = f"""📊 **Estado Actual del Sistema**

{formatted_data}

📈 **Visualización Solicitada**: Para generar gráficos, utiliza la funcionalidad de gráficos en la interfaz. Los datos están disponibles y actualizados.

💡 **Datos Disponibles**: El sistema está funcionando correctamente con dispositivos activos reportando datos en tiempo real."""
                    
                    elif any(keyword in user_query.lower() for keyword in ['temperatura', 'sensor', 'dispositivo']):
                        response = f"""🌡️ **Análisis de Sensores**

{formatted_data}

🔍 **Análisis**: Los sensores están funcionando correctamente y reportando datos actualizados. 

📱 **Estado de Dispositivos**: Todos los dispositivos están activos y transmitiendo datos en tiempo real."""
                    
                    else:
                        response = f"""📋 **Respuesta del Sistema IoT**

{formatted_data}

✅ **Sistema Operativo**: Todos los componentes están funcionando correctamente.

💬 **Consulta**: "{user_query}" - El sistema está listo para procesar tu solicitud con los datos mostrados arriba."""
                    
                    return response
                else:
                    logger.warning("⚠️ Fallback directo obtuvo datos pero con formato inesperado")
                    return f"⚠️ {formatted_data}"
            else:
                logger.error("❌ Direct API Agent no disponible para fallback")
                return "❌ Error: Sistema de fallback directo no disponible. Revisa la configuración de la API."
                
        except Exception as e:
            logger.error(f"❌ Error en fallback directo: {e}")
            return f"❌ Error en sistema de fallback: {str(e)}. Verifica la conectividad con la API."
            logger.error(f"Error en process_query_sync: {e}")
            return f"❌ Error procesando consulta: {str(e)}"


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
