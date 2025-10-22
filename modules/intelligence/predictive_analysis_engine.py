"""
Sistema de Análisis Predictivo Avanzado para IoT
===============================================

Motor de predicciones inteligente que utiliza múltiples algoritmos de machine learning
y análisis de series temporales para generar predicciones precisas y alertas tempranas.

Este sistema aprende de patrones históricos y predice comportamientos futuros.
"""

import logging
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import deque, defaultdict
import json
import statistics
from enum import Enum
import warnings

# Suprimir warnings de numpy y pandas
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class PredictionHorizon(Enum):
    """Horizontes de predicción disponibles"""
    SHORT_TERM = "1h"      # 1 hora
    MEDIUM_TERM = "6h"     # 6 horas  
    LONG_TERM = "24h"      # 24 horas
    EXTENDED = "7d"        # 7 días

class PredictionAlgorithm(Enum):
    """Algoritmos de predicción disponibles"""
    LINEAR_REGRESSION = "linear_regression"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"
    AUTOREGRESSIVE = "autoregressive"
    ENSEMBLE = "ensemble"

class AlertLevel(Enum):
    """Niveles de alerta predictiva"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class PredictionResult:
    """Resultado de una predicción individual"""
    sensor_id: str
    device_id: str
    sensor_type: str
    current_value: float
    predicted_value: float
    prediction_time: datetime
    horizon: PredictionHorizon
    algorithm_used: PredictionAlgorithm
    confidence: float  # 0.0 to 1.0
    confidence_interval: Tuple[float, float]
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    trend_strength: float  # 0.0 to 1.0
    seasonality_detected: bool
    anomaly_probability: float  # 0.0 to 1.0
    predicted_at: datetime

@dataclass
class PredictiveAlert:
    """Alerta predictiva generada"""
    alert_id: str
    level: AlertLevel
    title: str
    description: str
    prediction: PredictionResult
    time_to_event: timedelta
    probability: float
    impact_assessment: str
    recommended_actions: List[str]
    threshold_crossed: Optional[str] = None
    historical_precedent: Optional[Dict] = None
    generated_at: datetime = field(default_factory=datetime.now)

@dataclass
class FailurePrediction:
    """Predicción de fallo de dispositivo/sensor"""
    device_id: str
    sensor_type: str
    failure_type: str
    probability: float
    estimated_time_to_failure: timedelta
    confidence: float
    indicators: List[str]
    maintenance_window: str
    cost_impact: str
    prevention_actions: List[str]

class PredictiveAnalysisEngine:
    """
    Motor avanzado de análisis predictivo para sistemas IoT.
    
    Capacidades:
    - Predicciones multi-algoritmo con ensamble
    - Detección automática de estacionalidad
    - Predicción de fallos y degradación
    - Alertas tempranas inteligentes
    - Análisis de tendencias complejas
    - Adaptación automática de modelos
    """
    
    def __init__(self, jetson_api_url: str):
        self.jetson_api_url = jetson_api_url
        self.logger = logging.getLogger(__name__)
        
        # Historia de predicciones para aprendizaje
        self.prediction_history: deque = deque(maxlen=10000)
        self.model_performance: Dict[str, Dict] = {}
        
        # Configuración de algoritmos
        self.algorithm_config = {
            PredictionAlgorithm.LINEAR_REGRESSION: {
                'min_data_points': 10,
                'max_lookback_hours': 168,  # 1 semana
                'default_confidence': 0.7
            },
            PredictionAlgorithm.EXPONENTIAL_SMOOTHING: {
                'alpha': 0.3,  # Suavizado
                'beta': 0.1,   # Tendencia
                'gamma': 0.1,  # Estacionalidad
                'min_data_points': 15,
                'seasonal_periods': 24  # Horas para detectar ciclo diario
            },
            PredictionAlgorithm.SEASONAL_DECOMPOSITION: {
                'min_data_points': 48,  # 2 días para detectar estacionalidad
                'seasonal_periods': [24, 168],  # Diario y semanal
                'trend_window': 12
            },
            PredictionAlgorithm.AUTOREGRESSIVE: {
                'max_lags': 24,
                'min_data_points': 50,
                'significance_level': 0.05
            }
        }
        
        # Umbrales por tipo de sensor para alertas
        self.sensor_thresholds = {
            'temperature': {
                'normal_range': (15.0, 35.0),
                'warning_range': (10.0, 40.0),
                'critical_range': (5.0, 45.0),
                'rate_of_change_warning': 3.0,  # °C/hour
                'rate_of_change_critical': 5.0
            },
            'luminosity': {
                'normal_range': (50, 1000),
                'warning_range': (10, 1500),
                'critical_range': (0, 2000),
                'rate_of_change_warning': 200,
                'rate_of_change_critical': 500
            },
            'humidity': {
                'normal_range': (30.0, 70.0),
                'warning_range': (20.0, 80.0),
                'critical_range': (10.0, 90.0),
                'rate_of_change_warning': 10.0,
                'rate_of_change_critical': 20.0
            }
        }
        
        # Patrones de fallo conocidos
        self.failure_patterns = {
            'sensor_drift': {
                'indicators': ['gradual_bias_shift', 'increasing_noise', 'reduced_sensitivity'],
                'typical_duration': timedelta(days=30),
                'severity': 'medium'
            },
            'connection_degradation': {
                'indicators': ['intermittent_data', 'increasing_delays', 'packet_loss'],
                'typical_duration': timedelta(days=7),
                'severity': 'high'
            },
            'power_supply_failure': {
                'indicators': ['voltage_drops', 'unexpected_resets', 'data_corruption'],
                'typical_duration': timedelta(days=2),
                'severity': 'critical'
            },
            'environmental_stress': {
                'indicators': ['temperature_extremes', 'humidity_damage', 'corrosion_signs'],
                'typical_duration': timedelta(days=90),
                'severity': 'medium'
            }
        }
    
    async def generate_comprehensive_predictions(self, 
                                               raw_data: List[Dict],
                                               horizons: List[PredictionHorizon] = None,
                                               algorithms: List[PredictionAlgorithm] = None) -> Dict[str, Any]:
        """
        Genera predicciones comprehensivas usando múltiples algoritmos y horizontes.
        
        Args:
            raw_data: Datos históricos del sistema
            horizons: Horizontes de predicción a usar
            algorithms: Algoritmos específicos a aplicar
            
        Returns:
            Dict con todas las predicciones y alertas generadas
        """
        try:
            self.logger.info("🔮 Iniciando análisis predictivo comprehensivo...")
            
            if not raw_data:
                return self._create_empty_prediction_result("No hay datos para predicción")
            
            # Configurar valores por defecto
            if horizons is None:
                horizons = [PredictionHorizon.SHORT_TERM, PredictionHorizon.MEDIUM_TERM, PredictionHorizon.LONG_TERM]
            
            if algorithms is None:
                algorithms = [PredictionAlgorithm.LINEAR_REGRESSION, PredictionAlgorithm.EXPONENTIAL_SMOOTHING]
            
            df = pd.DataFrame(raw_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Estructura de resultados
            results = {
                'timestamp': datetime.now().isoformat(),
                'data_points_analyzed': len(df),
                'prediction_horizons': [h.value for h in horizons],
                'algorithms_used': [a.value for a in algorithms],
                'predictions': {},
                'predictive_alerts': [],
                'failure_predictions': [],
                'ensemble_predictions': {},
                'model_performance': {},
                'confidence_summary': {}
            }
            
            # 1. GENERAR PREDICCIONES INDIVIDUALES
            individual_predictions = await self._generate_individual_predictions(
                df, horizons, algorithms
            )
            results['predictions'] = individual_predictions
            
            # 2. CREAR PREDICCIONES DE ENSAMBLE
            ensemble_predictions = await self._create_ensemble_predictions(
                individual_predictions, df
            )
            results['ensemble_predictions'] = ensemble_predictions
            
            # 3. GENERAR ALERTAS PREDICTIVAS
            predictive_alerts = await self._generate_predictive_alerts(
                ensemble_predictions, df
            )
            results['predictive_alerts'] = predictive_alerts
            
            # 4. PREDICCIÓN DE FALLOS
            failure_predictions = await self._predict_failures(df)
            results['failure_predictions'] = failure_predictions
            
            # 5. EVALUAR RENDIMIENTO DE MODELOS
            model_performance = await self._evaluate_model_performance(
                individual_predictions, df
            )
            results['model_performance'] = model_performance
            
            # 6. RESUMEN DE CONFIANZA
            confidence_summary = self._calculate_confidence_summary(
                individual_predictions, ensemble_predictions
            )
            results['confidence_summary'] = confidence_summary
            
            # 7. ACTUALIZAR HISTORIA
            self._update_prediction_history(results)
            
            self.logger.info(f"✅ Análisis predictivo completado: "
                           f"{len(individual_predictions)} predicciones individuales, "
                           f"{len(predictive_alerts)} alertas generadas")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error en análisis predictivo: {e}")
            return self._create_empty_prediction_result(f"Error: {str(e)}")
    
    async def _generate_individual_predictions(self, 
                                             df: pd.DataFrame,
                                             horizons: List[PredictionHorizon],
                                             algorithms: List[PredictionAlgorithm]) -> Dict[str, List[PredictionResult]]:
        """Genera predicciones individuales para cada combinación sensor-algoritmo-horizonte"""
        predictions = {}
        
        try:
            # Procesar cada combinación única de dispositivo-sensor
            for (device_id, sensor_type), group in df.groupby(['device_id', 'sensor_type']):
                sensor_key = f"{device_id}_{sensor_type}"
                predictions[sensor_key] = []
                
                if len(group) < 10:  # Necesitamos datos suficientes
                    continue
                
                # Preparar datos temporales
                sensor_data = group.sort_values('timestamp').reset_index(drop=True)
                sensor_data = sensor_data.drop_duplicates(subset=['timestamp'])
                
                # Generar predicciones para cada combinación algoritmo-horizonte
                for algorithm in algorithms:
                    for horizon in horizons:
                        try:
                            prediction = await self._apply_prediction_algorithm(
                                sensor_data, device_id, sensor_type, algorithm, horizon
                            )
                            
                            if prediction:
                                predictions[sensor_key].append(prediction)
                                
                        except Exception as alg_error:
                            self.logger.warning(f"⚠️ Error con {algorithm.value} para {sensor_key}: {alg_error}")
                            continue
            
        except Exception as e:
            self.logger.error(f"❌ Error generando predicciones individuales: {e}")
        
        return predictions
    
    async def _apply_prediction_algorithm(self, 
                                        sensor_data: pd.DataFrame,
                                        device_id: str,
                                        sensor_type: str,
                                        algorithm: PredictionAlgorithm,
                                        horizon: PredictionHorizon) -> Optional[PredictionResult]:
        """Aplica un algoritmo específico de predicción"""
        try:
            config = self.algorithm_config.get(algorithm, {})
            min_points = config.get('min_data_points', 10)
            
            if len(sensor_data) < min_points:
                return None
            
            values = sensor_data['value'].values
            timestamps = sensor_data['timestamp'].values
            current_value = values[-1]
            
            # Calcular tiempo objetivo para la predicción
            last_timestamp = timestamps[-1]
            horizon_hours = self._horizon_to_hours(horizon)
            prediction_time = last_timestamp + pd.Timedelta(hours=horizon_hours)
            
            predicted_value = None
            confidence = 0.5
            confidence_interval = (current_value, current_value)
            trend_direction = 'stable'
            trend_strength = 0.0
            seasonality_detected = False
            
            # Aplicar algoritmo específico
            if algorithm == PredictionAlgorithm.LINEAR_REGRESSION:
                result = self._apply_linear_regression(values, horizon_hours)
                if result:
                    predicted_value, confidence, confidence_interval, trend_direction, trend_strength = result
            
            elif algorithm == PredictionAlgorithm.EXPONENTIAL_SMOOTHING:
                result = self._apply_exponential_smoothing(values, horizon_hours, config)
                if result:
                    predicted_value, confidence, confidence_interval, trend_direction, trend_strength = result
            
            elif algorithm == PredictionAlgorithm.SEASONAL_DECOMPOSITION:
                result = self._apply_seasonal_decomposition(
                    sensor_data, horizon_hours, config
                )
                if result:
                    predicted_value, confidence, confidence_interval, trend_direction, trend_strength, seasonality_detected = result
            
            elif algorithm == PredictionAlgorithm.AUTOREGRESSIVE:
                result = self._apply_autoregressive(values, horizon_hours, config)
                if result:
                    predicted_value, confidence, confidence_interval, trend_direction, trend_strength = result
            
            if predicted_value is None:
                return None
            
            # Calcular probabilidad de anomalía
            anomaly_probability = self._calculate_anomaly_probability(
                predicted_value, values, sensor_type
            )
            
            return PredictionResult(
                sensor_id=f"{device_id}_{sensor_type}",
                device_id=device_id,
                sensor_type=sensor_type,
                current_value=current_value,
                predicted_value=predicted_value,
                prediction_time=prediction_time.to_pydatetime(),
                horizon=horizon,
                algorithm_used=algorithm,
                confidence=confidence,
                confidence_interval=confidence_interval,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                seasonality_detected=seasonality_detected,
                anomaly_probability=anomaly_probability,
                predicted_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error aplicando {algorithm.value}: {e}")
            return None
    
    def _apply_linear_regression(self, values: np.ndarray, horizon_hours: float) -> Optional[Tuple]:
        """Aplica regresión lineal simple"""
        try:
            if len(values) < 3:
                return None
            
            x = np.arange(len(values))
            
            # Regresión lineal usando numpy
            slope, intercept = np.polyfit(x, values, 1)
            
            # Predicción
            future_x = len(values) + horizon_hours  # Aproximación simple
            predicted_value = slope * future_x + intercept
            
            # Calcular confianza basada en R²
            y_pred = slope * x + intercept
            ss_res = np.sum((values - y_pred) ** 2)
            ss_tot = np.sum((values - np.mean(values)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            confidence = max(0, min(r_squared, 1.0))
            
            # Calcular intervalo de confianza aproximado
            residual_std = np.sqrt(ss_res / len(values)) if len(values) > 2 else np.std(values)
            margin = 1.96 * residual_std  # 95% de confianza
            confidence_interval = (predicted_value - margin, predicted_value + margin)
            
            # Determinar dirección y fuerza de tendencia
            if abs(slope) < 0.01:
                trend_direction = 'stable'
                trend_strength = 0.0
            elif slope > 0:
                trend_direction = 'increasing'
                trend_strength = min(abs(slope) / np.std(values), 1.0)
            else:
                trend_direction = 'decreasing'
                trend_strength = min(abs(slope) / np.std(values), 1.0)
            
            return predicted_value, confidence, confidence_interval, trend_direction, trend_strength
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error en regresión lineal: {e}")
            return None
    
    def _apply_exponential_smoothing(self, values: np.ndarray, horizon_hours: float, config: Dict) -> Optional[Tuple]:
        """Aplica suavizado exponencial"""
        try:
            if len(values) < config.get('min_data_points', 15):
                return None
            
            alpha = config.get('alpha', 0.3)
            
            # Suavizado exponencial simple
            smoothed = [values[0]]
            
            for i in range(1, len(values)):
                smoothed_value = alpha * values[i] + (1 - alpha) * smoothed[i-1]
                smoothed.append(smoothed_value)
            
            # Predicción simple (extender la tendencia)
            if len(smoothed) >= 2:
                trend = smoothed[-1] - smoothed[-2]
                predicted_value = smoothed[-1] + trend * horizon_hours
            else:
                predicted_value = smoothed[-1]
            
            # Confianza basada en estabilidad del suavizado
            smoothed_std = np.std(smoothed[-10:]) if len(smoothed) >= 10 else np.std(smoothed)
            original_std = np.std(values[-10:]) if len(values) >= 10 else np.std(values)
            
            confidence = max(0.4, 1 - (smoothed_std / original_std)) if original_std > 0 else 0.5
            
            # Intervalo de confianza basado en variabilidad reciente
            margin = 1.5 * smoothed_std
            confidence_interval = (predicted_value - margin, predicted_value + margin)
            
            # Tendencia
            recent_trend = np.mean(np.diff(smoothed[-5:])) if len(smoothed) >= 5 else 0
            if abs(recent_trend) < 0.01:
                trend_direction = 'stable'
                trend_strength = 0.0
            elif recent_trend > 0:
                trend_direction = 'increasing'
                trend_strength = min(abs(recent_trend) / smoothed_std, 1.0)
            else:
                trend_direction = 'decreasing'
                trend_strength = min(abs(recent_trend) / smoothed_std, 1.0)
            
            return predicted_value, confidence, confidence_interval, trend_direction, trend_strength
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error en suavizado exponencial: {e}")
            return None
    
    def _apply_seasonal_decomposition(self, sensor_data: pd.DataFrame, horizon_hours: float, config: Dict) -> Optional[Tuple]:
        """Aplica descomposición estacional"""
        try:
            min_points = config.get('min_data_points', 48)
            if len(sensor_data) < min_points:
                return None
            
            # Crear serie temporal con índice de tiempo
            ts = sensor_data.set_index('timestamp')['value']
            ts = ts.resample('H').mean().fillna(method='ffill')  # Resample a horas
            
            if len(ts) < 24:  # Necesitamos al menos un día
                return None
            
            # Descomposición simple usando medias móviles
            seasonal_period = 24  # Ciclo diario
            
            # Calcular tendencia con media móvil
            trend = ts.rolling(window=min(12, len(ts)//2), center=True).mean()
            
            # Calcular componente estacional
            detrended = ts - trend
            seasonal = detrended.groupby(detrended.index.hour).mean()
            
            # Reconstruir serie estacional
            seasonal_series = detrended.index.to_series().dt.hour.map(seasonal)
            
            # Residuos
            residual = ts - trend - seasonal_series
            
            # Predicción combinando componentes
            last_trend = trend.dropna().iloc[-1] if not trend.dropna().empty else ts.mean()
            future_hour = (ts.index[-1] + pd.Timedelta(hours=horizon_hours)).hour
            seasonal_component = seasonal.get(future_hour, 0)
            
            predicted_value = last_trend + seasonal_component
            
            # Confianza basada en estabilidad estacional
            seasonal_stability = 1 - (seasonal.std() / ts.std()) if ts.std() > 0 else 0.5
            confidence = max(0.3, min(seasonal_stability, 0.9))
            
            # Intervalo de confianza
            residual_std = residual.std() if not residual.empty else ts.std()
            margin = 1.5 * residual_std
            confidence_interval = (predicted_value - margin, predicted_value + margin)
            
            # Tendencia
            trend_slope = 0
            if not trend.dropna().empty and len(trend.dropna()) >= 2:
                trend_values = trend.dropna().values
                trend_slope = np.mean(np.diff(trend_values[-5:])) if len(trend_values) >= 5 else 0
            
            if abs(trend_slope) < 0.01:
                trend_direction = 'stable'
                trend_strength = 0.0
            elif trend_slope > 0:
                trend_direction = 'increasing'
                trend_strength = min(abs(trend_slope) / ts.std(), 1.0)
            else:
                trend_direction = 'decreasing'
                trend_strength = min(abs(trend_slope) / ts.std(), 1.0)
            
            seasonality_detected = seasonal.std() > ts.std() * 0.1
            
            return predicted_value, confidence, confidence_interval, trend_direction, trend_strength, seasonality_detected
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error en descomposición estacional: {e}")
            return None
    
    def _apply_autoregressive(self, values: np.ndarray, horizon_hours: float, config: Dict) -> Optional[Tuple]:
        """Aplica modelo autorregresivo simple"""
        try:
            min_points = config.get('min_data_points', 50)
            max_lags = config.get('max_lags', 24)
            
            if len(values) < min_points:
                return None
            
            # Modelo AR simple usando correlación con lags
            best_lag = 1
            best_correlation = 0
            
            for lag in range(1, min(max_lags, len(values)//2)):
                if len(values) > lag:
                    correlation = np.corrcoef(values[:-lag], values[lag:])[0,1]
                    if not np.isnan(correlation) and abs(correlation) > best_correlation:
                        best_correlation = abs(correlation)
                        best_lag = lag
            
            # Predicción simple basada en el mejor lag
            if best_correlation > 0.3:  # Solo si hay correlación significativa
                lag_value = values[-best_lag] if len(values) > best_lag else values[-1]
                trend = np.mean(np.diff(values[-5:])) if len(values) >= 5 else 0
                predicted_value = lag_value + trend * horizon_hours
                confidence = best_correlation * 0.8  # Factor de confianza
            else:
                # Fallback a tendencia simple
                trend = np.mean(np.diff(values[-10:])) if len(values) >= 10 else 0
                predicted_value = values[-1] + trend * horizon_hours
                confidence = 0.4
            
            # Intervalo de confianza
            recent_std = np.std(values[-20:]) if len(values) >= 20 else np.std(values)
            margin = 2.0 * recent_std
            confidence_interval = (predicted_value - margin, predicted_value + margin)
            
            # Tendencia
            if abs(trend) < 0.01:
                trend_direction = 'stable'
                trend_strength = 0.0
            elif trend > 0:
                trend_direction = 'increasing'
                trend_strength = min(abs(trend) / recent_std, 1.0)
            else:
                trend_direction = 'decreasing'
                trend_strength = min(abs(trend) / recent_std, 1.0)
            
            return predicted_value, confidence, confidence_interval, trend_direction, trend_strength
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error en modelo autorregresivo: {e}")
            return None
    
    async def _create_ensemble_predictions(self, 
                                         individual_predictions: Dict[str, List[PredictionResult]],
                                         df: pd.DataFrame) -> Dict[str, PredictionResult]:
        """Crea predicciones de ensamble combinando múltiples algoritmos"""
        ensemble_predictions = {}
        
        try:
            for sensor_key, predictions in individual_predictions.items():
                if not predictions:
                    continue
                
                # Agrupar por horizonte
                by_horizon = {}
                for pred in predictions:
                    horizon = pred.horizon
                    if horizon not in by_horizon:
                        by_horizon[horizon] = []
                    by_horizon[horizon].append(pred)
                
                # Crear ensamble para cada horizonte
                for horizon, horizon_predictions in by_horizon.items():
                    if len(horizon_predictions) < 2:  # Necesitamos al menos 2 predicciones
                        continue
                    
                    ensemble_pred = self._combine_predictions(horizon_predictions, sensor_key, horizon)
                    if ensemble_pred:
                        ensemble_key = f"{sensor_key}_{horizon.value}"
                        ensemble_predictions[ensemble_key] = ensemble_pred
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error creando predicciones de ensamble: {e}")
        
        return ensemble_predictions
    
    def _combine_predictions(self, predictions: List[PredictionResult], 
                           sensor_key: str, horizon: PredictionHorizon) -> Optional[PredictionResult]:
        """Combina múltiples predicciones en una predicción de ensamble"""
        try:
            if not predictions:
                return None
            
            # Usar la primera predicción como base
            base_pred = predictions[0]
            
            # Combinar valores usando pesos basados en confianza
            total_weight = sum(p.confidence for p in predictions)
            if total_weight == 0:
                return None
            
            # Predicción ponderada
            weighted_prediction = sum(
                p.predicted_value * p.confidence for p in predictions
            ) / total_weight
            
            # Confianza promedio
            avg_confidence = np.mean([p.confidence for p in predictions])
            
            # Intervalo de confianza combinado
            all_intervals = [p.confidence_interval for p in predictions]
            combined_lower = np.mean([interval[0] for interval in all_intervals])
            combined_upper = np.mean([interval[1] for interval in all_intervals])
            
            # Tendencia por consenso
            trend_votes = [p.trend_direction for p in predictions]
            trend_direction = max(set(trend_votes), key=trend_votes.count)
            
            # Fuerza de tendencia promedio
            avg_trend_strength = np.mean([p.trend_strength for p in predictions])
            
            # Estacionalidad detectada (si al menos la mitad la detecta)
            seasonality_votes = sum(1 for p in predictions if p.seasonality_detected)
            seasonality_detected = seasonality_votes >= len(predictions) / 2
            
            # Probabilidad de anomalía promedio
            avg_anomaly_prob = np.mean([p.anomaly_probability for p in predictions])
            
            return PredictionResult(
                sensor_id=base_pred.sensor_id,
                device_id=base_pred.device_id,
                sensor_type=base_pred.sensor_type,
                current_value=base_pred.current_value,
                predicted_value=weighted_prediction,
                prediction_time=base_pred.prediction_time,
                horizon=horizon,
                algorithm_used=PredictionAlgorithm.ENSEMBLE,
                confidence=avg_confidence,
                confidence_interval=(combined_lower, combined_upper),
                trend_direction=trend_direction,
                trend_strength=avg_trend_strength,
                seasonality_detected=seasonality_detected,
                anomaly_probability=avg_anomaly_prob,
                predicted_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error combinando predicciones: {e}")
            return None
    
    async def _generate_predictive_alerts(self, 
                                        ensemble_predictions: Dict[str, PredictionResult],
                                        df: pd.DataFrame) -> List[PredictiveAlert]:
        """Genera alertas predictivas basadas en las predicciones"""
        alerts = []
        
        try:
            for pred_key, prediction in ensemble_predictions.items():
                sensor_type = prediction.sensor_type
                current_value = prediction.current_value
                predicted_value = prediction.predicted_value
                
                # Obtener umbrales para este tipo de sensor
                thresholds = self._get_sensor_thresholds(sensor_type)
                
                # Verificar diferentes tipos de alertas
                alert_conditions = []
                
                # 1. Cruce de umbral crítico
                if self._will_cross_critical_threshold(current_value, predicted_value, thresholds):
                    alert_conditions.append('critical_threshold')
                
                # 2. Tasa de cambio peligrosa
                if self._dangerous_rate_of_change(current_value, predicted_value, prediction.horizon, thresholds):
                    alert_conditions.append('dangerous_rate')
                
                # 3. Alta probabilidad de anomalía
                if prediction.anomaly_probability > 0.7:
                    alert_conditions.append('anomaly_risk')
                
                # 4. Tendencia sostenida preocupante
                if self._concerning_sustained_trend(prediction, thresholds):
                    alert_conditions.append('sustained_trend')
                
                # Crear alertas para cada condición
                for condition in alert_conditions:
                    alert = self._create_predictive_alert(prediction, condition, thresholds)
                    if alert:
                        alerts.append(alert)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error generando alertas predictivas: {e}")
        
        return alerts
    
    async def _predict_failures(self, df: pd.DataFrame) -> List[FailurePrediction]:
        """Predice posibles fallos de dispositivos/sensores"""
        failure_predictions = []
        
        try:
            # Analizar cada dispositivo-sensor por separado
            for (device_id, sensor_type), group in df.groupby(['device_id', 'sensor_type']):
                if len(group) < 50:  # Necesitamos historia suficiente
                    continue
                
                sensor_data = group.sort_values('timestamp').reset_index(drop=True)
                values = sensor_data['value'].values
                
                # Detectar indicadores de fallo
                failure_indicators = self._detect_failure_indicators(values, sensor_data)
                
                if failure_indicators:
                    # Estimar tipo de fallo más probable
                    failure_type = self._classify_failure_type(failure_indicators)
                    
                    # Calcular probabilidad y tiempo estimado
                    probability = self._calculate_failure_probability(failure_indicators)
                    time_to_failure = self._estimate_time_to_failure(failure_indicators, failure_type)
                    
                    if probability > 0.3:  # Solo fallos con probabilidad significativa
                        failure_pred = FailurePrediction(
                            device_id=device_id,
                            sensor_type=sensor_type,
                            failure_type=failure_type,
                            probability=probability,
                            estimated_time_to_failure=time_to_failure,
                            confidence=min(probability * 1.2, 0.9),
                            indicators=failure_indicators,
                            maintenance_window=self._suggest_maintenance_window(time_to_failure),
                            cost_impact=self._assess_cost_impact(failure_type, device_id),
                            prevention_actions=self._get_prevention_actions(failure_type, failure_indicators)
                        )
                        
                        failure_predictions.append(failure_pred)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error prediciendo fallos: {e}")
        
        return failure_predictions
    
    # MÉTODOS AUXILIARES
    
    def _horizon_to_hours(self, horizon: PredictionHorizon) -> float:
        """Convierte horizonte de predicción a horas"""
        horizon_map = {
            PredictionHorizon.SHORT_TERM: 1.0,
            PredictionHorizon.MEDIUM_TERM: 6.0,
            PredictionHorizon.LONG_TERM: 24.0,
            PredictionHorizon.EXTENDED: 168.0  # 7 días
        }
        return horizon_map.get(horizon, 1.0)
    
    def _calculate_anomaly_probability(self, predicted_value: float, 
                                     historical_values: np.ndarray, 
                                     sensor_type: str) -> float:
        """Calcula probabilidad de que el valor predicho sea anómalo"""
        try:
            if len(historical_values) < 10:
                return 0.0
            
            # Usar Z-score para calcular anomalía
            mean_val = np.mean(historical_values)
            std_val = np.std(historical_values)
            
            if std_val == 0:
                return 0.0
            
            z_score = abs(predicted_value - mean_val) / std_val
            
            # Convertir Z-score a probabilidad de anomalía
            if z_score > 3:
                return 0.95
            elif z_score > 2:
                return 0.80
            elif z_score > 1.5:
                return 0.60
            else:
                return max(0, (z_score - 1) / 2)  # Gradual entre 1 y 2
                
        except Exception:
            return 0.0
    
    def _get_sensor_thresholds(self, sensor_type: str) -> Dict:
        """Obtiene umbrales para un tipo de sensor"""
        # Mapear tipo de sensor a categoría
        sensor_lower = sensor_type.lower()
        
        if any(keyword in sensor_lower for keyword in ['temp', 'ntc', 't1', 't2', 'avg']):
            return self.sensor_thresholds['temperature']
        elif any(keyword in sensor_lower for keyword in ['ldr', 'light', 'lumino']):
            return self.sensor_thresholds['luminosity']
        elif any(keyword in sensor_lower for keyword in ['humid', 'moisture']):
            return self.sensor_thresholds['humidity']
        else:
            # Umbrales genéricos
            return {
                'normal_range': (0, 100),
                'warning_range': (-10, 110),
                'critical_range': (-20, 120),
                'rate_of_change_warning': 10,
                'rate_of_change_critical': 20
            }
    
    def _will_cross_critical_threshold(self, current: float, predicted: float, thresholds: Dict) -> bool:
        """Verifica si se cruzará un umbral crítico"""
        critical_low, critical_high = thresholds['critical_range']
        
        # Verificar cruce hacia arriba
        if current < critical_high <= predicted:
            return True
        
        # Verificar cruce hacia abajo
        if current > critical_low >= predicted:
            return True
        
        return False
    
    def _dangerous_rate_of_change(self, current: float, predicted: float, 
                                horizon: PredictionHorizon, thresholds: Dict) -> bool:
        """Verifica si la tasa de cambio es peligrosa"""
        horizon_hours = self._horizon_to_hours(horizon)
        rate_per_hour = abs(predicted - current) / horizon_hours if horizon_hours > 0 else 0
        
        critical_rate = thresholds.get('rate_of_change_critical', float('inf'))
        
        return rate_per_hour > critical_rate
    
    def _concerning_sustained_trend(self, prediction: PredictionResult, thresholds: Dict) -> bool:
        """Verifica si hay una tendencia sostenida preocupante"""
        if prediction.trend_strength < 0.5:  # Tendencia no lo suficientemente fuerte
            return False
        
        # Si la tendencia llevará fuera del rango normal
        normal_low, normal_high = thresholds['normal_range']
        
        if prediction.trend_direction == 'increasing' and prediction.predicted_value > normal_high:
            return True
        elif prediction.trend_direction == 'decreasing' and prediction.predicted_value < normal_low:
            return True
        
        return False
    
    def _create_predictive_alert(self, prediction: PredictionResult, 
                               condition: str, thresholds: Dict) -> Optional[PredictiveAlert]:
        """Crea una alerta predictiva específica"""
        try:
            alert_id = f"alert_{prediction.sensor_id}_{condition}_{datetime.now().strftime('%H%M%S')}"
            
            # Configurar según tipo de condición
            if condition == 'critical_threshold':
                level = AlertLevel.CRITICAL
                title = f"Umbral crítico será cruzado - {prediction.sensor_type}"
                description = f"Se predice que {prediction.sensor_type} en {prediction.device_id} " \
                            f"cruzará umbral crítico. Valor actual: {prediction.current_value:.2f}, " \
                            f"predicho: {prediction.predicted_value:.2f}"
                impact = "high"
                actions = [
                    "ACCIÓN INMEDIATA: Preparar intervención antes del cruce de umbral",
                    "Verificar condiciones que pueden estar causando el cambio",
                    "Tener personal técnico en standby"
                ]
                
            elif condition == 'dangerous_rate':
                level = AlertLevel.WARNING
                title = f"Tasa de cambio peligrosa - {prediction.sensor_type}"
                description = f"Se detecta tasa de cambio peligrosa en {prediction.sensor_type}. " \
                            f"El valor cambiará rápidamente de {prediction.current_value:.2f} " \
                            f"a {prediction.predicted_value:.2f} en {prediction.horizon.value}"
                impact = "medium"
                actions = [
                    "Monitorear estrechamente la evolución",
                    "Investigar causa de cambio rápido",
                    "Preparar medidas correctivas"
                ]
                
            elif condition == 'anomaly_risk':
                level = AlertLevel.WARNING
                title = f"Alta probabilidad de anomalía - {prediction.sensor_type}"
                description = f"Valor predicho ({prediction.predicted_value:.2f}) tiene " \
                            f"{prediction.anomaly_probability:.1%} probabilidad de ser anómalo"
                impact = "medium"
                actions = [
                    "Verificar calibración del sensor",
                    "Revisar condiciones ambientales",
                    "Considerar validación con sensor secundario"
                ]
                
            elif condition == 'sustained_trend':
                level = AlertLevel.INFO
                title = f"Tendencia sostenida preocupante - {prediction.sensor_type}"
                description = f"Tendencia {prediction.trend_direction} sostenida detectada " \
                            f"con fuerza {prediction.trend_strength:.1%}"
                impact = "low"
                actions = [
                    "Monitorear evolución de la tendencia",
                    "Evaluar si es comportamiento esperado",
                    "Ajustar umbrales si es necesario"
                ]
            
            else:
                return None
            
            # Calcular tiempo hasta el evento
            time_to_event = timedelta(hours=self._horizon_to_hours(prediction.horizon))
            
            return PredictiveAlert(
                alert_id=alert_id,
                level=level,
                title=title,
                description=description,
                prediction=prediction,
                time_to_event=time_to_event,
                probability=prediction.confidence,
                impact_assessment=impact,
                recommended_actions=actions,
                threshold_crossed=condition if 'threshold' in condition else None
            )
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error creando alerta predictiva: {e}")
            return None
    
    def _detect_failure_indicators(self, values: np.ndarray, sensor_data: pd.DataFrame) -> List[str]:
        """Detecta indicadores de posible fallo"""
        indicators = []
        
        try:
            # 1. Deriva gradual
            if len(values) >= 20:
                recent_mean = np.mean(values[-10:])
                older_mean = np.mean(values[-20:-10])
                
                if abs(recent_mean - older_mean) > np.std(values) * 2:
                    indicators.append('gradual_bias_shift')
            
            # 2. Aumento de ruido
            if len(values) >= 30:
                recent_std = np.std(values[-15:])
                older_std = np.std(values[-30:-15])
                
                if recent_std > older_std * 1.5:
                    indicators.append('increasing_noise')
            
            # 3. Valores estancados (sensor no responde)
            unique_recent = len(np.unique(values[-20:])) if len(values) >= 20 else len(np.unique(values))
            if unique_recent < len(values[-20:]) * 0.1:  # Menos del 10% de valores únicos
                indicators.append('reduced_sensitivity')
            
            # 4. Gaps en datos (problemas de comunicación)
            if len(sensor_data) >= 10:
                sensor_data_copy = sensor_data.copy()
                sensor_data_copy['timestamp'] = pd.to_datetime(sensor_data_copy['timestamp'])
                time_diffs = sensor_data_copy['timestamp'].diff().dropna()
                
                if len(time_diffs) > 0:
                    avg_interval = time_diffs.mean().total_seconds()
                    max_gap = time_diffs.max().total_seconds()
                    
                    if max_gap > avg_interval * 5:  # Gap 5 veces mayor que promedio
                        indicators.append('intermittent_data')
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error detectando indicadores de fallo: {e}")
        
        return indicators
    
    def _classify_failure_type(self, indicators: List[str]) -> str:
        """Clasifica el tipo de fallo más probable"""
        # Mapear indicadores a tipos de fallo
        failure_scores = defaultdict(int)
        
        for indicator in indicators:
            if indicator in ['gradual_bias_shift', 'increasing_noise', 'reduced_sensitivity']:
                failure_scores['sensor_drift'] += 1
            elif indicator in ['intermittent_data', 'increasing_delays']:
                failure_scores['connection_degradation'] += 1
            elif indicator in ['voltage_drops', 'unexpected_resets']:
                failure_scores['power_supply_failure'] += 1
        
        # Retornar tipo con mayor puntuación
        if failure_scores:
            return max(failure_scores.items(), key=lambda x: x[1])[0]
        else:
            return 'sensor_drift'  # Por defecto
    
    def _calculate_failure_probability(self, indicators: List[str]) -> float:
        """Calcula probabilidad de fallo basada en indicadores"""
        if not indicators:
            return 0.0
        
        # Cada indicador contribuye a la probabilidad
        base_prob = min(len(indicators) * 0.2, 0.8)  # Máximo 80%
        
        # Ajustar según severidad de indicadores
        severe_indicators = ['power_supply_failure', 'connection_degradation']
        if any(severe in indicator for indicator in indicators for severe in severe_indicators):
            base_prob += 0.2
        
        return min(base_prob, 0.95)  # Máximo 95%
    
    def _estimate_time_to_failure(self, indicators: List[str], failure_type: str) -> timedelta:
        """Estima tiempo hasta el fallo basado en patrones conocidos"""
        if failure_type in self.failure_patterns:
            typical_duration = self.failure_patterns[failure_type]['typical_duration']
            
            # Ajustar según número de indicadores
            severity_factor = len(indicators) / 5.0  # Normalizar
            adjusted_duration = typical_duration * (1 - severity_factor * 0.5)
            
            return max(adjusted_duration, timedelta(hours=1))  # Mínimo 1 hora
        
        return timedelta(days=30)  # Por defecto
    
    def _suggest_maintenance_window(self, time_to_failure: timedelta) -> str:
        """Sugiere ventana de mantenimiento"""
        if time_to_failure.days < 1:
            return "Inmediato (siguiente turno de mantenimiento)"
        elif time_to_failure.days < 7:
            return "Esta semana"
        elif time_to_failure.days < 30:
            return "Este mes"
        else:
            return "Próximo período de mantenimiento programado"
    
    def _assess_cost_impact(self, failure_type: str, device_id: str) -> str:
        """Evalúa impacto económico del fallo"""
        if failure_type == 'power_supply_failure':
            return "Alto - Requiere reemplazo de hardware"
        elif failure_type == 'connection_degradation':
            return "Medio - Posible reemplazo de cables/conectores"
        elif failure_type == 'sensor_drift':
            return "Bajo - Recalibración o reemplazo de sensor"
        else:
            return "Medio - Evaluación técnica requerida"
    
    def _get_prevention_actions(self, failure_type: str, indicators: List[str]) -> List[str]:
        """Obtiene acciones preventivas específicas"""
        actions = []
        
        if failure_type == 'sensor_drift':
            actions.extend([
                "Programar recalibración del sensor",
                "Verificar condiciones ambientales de instalación",
                "Evaluar necesidad de reemplazo del sensor"
            ])
        elif failure_type == 'connection_degradation':
            actions.extend([
                "Inspeccionar todas las conexiones físicas",
                "Verificar integridad de cables",
                "Probar conectividad de red"
            ])
        elif failure_type == 'power_supply_failure':
            actions.extend([
                "URGENTE: Verificar fuente de alimentación",
                "Medir voltajes en todos los puntos",
                "Preparar fuente de alimentación de respaldo"
            ])
        
        return actions
    
    async def _evaluate_model_performance(self, predictions: Dict, df: pd.DataFrame) -> Dict:
        """Evalúa rendimiento de modelos de predicción"""
        performance = {}
        
        try:
            # Evaluar cada algoritmo
            algorithm_scores = defaultdict(list)
            
            for sensor_key, sensor_predictions in predictions.items():
                for pred in sensor_predictions:
                    # Aquí se podría comparar con valores reales si estuvieran disponibles
                    # Por ahora, usar métricas internas
                    algorithm = pred.algorithm_used.value
                    confidence = pred.confidence
                    
                    algorithm_scores[algorithm].append(confidence)
            
            # Calcular métricas promedio por algoritmo
            for algorithm, scores in algorithm_scores.items():
                performance[algorithm] = {
                    'avg_confidence': np.mean(scores),
                    'predictions_count': len(scores),
                    'reliability_score': np.mean(scores) * len(scores) / 100  # Score compuesto
                }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error evaluando rendimiento: {e}")
        
        return performance
    
    def _calculate_confidence_summary(self, individual_predictions: Dict, 
                                    ensemble_predictions: Dict) -> Dict:
        """Calcula resumen de confianza de predicciones"""
        try:
            all_confidences = []
            
            # Recopilar todas las confianzas
            for predictions in individual_predictions.values():
                all_confidences.extend([p.confidence for p in predictions])
            
            ensemble_confidences = [p.confidence for p in ensemble_predictions.values()]
            
            return {
                'individual_predictions': {
                    'count': len(all_confidences),
                    'avg_confidence': np.mean(all_confidences) if all_confidences else 0,
                    'min_confidence': np.min(all_confidences) if all_confidences else 0,
                    'max_confidence': np.max(all_confidences) if all_confidences else 0
                },
                'ensemble_predictions': {
                    'count': len(ensemble_confidences),
                    'avg_confidence': np.mean(ensemble_confidences) if ensemble_confidences else 0,
                    'improvement_over_individual': 
                        (np.mean(ensemble_confidences) - np.mean(all_confidences)) 
                        if all_confidences and ensemble_confidences else 0
                },
                'overall_quality': 'high' if np.mean(all_confidences + ensemble_confidences) > 0.7 else
                                 'medium' if np.mean(all_confidences + ensemble_confidences) > 0.5 else 'low'
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculando resumen de confianza: {e}")
            return {}
    
    def _update_prediction_history(self, results: Dict):
        """Actualiza historia de predicciones para aprendizaje"""
        try:
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'predictions_count': len(results.get('predictions', {})),
                'alerts_count': len(results.get('predictive_alerts', [])),
                'failures_predicted': len(results.get('failure_predictions', [])),
                'avg_confidence': results.get('confidence_summary', {}).get('overall_quality', 'unknown')
            }
            
            self.prediction_history.append(history_entry)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error actualizando historia: {e}")
    
    def _create_empty_prediction_result(self, reason: str) -> Dict[str, Any]:
        """Crea resultado vacío de predicción"""
        return {
            'timestamp': datetime.now().isoformat(),
            'status': 'error',
            'reason': reason,
            'data_points_analyzed': 0,
            'prediction_horizons': [],
            'algorithms_used': [],
            'predictions': {},
            'predictive_alerts': [],
            'failure_predictions': [],
            'ensemble_predictions': {},
            'model_performance': {},
            'confidence_summary': {}
        }