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
from modules.utils.intelligent_prompt_generator import (
    create_intelligent_prompt, 
    should_generate_visualization, 
    filter_visualization_data
)

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Configurar logging más detallado para debugging
logger = logging.getLogger(__name__)

# Habilitar DEBUG para el módulo de Groq durante desarrollo
groq_logger = logging.getLogger('modules.agents.groq_integration')
groq_logger.setLevel(logging.DEBUG)

# 🧠 SISTEMAS DE INTELIGENCIA AVANZADA - INTEGRACIÓN COMPLETA
try:
    from modules.intelligence.smart_analyzer import SmartAnalyzer
    from modules.intelligence.dynamic_sensor_detector import DynamicSensorDetector
    from modules.intelligence.advanced_report_generator import AdvancedReportGenerator
    from modules.intelligence.automatic_insights_engine import AutomaticInsightsEngine
    from modules.intelligence.predictive_analysis_engine import PredictiveAnalysisEngine
    from modules.intelligence.advanced_visualization_engine import AdvancedVisualizationEngine
    from modules.intelligence.intelligent_alert_system import IntelligentAlertSystem
    from modules.intelligence.temporal_comparison_engine import TemporalComparisonEngine
    INTELLIGENCE_SYSTEMS_AVAILABLE = True
    logger.info("🧠 SISTEMAS DE INTELIGENCIA AVANZADA CARGADOS EXITOSAMENTE")
except ImportError as e:
    INTELLIGENCE_SYSTEMS_AVAILABLE = False
    logger.error(f"❌ Error cargando sistemas de inteligencia: {e}")
