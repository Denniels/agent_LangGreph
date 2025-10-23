"""
Sistema de Análisis Inteligente para IoT
=======================================

Módulo avanzado que proporciona análisis inteligente, detección de patrones,
insights automáticos y recomendaciones proactivas para datos de sensores IoT.

Este sistema transforma datos básicos en información valiosa y accionable.
"""

import logging
import statistics
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import math

logger = logging.getLogger(__name__)

@dataclass
class SensorInsight:
    """Insight específico de un sensor"""
    sensor_type: str
    device_id: str
    insight_type: str  # 'pattern', 'anomaly', 'trend', 'prediction', 'recommendation'
    severity: str      # 'info', 'warning', 'critical'
    title: str
    description: str
    confidence: float  # 0.0 to 1.0
    data_points: int
    timestamp: datetime
    suggested_action: Optional[str] = None
    technical_details: Optional[Dict] = None

@dataclass
class SystemInsight:
    """Insight general del sistema completo"""
    insight_type: str
    severity: str
    title: str
    description: str
    affected_devices: List[str]
    confidence: float
    timestamp: datetime
    recommendations: List[str]
    metrics: Dict[str, Any]

class SmartAnalyzer:
    """
    Sistema de análisis inteligente que convierte datos en insights accionables.
    
    Capacidades:
    - Detección automática de patrones y anomalías
    - Análisis estadístico avanzado
    - Generación de insights proactivos
    - Predicciones basadas en tendencias
    - Recomendaciones contextuales
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Thresholds configurables para diferentes tipos de sensores
        self.sensor_thresholds = {
            'temperature': {
                'normal_range': (15.0, 35.0),
                'warning_range': (10.0, 40.0),
                'critical_range': (5.0, 45.0),
                'stability_threshold': 2.0,  # Variación máxima normal
                'trend_threshold': 0.5,      # Cambio por hora que indica tendencia
                'anomaly_z_score': 2.5       # Z-score para detectar anomalías
            },
            'luminosity': {
                'normal_range': (50, 1000),
                'warning_range': (10, 1500),
                'critical_range': (0, 2000),
                'stability_threshold': 100,
                'trend_threshold': 50,
                'anomaly_z_score': 2.0
            },
            'humidity': {
                'normal_range': (30.0, 70.0),
                'warning_range': (20.0, 80.0),
                'critical_range': (10.0, 90.0),
                'stability_threshold': 5.0,
                'trend_threshold': 2.0,
                'anomaly_z_score': 2.0
            }
        }
        
        # Patrones conocidos para reconocimiento inteligente
        self.known_patterns = {
            'daily_cycle': {'period_hours': 24, 'confidence_threshold': 0.7},
            'heating_cooling': {'rate_threshold': 1.0, 'duration_min': 30},
            'sensor_drift': {'drift_rate': 0.1, 'time_window_hours': 12},
            'periodic_spike': {'spike_threshold': 3.0, 'min_occurrences': 3}
        }
    
    def analyze_comprehensive(self, raw_data: List[Dict], analysis_hours: float = 24.0) -> Dict[str, Any]:
        """
        Realiza análisis comprehensivo de datos IoT generando insights inteligentes.
        
        Returns:
            Dict con estructura completa de análisis inteligente
        """
        try:
            if not raw_data:
                return self._create_empty_analysis("No hay datos disponibles para análisis")
            
            # Convertir a DataFrame para análisis avanzado
            df = pd.DataFrame(raw_data)
            
            # Asegurar que tenemos columnas necesarias
            required_cols = ['timestamp', 'device_id', 'sensor_type', 'value']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                return self._create_empty_analysis(f"Columnas faltantes: {', '.join(missing_cols)}")
            
            # Convertir timestamp a datetime si es necesario
            if df['timestamp'].dtype == 'object':
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filtrar por período de análisis (con fallback a todos los datos)
            cutoff_time = datetime.now() - timedelta(hours=analysis_hours)
            df_filtered = df[df['timestamp'] >= cutoff_time].copy()
            
            # Si no hay datos en el período especificado, usar todos los datos disponibles
            if df_filtered.empty:
                self.logger.warning(f"No hay datos en las últimas {analysis_hours}h, usando todos los datos disponibles")
                df_filtered = df.copy()
                analysis_hours = 24 * 30  # Marcar como análisis de datos históricos (30 días)
            
            if df_filtered.empty:
                return self._create_empty_analysis("No hay datos disponibles para análisis")
            
            # Preparar estructura de análisis
            analysis_result = {
                'timestamp': datetime.now().isoformat(),
                'analysis_period_hours': analysis_hours,
                'total_data_points': len(df_filtered),
                'devices_analyzed': df_filtered['device_id'].unique().tolist(),
                'sensors_analyzed': df_filtered['sensor_type'].unique().tolist(),
                'summary': {},
                'sensor_insights': [],
                'system_insights': [],
                'predictions': {},
                'recommendations': [],
                'health_score': 0.0,
                'confidence_level': 0.0
            }
            
            # 1. ANÁLISIS POR SENSOR
            sensor_insights = self._analyze_sensors_detailed(df_filtered)
            analysis_result['sensor_insights'] = sensor_insights
            
            # 2. ANÁLISIS SISTÉMICO
            system_insights = self._analyze_system_patterns(df_filtered)
            analysis_result['system_insights'] = system_insights
            
            # 3. DETECCIÓN DE ANOMALÍAS INTELIGENTE
            anomalies = self._detect_intelligent_anomalies(df_filtered)
            analysis_result['anomalies'] = anomalies
            
            # 4. ANÁLISIS PREDICTIVO
            predictions = self._generate_predictions(df_filtered)
            analysis_result['predictions'] = predictions
            
            # 5. GENERACIÓN DE RECOMENDACIONES CONTEXTUALES
            recommendations = self._generate_smart_recommendations(
                df_filtered, sensor_insights, system_insights, anomalies
            )
            analysis_result['recommendations'] = recommendations
            
            # 6. CÁLCULO DE PUNTUACIONES DE SALUD Y CONFIANZA
            health_score, confidence = self._calculate_health_and_confidence(
                df_filtered, sensor_insights, system_insights, anomalies
            )
            analysis_result['health_score'] = health_score
            analysis_result['confidence_level'] = confidence
            
            # 7. RESUMEN EJECUTIVO INTELIGENTE
            executive_summary = self._generate_executive_summary(analysis_result)
            analysis_result['summary'] = executive_summary
            
            logger.info(f"✅ Análisis inteligente completado: {len(sensor_insights)} insights de sensores, "
                       f"{len(system_insights)} insights sistémicos, salud: {health_score:.1f}%")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Error en análisis comprehensive: {e}")
            return self._create_empty_analysis(f"Error en análisis: {str(e)}")
    
    def _analyze_sensors_detailed(self, df: pd.DataFrame) -> List[SensorInsight]:
        """Análisis detallado por sensor individual"""
        insights = []
        
        # Agrupar por dispositivo y sensor
        for (device_id, sensor_type), group in df.groupby(['device_id', 'sensor_type']):
            try:
                if len(group) < 3:  # Necesitamos al menos 3 puntos para análisis
                    continue
                
                values = group['value'].values
                timestamps = group['timestamp'].values
                
                # Obtener configuración para este tipo de sensor
                sensor_config = self._get_sensor_config(sensor_type)
                
                # 1. ANÁLISIS ESTADÍSTICO BÁSICO
                stats = {
                    'mean': np.mean(values),
                    'median': np.median(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'range': np.max(values) - np.min(values),
                    'cv': np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
                }
                
                # 2. DETECCIÓN DE TENDENCIAS
                trend_insight = self._analyze_trend(values, timestamps, sensor_config)
                if trend_insight:
                    insights.append(SensorInsight(
                        sensor_type=sensor_type,
                        device_id=device_id,
                        insight_type='trend',
                        severity=trend_insight['severity'],
                        title=trend_insight['title'],
                        description=trend_insight['description'],
                        confidence=trend_insight['confidence'],
                        data_points=len(values),
                        timestamp=datetime.now(),
                        suggested_action=trend_insight.get('action'),
                        technical_details=trend_insight.get('details')
                    ))
                
                # 3. ANÁLISIS DE ESTABILIDAD
                stability_insight = self._analyze_stability(values, sensor_config, stats)
                if stability_insight:
                    insights.append(SensorInsight(
                        sensor_type=sensor_type,
                        device_id=device_id,
                        insight_type='pattern',
                        severity=stability_insight['severity'],
                        title=stability_insight['title'],
                        description=stability_insight['description'],
                        confidence=stability_insight['confidence'],
                        data_points=len(values),
                        timestamp=datetime.now(),
                        suggested_action=stability_insight.get('action'),
                        technical_details=stability_insight.get('details')
                    ))
                
                # 4. DETECCIÓN DE ANOMALÍAS POR SENSOR
                anomaly_insights = self._detect_sensor_anomalies(values, timestamps, sensor_config, device_id, sensor_type)
                insights.extend(anomaly_insights)
                
                # 5. ANÁLISIS DE RANGOS OPERATIVOS
                range_insight = self._analyze_operational_range(values, sensor_config, device_id, sensor_type)
                if range_insight:
                    insights.append(range_insight)
                    
            except Exception as e:
                logger.warning(f"⚠️ Error analizando {device_id}/{sensor_type}: {e}")
                continue
        
        return insights
    
    def _analyze_system_patterns(self, df: pd.DataFrame) -> List[SystemInsight]:
        """Análisis de patrones a nivel sistémico"""
        insights = []
        
        try:
            # 1. ANÁLISIS DE CORRELACIONES ENTRE SENSORES
            correlation_insights = self._analyze_sensor_correlations(df)
            insights.extend(correlation_insights)
            
            # 2. ANÁLISIS DE SINCRONIZACIÓN TEMPORAL
            sync_insights = self._analyze_temporal_synchronization(df)
            insights.extend(sync_insights)
            
            # 3. ANÁLISIS DE DISPONIBILIDAD DE DISPOSITIVOS
            availability_insights = self._analyze_device_availability(df)
            insights.extend(availability_insights)
            
            # 4. DETECCIÓN DE PATRONES GLOBALES
            global_pattern_insights = self._detect_global_patterns(df)
            insights.extend(global_pattern_insights)
            
        except Exception as e:
            logger.warning(f"⚠️ Error en análisis sistémico: {e}")
        
        return insights
    
    def _detect_intelligent_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detección inteligente de anomalías usando múltiples algoritmos"""
        anomalies = []
        
        try:
            # Agrupar por sensor para análisis individualizado
            for (device_id, sensor_type), group in df.groupby(['device_id', 'sensor_type']):
                if len(group) < 5:  # Necesitamos suficientes datos
                    continue
                
                values = group['value'].values
                timestamps = group['timestamp'].values
                
                # 1. DETECCIÓN POR Z-SCORE
                z_scores = np.abs(statistics.zscore(values))
                z_threshold = self._get_sensor_config(sensor_type)['anomaly_z_score']
                
                z_anomalies = np.where(z_scores > z_threshold)[0]
                
                # 2. DETECCIÓN POR IQR (Interquartile Range)
                q1, q3 = np.percentile(values, [25, 75])
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                iqr_anomalies = np.where((values < lower_bound) | (values > upper_bound))[0]
                
                # 3. DETECCIÓN POR CAMBIOS SÚBITOS
                if len(values) > 1:
                    diff = np.abs(np.diff(values))
                    diff_threshold = np.std(values) * 2
                    sudden_changes = np.where(diff > diff_threshold)[0]
                
                # Consolidar anomalías encontradas
                all_anomaly_indices = set(z_anomalies) | set(iqr_anomalies)
                if len(values) > 1:
                    all_anomaly_indices |= set(sudden_changes)
                    
                for idx in all_anomaly_indices:
                    if idx < len(values) and idx < len(timestamps):
                        anomalies.append({
                            'device_id': device_id,
                            'sensor_type': sensor_type,
                            'timestamp': timestamps[idx],
                            'value': values[idx],
                            'expected_range': f"{np.mean(values):.2f} ± {np.std(values):.2f}",
                            'severity': self._classify_anomaly_severity(values[idx], values),
                            'detection_method': self._get_detection_methods(idx, z_anomalies, iqr_anomalies, sudden_changes if len(values) > 1 else []),
                            'confidence': min(z_scores[idx] / z_threshold if idx in z_anomalies else 0.5, 1.0)
                        })
            
        except Exception as e:
            logger.warning(f"⚠️ Error en detección de anomalías: {e}")
        
        return anomalies
    
    def _generate_predictions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Genera predicciones inteligentes basadas en tendencias históricas"""
        predictions = {}
        
        try:
            for (device_id, sensor_type), group in df.groupby(['device_id', 'sensor_type']):
                if len(group) < 5:  # Necesitamos datos suficientes para predicción
                    continue
                
                values = group['value'].values
                timestamps = pd.to_datetime(group['timestamp'])
                
                # Calcular tendencia lineal simple
                time_numeric = np.arange(len(values))
                
                if len(values) >= 3:
                    # Regresión lineal simple
                    slope, intercept = np.polyfit(time_numeric, values, 1)
                    
                    # Predicción para próxima hora
                    next_hour_prediction = slope * len(values) + intercept
                    
                    # Confianza basada en R²
                    y_pred = slope * time_numeric + intercept
                    ss_res = np.sum((values - y_pred) ** 2)
                    ss_tot = np.sum((values - np.mean(values)) ** 2)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                    
                    prediction_key = f"{device_id}_{sensor_type}"
                    predictions[prediction_key] = {
                        'device_id': device_id,
                        'sensor_type': sensor_type,
                        'current_value': values[-1],
                        'predicted_next_hour': next_hour_prediction,
                        'trend_slope': slope,
                        'confidence': max(0, min(r_squared, 1.0)),
                        'trend_direction': 'increasing' if slope > 0.1 else 'decreasing' if slope < -0.1 else 'stable',
                        'prediction_timestamp': datetime.now() + timedelta(hours=1),
                        'data_points_used': len(values)
                    }
        
        except Exception as e:
            logger.warning(f"⚠️ Error generando predicciones: {e}")
        
        return predictions
    
    def _generate_smart_recommendations(self, df: pd.DataFrame, sensor_insights: List[SensorInsight], 
                                       system_insights: List[SystemInsight], anomalies: List[Dict]) -> List[Dict[str, Any]]:
        """Genera recomendaciones inteligentes y contextuales"""
        recommendations = []
        
        try:
            # 1. RECOMENDACIONES BASADAS EN ANOMALÍAS
            critical_anomalies = [a for a in anomalies if a.get('severity') == 'critical']
            if critical_anomalies:
                recommendations.append({
                    'type': 'anomaly_response',
                    'priority': 'high',
                    'title': 'Anomalías Críticas Detectadas',
                    'description': f'Se detectaron {len(critical_anomalies)} anomalías críticas que requieren atención inmediata.',
                    'actions': [
                        'Verificar el estado físico de los sensores afectados',
                        'Revisar conexiones de red y alimentación',
                        'Considerar recalibración de sensores'
                    ],
                    'affected_devices': list(set([a['device_id'] for a in critical_anomalies])),
                    'urgency': 'immediate'
                })
            
            # 2. RECOMENDACIONES BASADAS EN TENDENCIAS
            trending_sensors = [s for s in sensor_insights if s.insight_type == 'trend' and s.severity in ['warning', 'critical']]
            if trending_sensors:
                recommendations.append({
                    'type': 'trend_management',
                    'priority': 'medium',
                    'title': 'Gestión de Tendencias Preocupantes',
                    'description': f'Se detectaron tendencias que requieren monitoreo en {len(trending_sensors)} sensores.',
                    'actions': [
                        'Monitorear la evolución de las tendencias detectadas',
                        'Establecer alertas para valores límite',
                        'Evaluar la necesidad de ajustes en el sistema'
                    ],
                    'affected_devices': list(set([s.device_id for s in trending_sensors])),
                    'urgency': 'planned'
                })
            
            # 3. RECOMENDACIONES DE MANTENIMIENTO PREDICTIVO
            unstable_sensors = [s for s in sensor_insights if 'inestable' in s.description.lower()]
            if unstable_sensors:
                recommendations.append({
                    'type': 'predictive_maintenance',
                    'priority': 'medium',
                    'title': 'Mantenimiento Predictivo Sugerido',
                    'description': f'Sensores con patrones de inestabilidad detectada requieren revisión.',
                    'actions': [
                        'Programar mantenimiento preventivo',
                        'Verificar calibración de sensores inestables',
                        'Evaluar condiciones ambientales de instalación'
                    ],
                    'affected_devices': list(set([s.device_id for s in unstable_sensors])),
                    'urgency': 'scheduled'
                })
            
            # 4. RECOMENDACIONES DE OPTIMIZACIÓN
            device_count = df['device_id'].nunique()
            sensor_count = df['sensor_type'].nunique()
            
            if device_count > 0 and sensor_count > 0:
                recommendations.append({
                    'type': 'system_optimization',
                    'priority': 'low',
                    'title': 'Oportunidades de Optimización',
                    'description': f'Sistema con {device_count} dispositivos y {sensor_count} tipos de sensores funcionando.',
                    'actions': [
                        'Evaluar la frecuencia de muestreo óptima',
                        'Considerar implementar alertas automáticas',
                        'Revisar configuración de umbrales de sensores'
                    ],
                    'affected_devices': df['device_id'].unique().tolist(),
                    'urgency': 'optimization'
                })
        
        except Exception as e:
            logger.warning(f"⚠️ Error generando recomendaciones: {e}")
        
        return recommendations
    
    def _calculate_health_and_confidence(self, df: pd.DataFrame, sensor_insights: List[SensorInsight], 
                                        system_insights: List[SystemInsight], anomalies: List[Dict]) -> Tuple[float, float]:
        """Calcula puntuaciones de salud del sistema y confianza del análisis"""
        try:
            # CÁLCULO DE SALUD (0-100)
            health_score = 100.0
            
            # Penalizar por anomalías críticas
            critical_anomalies = len([a for a in anomalies if a.get('severity') == 'critical'])
            health_score -= critical_anomalies * 15
            
            # Penalizar por anomalías de advertencia
            warning_anomalies = len([a for a in anomalies if a.get('severity') == 'warning'])
            health_score -= warning_anomalies * 5
            
            # Penalizar por insights críticos
            critical_insights = len([s for s in sensor_insights if s.severity == 'critical'])
            health_score -= critical_insights * 10
            
            # Penalizar por insights de advertencia
            warning_insights = len([s for s in sensor_insights + system_insights if s.severity == 'warning'])
            health_score -= warning_insights * 3
            
            # Asegurar que esté en rango 0-100
            health_score = max(0, min(100, health_score))
            
            # CÁLCULO DE CONFIANZA (0-1)
            total_data_points = len(df)
            devices_count = df['device_id'].nunique()
            
            # Confianza base según cantidad de datos
            if total_data_points >= 50:
                confidence = 0.95
            elif total_data_points >= 20:
                confidence = 0.80
            elif total_data_points >= 10:
                confidence = 0.65
            else:
                confidence = 0.40
            
            # Ajustar por diversidad de dispositivos
            if devices_count >= 2:
                confidence += 0.05
            
            # Ajustar por insights con alta confianza
            high_confidence_insights = [s for s in sensor_insights if s.confidence > 0.8]
            if len(high_confidence_insights) > 0:
                confidence += 0.05
            
            # Asegurar que esté en rango 0-1
            confidence = max(0, min(1, confidence))
            
            return health_score, confidence
            
        except Exception as e:
            logger.warning(f"⚠️ Error calculando salud y confianza: {e}")
            return 75.0, 0.5  # Valores por defecto conservadores
    
    def _generate_executive_summary(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Genera resumen ejecutivo inteligente"""
        try:
            sensor_insights = analysis_result.get('sensor_insights', [])
            system_insights = analysis_result.get('system_insights', [])
            anomalies = analysis_result.get('anomalies', [])
            predictions = analysis_result.get('predictions', {})
            health_score = analysis_result.get('health_score', 0)
            
            # Categorizar insights por severidad
            critical_issues = len([s for s in sensor_insights + system_insights if s.severity == 'critical'])
            warning_issues = len([s for s in sensor_insights + system_insights if s.severity == 'warning'])
            info_insights = len([s for s in sensor_insights + system_insights if s.severity == 'info'])
            
            # Generar estado general
            if health_score >= 90:
                overall_status = "Excelente"
                status_emoji = "🟢"
            elif health_score >= 75:
                overall_status = "Bueno"
                status_emoji = "🟡"
            elif health_score >= 50:
                overall_status = "Regular"
                status_emoji = "🟠"
            else:
                overall_status = "Crítico"
                status_emoji = "🔴"
            
            # Crear resumen
            summary = {
                'overall_status': overall_status,
                'status_emoji': status_emoji,
                'health_percentage': health_score,
                'key_metrics': {
                    'total_devices': len(analysis_result.get('devices_analyzed', [])),
                    'total_sensors': len(analysis_result.get('sensors_analyzed', [])),
                    'data_points': analysis_result.get('total_data_points', 0),
                    'analysis_period': analysis_result.get('analysis_period_hours', 0)
                },
                'issues_summary': {
                    'critical': critical_issues,
                    'warnings': warning_issues,
                    'informational': info_insights,
                    'anomalies_detected': len(anomalies)
                },
                'top_insights': self._extract_top_insights(sensor_insights + system_insights),
                'urgent_actions': self._extract_urgent_actions(analysis_result.get('recommendations', [])),
                'predictions_available': len(predictions) > 0,
                'confidence_level': analysis_result.get('confidence_level', 0)
            }
            
            return summary
            
        except Exception as e:
            logger.warning(f"⚠️ Error generando resumen ejecutivo: {e}")
            return {'overall_status': 'Error', 'status_emoji': '❌'}
    
    # MÉTODOS AUXILIARES
    
    def _create_empty_analysis(self, reason: str) -> Dict[str, Any]:
        """Crea estructura de análisis vacía con razón"""
        return {
            'timestamp': datetime.now().isoformat(),
            'status': 'no_data',
            'reason': reason,
            'summary': {'overall_status': 'Sin datos', 'status_emoji': '⚪'},
            'sensor_insights': [],
            'system_insights': [],
            'anomalies': [],
            'predictions': {},
            'recommendations': [],
            'health_score': 0.0,
            'confidence_level': 0.0
        }
    
    def _get_sensor_config(self, sensor_type: str) -> Dict[str, Any]:
        """Obtiene configuración para un tipo de sensor"""
        # Mapear tipos de sensores a categorías estándar
        if any(keyword in sensor_type.lower() for keyword in ['temp', 'ntc', 't1', 't2', 'avg']):
            return self.sensor_thresholds['temperature']
        elif any(keyword in sensor_type.lower() for keyword in ['ldr', 'light', 'lumino', 'bright']):
            return self.sensor_thresholds['luminosity']  
        elif any(keyword in sensor_type.lower() for keyword in ['humid', 'moisture']):
            return self.sensor_thresholds['humidity']
        else:
            # Configuración por defecto para sensores desconocidos
            return {
                'normal_range': (0, 100),
                'warning_range': (-10, 110),
                'critical_range': (-20, 120),
                'stability_threshold': 10,
                'trend_threshold': 5,
                'anomaly_z_score': 2.0
            }
    
    def _analyze_trend(self, values: np.ndarray, timestamps: np.ndarray, config: Dict) -> Optional[Dict]:
        """Analiza tendencias en los valores del sensor"""
        if len(values) < 3:
            return None
        
        try:
            # Calcular pendiente de la tendencia
            time_numeric = np.arange(len(values))
            slope, _ = np.polyfit(time_numeric, values, 1)
            
            trend_threshold = config['trend_threshold']
            
            if abs(slope) > trend_threshold:
                direction = "creciente" if slope > 0 else "decreciente"
                severity = "warning" if abs(slope) < trend_threshold * 2 else "critical"
                
                return {
                    'title': f'Tendencia {direction} detectada',
                    'description': f'El sensor muestra una tendencia {direction} sostenida con pendiente de {slope:.3f} unidades por lectura.',
                    'severity': severity,
                    'confidence': min(abs(slope) / trend_threshold, 1.0),
                    'action': f'Monitorear la evolución y verificar si la tendencia {direction} es esperada.',
                    'details': {'slope': slope, 'threshold': trend_threshold}
                }
        except Exception as e:
            logger.warning(f"⚠️ Error analizando tendencia: {e}")
        
        return None
    
    def _analyze_stability(self, values: np.ndarray, config: Dict, stats: Dict) -> Optional[Dict]:
        """Analiza estabilidad del sensor"""
        try:
            cv = stats['cv']  # Coeficiente de variación
            stability_threshold = config['stability_threshold']
            
            # Usar coeficiente de variación normalizado
            if stats['mean'] != 0:
                normalized_std = stats['std'] / abs(stats['mean']) * 100
            else:
                normalized_std = stats['std']
            
            if normalized_std > stability_threshold * 10:  # Convertir a porcentaje
                return {
                    'title': 'Sensor inestable detectado',
                    'description': f'El sensor presenta alta variabilidad ({normalized_std:.1f}% CV). Los valores oscilan significativamente.',
                    'severity': 'warning' if normalized_std < stability_threshold * 20 else 'critical',
                    'confidence': min(normalized_std / (stability_threshold * 10), 1.0),
                    'action': 'Verificar calibración del sensor y condiciones ambientales.',
                    'details': {'cv_percentage': normalized_std, 'threshold': stability_threshold}
                }
        except Exception as e:
            logger.warning(f"⚠️ Error analizando estabilidad: {e}")
        
        return None
    
    def _detect_sensor_anomalies(self, values: np.ndarray, timestamps: np.ndarray, 
                                config: Dict, device_id: str, sensor_type: str) -> List[SensorInsight]:
        """Detecta anomalías específicas de un sensor"""
        anomaly_insights = []
        
        try:
            # Usar Z-score para detección
            if len(values) >= 3:
                z_scores = np.abs(statistics.zscore(values))
                threshold = config['anomaly_z_score']
                
                anomalous_indices = np.where(z_scores > threshold)[0]
                
                if len(anomalous_indices) > 0:
                    severity = 'critical' if np.max(z_scores[anomalous_indices]) > threshold * 1.5 else 'warning'
                    
                    anomaly_insights.append(SensorInsight(
                        sensor_type=sensor_type,
                        device_id=device_id,
                        insight_type='anomaly',
                        severity=severity,
                        title=f'{len(anomalous_indices)} anomalías estadísticas detectadas',
                        description=f'Valores con desviación estadística significativa (Z-score > {threshold}). '
                                  f'Valor más anómalo: {values[anomalous_indices[np.argmax(z_scores[anomalous_indices])]]:.2f}',
                        confidence=min(np.max(z_scores[anomalous_indices]) / threshold, 1.0),
                        data_points=len(values),
                        timestamp=datetime.now(),
                        suggested_action='Investigar causas de los valores anómalos y verificar sensor.',
                        technical_details={
                            'max_z_score': float(np.max(z_scores[anomalous_indices])),
                            'anomalous_values': values[anomalous_indices].tolist(),
                            'threshold_used': threshold
                        }
                    ))
        
        except Exception as e:
            logger.warning(f"⚠️ Error detectando anomalías en sensor: {e}")
        
        return anomaly_insights
    
    def _analyze_operational_range(self, values: np.ndarray, config: Dict, 
                                  device_id: str, sensor_type: str) -> Optional[SensorInsight]:
        """Analiza si el sensor opera dentro de rangos esperados"""
        try:
            min_val, max_val = np.min(values), np.max(values)
            normal_min, normal_max = config['normal_range']
            warning_min, warning_max = config['warning_range']
            
            # Verificar si hay valores fuera de rango normal
            out_of_normal = np.sum((values < normal_min) | (values > normal_max))
            out_of_warning = np.sum((values < warning_min) | (values > warning_max))
            
            if out_of_warning > 0:
                severity = 'critical'
                description = f'{out_of_warning} lecturas fuera del rango crítico ({warning_min}-{warning_max})'
                action = 'ACCIÓN INMEDIATA: Verificar sensor y condiciones operativas'
            elif out_of_normal > 0:
                severity = 'warning'
                description = f'{out_of_normal} lecturas fuera del rango normal ({normal_min}-{normal_max})'
                action = 'Monitorear y considerar ajustes en el sistema'
            else:
                # Todo está en rango normal
                return None
            
            return SensorInsight(
                sensor_type=sensor_type,
                device_id=device_id,
                insight_type='range_analysis',
                severity=severity,
                title='Valores fuera de rango operativo',
                description=description,
                confidence=1.0,
                data_points=len(values),
                timestamp=datetime.now(),
                suggested_action=action,
                technical_details={
                    'normal_range': config['normal_range'],
                    'warning_range': config['warning_range'],
                    'out_of_normal_count': int(out_of_normal),
                    'out_of_warning_count': int(out_of_warning),
                    'min_value': float(min_val),
                    'max_value': float(max_val)
                }
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Error analizando rango operativo: {e}")
        
        return None
    
    def _analyze_sensor_correlations(self, df: pd.DataFrame) -> List[SystemInsight]:
        """Analiza correlaciones entre sensores diferentes"""
        insights = []
        
        try:
            # Crear matriz pivote para análisis de correlación
            pivot_df = df.pivot_table(
                values='value', 
                index='timestamp', 
                columns=['device_id', 'sensor_type'], 
                aggfunc='mean'
            ).fillna(method='ffill').fillna(method='bfill')
            
            if pivot_df.shape[1] >= 2:  # Necesitamos al menos 2 sensores
                correlation_matrix = pivot_df.corr()
                
                # Buscar correlaciones significativas (> 0.7 o < -0.7)
                strong_correlations = []
                
                for i in range(len(correlation_matrix.columns)):
                    for j in range(i+1, len(correlation_matrix.columns)):
                        corr_value = correlation_matrix.iloc[i, j]
                        
                        if abs(corr_value) > 0.7 and not pd.isna(corr_value):
                            sensor1 = correlation_matrix.columns[i]
                            sensor2 = correlation_matrix.columns[j]
                            
                            strong_correlations.append({
                                'sensor1': sensor1,
                                'sensor2': sensor2,
                                'correlation': corr_value,
                                'type': 'positive' if corr_value > 0 else 'negative'
                            })
                
                if strong_correlations:
                    correlation_type = 'positive' if strong_correlations[0]['correlation'] > 0 else 'negative'
                    
                    insights.append(SystemInsight(
                        insight_type='correlation',
                        severity='info',
                        title=f'Correlaciones {correlation_type}s detectadas entre sensores',
                        description=f'Se encontraron {len(strong_correlations)} correlaciones significativas entre sensores del sistema.',
                        affected_devices=list(set([str(sc['sensor1'][0]) for sc in strong_correlations] + 
                                                [str(sc['sensor2'][0]) for sc in strong_correlations])),
                        confidence=0.8,
                        timestamp=datetime.now(),
                        recommendations=[
                            'Las correlaciones indican comportamiento sistemático esperado',
                            'Monitorear que las correlaciones se mantengan estables'
                        ],
                        metrics={'correlations_found': len(strong_correlations)}
                    ))
        
        except Exception as e:
            logger.warning(f"⚠️ Error analizando correlaciones: {e}")
        
        return insights
    
    def _analyze_temporal_synchronization(self, df: pd.DataFrame) -> List[SystemInsight]:
        """Analiza sincronización temporal entre dispositivos"""
        insights = []
        
        try:
            # Agrupar por dispositivo y verificar frecuencia de datos
            device_frequencies = {}
            
            for device_id, group in df.groupby('device_id'):
                timestamps = pd.to_datetime(group['timestamp']).sort_values()
                if len(timestamps) > 1:
                    time_diffs = timestamps.diff().dropna()
                    avg_interval = time_diffs.mean().total_seconds()
                    device_frequencies[device_id] = avg_interval
            
            if len(device_frequencies) > 1:
                frequencies = list(device_frequencies.values())
                freq_std = np.std(frequencies)
                freq_mean = np.mean(frequencies)
                
                # Si hay gran variación en frecuencias, es un problema de sincronización
                if freq_std > freq_mean * 0.5:  # 50% de variación
                    insights.append(SystemInsight(
                        insight_type='synchronization',
                        severity='warning',
                        title='Desincronización temporal detectada',
                        description=f'Los dispositivos muestran intervalos de muestreo muy diferentes. '
                                  f'Promedio: {freq_mean:.1f}s, Desviación: {freq_std:.1f}s',
                        affected_devices=list(device_frequencies.keys()),
                        confidence=0.7,
                        timestamp=datetime.now(),
                        recommendations=[
                            'Verificar configuración de intervalos de muestreo',
                            'Sincronizar relojes de dispositivos',
                            'Evaluar conectividad de red de cada dispositivo'
                        ],
                        metrics={'frequency_variation': freq_std / freq_mean}
                    ))
        
        except Exception as e:
            logger.warning(f"⚠️ Error analizando sincronización: {e}")
        
        return insights
    
    def _analyze_device_availability(self, df: pd.DataFrame) -> List[SystemInsight]:
        """Analiza disponibilidad y actividad de dispositivos"""
        insights = []
        
        try:
            current_time = datetime.now()
            devices_analyzed = df['device_id'].unique()
            
            # Verificar última actividad de cada dispositivo
            inactive_devices = []
            
            for device_id in devices_analyzed:
                device_data = df[df['device_id'] == device_id]
                last_timestamp = pd.to_datetime(device_data['timestamp']).max()
                
                time_since_last = current_time - last_timestamp.to_pydatetime()
                
                # Si no hay datos en las últimas 2 horas, considerar potencialmente inactivo
                if time_since_last.total_seconds() > 7200:  # 2 horas
                    inactive_devices.append({
                        'device_id': device_id,
                        'last_seen': last_timestamp,
                        'hours_inactive': time_since_last.total_seconds() / 3600
                    })
            
            if inactive_devices:
                severity = 'critical' if any(d['hours_inactive'] > 24 for d in inactive_devices) else 'warning'
                
                insights.append(SystemInsight(
                    insight_type='availability',
                    severity=severity,
                    title=f'{len(inactive_devices)} dispositivos con actividad reducida',
                    description=f'Dispositivos sin datos recientes detectados. El más inactivo: '
                              f'{max(inactive_devices, key=lambda x: x["hours_inactive"])["hours_inactive"]:.1f} horas.',
                    affected_devices=[d['device_id'] for d in inactive_devices],
                    confidence=0.9,
                    timestamp=datetime.now(),
                    recommendations=[
                        'Verificar conectividad de dispositivos inactivos',
                        'Comprobar alimentación y estado físico',
                        'Revisar logs de red para problemas de comunicación'
                    ],
                    metrics={'inactive_devices': len(inactive_devices)}
                ))
        
        except Exception as e:
            logger.warning(f"⚠️ Error analizando disponibilidad: {e}")
        
        return insights
    
    def _detect_global_patterns(self, df: pd.DataFrame) -> List[SystemInsight]:
        """Detecta patrones globales del sistema"""
        insights = []
        
        try:
            # Análisis de patrones diarios si tenemos datos suficientes
            df_copy = df.copy()
            df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])
            df_copy['hour'] = df_copy['timestamp'].dt.hour
            
            # Buscar patrones por hora del día
            hourly_patterns = df_copy.groupby(['hour', 'sensor_type'])['value'].mean().unstack(fill_value=0)
            
            if len(hourly_patterns) >= 12:  # Al menos 12 horas de datos
                # Detectar si hay variación significativa por hora
                for sensor_type in hourly_patterns.columns:
                    hourly_values = hourly_patterns[sensor_type].values
                    hourly_std = np.std(hourly_values)
                    hourly_mean = np.mean(hourly_values)
                    
                    if hourly_std > hourly_mean * 0.1:  # 10% de variación
                        peak_hour = hourly_patterns[sensor_type].idxmax()
                        low_hour = hourly_patterns[sensor_type].idxmin()
                        
                        insights.append(SystemInsight(
                            insight_type='pattern',
                            severity='info',
                            title=f'Patrón diario detectado en {sensor_type}',
                            description=f'Variación diaria significativa. Pico a las {peak_hour}:00h, '
                                      f'mínimo a las {low_hour}:00h. Variación: {hourly_std:.2f}',
                            affected_devices=df[df['sensor_type'] == sensor_type]['device_id'].unique().tolist(),
                            confidence=0.6,
                            timestamp=datetime.now(),
                            recommendations=[
                                'El patrón diario es normal para este tipo de sensor',
                                'Considerar ajustar umbrales según la hora del día'
                            ],
                            metrics={
                                'peak_hour': int(peak_hour),
                                'low_hour': int(low_hour),
                                'daily_variation': float(hourly_std)
                            }
                        ))
        
        except Exception as e:
            logger.warning(f"⚠️ Error detectando patrones globales: {e}")
        
        return insights
    
    def _classify_anomaly_severity(self, value: float, all_values: np.ndarray) -> str:
        """Clasifica la severidad de una anomalía"""
        try:
            mean_val = np.mean(all_values)
            std_val = np.std(all_values)
            
            z_score = abs(value - mean_val) / std_val if std_val > 0 else 0
            
            if z_score > 3:
                return 'critical'
            elif z_score > 2:
                return 'warning'
            else:
                return 'info'
        except:
            return 'info'
    
    def _get_detection_methods(self, idx: int, z_anomalies: np.ndarray, 
                              iqr_anomalies: np.ndarray, sudden_changes: np.ndarray) -> List[str]:
        """Obtiene métodos de detección que identificaron la anomalía"""
        methods = []
        if idx in z_anomalies:
            methods.append('Z-Score')
        if idx in iqr_anomalies:
            methods.append('IQR')
        if idx in sudden_changes:
            methods.append('Cambio súbito')
        return methods if methods else ['Estadístico']
    
    def _extract_top_insights(self, all_insights: List) -> List[str]:
        """Extrae los insights más importantes"""
        try:
            # Ordenar por severidad y confianza
            priority_order = {'critical': 3, 'warning': 2, 'info': 1}
            
            sorted_insights = sorted(
                all_insights,
                key=lambda x: (priority_order.get(x.severity, 0), x.confidence),
                reverse=True
            )
            
            # Tomar los 3 más importantes
            top_insights = []
            for insight in sorted_insights[:3]:
                top_insights.append(f"{insight.title}: {insight.description[:100]}...")
            
            return top_insights
        except:
            return ["Análisis completado exitosamente"]
    
    def _extract_urgent_actions(self, recommendations: List[Dict]) -> List[str]:
        """Extrae acciones urgentes de las recomendaciones"""
        try:
            urgent_actions = []
            
            for rec in recommendations:
                if rec.get('urgency') in ['immediate', 'high'] or rec.get('priority') == 'high':
                    urgent_actions.extend(rec.get('actions', [])[:2])  # Máximo 2 acciones por recomendación
            
            return urgent_actions[:5]  # Máximo 5 acciones urgentes
        except:
            return []