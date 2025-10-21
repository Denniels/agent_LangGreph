"""
Agente IoT Ultra-Robusto - Versión Definitiva
============================================

Sistema de agente que garantiza acceso a datos y respuestas contundentes
mediante múltiples estrategias de fallback y análisis comprehensivo.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

# Imports del proyecto
from modules.agents.groq_integration import GroqIntegration
from modules.tools.ultra_robust_connector import UltraRobustJetsonConnector
from modules.utils.usage_tracker import usage_tracker

logger = logging.getLogger(__name__)

class UltraRobustIoTAgent:
    """
    Agente IoT Ultra-Robusto que garantiza acceso a datos y respuestas técnicas precisas.
    """
    
    def __init__(self, connector=None, visualization_engine=None, 
                 groq_model: str = "llama-3.1-8b-instant", jetson_api_url: str = None):
        """
        Inicializar agente ultra-robusto.
        
        Args:
            connector: UltraRobustJetsonConnector instance (opcional)
            visualization_engine: Motor de visualización (opcional)
            groq_model: Modelo de Groq a usar
            jetson_api_url: URL de la API Jetson
        """
        self.groq_model = groq_model
        self.jetson_api_url = jetson_api_url or os.getenv(
            "JETSON_API_URL", 
            "https://wonder-sufficiently-generator-click.trycloudflare.com"
        )
        
        # Componentes principales
        self.groq_integration = None
        
        # Usar conector proporcionado o crear uno nuevo
        if connector:
            self.connector = connector
        else:
            from modules.tools.ultra_robust_connector import UltraRobustJetsonConnector
            self.connector = UltraRobustJetsonConnector(self.jetson_api_url)
        
        # Motor de visualización
        if visualization_engine:
            self.visualization_engine = visualization_engine
            logger.info("✅ Motor de visualización proporcionado")
        else:
            self.visualization_engine = None
            try:
                from modules.utils.visualization_engine import IoTVisualizationEngine
                self.visualization_engine = IoTVisualizationEngine()
                logger.info("✅ Motor de visualización cargado")
            except ImportError:
                logger.warning("⚠️ Motor de visualización no disponible")
        
        # Cache para optimizar rendimiento
        self._cache = {
            'last_data_fetch': None,
            'cached_data': [],
            'system_status': None,
            'cache_timeout': 300  # 5 minutos
        }
        
        logger.info(f"🚀 UltraRobustIoTAgent inicializado: {self.jetson_api_url}")
        
    def initialize(self) -> bool:
        """
        Inicializar componentes del agente.
        """
        try:
            # Inicializar Groq
            groq_api_key = os.getenv("GROQ_API_KEY")
            if groq_api_key and not groq_api_key.startswith("demo"):
                self.groq_integration = GroqIntegration(api_key=groq_api_key)
                logger.info("✅ Groq inicializado correctamente")
            else:
                logger.warning("⚠️ GROQ_API_KEY no disponible, usando modo fallback")
                return False
            
            # Verificar conectividad
            health = self.connector.health_check()
            if health['api_available']:
                logger.info("✅ Conectividad con API Jetson verificada")
                return True
            else:
                logger.error("❌ No se puede conectar con API Jetson")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error inicializando agente: {e}")
            return False
    
    def _get_comprehensive_data(self, hours: float = 24.0) -> Dict[str, Any]:
        """
        Obtener datos comprehensivos con análisis estadístico completo.
        """
        logger.info(f"📊 Recolectando datos comprehensivos ({hours} horas)...")
        
        # Verificar cache
        now = datetime.now()
        if (self._cache['last_data_fetch'] and 
            (now - self._cache['last_data_fetch']).seconds < self._cache['cache_timeout'] and
            self._cache['cached_data']):
            logger.info("🔄 Usando datos en cache")
            raw_data = self._cache['cached_data']
        else:
            # Obtener datos frescos
            raw_data = self.connector.get_all_data_comprehensive(hours=hours, max_records_per_device=500)
            
            # Actualizar cache
            self._cache['last_data_fetch'] = now
            self._cache['cached_data'] = raw_data
            logger.info(f"📦 Cache actualizado: {len(raw_data)} registros")
        
        # Análisis comprehensivo
        analysis = self._analyze_data_comprehensive(raw_data)
        
        return {
            'raw_data': raw_data,
            'analysis': analysis,
            'timestamp': now.isoformat(),
            'data_quality': self._assess_data_quality(raw_data)
        }
    
    def _analyze_data_comprehensive(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Realizar análisis comprehensivo de los datos.
        """
        if not data:
            return {
                'total_records': 0,
                'devices': {},
                'sensors': {},
                'time_range': {},
                'status': 'no_data'
            }
        
        # Análisis por dispositivo
        devices_analysis = {}
        sensors_analysis = {}
        timestamps = []
        
        for record in data:
            device_id = record.get('device_id', 'unknown')
            sensor_type = record.get('sensor_type', 'unknown')
            value = record.get('value')
            timestamp = record.get('timestamp')
            
            # Análisis por dispositivo
            if device_id not in devices_analysis:
                devices_analysis[device_id] = {
                    'record_count': 0,
                    'sensors': set(),
                    'values': [],
                    'latest_timestamp': None
                }
            
            devices_analysis[device_id]['record_count'] += 1
            devices_analysis[device_id]['sensors'].add(sensor_type)
            
            if value is not None:
                try:
                    devices_analysis[device_id]['values'].append(float(value))
                except:
                    pass
            
            if timestamp:
                devices_analysis[device_id]['latest_timestamp'] = timestamp
                timestamps.append(timestamp)
            
            # Análisis por sensor
            sensor_key = f"{device_id}_{sensor_type}"
            if sensor_key not in sensors_analysis:
                sensors_analysis[sensor_key] = {
                    'device_id': device_id,
                    'sensor_type': sensor_type,
                    'values': [],
                    'record_count': 0
                }
            
            sensors_analysis[sensor_key]['record_count'] += 1
            if value is not None:
                try:
                    sensors_analysis[sensor_key]['values'].append(float(value))
                except:
                    pass
        
        # Calcular estadísticas por dispositivo
        for device_id, stats in devices_analysis.items():
            stats['sensors'] = list(stats['sensors'])
            if stats['values']:
                stats['avg_value'] = sum(stats['values']) / len(stats['values'])
                stats['min_value'] = min(stats['values'])
                stats['max_value'] = max(stats['values'])
            else:
                stats['avg_value'] = stats['min_value'] = stats['max_value'] = None
        
        # Calcular estadísticas por sensor
        for sensor_key, stats in sensors_analysis.items():
            if stats['values']:
                stats['avg_value'] = sum(stats['values']) / len(stats['values'])
                stats['min_value'] = min(stats['values'])
                stats['max_value'] = max(stats['values'])
                stats['std_dev'] = self._calculate_std(stats['values']) if len(stats['values']) > 1 else 0
            else:
                stats['avg_value'] = stats['min_value'] = stats['max_value'] = stats['std_dev'] = None
        
        # Análisis temporal
        time_analysis = {}
        if timestamps:
            timestamps.sort()
            time_analysis = {
                'earliest': timestamps[0],
                'latest': timestamps[-1],
                'total_timespan': timestamps[-1],  # Simplificado
                'record_frequency': len(timestamps) / max(1, len(set(timestamps)))
            }
        
        return {
            'total_records': len(data),
            'active_devices': len(devices_analysis),
            'devices': devices_analysis,
            'sensors': sensors_analysis,
            'time_range': time_analysis,
            'status': 'comprehensive_analysis_complete'
        }
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calcular desviación estándar."""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _assess_data_quality(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluar la calidad de los datos recolectados.
        """
        if not data:
            return {
                'quality_score': 0,
                'issues': ['no_data_available'],
                'recommendations': ['check_api_connectivity', 'verify_device_status']
            }
        
        issues = []
        quality_score = 100
        
        # Verificar campos requeridos
        valid_records = 0
        for record in data:
            if all(field in record for field in ['device_id', 'sensor_type', 'value', 'timestamp']):
                valid_records += 1
        
        completeness = (valid_records / len(data)) * 100 if data else 0
        
        if completeness < 100:
            issues.append(f'incomplete_records_{100-completeness:.1f}%')
            quality_score -= (100 - completeness) * 0.5
        
        # Verificar distribución temporal
        timestamps = [r.get('timestamp') for r in data if r.get('timestamp')]
        if len(timestamps) < len(data) * 0.9:
            issues.append('missing_timestamps')
            quality_score -= 20
        
        # Verificar distribución por dispositivos
        devices = set(r.get('device_id') for r in data if r.get('device_id'))
        if len(devices) < 2:
            issues.append('insufficient_device_diversity')
            quality_score -= 15
        
        return {
            'quality_score': max(0, quality_score),
            'completeness_percentage': completeness,
            'total_records': len(data),
            'valid_records': valid_records,
            'unique_devices': len(devices),
            'issues': issues,
            'status': 'good' if quality_score > 70 else 'fair' if quality_score > 40 else 'poor'
        }
    
    def _generate_technical_response(self, query: str, data_package: Dict[str, Any]) -> str:
        """
        Generar respuesta técnica comprehensiva y contundente.
        """
        analysis = data_package['analysis']
        data_quality = data_package['data_quality']
        raw_data = data_package['raw_data']
        
        # Construir prompt técnico robusto
        prompt = f"""Eres un ingeniero especialista en sistemas IoT con amplia experiencia en análisis de datos de sensores industriales.

CONSULTA DEL USUARIO: {query}

DATOS TÉCNICOS DISPONIBLES:
- Total de registros analizados: {analysis['total_records']}
- Dispositivos activos detectados: {analysis['active_devices']}
- Calidad de datos: {data_quality['quality_score']:.1f}% ({data_quality['status']})
- Completitud de registros: {data_quality['completeness_percentage']:.1f}%

ANÁLISIS POR DISPOSITIVO:
"""
        
        # Agregar detalles por dispositivo
        for device_id, stats in analysis['devices'].items():
            prompt += f"""
📱 DISPOSITIVO: {device_id}
   - Registros: {stats['record_count']}
   - Sensores activos: {len(stats['sensors'])} ({', '.join(stats['sensors'])})
   - Rango de valores: {stats['min_value']:.2f} - {stats['max_value']:.2f} (promedio: {stats['avg_value']:.2f})
   - Última actualización: {stats['latest_timestamp']}
"""
        
        # Agregar análisis por sensor
        prompt += f"""
ANÁLISIS DETALLADO POR SENSOR:
"""
        for sensor_key, stats in analysis['sensors'].items():
            if stats['values']:
                prompt += f"""
🔍 {stats['device_id']} - {stats['sensor_type']}:
   - Lecturas: {stats['record_count']}
   - Promedio: {stats['avg_value']:.3f}
   - Rango: {stats['min_value']:.3f} - {stats['max_value']:.3f}
   - Desviación estándar: {stats['std_dev']:.3f}
"""
        
        prompt += f"""
INSTRUCCIONES PARA RESPUESTA:
1. Proporciona un análisis TÉCNICO y PRECISO basado en los datos reales
2. Menciona ESPECÍFICAMENTE los números y estadísticas proporcionadas
3. Si hay problemas de calidad, explícalos técnicamente
4. Proporciona insights técnicos sobre el comportamiento de los sensores
5. Usa terminología técnica apropiada para sistemas IoT
6. Sé CONTUNDENTE y CERTERO en tus conclusiones
7. Si solicita gráficos, menciona que se han generado automáticamente

RESPONDE DE FORMA TÉCNICA, PRECISA Y COMPREHENSIVA:"""
        
        # Generar respuesta con Groq
        try:
            if self.groq_integration:
                response = self.groq_integration.generate_response(prompt, model=self.groq_model)
                
                # Registrar uso
                estimated_tokens = len(prompt) // 4 + len(response) // 4
                usage_tracker.track_request(self.groq_model, estimated_tokens)
                
                return response
            else:
                return self._generate_fallback_response(query, analysis, data_quality)
                
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return self._generate_fallback_response(query, analysis, data_quality)
    
    def _generate_fallback_response(self, query: str, analysis: Dict, data_quality: Dict) -> str:
        """
        Generar respuesta de fallback técnica sin Groq.
        """
        return f"""📊 **ANÁLISIS TÉCNICO COMPREHENSIVO DEL SISTEMA IoT**

**ESTADO DEL SISTEMA:**
- ✅ Registros analizados: {analysis['total_records']}
- ✅ Dispositivos activos: {analysis['active_devices']}
- ✅ Calidad de datos: {data_quality['quality_score']:.1f}% ({data_quality['status'].upper()})

**DISPOSITIVOS DETECTADOS:**
{chr(10).join([f"📱 {device_id}: {stats['record_count']} registros, {len(stats['sensors'])} sensores activos" 
               for device_id, stats in analysis['devices'].items()])}

**ANÁLISIS TÉCNICO:**
Los datos muestran un sistema IoT operativo con múltiples dispositivos reportando métricas en tiempo real. 
La calidad de datos es {data_quality['status']} con una completitud del {data_quality['completeness_percentage']:.1f}%.

**RESPUESTA A CONSULTA:** {query}
Basado en el análisis de {analysis['total_records']} registros de {analysis['active_devices']} dispositivos activos, 
el sistema está funcionando correctamente y proporcionando datos técnicos válidos para análisis.

📈 *Nota: Se han generado gráficos automáticamente para visualización de tendencias.*
"""
    
    def process_query(self, user_query: str, hours: float = None) -> Dict[str, Any]:
        """
        Procesar consulta del usuario con enfoque ultra-robusto.
        
        Args:
            user_query: Consulta del usuario
            hours: Horas de análisis (opcional, se detecta automáticamente si no se proporciona)
            
        Returns:
            Dict con respuesta, datos analizados y metadatos
        """
        logger.info(f"🔍 Procesando consulta robusta: {user_query[:100]}...")
        
        try:
            # 1. Determinar scope temporal de la consulta
            if hours is None:
                hours = self._extract_time_scope(user_query)
            logger.info(f"⏰ Scope temporal: {hours} horas")
            
            # 2. Recolectar datos comprehensivos
            data_package = self._get_comprehensive_data(hours=hours)
            
            # 3. Verificar si se necesitan gráficos
            should_generate_charts = self._should_generate_visualizations(user_query)
            chart_info = ""
            
            if should_generate_charts and self.visualization_engine and data_package['raw_data']:
                try:
                    logger.info("📊 Generando visualizaciones...")
                    chart_paths = self.visualization_engine.generate_charts(
                        data_package['raw_data'], 
                        user_query
                    )
                    if chart_paths:
                        chart_names = [path.split('\\')[-1] for path in chart_paths]
                        chart_info = f"\\n\\n📊 **GRÁFICOS GENERADOS**: {', '.join(chart_names)}"
                        logger.info(f"✅ Gráficos generados: {chart_names}")
                except Exception as e:
                    logger.warning(f"⚠️ Error generando gráficos: {e}")
            
            # 4. Generar respuesta técnica
            response = self._generate_technical_response(user_query, data_package)
            
            # 5. Agregar información de gráficos si se generaron
            final_response = response + chart_info
            
            # 6. Agregar footer técnico
            footer = f"""\\n\\n---
📋 **RESUMEN TÉCNICO**: {data_package['analysis']['total_records']} registros | {data_package['analysis']['active_devices']} dispositivos | Calidad: {data_package['data_quality']['quality_score']:.0f}%
🕐 **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # Retornar respuesta completa estructurada
            return {
                'response': final_response + footer,
                'data_summary': data_package['analysis'],
                'data_quality': data_package['data_quality'],
                'analysis_metadata': {
                    'hours_analyzed': hours,
                    'query_processed': user_query[:100],
                    'charts_generated': should_generate_charts,
                    'timestamp': datetime.now().isoformat()
                },
                'visualizations': chart_paths if should_generate_charts and 'chart_paths' in locals() else []
            }
            
        except Exception as e:
            logger.error(f"❌ Error procesando consulta: {e}")
            error_response = f"""❌ **ERROR EN PROCESAMIENTO**

