"""
Motor de Insights Automáticos para IoT
=====================================

Sistema inteligente que genera conclusiones automáticas, detecta patrones complejos,
proporciona recomendaciones contextuales y alertas predictivas.

Este motor transforma datos en conocimiento accionable y proactivo.
"""

import logging
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import statistics
from enum import Enum

logger = logging.getLogger(__name__)

class InsightType(Enum):
    """Tipos de insights automáticos"""
    ANOMALY_PATTERN = "anomaly_pattern"
    PREDICTIVE_ALERT = "predictive_alert"
    MAINTENANCE_SUGGESTION = "maintenance_suggestion"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    CORRELATION_DISCOVERY = "correlation_discovery"
    TREND_ANALYSIS = "trend_analysis"
    SYSTEM_HEALTH = "system_health"
    ENVIRONMENTAL_FACTOR = "environmental_factor"

class Priority(Enum):
    """Niveles de prioridad para insights"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFORMATIONAL = 5

@dataclass
class AutomaticInsight:
    """Insight generado automáticamente"""
    id: str
    type: InsightType
    priority: Priority
    title: str
    description: str
    evidence: Dict[str, Any]
    confidence: float  # 0.0 to 1.0
    affected_entities: List[str]  # devices, sensors, etc.
    generated_at: datetime
    
    # Campos de acción
    recommended_actions: List[str] = field(default_factory=list)
    estimated_impact: Optional[str] = None
    time_sensitivity: Optional[str] = None  # 'immediate', 'hours', 'days', 'weeks'
    
    # Contexto adicional
    related_insights: List[str] = field(default_factory=list)
    historical_context: Optional[Dict] = None
    predictive_context: Optional[Dict] = None

@dataclass
class PatternSignature:
    """Firma de un patrón detectado"""
    pattern_id: str
    pattern_type: str
    features: Dict[str, Any]
    confidence: float
    occurrences: int
    first_seen: datetime
    last_seen: datetime

class AutomaticInsightsEngine:
    """
    Motor avanzado de generación automática de insights.
    
    Capacidades:
    - Detección automática de patrones complejos
    - Generación de alertas predictivas
    - Análisis contextual inteligente
    - Recomendaciones proactivas
    - Aprendizaje de patrones históricos
    - Correlación automática de eventos
    """
    
    def __init__(self, jetson_api_url: str):
        self.jetson_api_url = jetson_api_url
        self.logger = logging.getLogger(__name__)
        
        # Cache de patrones aprendidos
        self.learned_patterns: Dict[str, PatternSignature] = {}
        self.insight_history: deque = deque(maxlen=1000)  # Últimos 1000 insights
        
        # Configuración de detección
        self.pattern_confidence_threshold = 0.6
        self.anomaly_sensitivity = 0.8
        self.prediction_horizon_hours = 24
        
        # Base de conocimiento de patrones conocidos
        self.knowledge_base = {
            'temperature_patterns': {
                'daily_cycle': {
                    'description': 'Ciclo diario normal de temperatura',
                    'indicators': ['periodic_variation', 'time_correlation'],
                    'normal_range': (15, 35),
                    'concern_threshold': 40
                },
                'heating_event': {
                    'description': 'Evento de calentamiento rápido',
                    'indicators': ['rapid_increase', 'sustained_high'],
                    'rate_threshold': 2.0,  # °C per hour
                    'duration_threshold': 30  # minutes
                },
                'sensor_drift': {
                    'description': 'Deriva gradual del sensor',
                    'indicators': ['gradual_change', 'bias_shift'],
                    'drift_rate': 0.1,  # °C per day
                    'detection_window': 168  # hours (1 week)
                }
            },
            'luminosity_patterns': {
                'light_cycle': {
                    'description': 'Ciclo natural de luz',
                    'indicators': ['day_night_pattern', 'solar_correlation'],
                    'expected_range': (0, 1000),
                    'anomaly_threshold': 2000
                },
                'artificial_lighting': {
                    'description': 'Iluminación artificial detectada',
                    'indicators': ['constant_level', 'square_wave'],
                    'stability_threshold': 50,
                    'duration_threshold': 120  # minutes
                }
            },
            'system_patterns': {
                'communication_issues': {
                    'description': 'Problemas de comunicación',
                    'indicators': ['data_gaps', 'irregular_timing'],
                    'gap_threshold': 300,  # seconds
                    'frequency_variation': 0.5
                },
                'device_degradation': {
                    'description': 'Degradación gradual del dispositivo',
                    'indicators': ['increasing_noise', 'reduced_accuracy'],
                    'noise_increase_rate': 0.1,
                    'accuracy_decline_rate': 0.05
                }
            }
        }
        
        # Templates de recomendaciones
        self.recommendation_templates = {
            InsightType.ANOMALY_PATTERN: [
                "Investigar la causa raíz de la anomalía detectada",
                "Verificar el estado físico del sensor afectado",
                "Considerar recalibración si el patrón persiste"
            ],
            InsightType.PREDICTIVE_ALERT: [
                "Tomar acción preventiva antes de que ocurra el problema",
                "Aumentar la frecuencia de monitoreo",
                "Preparar recursos para intervención si es necesaria"
            ],
            InsightType.MAINTENANCE_SUGGESTION: [
                "Programar mantenimiento preventivo",  
                "Verificar conexiones y alimentación",
                "Evaluar necesidad de reemplazo de componentes"
            ],
            InsightType.PERFORMANCE_OPTIMIZATION: [
                "Ajustar configuración para mejorar rendimiento",
                "Optimizar frecuencia de muestreo",
                "Considerar actualización de firmware"
            ]
        }
    
    async def analyze_and_generate_insights(self, raw_data: List[Dict], 
                                          smart_analysis: Dict,
                                          sensor_inventory: Dict) -> List[AutomaticInsight]:
        """
        Genera insights automáticos basados en análisis inteligente.
        
        Args:
            raw_data: Datos originales del sistema
            smart_analysis: Análisis previo del SmartAnalyzer
            sensor_inventory: Inventario dinámico de sensores
            
        Returns:
            Lista de insights automáticos generados
        """
        try:
            self.logger.info("🧠 Iniciando generación automática de insights...")
            
            insights = []
            
            if not raw_data:
                return insights
            
            df = pd.DataFrame(raw_data)
            
            # 1. ANÁLISIS DE PATRONES AUTOMÁTICO
            pattern_insights = await self._detect_automatic_patterns(df, smart_analysis)
            insights.extend(pattern_insights)
            
            # 2. GENERACIÓN DE ALERTAS PREDICTIVAS
            predictive_insights = await self._generate_predictive_alerts(df, smart_analysis)
            insights.extend(predictive_insights)
            
            # 3. DETECCIÓN DE CORRELACIONES COMPLEJAS
            correlation_insights = await self._detect_complex_correlations(df)
            insights.extend(correlation_insights)
            
            # 4. ANÁLISIS DE SALUD DEL SISTEMA
            health_insights = await self._analyze_system_health(df, smart_analysis, sensor_inventory)
            insights.extend(health_insights)
            
            # 5. SUGERENCIAS DE MANTENIMIENTO INTELIGENTE
            maintenance_insights = await self._generate_maintenance_suggestions(df, smart_analysis)
            insights.extend(maintenance_insights)
            
            # 6. OPTIMIZACIONES DE RENDIMIENTO
            performance_insights = await self._suggest_performance_optimizations(df, sensor_inventory)
            insights.extend(performance_insights)
            
            # 7. ANÁLISIS AMBIENTAL CONTEXTUAL
            environmental_insights = await self._analyze_environmental_factors(df)
            insights.extend(environmental_insights)
            
            # 8. POST-PROCESAMIENTO: PRIORIZACIÓN Y DEDUPLICACIÓN
            processed_insights = await self._process_and_prioritize_insights(insights)
            
            # 9. ACTUALIZAR HISTORIA DE INSIGHTS
            self.insight_history.extend(processed_insights)
            
            self.logger.info(f"✅ Generated {len(processed_insights)} automatic insights")
            
            return processed_insights
            
        except Exception as e:
            self.logger.error(f"❌ Error generating automatic insights: {e}")
            return []
    
    async def _detect_automatic_patterns(self, df: pd.DataFrame, smart_analysis: Dict) -> List[AutomaticInsight]:
        """Detecta patrones automáticamente usando knowledge base"""
        insights = []
        
        try:
            # Analizar patrones por tipo de sensor
            for sensor_type in df['sensor_type'].unique():
                sensor_data = df[df['sensor_type'] == sensor_type]
                
                if len(sensor_data) < 10:  # Necesitamos datos suficientes
                    continue
                
                # Determinar categoría del sensor
                sensor_category = self._categorize_sensor(sensor_type)
                
                if sensor_category in self.knowledge_base:
                    patterns = self.knowledge_base[sensor_category]
                    
                    for pattern_name, pattern_config in patterns.items():
                        pattern_detected = await self._check_pattern_match(
                            sensor_data, pattern_config, sensor_type
                        )
                        
                        if pattern_detected:
                            insight = self._create_pattern_insight(
                                pattern_name, pattern_config, pattern_detected, sensor_type
                            )
                            if insight:
                                insights.append(insight)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error detecting automatic patterns: {e}")
        
        return insights
    
    async def _generate_predictive_alerts(self, df: pd.DataFrame, smart_analysis: Dict) -> List[AutomaticInsight]:
        """Genera alertas predictivas basadas en tendencias"""
        insights = []
        
        try:
            predictions = smart_analysis.get('predictions', {})
            
            for prediction_key, prediction_data in predictions.items():
                device_id = prediction_data.get('device_id')
                sensor_type = prediction_data.get('sensor_type')
                current_value = prediction_data.get('current_value')
                predicted_value = prediction_data.get('predicted_next_hour')
                trend_direction = prediction_data.get('trend_direction')
                confidence = prediction_data.get('confidence', 0)
                
                if confidence < 0.6:  # Solo alertas con confianza suficiente
                    continue
                
                # Detectar situaciones que requieren alerta predictiva
                alert_conditions = []
                
                # 1. Tendencia peligrosa
                if trend_direction in ['increasing', 'decreasing']:
                    change_rate = abs(predicted_value - current_value)
                    
                    if self._is_dangerous_trend(sensor_type, current_value, predicted_value, change_rate):
                        alert_conditions.append('dangerous_trend')
                
                # 2. Cruce de umbral
                if self._will_cross_threshold(sensor_type, current_value, predicted_value):
                    alert_conditions.append('threshold_crossing')
                
                # 3. Comportamiento anómalo predicho
                if self._is_anomalous_prediction(sensor_type, predicted_value):
                    alert_conditions.append('anomalous_prediction')
                
                # Crear insight predictivo si hay condiciones
                if alert_conditions:
                    insight = AutomaticInsight(
                        id=f"pred_{device_id}_{sensor_type}_{datetime.now().strftime('%H%M%S')}",
                        type=InsightType.PREDICTIVE_ALERT,
                        priority=Priority.HIGH if 'dangerous_trend' in alert_conditions else Priority.MEDIUM,
                        title=f"Alerta Predictiva: {sensor_type} en {device_id}",
                        description=f"Se predice que el sensor {sensor_type} pasará de {current_value:.2f} a {predicted_value:.2f} en la próxima hora. "
                                  f"Tendencia {trend_direction} detectada.",
                        evidence={
                            'current_value': current_value,
                            'predicted_value': predicted_value,
                            'trend_direction': trend_direction,
                            'confidence': confidence,
                            'conditions': alert_conditions
                        },
                        confidence=confidence,
                        affected_entities=[device_id, sensor_type],
                        generated_at=datetime.now(),
                        recommended_actions=self._get_predictive_actions(sensor_type, alert_conditions),
                        time_sensitivity='hours',
                        estimated_impact='medium' if confidence > 0.8 else 'low'
                    )
                    
                    insights.append(insight)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error generating predictive alerts: {e}")
        
        return insights
    
    async def _detect_complex_correlations(self, df: pd.DataFrame) -> List[AutomaticInsight]:
        """Detecta correlaciones complejas entre sensores"""
        insights = []
        
        try:
            # Crear matriz pivote para correlaciones
            pivot_df = df.pivot_table(
                values='value',
                index='timestamp',
                columns=['device_id', 'sensor_type'],
                aggfunc='mean'
            ).fillna(method='ffill').fillna(method='bfill')
            
            if pivot_df.shape[1] < 2:
                return insights
            
            # Calcular correlaciones
            correlation_matrix = pivot_df.corr()
            
            # Buscar correlaciones interesantes
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    
                    if pd.isna(corr_value):
                        continue
                    
                    sensor1 = correlation_matrix.columns[i]
                    sensor2 = correlation_matrix.columns[j]
                    
                    # Correlaciones fuertes (>0.8 o <-0.8)
                    if abs(corr_value) > 0.8:
                        insight_type = "positive" if corr_value > 0 else "negative"
                        
                        # Determinar si esta correlación es esperada o sorprendente
                        is_expected = self._is_expected_correlation(sensor1, sensor2, corr_value)
                        
                        if not is_expected:  # Solo reportar correlaciones inesperadas
                            insight = AutomaticInsight(
                                id=f"corr_{hash(str(sensor1) + str(sensor2))}",
                                type=InsightType.CORRELATION_DISCOVERY,
                                priority=Priority.MEDIUM,
                                title=f"Correlación {insight_type} inesperada detectada",
                                description=f"Correlación {insight_type} fuerte ({corr_value:.3f}) detectada entre "
                                          f"{sensor1[1]} en {sensor1[0]} y {sensor2[1]} en {sensor2[0]}. "
                                          f"Esta correlación no era esperada y merece investigación.",
                                evidence={
                                    'correlation_coefficient': corr_value,
                                    'sensor1': sensor1,
                                    'sensor2': sensor2,
                                    'correlation_type': insight_type,
                                    'is_expected': is_expected
                                },
                                confidence=min(abs(corr_value), 0.95),
                                affected_entities=[sensor1[0], sensor2[0]],
                                generated_at=datetime.now(),
                                recommended_actions=[
                                    "Investigar la causa física de esta correlación",
                                    "Verificar si existe interferencia entre sensores",
                                    "Evaluar si indica un problema sistémico común"
                                ],
                                time_sensitivity='days',
                                estimated_impact='medium'
                            )
                            
                            insights.append(insight)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error detecting correlations: {e}")
        
        return insights
    
    async def _analyze_system_health(self, df: pd.DataFrame, smart_analysis: Dict, 
                                   sensor_inventory: Dict) -> List[AutomaticInsight]:
        """Analiza salud general del sistema y genera insights"""
        insights = []
        
        try:
            health_score = smart_analysis.get('health_score', 0)
            devices_analyzed = smart_analysis.get('devices_analyzed', [])
            
            # 1. ANÁLISIS DE SALUD GENERAL
            if health_score < 50:
                priority = Priority.CRITICAL
                urgency = 'immediate'
            elif health_score < 75:
                priority = Priority.HIGH
                urgency = 'hours'
            else:
                priority = Priority.LOW
                urgency = 'days'
            
            # Crear insight de salud general
            health_insight = AutomaticInsight(
                id=f"health_general_{datetime.now().strftime('%Y%m%d_%H%M')}",
                type=InsightType.SYSTEM_HEALTH,
                priority=priority,
                title=f"Salud del Sistema: {health_score:.1f}%",
                description=self._generate_health_description(health_score, smart_analysis),
                evidence={
                    'health_score': health_score,
                    'devices_count': len(devices_analyzed),
                    'anomalies_count': len(smart_analysis.get('anomalies', [])),
                    'sensor_insights_count': len(smart_analysis.get('sensor_insights', []))
                },
                confidence=smart_analysis.get('confidence_level', 0.5),
                affected_entities=devices_analyzed,
                generated_at=datetime.now(),
                recommended_actions=self._get_health_actions(health_score),
                time_sensitivity=urgency,
                estimated_impact='high' if health_score < 70 else 'medium'
            )
            
            insights.append(health_insight)
            
            # 2. ANÁLISIS DE DISPONIBILIDAD DE DISPOSITIVOS
            device_availability = await self._analyze_device_availability(df, sensor_inventory)
            if device_availability:
                insights.extend(device_availability)
            
            # 3. ANÁLISIS DE CALIDAD DE DATOS
            data_quality_insights = await self._analyze_data_quality(df)
            insights.extend(data_quality_insights)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error analyzing system health: {e}")
        
        return insights
    
    async def _generate_maintenance_suggestions(self, df: pd.DataFrame, smart_analysis: Dict) -> List[AutomaticInsight]:
        """Genera sugerencias inteligentes de mantenimiento"""
        insights = []
        
        try:
            sensor_insights = smart_analysis.get('sensor_insights', [])
            
            # Agrupar insights por dispositivo para análisis de mantenimiento
            device_issues = defaultdict(list)
            
            for insight in sensor_insights:
                device_id = insight.device_id
                device_issues[device_id].append(insight)
            
            # Analizar cada dispositivo para mantenimiento
            for device_id, issues in device_issues.items():
                maintenance_needed = False
                maintenance_reasons = []
                priority_level = Priority.LOW
                
                # Detectar patrones que indican necesidad de mantenimiento
                critical_issues = [i for i in issues if i.severity == 'critical']
                warning_issues = [i for i in issues if i.severity == 'warning']
                
                if critical_issues:
                    maintenance_needed = True
                    priority_level = Priority.CRITICAL
                    maintenance_reasons.append(f"{len(critical_issues)} problemas críticos detectados")
                
                elif len(warning_issues) >= 3:
                    maintenance_needed = True
                    priority_level = Priority.HIGH
                    maintenance_reasons.append(f"{len(warning_issues)} advertencias acumuladas")
                
                # Detectar patrones específicos de mantenimiento
                maintenance_patterns = self._detect_maintenance_patterns(issues)
                if maintenance_patterns:
                    maintenance_needed = True
                    maintenance_reasons.extend(maintenance_patterns)
                
                # Crear insight de mantenimiento si es necesario
                if maintenance_needed:
                    maintenance_insight = AutomaticInsight(
                        id=f"maint_{device_id}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                        type=InsightType.MAINTENANCE_SUGGESTION,
                        priority=priority_level,
                        title=f"Mantenimiento recomendado para {device_id}",
                        description=f"El análisis indica necesidad de mantenimiento para {device_id}. "
                                  f"Razones: {', '.join(maintenance_reasons)}",
                        evidence={
                            'device_id': device_id,
                            'critical_issues': len(critical_issues),
                            'warning_issues': len(warning_issues),
                            'maintenance_reasons': maintenance_reasons
                        },
                        confidence=0.8 if critical_issues else 0.6,
                        affected_entities=[device_id],
                        generated_at=datetime.now(),
                        recommended_actions=self._get_maintenance_actions(device_id, issues),
                        time_sensitivity='days' if priority_level == Priority.CRITICAL else 'weeks',
                        estimated_impact='high' if critical_issues else 'medium'
                    )
                    
                    insights.append(maintenance_insight)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error generating maintenance suggestions: {e}")
        
        return insights
    
    async def _suggest_performance_optimizations(self, df: pd.DataFrame, sensor_inventory: Dict) -> List[AutomaticInsight]:
        """Sugiere optimizaciones de rendimiento del sistema"""
        insights = []
        
        try:
            # 1. ANÁLISIS DE FRECUENCIA DE MUESTREO
            sampling_analysis = await self._analyze_sampling_frequency(df)
            if sampling_analysis:
                insights.append(sampling_analysis)
            
            # 2. ANÁLISIS DE EFICIENCIA DE DATOS
            data_efficiency = await self._analyze_data_efficiency(df)
            if data_efficiency:
                insights.append(data_efficiency)
            
            # 3. OPTIMIZACIÓN DE CONFIGURACIÓN DE SENSORES
            sensor_config_opts = await self._suggest_sensor_optimizations(df, sensor_inventory)
            insights.extend(sensor_config_opts)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error suggesting optimizations: {e}")
        
        return insights
    
    async def _analyze_environmental_factors(self, df: pd.DataFrame) -> List[AutomaticInsight]:
        """Analiza factores ambientales que podrían afectar las lecturas"""
        insights = []
        
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.day_of_week
            
            # Analizar patrones temporales que sugieren factores ambientales
            for sensor_type in df['sensor_type'].unique():
                sensor_data = df[df['sensor_type'] == sensor_type]
                
                if len(sensor_data) < 24:  # Necesitamos al menos un día de datos
                    continue
                
                # Análisis por hora del día
                hourly_pattern = sensor_data.groupby('hour')['value'].agg(['mean', 'std']).reset_index()
                
                # Detectar patrones ambientales
                environmental_patterns = self._detect_environmental_patterns(hourly_pattern, sensor_type)
                
                for pattern in environmental_patterns:
                    insight = AutomaticInsight(
                        id=f"env_{sensor_type}_{pattern['type']}_{datetime.now().strftime('%H%M%S')}",
                        type=InsightType.ENVIRONMENTAL_FACTOR,
                        priority=Priority.INFORMATIONAL,
                        title=f"Factor ambiental detectado: {pattern['title']}",
                        description=pattern['description'],
                        evidence=pattern['evidence'],
                        confidence=pattern['confidence'],
                        affected_entities=[sensor_type],
                        generated_at=datetime.now(),
                        recommended_actions=pattern.get('actions', []),
                        time_sensitivity='weeks',
                        estimated_impact='low'
                    )
                    
                    insights.append(insight)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error analyzing environmental factors: {e}")
        
        return insights
    
    async def _process_and_prioritize_insights(self, insights: List[AutomaticInsight]) -> List[AutomaticInsight]:
        """Post-procesa y prioriza insights generados"""
        try:
            # 1. DEDUPLICACIÓN
            unique_insights = self._deduplicate_insights(insights)
            
            # 2. PRIORIZACIÓN INTELIGENTE
            prioritized_insights = self._intelligent_prioritization(unique_insights)
            
            # 3. ENRIQUECIMIENTO CONTEXTUAL
            enriched_insights = await self._enrich_with_context(prioritized_insights)
            
            # 4. LIMITACIÓN POR RELEVANCIA (top insights)
            final_insights = self._limit_by_relevance(enriched_insights, max_insights=20)
            
            return final_insights
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error processing insights: {e}")
            return insights
    
    # MÉTODOS AUXILIARES
    
    def _categorize_sensor(self, sensor_type: str) -> str:
        """Categoriza un sensor según su tipo"""
        sensor_lower = sensor_type.lower()
        
        if any(keyword in sensor_lower for keyword in ['temp', 'ntc', 't1', 't2', 'avg']):
            return 'temperature_patterns'
        elif any(keyword in sensor_lower for keyword in ['ldr', 'light', 'lumino']):
            return 'luminosity_patterns'
        else:
            return 'system_patterns'
    
    async def _check_pattern_match(self, sensor_data: pd.DataFrame, 
                                 pattern_config: Dict, sensor_type: str) -> Optional[Dict]:
        """Verifica si los datos coinciden con un patrón específico"""
        try:
            values = sensor_data['value'].values
            
            if pattern_config.get('description') == 'Ciclo diario normal de temperatura':
                # Verificar si hay variación cíclica
                if len(values) >= 24:  # Al menos 24 horas
                    # Calcular variación horaria
                    sensor_data_copy = sensor_data.copy()
                    sensor_data_copy['timestamp'] = pd.to_datetime(sensor_data_copy['timestamp'])
                    sensor_data_copy['hour'] = sensor_data_copy['timestamp'].dt.hour
                    
                    hourly_means = sensor_data_copy.groupby('hour')['value'].mean()
                    variation = hourly_means.max() - hourly_means.min()
                    
                    if variation > 2.0:  # Variación significativa
                        return {
                            'match_type': 'daily_cycle',
                            'variation': variation,
                            'confidence': min(variation / 10.0, 1.0)
                        }
            
            elif pattern_config.get('description') == 'Evento de calentamiento rápido':
                # Detectar aumentos rápidos de temperatura
                if len(values) > 1:
                    diffs = np.diff(values)
                    max_increase = np.max(diffs)
                    
                    if max_increase > pattern_config.get('rate_threshold', 2.0):
                        return {
                            'match_type': 'heating_event',
                            'max_increase': max_increase,
                            'confidence': min(max_increase / 5.0, 1.0)
                        }
            
            # Agregar más verificaciones de patrones según necesidad...
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error checking pattern match: {e}")
        
        return None
    
    def _create_pattern_insight(self, pattern_name: str, pattern_config: Dict, 
                              pattern_match: Dict, sensor_type: str) -> Optional[AutomaticInsight]:
        """Crea insight basado en patrón detectado"""
        try:
            match_type = pattern_match.get('match_type')
            confidence = pattern_match.get('confidence', 0.5)
            
            if confidence < self.pattern_confidence_threshold:
                return None
            
            # Determinar prioridad basada en el tipo de patrón
            if 'heating_event' in match_type:
                priority = Priority.HIGH
                time_sensitivity = 'immediate'
            elif 'daily_cycle' in match_type:
                priority = Priority.INFORMATIONAL
                time_sensitivity = 'days'
            else:
                priority = Priority.MEDIUM
                time_sensitivity = 'hours'
            
            insight = AutomaticInsight(
                id=f"pattern_{pattern_name}_{sensor_type}_{datetime.now().strftime('%H%M%S')}",
                type=InsightType.ANOMALY_PATTERN if 'heating' in pattern_name else InsightType.TREND_ANALYSIS,
                priority=priority,
                title=f"Patrón detectado: {pattern_config['description']}",
                description=f"Se detectó el patrón '{pattern_config['description']}' en el sensor {sensor_type}. "
                          f"Confianza: {confidence:.1%}",
                evidence={
                    'pattern_name': pattern_name,
                    'pattern_type': match_type,
                    'pattern_data': pattern_match,
                    'sensor_type': sensor_type
                },
                confidence=confidence,
                affected_entities=[sensor_type],
                generated_at=datetime.now(),
                recommended_actions=self.recommendation_templates.get(
                    InsightType.ANOMALY_PATTERN if 'heating' in pattern_name else InsightType.TREND_ANALYSIS,
                    ["Monitorear continuamente el patrón detectado"]
                ),
                time_sensitivity=time_sensitivity
            )
            
            return insight
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error creating pattern insight: {e}")
            return None
    
    def _is_dangerous_trend(self, sensor_type: str, current: float, predicted: float, rate: float) -> bool:
        """Determina si una tendencia es peligrosa"""
        sensor_category = self._categorize_sensor(sensor_type)
        
        if sensor_category == 'temperature_patterns':
            return rate > 5.0 or predicted > 45.0 or predicted < 0.0
        elif sensor_category == 'luminosity_patterns':
            return rate > 500 or predicted > 2000
        
        return False
    
    def _will_cross_threshold(self, sensor_type: str, current: float, predicted: float) -> bool:
        """Determina si se cruzará un umbral crítico"""
        sensor_category = self._categorize_sensor(sensor_type)
        
        if sensor_category == 'temperature_patterns':
            critical_high = 40.0
            critical_low = 5.0
            return (current < critical_high < predicted) or (current > critical_low > predicted)
        
        return False
    
    def _is_anomalous_prediction(self, sensor_type: str, predicted_value: float) -> bool:
        """Determina si un valor predicho es anómalo"""
        sensor_category = self._categorize_sensor(sensor_type)
        
        if sensor_category == 'temperature_patterns':
            return predicted_value > 50.0 or predicted_value < -10.0
        elif sensor_category == 'luminosity_patterns':
            return predicted_value > 3000 or predicted_value < 0
        
        return False
    
    def _get_predictive_actions(self, sensor_type: str, conditions: List[str]) -> List[str]:
        """Obtiene acciones recomendadas para alertas predictivas"""
        actions = []
        
        if 'dangerous_trend' in conditions:
            actions.append("ACCIÓN INMEDIATA: Verificar el sistema antes de que la tendencia empeore")
            
        if 'threshold_crossing' in conditions:
            actions.append("Prepararse para intervención cuando se cruce el umbral crítico")
            
        if 'anomalous_prediction' in conditions:
            actions.append("Investigar las causas del comportamiento anómalo predicho")
        
        actions.extend([
            "Aumentar frecuencia de monitoreo temporalmente",
            "Tener personal técnico disponible para respuesta rápida"
        ])
        
        return actions
    
    def _is_expected_correlation(self, sensor1: Tuple, sensor2: Tuple, correlation: float) -> bool:
        """Determina si una correlación es esperada o sorprendente"""
        # Extraer tipos de sensores
        sensor1_type = sensor1[1].lower()
        sensor2_type = sensor2[1].lower()
        
        # Correlaciones esperadas
        expected_correlations = [
            (['temp', 'ntc', 't1', 't2'], ['temp', 'ntc', 't1', 't2']),  # Temperaturas entre sí
            (['ldr', 'light'], ['ldr', 'light'])  # Sensores de luz entre sí
        ]
        
        for group1, group2 in expected_correlations:
            if (any(k in sensor1_type for k in group1) and any(k in sensor2_type for k in group2)):
                return True
        
        return False
    
    def _generate_health_description(self, health_score: float, smart_analysis: Dict) -> str:
        """Genera descripción de salud del sistema"""
        if health_score >= 90:
            return f"El sistema está funcionando de manera excelente con una puntuación de {health_score:.1f}%. " \
                   f"Todos los componentes operan dentro de parámetros normales."
        elif health_score >= 75:
            return f"El sistema tiene una salud buena ({health_score:.1f}%) con algunos puntos de atención menores. " \
                   f"Se recomienda monitoreo continuo."
        elif health_score >= 50:
            return f"El sistema presenta problemas moderados (salud: {health_score:.1f}%). " \
                   f"Se requiere atención para evitar degradación adicional."
        else:
            return f"El sistema está en estado crítico (salud: {health_score:.1f}%). " \
                   f"Se requiere intervención inmediata para restaurar la operación normal."
    
    def _get_health_actions(self, health_score: float) -> List[str]:
        """Obtiene acciones recomendadas basadas en salud del sistema"""
        if health_score >= 90:
            return [
                "Mantener rutinas de monitoreo preventivo",
                "Documentar configuración actual como referencia",
                "Planificar mantenimiento programado regular"
            ]
        elif health_score >= 75:
            return [
                "Incrementar frecuencia de monitoreo",
                "Revisar advertencias pendientes",
                "Evaluar necesidad de ajustes menores"
            ]
        elif health_score >= 50:
            return [
                "Programar mantenimiento correctivo en 24-48 horas",
                "Identificar y abordar problemas principales",
                "Considerar respaldo de configuraciones críticas"
            ]
        else:
            return [
                "ACCIÓN INMEDIATA: Intervención técnica urgente",
                "Evaluar posible parada controlada si es necesario",
                "Contactar soporte técnico especializado",
                "Preparar protocolos de contingencia"
            ]
    
    async def _analyze_device_availability(self, df: pd.DataFrame, sensor_inventory: Dict) -> List[AutomaticInsight]:
        """Analiza disponibilidad de dispositivos"""
        insights = []
        
        try:
            current_time = datetime.now()
            
            for device_id in df['device_id'].unique():
                device_data = df[df['device_id'] == device_id]
                
                if device_data.empty:
                    continue
                
                # Verificar última actividad
                last_timestamp_str = device_data['timestamp'].max()
                last_timestamp = pd.to_datetime(last_timestamp_str)
                
                hours_since_last = (current_time - last_timestamp.to_pydatetime()).total_seconds() / 3600
                
                # Crear insight si hay problemas de disponibilidad
                if hours_since_last > 6:  # Más de 6 horas sin datos
                    priority = Priority.CRITICAL if hours_since_last > 24 else Priority.HIGH
                    
                    insight = AutomaticInsight(
                        id=f"avail_{device_id}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                        type=InsightType.SYSTEM_HEALTH,
                        priority=priority,
                        title=f"Dispositivo {device_id} con baja disponibilidad",
                        description=f"El dispositivo {device_id} no ha enviado datos en {hours_since_last:.1f} horas. "
                                  f"Última actividad: {last_timestamp.strftime('%d/%m/%Y %H:%M:%S')}",
                        evidence={
                            'device_id': device_id,
                            'hours_since_last': hours_since_last,
                            'last_timestamp': last_timestamp_str
                        },
                        confidence=0.95,
                        affected_entities=[device_id],
                        generated_at=current_time,
                        recommended_actions=[
                            "Verificar conectividad de red del dispositivo",
                            "Comprobar estado de alimentación",
                            "Revisar logs de sistema para errores"
                        ],
                        time_sensitivity='immediate' if hours_since_last > 24 else 'hours',
                        estimated_impact='high'
                    )
                    
                    insights.append(insight)
        
        except Exception as e:
            self.logger.warning(f"⚠️ Error analyzing device availability: {e}")
        
        return insights
    
    async def _analyze_data_quality(self, df: pd.DataFrame) -> List[AutomaticInsight]:
        """Analiza calidad de los datos"""
        insights = []
        
        try:
            # Detectar datos duplicados
            duplicates = df.duplicated().sum()
            
            if duplicates > 0:
                duplicate_percentage = (duplicates / len(df)) * 100
                
                if duplicate_percentage > 5:  # Más del 5% de duplicados
                    insight = AutomaticInsight(
                        id=f"quality_duplicates_{datetime.now().strftime('%H%M%S')}",
                        type=InsightType.SYSTEM_HEALTH,
                        priority=Priority.MEDIUM,
                        title=f"Datos duplicados detectados ({duplicate_percentage:.1f}%)",
                        description=f"Se encontraron {duplicates} registros duplicados de {len(df)} total "
                                  f"({duplicate_percentage:.1f}%). Esto puede indicar problemas de sincronización.",
                        evidence={
                            'duplicate_count': duplicates,
                            'total_records': len(df),
                            'duplicate_percentage': duplicate_percentage
                        },
                        confidence=0.9,
                        affected_entities=df['device_id'].unique().tolist(),
                        generated_at=datetime.now(),
                        recommended_actions=[
                            "Revisar lógica de envío de datos en dispositivos",
                            "Implementar deduplicación en el servidor",
                            "Verificar sincronización de relojes"
                        ],
                        time_sensitivity='days',
                        estimated_impact='medium'
                    )
                    
                    insights.append(insight)
        
        except Exception as e:
            self.logger.warning(f"⚠️ Error analyzing data quality: {e}")
        
        return insights
    
    def _detect_maintenance_patterns(self, issues: List) -> List[str]:
        """Detecta patrones que indican necesidad de mantenimiento"""
        patterns = []
        
        # Patrón de degradación gradual
        trend_issues = [i for i in issues if i.insight_type == 'trend']
        if len(trend_issues) >= 2:
            patterns.append("Múltiples tendencias negativas detectadas")
        
        # Patrón de inestabilidad
        stability_issues = [i for i in issues if 'inestable' in i.description.lower()]
        if stability_issues:
            patterns.append("Inestabilidad en sensores detectada")
        
        # Patrón de anomalías recurrentes
        anomaly_issues = [i for i in issues if i.insight_type == 'anomaly']
        if len(anomaly_issues) >= 3:
            patterns.append("Anomalías recurrentes sugieren desgaste")
        
        return patterns
    
    def _get_maintenance_actions(self, device_id: str, issues: List) -> List[str]:
        """Obtiene acciones de mantenimiento específicas"""
        actions = [
            f"Programar inspección física de {device_id}",
            "Verificar todas las conexiones eléctricas",
            "Comprobar estado de sensores y actuadores"
        ]
        
        # Acciones específicas basadas en tipos de problemas
        critical_issues = [i for i in issues if i.severity == 'critical']
        if critical_issues:
            actions.insert(0, "PRIORIDAD ALTA: Revisión inmediata requerida")
        
        return actions
    
    async def _analyze_sampling_frequency(self, df: pd.DataFrame) -> Optional[AutomaticInsight]:
        """Analiza si la frecuencia de muestreo es óptima"""
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calcular intervalos entre muestras
            intervals = []
            for device_id in df['device_id'].unique():
                device_data = df[df['device_id'] == device_id].sort_values('timestamp')
                if len(device_data) > 1:
                    device_intervals = device_data['timestamp'].diff().dropna()
                    intervals.extend([i.total_seconds() for i in device_intervals])
            
            if not intervals:
                return None
            
            avg_interval = np.mean(intervals)
            std_interval = np.std(intervals)
            
            # Evaluar si la frecuencia es sub-óptima
            if std_interval > avg_interval * 0.5:  # Alta variabilidad
                return AutomaticInsight(
                    id=f"sampling_freq_{datetime.now().strftime('%H%M%S')}",
                    type=InsightType.PERFORMANCE_OPTIMIZATION,
                    priority=Priority.MEDIUM,
                    title="Frecuencia de muestreo irregular detectada",
                    description=f"La frecuencia de muestreo presenta alta variabilidad. "
                              f"Intervalo promedio: {avg_interval:.1f}s ± {std_interval:.1f}s",
                    evidence={
                        'avg_interval': avg_interval,
                        'std_interval': std_interval,
                        'variability_ratio': std_interval / avg_interval
                    },
                    confidence=0.7,
                    affected_entities=df['device_id'].unique().tolist(),
                    generated_at=datetime.now(),
                    recommended_actions=[
                        "Estandarizar intervalos de muestreo",
                        "Revisar configuración de timers en dispositivos",
                        "Considerar implementar muestreo adaptativo"
                    ],
                    time_sensitivity='weeks',
                    estimated_impact='medium'
                )
        
        except Exception as e:
            self.logger.warning(f"⚠️ Error analyzing sampling frequency: {e}")
        
        return None
    
    async def _analyze_data_efficiency(self, df: pd.DataFrame) -> Optional[AutomaticInsight]:
        """Analiza eficiencia en el uso de datos"""
        try:
            # Calcular métricas de eficiencia
            total_records = len(df)
            unique_values = df['value'].nunique()
            value_diversity = unique_values / total_records if total_records > 0 else 0
            
            # Si hay muy poca diversidad, podría ser ineficiente
            if value_diversity < 0.1 and total_records > 100:  # Menos del 10% de valores únicos
                return AutomaticInsight(
                    id=f"data_efficiency_{datetime.now().strftime('%H%M%S')}",
                    type=InsightType.PERFORMANCE_OPTIMIZATION,
                    priority=Priority.LOW,
                    title="Baja diversidad en datos detectada",
                    description=f"Los datos muestran poca variabilidad ({value_diversity:.1%} de valores únicos). "
                              f"Esto podría indicar sobre-muestreo o sensores estancados.",
                    evidence={
                        'total_records': total_records,
                        'unique_values': unique_values,
                        'value_diversity': value_diversity
                    },
                    confidence=0.6,
                    affected_entities=df['device_id'].unique().tolist(),
                    generated_at=datetime.now(),
                    recommended_actions=[
                        "Evaluar reducir frecuencia de muestreo",
                        "Implementar muestreo basado en cambios",
                        "Verificar que sensores respondan a cambios ambientales"
                    ],
                    time_sensitivity='weeks',
                    estimated_impact='low'
                )
        
        except Exception as e:
            self.logger.warning(f"⚠️ Error analyzing data efficiency: {e}")
        
        return None
    
    async def _suggest_sensor_optimizations(self, df: pd.DataFrame, sensor_inventory: Dict) -> List[AutomaticInsight]:
        """Sugiere optimizaciones específicas de sensores"""
        insights = []
        
        try:
            for sensor_type in df['sensor_type'].unique():
                sensor_data = df[df['sensor_type'] == sensor_type]
                
                if len(sensor_data) < 10:
                    continue
                
                values = sensor_data['value'].values
                
                # Analizar rango dinámico
                value_range = np.max(values) - np.min(values)
                value_std = np.std(values)
                
                # Si el rango es muy pequeño comparado con la precisión típica
                if value_range < value_std * 2:
                    insight = AutomaticInsight(
                        id=f"sensor_opt_{sensor_type}_{datetime.now().strftime('%H%M%S')}",
                        type=InsightType.PERFORMANCE_OPTIMIZATION,
                        priority=Priority.LOW,
                        title=f"Optimización sugerida para {sensor_type}",
                        description=f"El sensor {sensor_type} muestra rango dinámico limitado. "
                                  f"Rango: {value_range:.2f}, Desviación: {value_std:.2f}",
                        evidence={
                            'sensor_type': sensor_type,
                            'value_range': value_range,
                            'value_std': value_std,
                            'efficiency_ratio': value_range / value_std if value_std > 0 else 0
                        },
                        confidence=0.5,
                        affected_entities=[sensor_type],
                        generated_at=datetime.now(),
                        recommended_actions=[
                            "Evaluar calibración del sensor",
                            "Considerar ajustar ganancia o resolución",
                            "Verificar condiciones ambientales de instalación"
                        ],
                        time_sensitivity='weeks',
                        estimated_impact='low'
                    )
                    
                    insights.append(insight)
        
        except Exception as e:
            self.logger.warning(f"⚠️ Error suggesting sensor optimizations: {e}")
        
        return insights
    
    def _detect_environmental_patterns(self, hourly_pattern: pd.DataFrame, sensor_type: str) -> List[Dict]:
        """Detecta patrones que sugieren factores ambientales"""
        patterns = []
        
        try:
            if len(hourly_pattern) < 12:  # Necesitamos suficientes horas
                return patterns
            
            means = hourly_pattern['mean'].values
            variation = np.max(means) - np.min(means)
            
            # Detectar ciclo diario para sensores de temperatura
            if self._categorize_sensor(sensor_type) == 'temperature_patterns':
                if variation > 3.0:  # Variación diaria significativa
                    peak_hour = hourly_pattern.loc[hourly_pattern['mean'].idxmax(), 'hour']
                    
                    patterns.append({
                        'type': 'daily_thermal_cycle',
                        'title': 'Ciclo térmico diario detectado',
                        'description': f'Variación diaria de {variation:.1f}°C con pico a las {peak_hour}:00h. '
                                     f'Esto sugiere influencia de temperatura ambiente.',
                        'evidence': {
                            'daily_variation': variation,
                            'peak_hour': int(peak_hour),
                            'pattern_type': 'thermal_cycle'
                        },
                        'confidence': min(variation / 10.0, 0.9),
                        'actions': [
                            'Considerar compensación térmica',
                            'Evaluar aislamiento del sensor',
                            'Monitorear correlación con temperatura externa'
                        ]
                    })
            
            # Detectar patrones de iluminación
            elif self._categorize_sensor(sensor_type) == 'luminosity_patterns':
                if variation > 200:  # Variación significativa en luminosidad
                    patterns.append({
                        'type': 'lighting_cycle',
                        'title': 'Ciclo de iluminación detectado',
                        'description': f'Variación diaria de luminosidad de {variation:.0f} unidades. '
                                     f'Indica influencia de luz natural o artificial.',
                        'evidence': {
                            'daily_variation': variation,
                            'pattern_type': 'lighting_cycle'
                        },
                        'confidence': min(variation / 1000.0, 0.8),
                        'actions': [
                            'Verificar ubicación del sensor LDR',
                            'Considerar protección contra luz directa',
                            'Evaluar si es apropiado para la aplicación'
                        ]
                    })
        
        except Exception as e:
            self.logger.warning(f"⚠️ Error detecting environmental patterns: {e}")
        
        return patterns
    
    def _deduplicate_insights(self, insights: List[AutomaticInsight]) -> List[AutomaticInsight]:
        """Elimina insights duplicados o muy similares"""
        unique_insights = []
        seen_signatures = set()
        
        for insight in insights:
            # Crear firma única basada en tipo, entidades afectadas y descripción clave
            signature = f"{insight.type.value}_{hash(''.join(insight.affected_entities))}_{hash(insight.title[:50])}"
            
            if signature not in seen_signatures:
                unique_insights.append(insight)
                seen_signatures.add(signature)
        
        return unique_insights
    
    def _intelligent_prioritization(self, insights: List[AutomaticInsight]) -> List[AutomaticInsight]:
        """Prioriza insights de manera inteligente"""
        def priority_score(insight: AutomaticInsight) -> float:
            # Puntuación base por prioridad
            priority_scores = {
                Priority.CRITICAL: 100,
                Priority.HIGH: 80,
                Priority.MEDIUM: 60,
                Priority.LOW: 40,
                Priority.INFORMATIONAL: 20
            }
            
            score = priority_scores.get(insight.priority, 50)
            
            # Bonificación por confianza
            score += insight.confidence * 20
            
            # Bonificación por urgencia temporal
            time_bonuses = {
                'immediate': 30,
                'hours': 20,
                'days': 10,
                'weeks': 5
            }
            score += time_bonuses.get(insight.time_sensitivity, 0)
            
            # Bonificación por impacto estimado
            impact_bonuses = {
                'high': 25,
                'medium': 15,
                'low': 5
            }
            score += impact_bonuses.get(insight.estimated_impact, 0)
            
            return score
        
        # Ordenar por puntuación descendente
        return sorted(insights, key=priority_score, reverse=True)
    
    async def _enrich_with_context(self, insights: List[AutomaticInsight]) -> List[AutomaticInsight]:
        """Enriquece insights con contexto adicional"""
        for insight in insights:
            # Agregar contexto histórico si es relevante
            similar_past_insights = [
                i for i in self.insight_history 
                if i.type == insight.type and 
                any(entity in insight.affected_entities for entity in i.affected_entities)
            ]
            
            if similar_past_insights:
                insight.historical_context = {
                    'similar_insights_count': len(similar_past_insights),
                    'last_occurrence': similar_past_insights[-1].generated_at.isoformat(),
                    'frequency': 'recurrent' if len(similar_past_insights) > 2 else 'occasional'
                }
        
        return insights
    
    def _limit_by_relevance(self, insights: List[AutomaticInsight], max_insights: int = 20) -> List[AutomaticInsight]:
        """Limita insights por relevancia, manteniendo los más importantes"""
        if len(insights) <= max_insights:
            return insights
        
        # Mantener todos los críticos y de alta prioridad
        critical_high = [i for i in insights if i.priority in [Priority.CRITICAL, Priority.HIGH]]
        
        # Completar con los mejor puntuados del resto
        others = [i for i in insights if i.priority not in [Priority.CRITICAL, Priority.HIGH]]
        remaining_slots = max_insights - len(critical_high)
        
        if remaining_slots > 0:
            return critical_high + others[:remaining_slots]
        else:
            return critical_high[:max_insights]