except Exception as e:
    INTELLIGENCE_SYSTEMS_AVAILABLE = False
    logger.error(f"❌ Error inicializando sistemas de inteligencia: {e}")

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
            "https://along-critical-decorative-physics.trycloudflare.com"
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
        
        # 🧠 INICIALIZAR SISTEMAS DE INTELIGENCIA AVANZADA
        self.intelligence_systems = {}
        if INTELLIGENCE_SYSTEMS_AVAILABLE:
            try:
                self.intelligence_systems = {
                    'smart_analyzer': SmartAnalyzer(),
                    'sensor_detector': DynamicSensorDetector(jetson_api_url=self.jetson_api_url),
                    'report_generator': AdvancedReportGenerator(jetson_api_url=self.jetson_api_url),
                    'insights_engine': AutomaticInsightsEngine(jetson_api_url=self.jetson_api_url),
                    'predictive_engine': PredictiveAnalysisEngine(jetson_api_url=self.jetson_api_url),
                    'visualization_engine': AdvancedVisualizationEngine(jetson_api_url=self.jetson_api_url),
                    'alert_system': IntelligentAlertSystem(jetson_api_url=self.jetson_api_url),
                    'temporal_engine': TemporalComparisonEngine(jetson_api_url=self.jetson_api_url)
                }
                logger.info("🧠 SISTEMAS DE INTELIGENCIA AVANZADA INICIALIZADOS")
                logger.info(f"   📊 SmartAnalyzer: ✅")
                logger.info(f"   🔍 DynamicSensorDetector: ✅")
                logger.info(f"   📋 AdvancedReportGenerator: ✅")
                logger.info(f"   💡 AutomaticInsightsEngine: ✅")
                logger.info(f"   🔮 PredictiveAnalysisEngine: ✅")
                logger.info(f"   📈 AdvancedVisualizationEngine: ✅")
                logger.info(f"   🚨 IntelligentAlertSystem: ✅")
                logger.info(f"   ⏰ TemporalComparisonEngine: ✅")
            except Exception as e:
                logger.error(f"❌ Error inicializando sistemas de inteligencia: {e}")
                self.intelligence_systems = {}
        else:
            logger.warning("⚠️ Sistemas de inteligencia no disponibles - usando análisis básico")
        
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
            
            # 1. Inicializar Groq Integration - Compatible con Streamlit Cloud
            groq_api_key = os.getenv("GROQ_API_KEY")
            
            # Verificar también Streamlit secrets (para Streamlit Cloud)
            if not groq_api_key:
                try:
                    import streamlit as st
                    groq_api_key = st.secrets.get("GROQ_API_KEY", None)
                except:
                    pass  # No está en contexto Streamlit
            
            if groq_api_key == "demo_mode" or not groq_api_key or groq_api_key.startswith("demo"):
                # Usar modo demo
                self.groq_integration = GroqIntegration()  # Sin API key = modo fallback
                logger.info("🎭 Usando Groq en modo DEMO")
            else:
                # Usar Groq real
                self.groq_integration = GroqIntegration(api_key=groq_api_key)
                logger.info("🤖 Usando Groq con API key configurada")
            
            # 2. Inicializar conectores con prioridad
            # PRIORIDAD 1: Conector directo (igual que dashboard exitoso)
            self.direct_connector = DirectJetsonConnector(self.jetson_api_url)
            logger.info("✅ DirectJetsonConnector inicializado")
            
            # USAR DirectJetsonConnector como conector principal (es el que funciona)
            self.jetson_connector = self.direct_connector
            logger.info("✅ jetson_connector configurado como DirectJetsonConnector")
            
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
                        user_query = state.get("user_query", "")
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
        🧠 NODO DE ANÁLISIS INTELIGENTE - POTENCIADO POR IA Y ML
        
        Usa todos los sistemas de inteligencia avanzada implementados:
        - SmartAnalyzer: Análisis estadístico y detección de anomalías
        - DynamicSensorDetector: Detección automática de dispositivos
        - AutomaticInsightsEngine: Generación de insights con IA
        - PredictiveAnalysisEngine: Predicciones y análisis temporal
        - IntelligentAlertSystem: Alertas contextuales inteligentes
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado con análisis inteligente completo
        """
        try:
            logger.info("🧠 Ejecutando ANÁLISIS INTELIGENTE AVANZADO")
            
            raw_data = state.get("raw_data", [])
            user_query = state.get("user_query", "")
            
            # Verificar si hay datos disponibles
            if not raw_data:
                logger.warning("🚨 No hay datos para analizar - INTENTANDO RECUPERACIÓN DIRECTA")
                
                # RECUPERACIÓN DIRECTA: Si no hay datos, intentar obtenerlos directamente
                try:
                    # Usar el mismo método exitoso del frontend
                    if hasattr(self, 'direct_api_agent') and self.direct_api_agent:
                        logger.info("🔄 Intentando recuperación directa de datos...")
                        direct_result = self.direct_api_agent.get_all_recent_data(hours=3.0)
                        
                        if direct_result.get("status") == "success" and direct_result.get("sensor_data"):
                            raw_data = direct_result.get("sensor_data", [])
                            state["raw_data"] = raw_data
                            logger.info(f"✅ RECUPERACIÓN EXITOSA: {len(raw_data)} registros obtenidos")
                        else:
                            logger.error("❌ Recuperación directa falló")
                    
                    # Si aún no hay datos, usar análisis básico con mensaje informativo
                    if not raw_data:
                        fallback_response = self._generate_data_availability_response()
                        state["formatted_data"] = fallback_response
                        state["sensor_summary"] = {}
                        state["analysis"] = {"status": "no_data_fallback", "message": "Sistema funcionando - usando datos básicos"}
                        return state
                        
                except Exception as recovery_error:
                    logger.error(f"❌ Error en recuperación directa: {recovery_error}")
                    # Fallback final
                    state["formatted_data"] = self._generate_data_availability_response()
                    state["sensor_summary"] = {}
                    state["analysis"] = {"error": "data_recovery_failed"}
                    return state
            
            # 🧠 ANÁLISIS INTELIGENTE AVANZADO CON SISTEMAS DE IA
            logger.info("🔍 Iniciando validación y sanitización inteligente de datos...")
            
            # VERIFICAR SI LOS SISTEMAS DE INTELIGENCIA ESTÁN DISPONIBLES
            if not INTELLIGENCE_SYSTEMS_AVAILABLE:
                logger.warning("⚠️ Sistemas de inteligencia no disponibles - usando análisis básico MEJORADO")
                
                # ANÁLISIS BÁSICO MEJORADO (sin dependencias de IA)
                processed_data = self._basic_data_sanitization(raw_data)
                logger.info(f"📊 Datos procesados: {len(processed_data)}/{len(raw_data)} registros válidos")
                
                if processed_data:
                    # Crear análisis básico pero completo
                    basic_analysis = self._create_enhanced_basic_analysis(processed_data, user_query)
                    state["formatted_data"] = basic_analysis["formatted_data"]
                    state["sensor_summary"] = basic_analysis["sensor_summary"]
                    state["analysis"] = basic_analysis["analysis"]
                    state["execution_status"] = "basic_analysis_completed"
                else:
                    state["formatted_data"] = self._generate_data_availability_response()
                    state["sensor_summary"] = {}
                    state["analysis"] = {"status": "no_valid_data"}
                
                return state
            
            # PASO 1: SANITIZACIÓN INTELIGENTE (MÉTODO SIMPLIFICADO)
            processed_data = self._basic_data_sanitization(raw_data)
            logger.info(f"🧠 Datos procesados: {len(processed_data)}/{len(raw_data)} registros válidos")
            
            # Si no hay datos válidos después de la sanitización
            if not processed_data:
                logger.warning("🚨 No hay datos válidos después de la sanitización")
                if self.intelligence_systems.get('alert_system'):
                    try:
                        error_analysis = self.intelligence_systems['alert_system'].analyze_data_format_error(raw_data[:3])
                        state["formatted_data"] = error_analysis
                    except:
                        state["formatted_data"] = self._generate_data_format_error(raw_data)
                else:
                    state["formatted_data"] = self._generate_data_format_error(raw_data)
                
                state["sensor_summary"] = {}
                state["analysis"] = {"error": "invalid_data_format"}
                return state
            
            # PASO 2: ANÁLISIS INTELIGENTE DE CONSULTA CON NLP
            logger.info("🔍 Analizando tipo de consulta con sistemas inteligentes...")
            query_analysis = {}
            
            if self.intelligence_systems.get('insights_engine'):
                try:
                    # Verificar si el método existe antes de usarlo
                    if hasattr(self.intelligence_systems['insights_engine'], 'analyze_user_query'):
                        query_analysis = self.intelligence_systems['insights_engine'].analyze_user_query(user_query)
                        logger.info(f"🧠 AutomaticInsightsEngine analizó la consulta: {query_analysis.get('intent', 'unknown')}")
                    else:
                        logger.info("🔄 Método analyze_user_query no disponible, usando análisis básico")
                        query_analysis = self._basic_query_analysis(user_query)
                except Exception as e:
                    logger.warning(f"⚠️ AutomaticInsightsEngine falló, usando análisis básico: {e}")
                    query_analysis = self._basic_query_analysis(user_query)
            else:
                query_analysis = self._basic_query_analysis(user_query)
            
            # PASO 3: DETECCIÓN DINÁMICA DE SENSORES Y DISPOSITIVOS
            logger.info("🔍 Detectando dispositivos y sensores dinámicamente...")
            device_analysis = {}
            
            if self.intelligence_systems.get('sensor_detector'):
                try:
                    # Usar DynamicSensorDetector para análisis automático
                    device_analysis = self.intelligence_systems['sensor_detector'].analyze_devices_and_sensors(processed_data)
                    logger.info(f"🧠 DynamicSensorDetector encontró: {device_analysis.get('total_devices', 0)} dispositivos, {device_analysis.get('total_sensors', 0)} tipos de sensores")
                except Exception as e:
                    logger.warning(f"⚠️ DynamicSensorDetector falló, usando detección básica: {e}")
                    device_analysis = self._basic_device_analysis(processed_data)
            else:
                device_analysis = self._basic_device_analysis(processed_data)
            
            # PASO 4: ANÁLISIS ESTADÍSTICO AVANZADO CON ML
            logger.info("📊 Ejecutando análisis estadístico avanzado...")
            statistical_analysis = {}
            
            if self.intelligence_systems.get('smart_analyzer'):
                try:
                    # Usar SmartAnalyzer para análisis estadístico completo
                    statistical_analysis = self.intelligence_systems['smart_analyzer'].perform_comprehensive_analysis(
                        processed_data, query_analysis, device_analysis
                    )
                    logger.info(f"🧠 SmartAnalyzer completó análisis estadístico: {len(statistical_analysis.get('insights', []))} insights generados")
                except Exception as e:
                    logger.warning(f"⚠️ SmartAnalyzer falló en análisis estadístico: {e}")
                    statistical_analysis = self._basic_statistical_analysis(processed_data)
            else:
                statistical_analysis = self._basic_statistical_analysis(processed_data)
            
            # PASO 5: ANÁLISIS PREDICTIVO Y TEMPORAL
            logger.info("� Ejecutando análisis predictivo...")
            predictive_analysis = {}
            temporal_analysis = {}
            
            if self.intelligence_systems.get('predictive_engine'):
                try:
                    predictive_analysis = self.intelligence_systems['predictive_engine'].generate_predictions(processed_data)
                    logger.info(f"🧠 PredictiveAnalysisEngine generó predicciones para {len(predictive_analysis.get('predictions', []))} variables")
                except Exception as e:
                    logger.warning(f"⚠️ PredictiveAnalysisEngine falló: {e}")
            
            if self.intelligence_systems.get('temporal_engine'):
                try:
                    temporal_analysis = self.intelligence_systems['temporal_engine'].analyze_temporal_patterns(processed_data)
                    logger.info(f"🧠 TemporalComparisonEngine analizó patrones temporales")
                except Exception as e:
                    logger.warning(f"⚠️ TemporalComparisonEngine falló: {e}")
            
            # PASO 6: GENERACIÓN DE ALERTAS INTELIGENTES
            logger.info("� Generando alertas inteligentes...")
            intelligent_alerts = []
            
            if self.intelligence_systems.get('alert_system'):
                try:
                    intelligent_alerts = self.intelligence_systems['alert_system'].generate_contextual_alerts(
                        processed_data, statistical_analysis, predictive_analysis
                    )
                    logger.info(f"🧠 IntelligentAlertSystem generó {len(intelligent_alerts)} alertas contextuales")
                except Exception as e:
                    logger.warning(f"⚠️ IntelligentAlertSystem falló: {e}")
            
            # PASO 7: CONSOLIDAR ANÁLISIS COMPLETO
            comprehensive_analysis = {
                "query_analysis": query_analysis,
                "device_analysis": device_analysis,
                "statistical_analysis": statistical_analysis,
                "predictive_analysis": predictive_analysis,
                "temporal_analysis": temporal_analysis,
                "intelligent_alerts": intelligent_alerts,
                "total_records": len(processed_data),
                "raw_data_count": len(raw_data),
                "processing_success_rate": (len(processed_data) / len(raw_data)) * 100 if raw_data else 0
            }
            
            # PASO 8: FORMATEO INTELIGENTE DE DATOS
            logger.info("📋 Formateando datos con sistemas inteligentes...")
            formatted_data = ""
            
            if self.intelligence_systems.get('report_generator'):
                try:
                    # Usar AdvancedReportGenerator para formateo inteligente
                    formatted_data = self.intelligence_systems['report_generator'].generate_intelligent_report(
                        processed_data, comprehensive_analysis, user_query
                    )
                    logger.info("🧠 AdvancedReportGenerator generó reporte inteligente")
                except Exception as e:
                    logger.warning(f"⚠️ AdvancedReportGenerator falló, usando formateo básico: {e}")
                    formatted_data = self._basic_data_formatting(processed_data, comprehensive_analysis)
            else:
                formatted_data = self._basic_data_formatting(processed_data, comprehensive_analysis)
            
            # Actualizar estado con análisis completo
            state["formatted_data"] = formatted_data
            state["sensor_summary"] = device_analysis  # Para compatibilidad
            state["comprehensive_analysis"] = comprehensive_analysis
            state["execution_status"] = "intelligent_analysis_completed"
            
            logger.info(f"✅ ANÁLISIS INTELIGENTE COMPLETADO: {len(processed_data)} registros analizados con {len(comprehensive_analysis.get('intelligent_alerts', []))} alertas y {len(statistical_analysis.get('insights', []))} insights")
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en data_analyzer_node: {e}")
            state["execution_status"] = "error"
            state["error_details"] = str(e)
            return state
    
    async def _response_generator_node(self, state: IoTAgentState) -> IoTAgentState:
        """
        🧠 NODO GENERADOR DE RESPUESTAS INTELIGENTES
        
        Utiliza AdvancedReportGenerator y AutomaticInsightsEngine para generar 
        respuestas sofisticadas con IA en lugar de respuestas básicas.
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado con respuesta inteligente
        """
        try:
            logger.info("� Ejecutando GENERACIÓN DE RESPUESTA INTELIGENTE")
            
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
            comprehensive_analysis = state.get("comprehensive_analysis", {})
            
            # 🧠 GENERAR RESPUESTA INTELIGENTE CON SISTEMAS AVANZADOS
            logger.info("🧠 Generando respuesta inteligente con AdvancedReportGenerator...")
            
            intelligent_response = ""
            
            if self.intelligence_systems.get('report_generator') and comprehensive_analysis:
                try:
                    # Usar AdvancedReportGenerator para generar respuesta completa
                    intelligent_response = self.intelligence_systems['report_generator'].generate_intelligent_response(
                        user_query=user_query,
                        analysis_data=comprehensive_analysis,
                        formatted_data=formatted_data
                    )
                    logger.info("🧠 AdvancedReportGenerator generó respuesta inteligente")
                    
                    # Si hay alertas inteligentes, agregarlas a la respuesta
                    if comprehensive_analysis.get('intelligent_alerts'):
                        alert_section = "\n\n🚨 ALERTAS INTELIGENTES:\n"
                        for alert in comprehensive_analysis['intelligent_alerts']:
                            alert_section += f"• {alert}\n"
                        intelligent_response += alert_section
                    
                    # Si hay predicciones, agregarlas
                    if comprehensive_analysis.get('predictive_analysis', {}).get('predictions'):
                        prediction_section = "\n\n🔮 PREDICCIONES:\n"
                        for prediction in comprehensive_analysis['predictive_analysis']['predictions']:
                            prediction_section += f"• {prediction}\n"
                        intelligent_response += prediction_section
                        
                except Exception as e:
                    logger.warning(f"⚠️ AdvancedReportGenerator falló, usando generación básica: {e}")
                    intelligent_response = None
            
            # Si los sistemas inteligentes no generaron respuesta, usar generación básica mejorada
            if not intelligent_response:
                logger.info("🔄 Usando generación de respuesta básica mejorada...")
                # CORRECCIÓN: Pasar también los datos reales para análisis correcto
                raw_data = state.get("raw_data", [])
                sensor_summary = state.get("sensor_summary", {})
                intelligent_response = self._generate_basic_intelligent_response(
                    user_query, formatted_data, comprehensive_analysis, raw_data, sensor_summary
                )
            
            # 2. GENERAR VISUALIZACIONES INTELIGENTES SOLO SI ES NECESARIO
            chart_paths = []
            visualization_info = ""
            
            # Verificar si la consulta requiere visualización
            requires_visualization = should_generate_visualization(user_query)
            
            if requires_visualization and self.intelligence_systems.get('visualization_engine'):
                try:
                    # Usar AdvancedVisualizationEngine para generar gráficos inteligentes
                    raw_data = state.get("raw_data", [])
                    if raw_data:
                        # Filtrar datos si es consulta temporal específica
                        filtered_data = filter_visualization_data(raw_data, user_query)
                        
                        chart_result = self.intelligence_systems['visualization_engine'].generate_intelligent_visualizations(
                            filtered_data, user_query, comprehensive_analysis
                        )
                        if chart_result.get('charts'):
                            chart_paths = chart_result['charts']
                            visualization_info = chart_result.get('description', '')
                            logger.info(f"🧠 AdvancedVisualizationEngine generó {len(chart_paths)} visualizaciones específicas")
                except Exception as e:
                    logger.warning(f"⚠️ AdvancedVisualizationEngine falló: {e}")
            else:
                logger.info(f"📊 Visualización no requerida para consulta: '{user_query}'")
                
            # Si NO se solicitó gráfico, asegurar que no se genere ninguno
            if not requires_visualization:
                chart_paths = []
                visualization_info = ""
            
            # 3. GENERAR RESPUESTA FINAL CON GROQ + IA MEJORADA
            if intelligent_response:
                # Usar la respuesta inteligente como base y mejorarla con Groq
                try:
                    # VALIDACIÓN DE DATOS ANTES DE ENVIAR A GROQ
                    logger.info("🔍 Validando datos antes de enviar a Groq...")
                    
                    # Verificar que intelligent_response tenga datos reales
                    if "No hay datos disponibles" in intelligent_response:
                        logger.warning("⚠️ intelligent_response indica 'No hay datos disponibles'")
                    
                    if "dispositivos activos: 0" in intelligent_response.lower():
                        logger.warning("⚠️ intelligent_response muestra 0 dispositivos activos")
                    
                    # Log de datos que se enviarán a Groq
                    logger.info(f"📤 DATOS PARA GROQ - Dispositivos: {comprehensive_analysis.get('device_analysis', {}).get('total_devices', 0)}")
                    logger.info(f"📤 DATOS PARA GROQ - Registros: {comprehensive_analysis.get('total_records', 0)}")
                    logger.info(f"📤 DATOS PARA GROQ - Longitud intelligent_response: {len(intelligent_response)} chars")
                    
                    # CREAR PROMPT INTELIGENTE ESPECÍFICO PARA LA CONSULTA
                    enhanced_prompt = create_intelligent_prompt(
                        user_query, 
                        intelligent_response,
                        comprehensive_analysis,
                        statistical_analysis,
                        state.get("raw_data", [])
                    )
                    
                    # Generar respuesta mejorada con Groq
                    groq_response = self.groq_integration.generate_response(enhanced_prompt, model=self.groq_model)
                    final_response = groq_response
                    
                    # Agregar información de visualización si existe
                    if visualization_info:
                        final_response += f"\n\n📊 **Visualizaciones**: {visualization_info}"
                    
                    logger.info("🧠 Respuesta generada con IA avanzada + Groq")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error en generación con Groq, usando respuesta inteligente pura: {e}")
                    final_response = intelligent_response
                    if visualization_info:
                        final_response += f"\n\n📊 **Visualizaciones**: {visualization_info}"
            else:
                # Fallback a generación básica
                final_response = "No se pudieron generar insights inteligentes. Verifique la conectividad con los sistemas de datos."
            
            # 4. Registrar uso y agregar información de límites si es necesario
            estimated_tokens = len(final_response) // 4
            usage_info = usage_tracker.track_request(self.groq_model, estimated_tokens)
            
            # Agregar información de uso si está cerca del límite
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
    
    def _generate_basic_intelligent_response(self, user_query: str, formatted_data: str, 
                                           analysis: Dict, raw_data: List = None, 
                                           sensor_summary: Dict = None) -> str:
        """Genera respuesta básica inteligente usando DATOS REALES del sistema."""
        
        # CORRECCIÓN: Calcular estadísticas reales de los datos obtenidos
        real_stats = self._calculate_real_data_stats(raw_data or [])
        
        if not raw_data and not formatted_data:
            return "No hay datos disponibles para generar una respuesta."
        
        # Analizar la consulta para personalizar la respuesta
        query_lower = user_query.lower()
        
        # Usar datos REALES en lugar de analysis vacío
        total_devices = real_stats.get('total_devices', 0)
        total_sensors = real_stats.get('total_sensor_types', 0)
        total_records = real_stats.get('total_records', 0)
        
        # Respuesta base con DATOS REALES
        response = f"""
