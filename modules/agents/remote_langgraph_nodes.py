"""
Remote LangGraph Nodes - Versión para API de Jetson
===================================================

Nodos modificados para usar la API remota de Jetson en lugar de la base de datos local.
"""

import time
import sys
import os
from typing import Dict, Any, List
from datetime import datetime

# Añadir el directorio padre al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from modules.agents.langgraph_state import (
    IoTAgentState, QueryIntent, ToolType, ExecutionStatus
)
from modules.agents.remote_data_collector import RemoteDataCollectorNode
from modules.tools.analysis_tools import AnalysisTools
from modules.agents.ollama_integration import OllamaLLMIntegration
from modules.utils.logger import setup_logger

logger = setup_logger(__name__)


class RemoteLangGraphNodes:
    """Nodos de procesamiento para el grafo LangGraph usando API remota de Jetson."""
    
    def __init__(self):
        self.ollama = OllamaLLMIntegration()
        self.remote_collector = RemoteDataCollectorNode()
        self.analysis_tools = AnalysisTools()
        
    async def query_analyzer_node(self, state: IoTAgentState) -> IoTAgentState:
        """
        Analiza la consulta del usuario para determinar intención y herramientas necesarias.
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado con intención y herramientas identificadas
        """
        try:
            logger.info(f"🔍 Analizando consulta: {state['user_query']}")
            
            # Marcar inicio del nodo
            state["execution_metadata"]["start_time"] = datetime.now()
            state["execution_metadata"]["nodes_executed"].append("query_analyzer")
            
            query = state["user_query"].lower()
            
            # Detectar intención basada en palabras clave
            if any(word in query for word in ["temperatura", "temperature", "grados", "calor", "frio"]):
                state["query_intent"] = QueryIntent.SENSOR_DATA
                state["analyzed_query"] = {
                    "data_type": "temperature",
                    "intent": "get_temperature_data",
                    "device_filter": None
                }
            elif any(word in query for word in ["arduino", "eth_001"]):
                state["query_intent"] = QueryIntent.DEVICE_STATUS
                state["analyzed_query"] = {
                    "data_type": "device_specific",
                    "intent": "get_device_data",
                    "device_filter": "arduino_eth_001"
                }
            elif any(word in query for word in ["esp32", "wifi_001"]):
                state["query_intent"] = QueryIntent.DEVICE_STATUS
                state["analyzed_query"] = {
                    "data_type": "device_specific", 
                    "intent": "get_device_data",
                    "device_filter": "esp32_wifi_001"
                }
            elif any(word in query for word in ["análisis", "analizar", "trends", "tendencias"]):
                state["query_intent"] = QueryIntent.ANALYSIS
                state["analyzed_query"] = {
                    "data_type": "analysis",
                    "intent": "analyze_data",
                    "device_filter": None
                }
            elif any(word in query for word in ["estadísticas", "statistics", "promedio", "max", "min"]):
                state["query_intent"] = QueryIntent.STATISTICS
                state["analyzed_query"] = {
                    "data_type": "statistics",
                    "intent": "calculate_stats",
                    "device_filter": None
                }
            else:
                state["query_intent"] = QueryIntent.SENSOR_DATA
                state["analyzed_query"] = {
                    "data_type": "general",
                    "intent": "get_all_data",
                    "device_filter": None
                }
            
            # Determinar herramientas necesarias (ahora solo API remota)
            state["required_tools"] = [ToolType.GET_SENSOR_DATA]
            
            logger.info(f"✅ Intención detectada: {state['query_intent']}")
            logger.info(f"📋 Herramientas requeridas: {state['required_tools']}")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en query_analyzer_node: {e}")
            state["error_info"] = {
                "node": "query_analyzer",
                "error": str(e),
                "timestamp": datetime.now()
            }
            return state
    
    async def remote_data_collector_node(self, state: IoTAgentState) -> IoTAgentState:
        """
        Recopila datos usando la API remota de Jetson.
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado con datos recopilados
        """
        try:
            logger.info("📡 Recopilando datos desde API remota de Jetson")
            
            state["execution_metadata"]["nodes_executed"].append("remote_data_collector")
            
            # Verificar salud de la API primero
            health_check = self.remote_collector.check_api_health()
            if health_check.get('status') != 'healthy':
                logger.warning("⚠️ API health check failed")
                state['data_collection_error'] = "API remota no disponible"
                state['raw_data'] = []
                state['formatted_data'] = "Error: API remota no disponible."
                return state
            
            # Obtener el query analizado para determinar qué datos recolectar
            analyzed_query = state.get('analyzed_query', {})
            query_type = analyzed_query.get('data_type', 'general')
            
            # Recopilar datos según el tipo de consulta
            if query_type == 'temperature':
                # Obtener datos de temperatura específicamente
                raw_data = self.remote_collector.get_temperature_data(limit=50)
                logger.info(f"🌡️ Obtenidos {len(raw_data)} registros de temperatura")
                
            elif query_type == 'device_specific':
                # Obtener datos de un dispositivo específico
                device_id = analyzed_query.get('device_filter')
                if device_id:
                    raw_data = self.remote_collector.get_device_specific_data(device_id, limit=40)
                    logger.info(f"📱 Obtenidos {len(raw_data)} registros de {device_id}")
                else:
                    raw_data = self.remote_collector.get_all_sensor_data(limit=50)
                    logger.info(f"📊 Obtenidos {len(raw_data)} registros generales")
            else:
                # Obtener todos los datos de sensores
                raw_data = self.remote_collector.get_all_sensor_data(limit=50)
                logger.info(f"📊 Obtenidos {len(raw_data)} registros de sensores")
            
            # Formatear datos para el LLM
            formatted_data = self.remote_collector.format_data_for_analysis(raw_data)
            
            # Obtener resumen de sensores
            sensor_summary = self.remote_collector.get_latest_readings_summary()
            
            # Actualizar estado
            state['raw_data'] = raw_data
            state['formatted_data'] = formatted_data
            state['sensor_summary'] = sensor_summary
            state['data_source'] = 'jetson_api'
            state['data_collection_success'] = True
            state['data_collection_timestamp'] = health_check.get('api_health', {}).get('timestamp')
            
            # Preparar contexto de datos para análisis
            context_data = {
                'total_records': len(raw_data),
                'devices_found': len(set(record.get('device_id') for record in raw_data)),
                'sensor_types': list(set(record.get('sensor_type') for record in raw_data)),
                'latest_timestamp': raw_data[0].get('timestamp') if raw_data else None,
                'data_summary': sensor_summary
            }
            state['context_data'] = context_data
            
            logger.info(f"✅ Recopilación remota exitosa: {len(raw_data)} registros")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en remote_data_collector_node: {e}")
            state['data_collection_error'] = str(e)
            state['raw_data'] = []
            state['formatted_data'] = "Error al obtener datos de sensores remotos."
            state["error_info"] = {
                "node": "remote_data_collector",
                "error": str(e),
                "timestamp": datetime.now()
            }
            return state
    
    async def data_analyzer_node(self, state: IoTAgentState) -> IoTAgentState:
        """
        Analiza los datos recopilados para extraer insights.
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado con resultados de análisis
        """
        try:
            logger.info("🔬 Analizando datos recopilados")
            
            state["execution_metadata"]["nodes_executed"].append("data_analyzer")
            
            analysis_results = {}
            raw_data = state.get('raw_data', [])
            
            if not raw_data:
                analysis_results["summary"] = "No hay datos disponibles para analizar."
                state["analysis_results"] = analysis_results
                return state
            
            # Análisis basado en la intención
            if state["query_intent"] == QueryIntent.ANALYSIS:
                analysis_results["trends"] = await self._analyze_trends(raw_data)
                analysis_results["anomalies"] = await self._detect_anomalies(raw_data)
            
            elif state["query_intent"] == QueryIntent.STATISTICS:
                analysis_results["statistics"] = await self._calculate_statistics(raw_data)
            
            # Análisis general siempre aplicado
            analysis_results["summary"] = self._generate_data_summary(raw_data)
            analysis_results["device_status"] = self._analyze_device_status(state.get('sensor_summary', {}))
            
            state["analysis_results"] = analysis_results
            
            logger.info("✅ Análisis de datos completado")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en data_analyzer_node: {e}")
            state["error_info"] = {
                "node": "data_analyzer",
                "error": str(e),
                "timestamp": datetime.now()
            }
            return state
    
    async def response_generator_node(self, state: IoTAgentState) -> IoTAgentState:
        """
        Genera respuesta final usando el LLM.
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado con respuesta final
        """
        try:
            logger.info("🤖 Generando respuesta con LLM")
            
            state["execution_metadata"]["nodes_executed"].append("response_generator")
            
            # Preparar contexto para el LLM
            user_query = state.get('user_query', '')
            context_data = {
                'intent': state.get('query_intent'),
                'analysis': state.get('analysis_results', {}),
                'summary': state.get('sensor_summary', {}),
                'data_source': 'API remota de Jetson',
                'timestamp': state.get('data_collection_timestamp')
            }
            
            # Preparar resultados de herramientas con datos de sensores
            tools_results = {
                'sensor_data': state.get('raw_data', []),
                'formatted_data': state.get('formatted_data', ''),
                'devices': state.get('sensor_summary', {}).get('sensors', {})
            }
            
            # Generar respuesta usando Ollama
            response = await self.ollama.generate_response(
                user_message=user_query,
                context_data=context_data,
                tools_results=tools_results
            )
            
            state["final_response"] = response
            state["execution_status"] = ExecutionStatus.SUCCESS
            
            # Marcar tiempo de finalización
            state["execution_metadata"]["end_time"] = datetime.now()
            start_time = state["execution_metadata"]["start_time"]
            execution_time = (state["execution_metadata"]["end_time"] - start_time).total_seconds()
            state["execution_metadata"]["total_execution_time"] = execution_time
            
            logger.info(f"✅ Respuesta generada en {execution_time:.2f}s")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en response_generator_node: {e}")
            state["error_info"] = {
                "node": "response_generator",
                "error": str(e),
                "timestamp": datetime.now()
            }
            state["execution_status"] = ExecutionStatus.ERROR
            return state
    
    async def data_verification_node(self, state: IoTAgentState) -> IoTAgentState:
        """
        Verifica que la respuesta no contenga alucinaciones.
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado con respuesta verificada
        """
        try:
            logger.info("✅ Verificando respuesta para prevenir alucinaciones")
            
            state["execution_metadata"]["nodes_executed"].append("data_verification")
            
            response = state.get("final_response", "")
            raw_data = state.get('raw_data', [])
            
            logger.info(f"🔍 Verificando respuesta. Datos disponibles: {len(raw_data)} registros")
            
            # Obtener tipos de sensores reales desde los datos
            real_sensor_types = set()
            if raw_data:
                for record in raw_data:
                    sensor_type = record.get('sensor_type')
                    if sensor_type:
                        real_sensor_types.add(sensor_type)
            
            logger.info(f"🔍 Sensores reales detectados: {real_sensor_types}")
            
            # Lista de sensores que NO existen
            prohibited_sensors = ['humidity', 'humedad', 'pressure', 'presion', 'motion', 'movimiento']
            
            # Verificar alucinaciones
            hallucinations_found = []
            response_lower = response.lower()
            
            for prohibited in prohibited_sensors:
                if prohibited in response_lower:
                    hallucinations_found.append(prohibited)
            
            if hallucinations_found:
                logger.warning(f"⚠️ Alucinaciones detectadas: {hallucinations_found}")
                
                # Corregir la respuesta
                correction_prompt = f"""
                La respuesta contiene información sobre sensores que NO existen en el sistema.
                Sensores que NO existen: {hallucinations_found}
                Sensores que SÍ existen: {list(real_sensor_types)}
                
                Corrige la respuesta eliminando referencias a sensores inexistentes.
                """
                
                # Crear mensaje de corrección
                correction_message = f"""
                CORRECCIÓN REQUERIDA: La respuesta anterior contiene información sobre sensores que NO existen.
                
                Sensores que NO existen: {hallucinations_found}
                Sensores que SÍ existen: {list(real_sensor_types)}
                
                Respuesta original: {response}
                
                Por favor, corrige la respuesta eliminando cualquier referencia a sensores inexistentes y 
                basándote ÚNICAMENTE en los sensores reales disponibles.
                """
                
                corrected_context = {
                    'real_sensors': list(real_sensor_types),
                    'data_source': 'API remota de Jetson - Datos verificados'
                }
                
                tools_results = {
                    'sensor_data': state.get('raw_data', []),
                    'formatted_data': state.get('formatted_data', ''),
                    'correction_needed': True
                }
                
                corrected_response = await self.ollama.generate_response(
                    user_message=correction_message,
                    context_data=corrected_context,
                    tools_results=tools_results
                )
                state["final_response"] = corrected_response
                state["verification_status"] = "corrected"
                state["hallucinations_detected"] = hallucinations_found
                
                logger.info("✅ Respuesta corregida para eliminar alucinaciones")
            else:
                state["verification_status"] = "verified"
                logger.info("✅ No se detectaron alucinaciones")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en data_verification_node: {e}")
            state["error_info"] = {
                "node": "data_verification",
                "error": str(e),
                "timestamp": datetime.now()
            }
            return state
    
    # Métodos auxiliares para análisis
    async def _analyze_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analizar tendencias en los datos"""
        try:
            # Agrupar por tipo de sensor y calcular tendencias
            sensor_trends = {}
            
            for record in data:
                sensor_type = record.get('sensor_type')
                value = record.get('value')
                
                if sensor_type not in sensor_trends:
                    sensor_trends[sensor_type] = []
                sensor_trends[sensor_type].append(float(value))
            
            trends = {}
            for sensor, values in sensor_trends.items():
                if len(values) > 1:
                    if values[-1] > values[0]:
                        trends[sensor] = "aumentando"
                    elif values[-1] < values[0]:
                        trends[sensor] = "disminuyendo"
                    else:
                        trends[sensor] = "estable"
                else:
                    trends[sensor] = "datos insuficientes"
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {}
    
    async def _detect_anomalies(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detectar anomalías en los datos"""
        anomalies = []
        
        try:
            # Detectar valores extremos por sensor
            for record in data:
                value = record.get('value', 0)
                sensor_type = record.get('sensor_type')
                
                # Rangos normales (puedes ajustar según tus sensores)
                normal_ranges = {
                    't1': (0, 50),
                    't2': (0, 50),
                    'avg': (0, 50),
                    'ntc_entrada': (0, 60),
                    'ntc_salida': (0, 60),
                    'ldr': (0, 100)
                }
                
                if sensor_type in normal_ranges:
                    min_val, max_val = normal_ranges[sensor_type]
                    if value < min_val or value > max_val:
                        anomalies.append({
                            'sensor': sensor_type,
                            'value': value,
                            'expected_range': f"{min_val}-{max_val}",
                            'timestamp': record.get('timestamp')
                        })
        
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
        
        return anomalies
    
    async def _calculate_statistics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcular estadísticas de los datos"""
        stats = {}
        
        try:
            # Agrupar por tipo de sensor
            sensor_data = {}
            for record in data:
                sensor_type = record.get('sensor_type')
                value = record.get('value')
                
                if sensor_type not in sensor_data:
                    sensor_data[sensor_type] = []
                sensor_data[sensor_type].append(float(value))
            
            # Calcular estadísticas por sensor
            for sensor, values in sensor_data.items():
                if values:
                    stats[sensor] = {
                        'count': len(values),
                        'average': sum(values) / len(values),
                        'min': min(values),
                        'max': max(values),
                        'latest': values[-1]
                    }
        
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
        
        return stats
    
    def _generate_data_summary(self, data: List[Dict[str, Any]]) -> str:
        """Generar resumen de datos"""
        if not data:
            return "No hay datos disponibles."
        
        device_count = len(set(record.get('device_id') for record in data))
        sensor_count = len(set(record.get('sensor_type') for record in data))
        latest_timestamp = data[0].get('timestamp') if data else 'N/A'
        
        return f"Se encontraron {len(data)} registros de {device_count} dispositivos con {sensor_count} tipos de sensores. Última actualización: {latest_timestamp}"
    
    def _analyze_device_status(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar estado de dispositivos"""
        return {
            'devices_online': summary.get('devices_online', 0),
            'devices_total': summary.get('devices_total', 0),
            'last_update': summary.get('last_update'),
            'sensors_active': len(summary.get('sensors', {}))
        }