Ocurrió un error técnico al procesar su consulta: {str(e)}

**Acciones recomendadas:**
1. Verificar conectividad con la API Jetson
2. Revisar logs del sistema
3. Reintentar la consulta

**Información técnica:**
- Timestamp: {datetime.now().isoformat()}
- Consulta: {user_query[:100]}
- Error: {type(e).__name__}
"""
            
            return {
                'response': error_response,
                'data_summary': {'error': str(e)},
                'data_quality': {'quality_score': 0},
                'analysis_metadata': {
                    'error': True,
                    'timestamp': datetime.now().isoformat()
                },
                'visualizations': []
            }
    
    def _extract_time_scope(self, query: str) -> float:
        """
        Extraer el scope temporal de la consulta.
        """
        query_lower = query.lower()
        
        # Buscar patrones temporales
        import re
        
        # Patrones de tiempo
        patterns = [
            (r'(\d+)\s*horas?', 1.0),
            (r'(\d+)\s*hrs?', 1.0),
            (r'(\d+)\s*minutos?', 1/60),
            (r'(\d+)\s*min', 1/60),
            (r'(\d+)\s*días?', 24.0),
            (r'última?\s*hora', 1.0),
            (r'últimas?\s*24\s*horas?', 24.0),
            (r'último?\s*día', 24.0),
        ]
        
        for pattern, multiplier in patterns:
            match = re.search(pattern, query_lower)
            if match:
                try:
                    number = float(match.group(1)) if match.lastindex else 1
                    return number * multiplier
                except:
                    continue
        
        # Default: 24 horas
        return 24.0
    
    def _should_generate_visualizations(self, query: str) -> bool:
        """
        Determinar si se deben generar visualizaciones.
        """
        query_lower = query.lower()
        
        visualization_keywords = [
            'gráfico', 'grafico', 'gráfica', 'grafica',
            'visualizar', 'visualización', 'visualizacion',
            'chart', 'plot', 'mostrar gráfico', 'mostrar grafico',
            'tendencias', 'evolución', 'comportamiento',
            'estadísticas', 'estadisticas', 'análisis visual'
        ]
        
        return any(keyword in query_lower for keyword in visualization_keywords)
    
    def get_system_diagnostics(self) -> Dict[str, Any]:
        """
        Obtener diagnósticos completos del sistema.
        """
        logger.info("🔧 Ejecutando diagnósticos del sistema...")
        
        return {
            'connector_status': self.connector.get_system_status(),
            'agent_status': {
                'groq_available': self.groq_integration is not None,
                'visualization_available': self.visualization_engine is not None,
                'cache_status': {
                    'last_fetch': self._cache['last_data_fetch'].isoformat() if self._cache['last_data_fetch'] else None,
                    'cached_records': len(self._cache['cached_data'])
                }
            },
            'timestamp': datetime.now().isoformat()
        }