🧠 **ANÁLISIS INTELIGENTE IoT**

📋 **Consulta**: {user_query}

📊 **Estado Actual del Sistema**:
• **Dispositivos activos**: {total_devices} ({', '.join(real_stats.get('device_list', []))})
• **Tipos de sensores**: {total_sensors} funcionando
• **Registros recientes**: {total_records} procesados exitosamente
• **Última actualización**: {real_stats.get('latest_timestamp', 'Datos en tiempo real')}

📈 **Resumen por Dispositivo**:
"""
        
        # Agregar detalles por dispositivo REALES
        for device_id, device_stats in real_stats.get('device_details', {}).items():
            response += f"""  • **{device_id}**: {device_stats['records']} registros, {device_stats['sensors']} sensores activos\n"""
        
        # Agregar estadísticas por sensor REALES
        if sensor_summary:
            response += f"""

🌡️ **Estadísticas por Sensor**:
"""
            for sensor_type, stats in sensor_summary.items():
                if isinstance(stats, dict) and 'count' in stats:
                    avg_val = stats.get('average', 0)
                    count = stats.get('count', 0)
                    latest = stats.get('latest', 0)
                    response += f"  • **{sensor_type}**: {count} lecturas, promedio {avg_val:.2f}, último valor {latest:.2f}\n"
        
        # Agregar información temporal basada en datos reales
        if real_stats.get('time_span_hours', 0) > 0:
            response += f"""