if __name__ == "__main__":
    # Prueba básica de los nodos remotos
    print("🧪 PRUEBA DE REMOTE LANGGRAPH NODES")
    print("=" * 50)
    
    import asyncio
    
    async def test_nodes():
        nodes = RemoteLangGraphNodes()
        
        # Estado de prueba
        test_state = {
            'user_query': 'Cuál es la temperatura actual?',
            'execution_metadata': {
                'start_time': datetime.now(),
                'nodes_executed': [],
                'total_execution_time': 0
            }
        }
        
        # Test query analyzer
        print("1️⃣ Testing query analyzer...")
        state = await nodes.query_analyzer_node(test_state)
        print(f"   Intent: {state.get('query_intent')}")
        print(f"   Query type: {state.get('analyzed_query', {}).get('data_type')}")
        
        # Test remote data collector
        print("\n2️⃣ Testing remote data collector...")
        state = await nodes.remote_data_collector_node(state)
        print(f"   Records collected: {len(state.get('raw_data', []))}")
        print(f"   Data source: {state.get('data_source')}")
        
        # Test data analyzer
        print("\n3️⃣ Testing data analyzer...")
        state = await nodes.data_analyzer_node(state)
        analysis = state.get('analysis_results', {})
        print(f"   Analysis keys: {list(analysis.keys())}")
        
        print("\n✅ All node tests completed")
    
    asyncio.run(test_nodes())