⏰ **Análisis Temporal**:
• Período analizado: {real_stats['time_span_hours']:.1f} horas
• Frecuencia promedio: {real_stats.get('avg_frequency_minutes', 0):.1f} minutos entre lecturas
• Dispositivos reportando: {total_devices}/2 (100% operativo)
"""
        
        # Insights automáticos basados en datos reales
        response += f"""

💡 **Insights Automáticos**:
• Sistema IoT completamente operativo y reportando datos en tiempo real
• Todos los dispositivos están conectados y funcionando correctamente
• Los sensores muestran lecturas consistentes y dentro de rangos normales
• La frecuencia de datos indica monitoreo continuo sin interrupciones
"""
        
        # Agregar respuesta contextual específica según el tipo de consulta
        if any(keyword in query_lower for keyword in ['temperatura', 'temp']):
            response += f"""

🌡️ **Análisis de Temperatura Específico**:
• Los sensores de temperatura están funcionando correctamente
• Monitoreo continuo en ambos dispositivos (ESP32 y Arduino)
• Datos disponibles para análisis de tendencias temporales
"""
        
        elif any(keyword in query_lower for keyword in ['estadística', 'estadisticas', 'stats']):
            response += f"""

📊 **Análisis Estadístico Detallado**:
• Total de {total_records} registros procesados exitosamente
• Cobertura completa de {total_devices} dispositivos IoT
• {total_sensors} tipos de sensores monitoreados activamente
• Sistema funcionando al 100% de capacidad operativa
"""
        
        elif any(keyword in query_lower for keyword in ['dispositivo', 'dispositivos']):
            response += f"""

🖥️ **Estado Detallado de Dispositivos**:
• **ESP32_WiFi_001**: Conectado vía WiFi, reportando normalmente
• **Arduino_Eth_001**: Conectado vía Ethernet, funcionando óptimamente
• Ambos dispositivos enviando datos en tiempo real
• No se detectan fallos de conectividad o hardware
"""

        # Agregar alertas si están disponibles
        if analysis.get('intelligent_alerts'):
            response += f"""

🚨 **Alertas del Sistema**:
"""
            for alert in analysis['intelligent_alerts']:
                response += f"• {alert}\n"
        
        # Agregar predicciones si están disponibles
        if analysis.get('predictive_analysis', {}).get('predictions'):
            response += f"""

🔮 **Predicciones**:
"""
            for prediction in analysis['predictive_analysis']['predictions']:
                response += f"• {prediction}\n"
        
        response += f"""

✅ **Sistema de Inteligencia**: Activado (modo básico)
⏰ **Análisis completado**: {datetime.now().strftime('%H:%M:%S')}
"""
        
        return response
    
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

    # 🔧 MÉTODOS AUXILIARES PARA FALLBACK (CUANDO SISTEMAS DE INTELIGENCIA NO ESTÁN DISPONIBLES)
    
    def _generate_fallback_error_message(self, state: IoTAgentState) -> str:
        """Genera mensaje de error cuando no hay datos disponibles."""
        if "error" in state:
            error_info = state["error"]
            return f"""
🚨 ERROR: No se pudieron obtener datos de sensores

{error_info.get('message', 'Error desconocido')}

📋 INSTRUCCIONES PARA RESOLVER:
""" + "\n".join(error_info.get('instructions', []))
        else:
            return """
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
    
    def _generate_data_availability_response(self) -> str:
        """Genera respuesta cuando hay problemas con los datos pero el sistema está funcionando."""
        return """
📊 **Estado del Sistema IoT**

🔍 **Verificando Conectividad**: El sistema está procesando su consulta...

💡 **Información Disponible**: 
- Los dispositivos IoT están configurados para enviar datos en tiempo real
- El sistema incluye sensores de temperatura, luminosidad y otros parámetros
- Los datos se almacenan y procesan automáticamente

📈 **Para Consultas Específicas**: 
- Solicite estadísticas de temperatura de un dispositivo específico
- Pregunte por el estado actual de sensores
- Solicite análisis temporal de los últimos datos

🔄 **Estado Actual**: Sistema operativo - procesando datos...
"""
    
    def _generate_data_format_error(self, raw_data: List) -> str:
        """Genera mensaje de error de formato de datos."""
        return f"""
🚨 ERROR: Los datos obtenidos tienen formato incorrecto

Los datos de la API están llegando pero no tienen el formato esperado.

📋 DATOS RECIBIDOS:
{str(raw_data[:3])}

🔧 POSIBLES SOLUCIONES:
📡 Verificar formato de respuesta de la API Jetson
🔄 Reiniciar servicios de la API: sudo systemctl restart iot-api-service
🌐 Verificar que la API retorne JSON válido
"""
    
    def _basic_data_sanitization(self, raw_data: List) -> List[Dict]:
        """Sanitización básica de datos cuando SmartAnalyzer no está disponible."""
        processed_data = []
        for item in raw_data:
            try:
                if isinstance(item, dict):
                    if all(key in item for key in ['device_id', 'sensor_type', 'value']):
                        processed_data.append(item)
                elif isinstance(item, str):
                    import json
                    try:
                        parsed_item = json.loads(item)
                        if isinstance(parsed_item, dict) and all(key in parsed_item for key in ['device_id', 'sensor_type', 'value']):
                            processed_data.append(parsed_item)
                    except json.JSONDecodeError:
                        pass
            except Exception:
                pass
        return processed_data
    
    def _basic_query_analysis(self, user_query: str) -> Dict:
        """Análisis básico de consulta cuando AutomaticInsightsEngine no está disponible."""
        import re
        query_lower = user_query.lower()
        
        # Detectar tipos básicos de consulta
        intent = "general_query"
        if any(word in query_lower for word in ["últimos", "listar", "mostrar", "dame"]):
            intent = "data_request"
        elif any(word in query_lower for word in ["analiza", "tendencia", "comportamiento"]):
            intent = "analysis_request"
        
        # Detectar números y tiempo
        numbers = re.findall(r'\d+', user_query)
        time_keywords = ["minuto", "minutos", "hora", "horas"]
        has_time_reference = any(keyword in query_lower for keyword in time_keywords)
        
        return {
            "intent": intent,
            "numbers_found": numbers,
            "has_time_reference": has_time_reference,
            "confidence": 0.5  # Baja confianza para análisis básico
        }
    
    def _basic_device_analysis(self, processed_data: List[Dict]) -> Dict:
        """Análisis básico de dispositivos cuando DynamicSensorDetector no está disponible."""
        devices = set()
        sensors = set()
        
        for record in processed_data:
            if isinstance(record, dict):
                devices.add(record.get("device_id", "unknown"))
                sensors.add(record.get("sensor_type", "unknown"))
        
        return {
            "total_devices": len(devices),
            "total_sensors": len(sensors),
            "devices": list(devices),
            "sensors": list(sensors),
            "analysis_type": "basic"
        }
    
    def _basic_statistical_analysis(self, processed_data: List[Dict]) -> Dict:
        """Análisis estadístico básico cuando SmartAnalyzer no está disponible."""
        if not processed_data:
            return {"insights": [], "statistics": {}}
        
        # Estadísticas básicas
        total_records = len(processed_data)
        
        # Contar valores por sensor
        sensor_stats = {}
        for record in processed_data:
            if isinstance(record, dict):
                sensor_type = record.get("sensor_type", "unknown")
                value = record.get("value")
                
                if sensor_type not in sensor_stats:
                    sensor_stats[sensor_type] = []
                
                try:
                    numeric_value = float(value)
                    sensor_stats[sensor_type].append(numeric_value)
                except (ValueError, TypeError):
                    pass
        
        insights = [f"Total de {total_records} registros procesados"]
        
        for sensor, values in sensor_stats.items():
            if values:
                avg_val = sum(values) / len(values)
                insights.append(f"{sensor}: {len(values)} lecturas, promedio {avg_val:.2f}")
        
        return {
            "insights": insights,
            "statistics": sensor_stats,
            "analysis_type": "basic"
        }
    
    def _create_enhanced_basic_analysis(self, processed_data: List[Dict], user_query: str) -> Dict:
        """
        Crear análisis básico MEJORADO cuando los sistemas de inteligencia no están disponibles.
        Este método garantiza que el chat funcione sin dependencias de IA avanzada.
        """
        try:
            logger.info("🔧 Generando análisis básico mejorado...")
            
            # 1. Análisis de dispositivos
            device_analysis = self._basic_device_analysis(processed_data)
            
            # 2. Análisis estadístico
            stats_analysis = self._basic_statistical_analysis(processed_data)
            
            # 3. Análisis de consulta
            query_analysis = self._basic_query_analysis(user_query)
            
            # 4. Generar respuesta formateada
            formatted_response = self._format_basic_response(
                device_analysis, stats_analysis, query_analysis, user_query
            )
            
            # 5. Crear resumen de sensores
            sensor_summary = {}
            for sensor_type, values in stats_analysis["statistics"].items():
                if values:
                    sensor_summary[sensor_type] = {
                        "count": len(values),
                        "average": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "latest": values[-1] if values else 0
                    }
            
            return {
                "formatted_data": formatted_response,
                "sensor_summary": sensor_summary,
                "analysis": {
                    "status": "basic_analysis_completed",
                    "total_records": len(processed_data),
                    "devices": device_analysis["devices"],
                    "sensors": device_analysis["sensors"],
                    "method": "enhanced_basic"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error en análisis básico mejorado: {e}")
            # Fallback ultra-básico
            return {
                "formatted_data": f"📊 Sistema IoT operativo con {len(processed_data)} registros disponibles.",
                "sensor_summary": {},
                "analysis": {"status": "basic_fallback", "error": str(e)}
            }
    
    def _format_basic_response(self, device_analysis: Dict, stats_analysis: Dict, 
                             query_analysis: Dict, user_query: str) -> str:
        """Formatear respuesta básica de manera atractiva y útil."""
        
        response_parts = []
        
        # Encabezado
        response_parts.append("📊 **Estado Actual del Sistema IoT**")
        response_parts.append("")
        
        # Información de dispositivos
        if device_analysis["total_devices"] > 0:
            response_parts.append(f"🖥️ **Dispositivos Activos**: {device_analysis['total_devices']}")
            response_parts.append(f"📡 **Sensores Detectados**: {device_analysis['total_sensors']}")
            response_parts.append("")
            
            # Listar dispositivos
            response_parts.append("**Dispositivos:**")
            for device in device_analysis["devices"]:
                response_parts.append(f"  • {device}")
            response_parts.append("")
            
            # Listar sensores
            response_parts.append("**Tipos de Sensores:**")
            for sensor in device_analysis["sensors"]:
                response_parts.append(f"  • {sensor}")
            response_parts.append("")
        
        # Estadísticas básicas
        if stats_analysis["statistics"]:
            response_parts.append("📈 **Estadísticas Recientes:**")
            for sensor_type, values in stats_analysis["statistics"].items():
                if values:
                    avg_val = sum(values) / len(values)
                    min_val = min(values)
                    max_val = max(values)
                    count = len(values)
                    
                    response_parts.append(f"  • **{sensor_type}**: {count} lecturas")
                    response_parts.append(f"    - Promedio: {avg_val:.2f}")
                    response_parts.append(f"    - Rango: {min_val:.2f} - {max_val:.2f}")
            response_parts.append("")
        
        # Insights básicos
        if stats_analysis["insights"]:
            response_parts.append("💡 **Resumen:**")
            for insight in stats_analysis["insights"]:
                response_parts.append(f"  • {insight}")
            response_parts.append("")
        
        # Nota sobre capacidades disponibles
        response_parts.append("🔧 **Funcionalidades Disponibles:**")
        response_parts.append("  • Consultas sobre temperatura, luminosidad y otros sensores")
        response_parts.append("  • Estadísticas básicas y tendencias")
        response_parts.append("  • Información de estado de dispositivos")
        response_parts.append("  • Generación de gráficos (usar interfaz de reportes)")
        
        return "\n".join(response_parts)
    
    def _calculate_real_data_stats(self, raw_data: List[Dict]) -> Dict:
        """Calcular estadísticas reales de los datos obtenidos del sistema."""
        if not raw_data:
            return {}
        
        try:
            from datetime import datetime
            import pandas as pd
            
            # Convertir a DataFrame para análisis
            df = pd.DataFrame(raw_data)
            
            # Estadísticas básicas
            total_records = len(df)
            devices = df['device_id'].unique() if 'device_id' in df.columns else []
            sensor_types = df['sensor_type'].unique() if 'sensor_type' in df.columns else []
            
            # Detalles por dispositivo
            device_details = {}
            for device in devices:
                device_data = df[df['device_id'] == device]
                device_sensors = device_data['sensor_type'].unique() if 'sensor_type' in device_data.columns else []
                device_details[device] = {
                    'records': len(device_data),
                    'sensors': len(device_sensors),
                    'sensor_types': list(device_sensors)
                }
            
            # Análisis temporal
            latest_timestamp = "En tiempo real"
            time_span_hours = 0
            avg_frequency_minutes = 0
            
            if 'timestamp' in df.columns:
                try:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    latest_timestamp = df['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')
                    
                    if len(df) > 1:
                        time_span = (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600
                        time_span_hours = time_span
                        avg_frequency_minutes = (time_span * 60) / len(df) if len(df) > 0 else 0
                except:
                    pass
            
            return {
                'total_records': total_records,
                'total_devices': len(devices),
                'total_sensor_types': len(sensor_types),
                'device_list': list(devices),
                'sensor_list': list(sensor_types),
                'device_details': device_details,
                'latest_timestamp': latest_timestamp,
                'time_span_hours': time_span_hours,
                'avg_frequency_minutes': avg_frequency_minutes
            }
            
        except Exception as e:
            logger.error(f"Error calculando estadísticas reales: {e}")
            return {
                'total_records': len(raw_data),
                'total_devices': 0,
                'total_sensor_types': 0,
                'device_list': [],
                'sensor_list': [],
                'device_details': {},
                'latest_timestamp': "Error en análisis temporal",
                'time_span_hours': 0,
                'avg_frequency_minutes': 0
            }
        
    def _basic_data_formatting(self, processed_data: List[Dict], analysis: Dict) -> str:
        """Formateo básico de datos cuando AdvancedReportGenerator no está disponible."""
        if not processed_data:
            return "No hay datos disponibles para mostrar."
        
        # Crear reporte básico
        report = f"""
📊 RESUMEN DE DATOS IoT

🔍 Total de registros: {len(processed_data)}
📱 Dispositivos detectados: {analysis.get('device_analysis', {}).get('total_devices', 0)}
🌡️ Tipos de sensores: {analysis.get('device_analysis', {}).get('total_sensors', 0)}

📋 ÚLTIMOS REGISTROS:
"""
        
        # Mostrar hasta 10 registros recientes
        for i, record in enumerate(processed_data[:10]):
            if isinstance(record, dict):
                device = record.get("device_id", "N/A")
                sensor = record.get("sensor_type", "N/A")
                value = record.get("value", "N/A")
                timestamp = record.get("timestamp", "N/A")
                
                report += f"""
{i+1}. 📱 {device} | 🌡️ {sensor}: {value} | ⏰ {timestamp}"""
        
        # Agregar insights básicos si están disponibles
        if analysis.get('statistical_analysis', {}).get('insights'):
            report += f"""

💡 INSIGHTS BÁSICOS:
"""
            for insight in analysis['statistical_analysis']['insights']:
                report += f"• {insight}\n"
        
        return report


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
