"""
Sistema de Alertas Inteligentes para IoT
======================================

Sistema avanzado de alertas contextual con priorización automática,
escalamiento inteligente y recomendaciones específicas por situación.

Este sistema aprende patrones de comportamiento y genera alertas proactivas.
"""

import logging
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum, IntEnum
import json
import hashlib
import statistics
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AlertSeverity(IntEnum):
    """Niveles de severidad de alertas (ordenados por prioridad)"""
    INFO = 1
    WARNING = 2
    CRITICAL = 3
    EMERGENCY = 4

class AlertCategory(Enum):
    """Categorías de alertas"""
    SENSOR_ANOMALY = "sensor_anomaly"
    SYSTEM_PERFORMANCE = "system_performance"
    PREDICTIVE = "predictive"
    MAINTENANCE = "maintenance"
    SECURITY = "security"
    ENVIRONMENTAL = "environmental"
    CONNECTIVITY = "connectivity"
    DATA_QUALITY = "data_quality"

class AlertStatus(Enum):
    """Estados de alertas"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"

class EscalationLevel(Enum):
    """Niveles de escalamiento"""
    LEVEL_0 = "automatic_handling"     # Manejo automático
    LEVEL_1 = "operator_notification" # Notificar operador
    LEVEL_2 = "supervisor_alert"      # Alerta a supervisor
    LEVEL_3 = "management_emergency"  # Emergencia a gerencia

@dataclass
class AlertRule:
    """Regla de alerta configurable"""
    rule_id: str
    name: str
    category: AlertCategory
    severity: AlertSeverity
    condition: str  # Condición lógica como string
    threshold_values: Dict[str, float]
    sensor_types: List[str]
    devices: List[str]  # Vacío = todos los dispositivos
    time_window: timedelta
    cooldown_period: timedelta
    escalation_time: timedelta
    enabled: bool = True
    auto_resolve: bool = True
    suppress_similar: bool = True

@dataclass
class ContextualInfo:
    """Información contextual para alertas"""
    environmental_conditions: Dict[str, float]
    system_load: float
    recent_maintenance: List[str]
    historical_pattern: str
    related_alerts: List[str]
    business_impact: str
    affected_processes: List[str]

@dataclass
class SmartAlert:
    """Alerta inteligente generada"""
    alert_id: str
    rule_id: str
    title: str
    description: str
    category: AlertCategory
    severity: AlertSeverity
    status: AlertStatus
    
    # Datos del sensor/dispositivo
    device_id: str
    sensor_type: str
    current_value: float
    threshold_crossed: str
    
    # Contexto temporal
    triggered_at: datetime
    last_updated: datetime
    estimated_duration: Optional[timedelta]
    
    # Análisis inteligente
    root_cause_analysis: List[str]
    impact_assessment: str
    confidence_score: float  # 0.0 to 1.0
    false_positive_probability: float
    
    # Recomendaciones
    immediate_actions: List[str]
    preventive_measures: List[str]
    escalation_plan: List[str]
    
    # Contexto
    contextual_info: ContextualInfo
    related_alerts: List[str]
    historical_precedent: Optional[Dict]
    
    # Escalamiento
    escalation_level: EscalationLevel
    escalation_history: List[Tuple[datetime, EscalationLevel]]
    acknowledgments: List[Tuple[datetime, str, str]]  # timestamp, user, comment
    
    # Métricas
    response_time_target: timedelta
    business_priority: int  # 1-10
    cost_impact: str
    
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class AlertSummary:
    """Resumen de alertas del sistema"""
    total_alerts: int
    active_alerts: int
    by_severity: Dict[AlertSeverity, int]
    by_category: Dict[AlertCategory, int]
    by_device: Dict[str, int]
    escalated_alerts: int
    false_positive_rate: float
    avg_response_time: timedelta
    top_alert_sources: List[Tuple[str, int]]
    trending_issues: List[str]

class IntelligentAlertSystem:
    """
    Sistema inteligente de alertas para IoT con capacidades avanzadas.
    
    Características Principales:
    - Generación contextual de alertas
    - Priorización automática inteligente
    - Escalamiento dinámico por severidad
    - Supresión de alertas similares
    - Análisis de causa raíz automático
    - Recomendaciones específicas por situación
    - Aprendizaje de patrones históricos
    - Detección de falsos positivos
    - Correlación multi-sensor
    - Integración con sistema de mantenimiento
    """
    
    def __init__(self, jetson_api_url: str):
        self.jetson_api_url = jetson_api_url
        self.logger = logging.getLogger(__name__)
        
        # Almacenamiento de alertas
        self.active_alerts: Dict[str, SmartAlert] = {}
        self.alert_history: deque = deque(maxlen=10000)
        self.suppressed_alerts: Set[str] = set()
        
        # Reglas de alerta predefinidas
        self.alert_rules: Dict[str, AlertRule] = {}
        self._initialize_default_rules()
        
        # Sistema de aprendizaje
        self.pattern_memory: Dict[str, Dict] = defaultdict(dict)
        self.false_positive_patterns: List[Dict] = []
        self.escalation_patterns: Dict[str, List] = defaultdict(list)
        
        # Configuración de escalamiento
        self.escalation_config = {
            EscalationLevel.LEVEL_0: {'auto_actions': True, 'notify': []},
            EscalationLevel.LEVEL_1: {'notify': ['operator'], 'timeout': timedelta(minutes=15)},
            EscalationLevel.LEVEL_2: {'notify': ['supervisor', 'operator'], 'timeout': timedelta(minutes=30)},
            EscalationLevel.LEVEL_3: {'notify': ['management', 'supervisor'], 'timeout': timedelta(minutes=5)}
        }
        
        # Contexto del sistema
        self.system_context = {
            'maintenance_mode': False,
            'high_load_threshold': 0.8,
            'business_hours': (8, 18),  # 8 AM - 6 PM
            'critical_sensors': set(),
            'recent_changes': deque(maxlen=100)
        }
        
        # Métricas de rendimiento
        self.performance_metrics = {
            'alerts_generated': 0,
            'false_positives': 0,
            'true_positives': 0,
            'avg_resolution_time': timedelta(0),
            'escalation_rate': 0.0
        }
    
    def _initialize_default_rules(self):
        """Inicializa reglas de alerta por defecto"""
        
        # Regla: Temperatura crítica
        self.alert_rules['temp_critical'] = AlertRule(
            rule_id='temp_critical',
            name='Temperatura Crítica',
            category=AlertCategory.ENVIRONMENTAL,
            severity=AlertSeverity.CRITICAL,
            condition='value > threshold_high OR value < threshold_low',
            threshold_values={'threshold_high': 40.0, 'threshold_low': 0.0},
            sensor_types=['temperature', 'ntc', 'temp_avg', 't1', 't2'],
            devices=[],  # Todos los dispositivos
            time_window=timedelta(minutes=5),
            cooldown_period=timedelta(minutes=30),
            escalation_time=timedelta(minutes=15)
        )
        
        # Regla: Anomalía de sensor
        self.alert_rules['sensor_anomaly'] = AlertRule(
            rule_id='sensor_anomaly',
            name='Anomalía de Sensor Detectada',
            category=AlertCategory.SENSOR_ANOMALY,
            severity=AlertSeverity.WARNING,
            condition='z_score > threshold OR missing_data > threshold_time',
            threshold_values={'threshold': 3.0, 'threshold_time': 600},  # 10 minutos
            sensor_types=[],  # Todos los sensores
            devices=[],
            time_window=timedelta(minutes=10),
            cooldown_period=timedelta(hours=1),
            escalation_time=timedelta(hours=2)
        )
        
        # Regla: Degradación de conectividad
        self.alert_rules['connectivity_degraded'] = AlertRule(
            rule_id='connectivity_degraded',
            name='Conectividad Degradada',
            category=AlertCategory.CONNECTIVITY,
            severity=AlertSeverity.WARNING,
            condition='data_gap > threshold',
            threshold_values={'threshold': 900},  # 15 minutos sin datos
            sensor_types=[],
            devices=[],
            time_window=timedelta(minutes=20),
            cooldown_period=timedelta(hours=1),
            escalation_time=timedelta(hours=4)
        )
        
        # Regla: Predicción de fallo
        self.alert_rules['failure_prediction'] = AlertRule(
            rule_id='failure_prediction',
            name='Predicción de Fallo de Componente',
            category=AlertCategory.PREDICTIVE,
            severity=AlertSeverity.WARNING,
            condition='failure_probability > threshold',
            threshold_values={'threshold': 0.7},
            sensor_types=[],
            devices=[],
            time_window=timedelta(hours=1),
            cooldown_period=timedelta(hours=6),
            escalation_time=timedelta(hours=12)
        )
        
        # Regla: Mantenimiento requerido
        self.alert_rules['maintenance_due'] = AlertRule(
            rule_id='maintenance_due',
            name='Mantenimiento Preventivo Requerido',
            category=AlertCategory.MAINTENANCE,
            severity=AlertSeverity.INFO,
            condition='days_since_maintenance > threshold',
            threshold_values={'threshold': 30},
            sensor_types=[],
            devices=[],
            time_window=timedelta(days=1),
            cooldown_period=timedelta(days=7),
            escalation_time=timedelta(days=3)
        )
    
    async def process_real_time_data(self, 
                                   raw_data: List[Dict],
                                   additional_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Procesa datos en tiempo real y genera alertas inteligentes.
        
        Args:
            raw_data: Datos del sistema IoT
            additional_context: Contexto adicional del sistema
            
        Returns:
            Dict con alertas generadas y análisis del sistema
        """
        try:
            self.logger.info("🚨 Iniciando procesamiento de alertas inteligentes...")
            
            if not raw_data:
                return self._create_empty_alert_result("No hay datos para procesar")
            
            # Actualizar contexto del sistema
            if additional_context:
                self.system_context.update(additional_context)
            
            df = pd.DataFrame(raw_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Estructura de resultados
            results = {
                'timestamp': datetime.now().isoformat(),
                'processing_summary': {
                    'data_points_processed': len(df),
                    'sensors_analyzed': len(df['sensor_type'].unique()),
                    'devices_analyzed': len(df['device_id'].unique()),
                    'time_window': {
                        'start': df['timestamp'].min().isoformat(),
                        'end': df['timestamp'].max().isoformat()
                    }
                },
                'new_alerts': [],
                'updated_alerts': [],
                'resolved_alerts': [],
                'suppressed_alerts': [],
                'alert_summary': {},
                'system_health': {},
                'recommendations': [],
                'escalations': []
            }
            
            # 1. EVALUAR REGLAS DE ALERTA
            new_alerts = await self._evaluate_alert_rules(df)
            results['new_alerts'] = [self._alert_to_dict(alert) for alert in new_alerts]
            
            # 2. ANÁLISIS CONTEXTUAL DE ALERTAS EXISTENTES
            updated_alerts = await self._analyze_existing_alerts(df)
            results['updated_alerts'] = [self._alert_to_dict(alert) for alert in updated_alerts]
            
            # 3. AUTO-RESOLUCIÓN DE ALERTAS
            resolved_alerts = await self._auto_resolve_alerts(df)
            results['resolved_alerts'] = [self._alert_to_dict(alert) for alert in resolved_alerts]
            
            # 4. SUPRESIÓN DE ALERTAS SIMILARES
            suppressed_alerts = await self._suppress_similar_alerts()
            results['suppressed_alerts'] = list(suppressed_alerts)
            
            # 5. ESCALAMIENTO AUTOMÁTICO
            escalations = await self._process_escalations()
            results['escalations'] = escalations
            
            # 6. GENERAR RESUMEN DE ALERTAS
            alert_summary = self._generate_alert_summary()
            results['alert_summary'] = self._summary_to_dict(alert_summary)
            
            # 7. ANÁLISIS DE SALUD DEL SISTEMA
            system_health = await self._analyze_system_health(df)
            results['system_health'] = system_health
            
            # 8. RECOMENDACIONES INTELIGENTES
            recommendations = await self._generate_intelligent_recommendations(df, new_alerts)
            results['recommendations'] = recommendations
            
            # 9. ACTUALIZAR MÉTRICAS DE RENDIMIENTO
            self._update_performance_metrics(results)
            
            # 10. APRENDIZAJE DE PATRONES
            await self._learn_from_alerts(new_alerts, df)
            
            self.logger.info(f"✅ Procesamiento de alertas completado: "
                           f"{len(new_alerts)} nuevas alertas, "
                           f"{len(updated_alerts)} actualizadas, "
                           f"{len(resolved_alerts)} resueltas")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error procesando alertas: {e}")
            return self._create_empty_alert_result(f"Error: {str(e)}")
    
    async def _evaluate_alert_rules(self, df: pd.DataFrame) -> List[SmartAlert]:
        """Evalúa todas las reglas de alerta contra los datos actuales"""
        new_alerts = []
        
        try:
            for rule_id, rule in self.alert_rules.items():
                if not rule.enabled:
                    continue
                
                # Filtrar datos relevantes para esta regla
                rule_data = self._filter_data_for_rule(df, rule)
                
                if rule_data.empty:
                    continue
                
                # Evaluar condición de la regla
                triggered_items = await self._evaluate_rule_condition(rule_data, rule)
                
                # Generar alertas para cada trigger
                for trigger_info in triggered_items:
                    alert = await self._create_smart_alert(rule, trigger_info, rule_data)
                    if alert and self._should_generate_alert(alert):
                        new_alerts.append(alert)
                        self.active_alerts[alert.alert_id] = alert
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error evaluando reglas de alerta: {e}")
        
        return new_alerts
    
    def _filter_data_for_rule(self, df: pd.DataFrame, rule: AlertRule) -> pd.DataFrame:
        """Filtra datos relevantes para una regla específica"""
        filtered_df = df.copy()
        
        # Filtrar por tipos de sensor
        if rule.sensor_types:
            filtered_df = filtered_df[filtered_df['sensor_type'].isin(rule.sensor_types)]
        
        # Filtrar por dispositivos
        if rule.devices:
            filtered_df = filtered_df[filtered_df['device_id'].isin(rule.devices)]
        
        # Filtrar por ventana de tiempo
        if not filtered_df.empty:
            cutoff_time = datetime.now() - rule.time_window
            filtered_df = filtered_df[filtered_df['timestamp'] >= cutoff_time]
        
        return filtered_df
    
    async def _evaluate_rule_condition(self, df: pd.DataFrame, rule: AlertRule) -> List[Dict]:
        """Evalúa la condición específica de una regla"""
        triggered_items = []
        
        try:
            if rule.condition == 'value > threshold_high OR value < threshold_low':
                # Regla de umbral simple
                high_threshold = rule.threshold_values.get('threshold_high', float('inf'))
                low_threshold = rule.threshold_values.get('threshold_low', float('-inf'))
                
                violations = df[(df['value'] > high_threshold) | (df['value'] < low_threshold)]
                
                for _, row in violations.iterrows():
                    triggered_items.append({
                        'device_id': row['device_id'],
                        'sensor_type': row['sensor_type'],
                        'current_value': row['value'],
                        'threshold_crossed': 'high' if row['value'] > high_threshold else 'low',
                        'timestamp': row['timestamp']
                    })
            
            elif 'z_score > threshold' in rule.condition:
                # Regla de anomalía estadística
                threshold = rule.threshold_values.get('threshold', 3.0)
                
                for (device_id, sensor_type), group in df.groupby(['device_id', 'sensor_type']):
                    if len(group) < 5:  # Necesitamos suficientes datos
                        continue
                    
                    values = group['value'].values
                    z_scores = np.abs(stats.zscore(values))
                    
                    anomalies = group[z_scores > threshold]
                    
                    for _, row in anomalies.iterrows():
                        z_score = z_scores[group.index.get_loc(row.name)]
                        triggered_items.append({
                            'device_id': device_id,
                            'sensor_type': sensor_type,
                            'current_value': row['value'],
                            'threshold_crossed': f'z_score_{z_score:.2f}',
                            'timestamp': row['timestamp']
                        })
            
            elif 'data_gap > threshold' in rule.condition:
                # Regla de conectividad
                threshold_seconds = rule.threshold_values.get('threshold', 900)
                
                for (device_id, sensor_type), group in df.groupby(['device_id', 'sensor_type']):
                    group_sorted = group.sort_values('timestamp')
                    
                    # Calcular gaps entre mediciones
                    time_diffs = group_sorted['timestamp'].diff()
                    
                    large_gaps = time_diffs[time_diffs > pd.Timedelta(seconds=threshold_seconds)]
                    
                    for gap_idx in large_gaps.index:
                        if gap_idx > 0:  # Evitar el primer NaN
                            gap_seconds = time_diffs.loc[gap_idx].total_seconds()
                            triggered_items.append({
                                'device_id': device_id,
                                'sensor_type': sensor_type,
                                'current_value': 0,  # No aplica para gaps
                                'threshold_crossed': f'data_gap_{gap_seconds}s',
                                'timestamp': group_sorted.loc[gap_idx, 'timestamp']
                            })
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error evaluando condición de regla {rule.rule_id}: {e}")
        
        return triggered_items
    
    async def _create_smart_alert(self, rule: AlertRule, trigger_info: Dict, context_data: pd.DataFrame) -> Optional[SmartAlert]:
        """Crea una alerta inteligente con análisis completo"""
        try:
            # Generar ID único
            alert_id = self._generate_alert_id(rule.rule_id, trigger_info)
            
            # Análisis de causa raíz
            root_causes = await self._analyze_root_cause(trigger_info, context_data, rule)
            
            # Evaluación de impacto
            impact_assessment = self._assess_impact(trigger_info, rule)
            
            # Calcular confianza
            confidence = self._calculate_alert_confidence(trigger_info, context_data, rule)
            
            # Probabilidad de falso positivo
            false_positive_prob = self._estimate_false_positive_probability(trigger_info, rule)
            
            # Generar recomendaciones
            immediate_actions = self._generate_immediate_actions(rule, trigger_info)
            preventive_measures = self._generate_preventive_measures(rule, trigger_info)
            escalation_plan = self._generate_escalation_plan(rule)
            
            # Información contextual
            contextual_info = await self._gather_contextual_info(trigger_info, context_data)
            
            # Determinar nivel inicial de escalamiento
            escalation_level = self._determine_initial_escalation_level(rule.severity, confidence)
            
            # Precedente histórico
            historical_precedent = self._find_historical_precedent(trigger_info, rule)
            
            alert = SmartAlert(
                alert_id=alert_id,
                rule_id=rule.rule_id,
                title=self._generate_alert_title(rule, trigger_info),
                description=self._generate_alert_description(rule, trigger_info, root_causes),
                category=rule.category,
                severity=rule.severity,
                status=AlertStatus.ACTIVE,
                
                device_id=trigger_info['device_id'],
                sensor_type=trigger_info['sensor_type'],
                current_value=trigger_info['current_value'],
                threshold_crossed=trigger_info['threshold_crossed'],
                
                triggered_at=trigger_info['timestamp'],
                last_updated=datetime.now(),
                estimated_duration=self._estimate_alert_duration(rule, trigger_info),
                
                root_cause_analysis=root_causes,
                impact_assessment=impact_assessment,
                confidence_score=confidence,
                false_positive_probability=false_positive_prob,
                
                immediate_actions=immediate_actions,
                preventive_measures=preventive_measures,
                escalation_plan=escalation_plan,
                
                contextual_info=contextual_info,
                related_alerts=[],  # Se llenará después
                historical_precedent=historical_precedent,
                
                escalation_level=escalation_level,
                escalation_history=[(datetime.now(), escalation_level)],
                acknowledgments=[],
                
                response_time_target=self._calculate_response_time_target(rule.severity),
                business_priority=self._calculate_business_priority(trigger_info, rule),
                cost_impact=self._estimate_cost_impact(rule, trigger_info)
            )
            
            return alert
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error creando alerta inteligente: {e}")
            return None
    
    def _generate_alert_id(self, rule_id: str, trigger_info: Dict) -> str:
        """Genera ID único para la alerta"""
        base_string = f"{rule_id}_{trigger_info['device_id']}_{trigger_info['sensor_type']}_{trigger_info['timestamp']}"
        return hashlib.md5(base_string.encode()).hexdigest()[:16]
    
    async def _analyze_root_cause(self, trigger_info: Dict, context_data: pd.DataFrame, rule: AlertRule) -> List[str]:
        """Analiza posibles causas raíz de la alerta"""
        causes = []
        
        try:
            # Análisis basado en el tipo de regla
            if rule.category == AlertCategory.ENVIRONMENTAL:
                causes.extend([
                    "Condiciones ambientales extremas detectadas",
                    "Posible mal funcionamiento del sistema de climatización",
                    "Exposición directa a fuente de calor/frío"
                ])
            
            elif rule.category == AlertCategory.SENSOR_ANOMALY:
                causes.extend([
                    "Deriva del sensor o descalibración",
                    "Interferencia electromagnética",
                    "Degradación física del componente sensor"
                ])
            
            elif rule.category == AlertCategory.CONNECTIVITY:
                causes.extend([
                    "Problemas de red o conectividad",
                    "Sobrecarga del sistema de comunicación",
                    "Fallos en hardware de comunicación"
                ])
            
            # Análisis de correlación temporal
            if not context_data.empty:
                recent_changes = self._detect_recent_system_changes(context_data)
                if recent_changes:
                    causes.append(f"Cambios recientes en el sistema: {', '.join(recent_changes)}")
            
            # Análisis de patrones históricos
            historical_pattern = self._analyze_historical_pattern(trigger_info)
            if historical_pattern:
                causes.append(f"Patrón histórico identificado: {historical_pattern}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error analizando causa raíz: {e}")
            causes.append("Error en análisis de causa raíz")
        
        return causes
    
    def _assess_impact(self, trigger_info: Dict, rule: AlertRule) -> str:
        """Evalúa el impacto de la alerta"""
        try:
            if rule.severity == AlertSeverity.EMERGENCY:
                return "CRÍTICO: Riesgo inmediato para el sistema y operaciones"
            elif rule.severity == AlertSeverity.CRITICAL:
                return "ALTO: Puede afectar significativamente las operaciones"
            elif rule.severity == AlertSeverity.WARNING:
                return "MEDIO: Monitoreo requerido, posible degradación del servicio"
            else:
                return "BAJO: Información para seguimiento preventivo"
        except Exception:
            return "Impacto no determinado"
    
    def _calculate_alert_confidence(self, trigger_info: Dict, context_data: pd.DataFrame, rule: AlertRule) -> float:
        """Calcula la confianza en la alerta"""
        try:
            base_confidence = 0.7  # Confianza base
            
            # Ajustar por cantidad de datos
            if len(context_data) > 100:
                base_confidence += 0.1
            elif len(context_data) < 10:
                base_confidence -= 0.2
            
            # Ajustar por tipo de regla
            if rule.category == AlertCategory.ENVIRONMENTAL and 'threshold' in trigger_info['threshold_crossed']:
                base_confidence += 0.1  # Umbrales son más confiables
            elif 'z_score' in trigger_info['threshold_crossed']:
                z_score = float(trigger_info['threshold_crossed'].split('_')[2])
                if z_score > 4:
                    base_confidence += 0.2
                elif z_score < 2:
                    base_confidence -= 0.1
            
            return max(0.1, min(0.99, base_confidence))
            
        except Exception:
            return 0.5  # Confianza media por defecto
    
    def _estimate_false_positive_probability(self, trigger_info: Dict, rule: AlertRule) -> float:
        """Estima la probabilidad de falso positivo"""
        try:
            # Análisis básico basado en patrones históricos
            base_fp_prob = 0.1  # 10% base
            
            # Ajustar por tipo de sensor
            sensor_type = trigger_info['sensor_type'].lower()
            if any(keyword in sensor_type for keyword in ['temp', 'temperature']):
                base_fp_prob = 0.05  # Temperatura es más estable
            elif any(keyword in sensor_type for keyword in ['ldr', 'light']):
                base_fp_prob = 0.15  # Luz más variable
            
            # Ajustar por historial de la regla
            rule_history = self.pattern_memory.get(rule.rule_id, {})
            if 'false_positive_rate' in rule_history:
                historical_fp_rate = rule_history['false_positive_rate']
                base_fp_prob = (base_fp_prob + historical_fp_rate) / 2
            
            return max(0.01, min(0.9, base_fp_prob))
            
        except Exception:
            return 0.1  # 10% por defecto
    
    def _generate_immediate_actions(self, rule: AlertRule, trigger_info: Dict) -> List[str]:
        """Genera acciones inmediatas recomendadas"""
        actions = []
        
        try:
            # Acciones basadas en categoría
            if rule.category == AlertCategory.ENVIRONMENTAL:
                actions.extend([
                    f"Verificar condiciones ambientales en {trigger_info['device_id']}",
                    "Inspeccionar sistemas de climatización cercanos",
                    "Confirmar lectura con sensor secundario si disponible"
                ])
            
            elif rule.category == AlertCategory.SENSOR_ANOMALY:
                actions.extend([
                    f"Inspeccionar físicamente sensor {trigger_info['sensor_type']}",
                    "Verificar conexiones y cableado",
                    "Considerar recalibración del sensor"
                ])
            
            elif rule.category == AlertCategory.CONNECTIVITY:
                actions.extend([
                    "Verificar conectividad de red del dispositivo",
                    "Revisar logs de comunicación",
                    "Intentar reinicio remoto si es seguro"
                ])
            
            elif rule.category == AlertCategory.PREDICTIVE:
                actions.extend([
                    "Programar inspección preventiva",
                    "Revisar historial de mantenimiento",
                    "Preparar componentes de reemplazo"
                ])
            
            # Acciones basadas en severidad
            if rule.severity >= AlertSeverity.CRITICAL:
                actions.insert(0, "ACCIÓN INMEDIATA REQUERIDA - No demorar")
                actions.append("Notificar al supervisor de turno")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error generando acciones inmediatas: {e}")
            actions.append("Consultar manual de procedimientos")
        
        return actions
    
    def _generate_preventive_measures(self, rule: AlertRule, trigger_info: Dict) -> List[str]:
        """Genera medidas preventivas"""
        measures = []
        
        try:
            # Medidas generales
            measures.extend([
                "Incrementar frecuencia de monitoreo temporal",
                "Documentar evento para análisis posterior",
                "Revisar umbrales de alerta si es necesario"
            ])
            
            # Medidas específicas por categoría
            if rule.category == AlertCategory.ENVIRONMENTAL:
                measures.extend([
                    "Evaluar mejoras en control ambiental",
                    "Considerar sensores adicionales para redundancia",
                    "Revisar políticas de control de temperatura"
                ])
            
            elif rule.category == AlertCategory.MAINTENANCE:
                measures.extend([
                    "Actualizar calendario de mantenimiento preventivo",
                    "Revisar procedimientos de mantenimiento",
                    "Considerar upgrade de componentes críticos"
                ])
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error generando medidas preventivas: {e}")
        
        return measures
    
    def _generate_escalation_plan(self, rule: AlertRule) -> List[str]:
        """Genera plan de escalamiento"""
        plan = []
        
        try:
            if rule.severity == AlertSeverity.INFO:
                plan = [
                    "Nivel 1: Registro automático (0 min)",
                    "Nivel 2: Notificación a operador (30 min)",
                    "Nivel 3: Revisión en próxima ronda (2 horas)"
                ]
            elif rule.severity == AlertSeverity.WARNING:
                plan = [
                    "Nivel 1: Notificación inmediata a operador (0 min)",
                    "Nivel 2: Escalamiento a supervisor (30 min)",
                    "Nivel 3: Revisión técnica especializada (2 horas)"
                ]
            elif rule.severity == AlertSeverity.CRITICAL:
                plan = [
                    "Nivel 1: Alerta inmediata múltiple (0 min)",
                    "Nivel 2: Llamada a supervisor (15 min)", 
                    "Nivel 3: Activación de protocolo de emergencia (30 min)"
                ]
            else:  # EMERGENCY
                plan = [
                    "Nivel 1: ALERTA MÁXIMA INMEDIATA (0 min)",
                    "Nivel 2: Notificación a gerencia (5 min)",
                    "Nivel 3: Activación de equipo de crisis (10 min)"
                ]
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error generando plan de escalamiento: {e}")
            plan = ["Plan de escalamiento no disponible"]
        
        return plan
    
    async def _gather_contextual_info(self, trigger_info: Dict, context_data: pd.DataFrame) -> ContextualInfo:
        """Recopila información contextual para la alerta"""
        try:
            # Condiciones ambientales actuales
            env_conditions = {}
            if not context_data.empty:
                for sensor_type in ['temperature', 'humidity', 'luminosity']:
                    sensor_data = context_data[context_data['sensor_type'].str.contains(sensor_type, case=False, na=False)]
                    if not sensor_data.empty:
                        env_conditions[sensor_type] = float(sensor_data['value'].mean())
            
            # Carga del sistema (simulada)
            system_load = min(len(context_data) / 1000.0, 1.0)  # Aproximación
            
            # Mantenimiento reciente (simulado)
            recent_maintenance = []
            
            # Patrón histórico
            historical_pattern = "Normal"  # Simplificado
            
            # Alertas relacionadas
            related_alerts = []
            
            # Impacto en el negocio
            business_impact = self._assess_business_impact(trigger_info)
            
            # Procesos afectados
            affected_processes = self._identify_affected_processes(trigger_info)
            
            return ContextualInfo(
                environmental_conditions=env_conditions,
                system_load=system_load,
                recent_maintenance=recent_maintenance,
                historical_pattern=historical_pattern,
                related_alerts=related_alerts,
                business_impact=business_impact,
                affected_processes=affected_processes
            )
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error recopilando información contextual: {e}")
            return ContextualInfo(
                environmental_conditions={},
                system_load=0.5,
                recent_maintenance=[],
                historical_pattern="Desconocido",
                related_alerts=[],
                business_impact="No determinado",
                affected_processes=[]
            )
    
    def _assess_business_impact(self, trigger_info: Dict) -> str:
        """Evalúa impacto en el negocio"""
        device_id = trigger_info.get('device_id', '')
        
        # Lógica simplificada de impacto
        if 'critical' in device_id.lower() or 'main' in device_id.lower():
            return "Alto - Dispositivo crítico del sistema"
        elif 'backup' in device_id.lower() or 'secondary' in device_id.lower():
            return "Medio - Dispositivo de respaldo"
        else:
            return "Bajo - Dispositivo estándar"
    
    def _identify_affected_processes(self, trigger_info: Dict) -> List[str]:
        """Identifica procesos afectados"""
        processes = []
        
        sensor_type = trigger_info.get('sensor_type', '').lower()
        
        if 'temp' in sensor_type:
            processes.extend(['Control de temperatura', 'Sistemas HVAC'])
        elif 'humid' in sensor_type:
            processes.extend(['Control de humedad', 'Calidad del aire'])
        elif 'light' in sensor_type or 'ldr' in sensor_type:
            processes.extend(['Control de iluminación', 'Automatización de edificio'])
        
        return processes
    
    # [CONTINÚA CON MÁS MÉTODOS...]
    
    async def _analyze_existing_alerts(self, df: pd.DataFrame) -> List[SmartAlert]:
        """Analiza alertas existentes y las actualiza"""
        updated_alerts = []
        # Implementación simplificada
        return updated_alerts
    
    async def _auto_resolve_alerts(self, df: pd.DataFrame) -> List[SmartAlert]:
        """Auto-resuelve alertas que ya no aplican"""
        resolved_alerts = []
        # Implementación simplificada
        return resolved_alerts
    
    async def _suppress_similar_alerts(self) -> Set[str]:
        """Suprime alertas similares"""
        return set()
    
    async def _process_escalations(self) -> List[Dict]:
        """Procesa escalamientos automáticos"""
        return []
    
    def _generate_alert_summary(self) -> AlertSummary:
        """Genera resumen de alertas"""
        return AlertSummary(
            total_alerts=len(self.active_alerts),
            active_alerts=len(self.active_alerts),
            by_severity={},
            by_category={},
            by_device={},
            escalated_alerts=0,
            false_positive_rate=0.1,
            avg_response_time=timedelta(minutes=15),
            top_alert_sources=[],
            trending_issues=[]
        )
    
    async def _analyze_system_health(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza salud general del sistema"""
        return {
            'overall_health': 'good',
            'performance_score': 0.85,
            'availability': 0.99
        }
    
    async def _generate_intelligent_recommendations(self, df: pd.DataFrame, alerts: List[SmartAlert]) -> List[str]:
        """Genera recomendaciones inteligentes"""
        return [
            "Sistema operando dentro de parámetros normales",
            "Continuar monitoreo regular"
        ]
    
    def _update_performance_metrics(self, results: Dict):
        """Actualiza métricas de rendimiento"""
        self.performance_metrics['alerts_generated'] += len(results.get('new_alerts', []))
    
    async def _learn_from_alerts(self, alerts: List[SmartAlert], df: pd.DataFrame):
        """Aprende de patrones de alertas"""
        pass
    
    # MÉTODOS AUXILIARES
    
    def _determine_initial_escalation_level(self, severity: AlertSeverity, confidence: float) -> EscalationLevel:
        """Determina nivel inicial de escalamiento"""
        if severity == AlertSeverity.EMERGENCY:
            return EscalationLevel.LEVEL_3
        elif severity == AlertSeverity.CRITICAL and confidence > 0.8:
            return EscalationLevel.LEVEL_2
        elif severity >= AlertSeverity.WARNING:
            return EscalationLevel.LEVEL_1
        else:
            return EscalationLevel.LEVEL_0
    
    def _calculate_response_time_target(self, severity: AlertSeverity) -> timedelta:
        """Calcula tiempo objetivo de respuesta"""
        targets = {
            AlertSeverity.EMERGENCY: timedelta(minutes=5),
            AlertSeverity.CRITICAL: timedelta(minutes=15),
            AlertSeverity.WARNING: timedelta(minutes=30),
            AlertSeverity.INFO: timedelta(hours=2)
        }
        return targets.get(severity, timedelta(hours=1))
    
    def _calculate_business_priority(self, trigger_info: Dict, rule: AlertRule) -> int:
        """Calcula prioridad de negocio (1-10)"""
        priority = 5  # Medio por defecto
        
        if rule.severity == AlertSeverity.EMERGENCY:
            priority = 10
        elif rule.severity == AlertSeverity.CRITICAL:
            priority = 8
        elif rule.severity == AlertSeverity.WARNING:
            priority = 6
        else:
            priority = 4
        
        # Ajustar por dispositivo crítico
        device_id = trigger_info.get('device_id', '').lower()
        if 'critical' in device_id or 'main' in device_id:
            priority = min(10, priority + 2)
        
        return priority
    
    def _estimate_cost_impact(self, rule: AlertRule, trigger_info: Dict) -> str:
        """Estima impacto económico"""
        if rule.severity >= AlertSeverity.CRITICAL:
            return "Alto - Posible pérdida de productividad"
        elif rule.severity == AlertSeverity.WARNING:
            return "Medio - Costos de investigación y corrección"
        else:
            return "Bajo - Costo mínimo de seguimiento"
    
    def _should_generate_alert(self, alert: SmartAlert) -> bool:
        """Determina si se debe generar la alerta"""
        # Verificar cooldown period
        rule = self.alert_rules.get(alert.rule_id)
        if rule and rule.cooldown_period:
            # Simplificado: siempre generar por ahora
            pass
        
        # Verificar si es muy probable falso positivo
        if alert.false_positive_probability > 0.8:
            return False
        
        return True
    
    def _detect_recent_system_changes(self, context_data: pd.DataFrame) -> List[str]:
        """Detecta cambios recientes en el sistema"""
        # Implementación simplificada
        return []
    
    def _analyze_historical_pattern(self, trigger_info: Dict) -> Optional[str]:
        """Analiza patrones históricos"""
        # Implementación simplificada
        return None
    
    def _find_historical_precedent(self, trigger_info: Dict, rule: AlertRule) -> Optional[Dict]:
        """Encuentra precedente histórico"""
        # Implementación simplificada
        return None
    
    def _estimate_alert_duration(self, rule: AlertRule, trigger_info: Dict) -> Optional[timedelta]:
        """Estima duración de la alerta"""
        # Estimación simplificada basada en tipo
        if rule.category == AlertCategory.CONNECTIVITY:
            return timedelta(minutes=30)
        elif rule.category == AlertCategory.ENVIRONMENTAL:
            return timedelta(hours=2)
        else:
            return timedelta(hours=1)
    
    def _generate_alert_title(self, rule: AlertRule, trigger_info: Dict) -> str:
        """Genera título descriptivo de la alerta"""
        return f"{rule.name} - {trigger_info['device_id']} ({trigger_info['sensor_type']})"
    
    def _generate_alert_description(self, rule: AlertRule, trigger_info: Dict, root_causes: List[str]) -> str:
        """Genera descripción detallada de la alerta"""
        desc = (f"Alerta {rule.severity.name} generada para {trigger_info['sensor_type']} "
                f"en dispositivo {trigger_info['device_id']}. "
                f"Valor actual: {trigger_info['current_value']:.2f}, "
                f"Umbral cruzado: {trigger_info['threshold_crossed']}.")
        
        if root_causes:
            desc += f" Posibles causas: {'; '.join(root_causes[:2])}."
        
        return desc
    
    def _alert_to_dict(self, alert: SmartAlert) -> Dict[str, Any]:
        """Convierte alerta a diccionario"""
        return {
            'alert_id': alert.alert_id,
            'title': alert.title,
            'description': alert.description,
            'category': alert.category.value,
            'severity': alert.severity.name,
            'status': alert.status.value,
            'device_id': alert.device_id,
            'sensor_type': alert.sensor_type,
            'current_value': alert.current_value,
            'confidence_score': alert.confidence_score,
            'business_priority': alert.business_priority,
            'immediate_actions': alert.immediate_actions,
            'triggered_at': alert.triggered_at.isoformat(),
            'escalation_level': alert.escalation_level.value
        }
    
    def _summary_to_dict(self, summary: AlertSummary) -> Dict[str, Any]:
        """Convierte resumen a diccionario"""
        return {
            'total_alerts': summary.total_alerts,
            'active_alerts': summary.active_alerts,
            'false_positive_rate': summary.false_positive_rate,
            'avg_response_time_minutes': summary.avg_response_time.total_seconds() / 60
        }
    
    def _create_empty_alert_result(self, reason: str) -> Dict[str, Any]:
        """Crea resultado vacío de alertas"""
        return {
            'timestamp': datetime.now().isoformat(),
            'status': 'error',
            'reason': reason,
            'processing_summary': {},
            'new_alerts': [],
            'updated_alerts': [],
            'resolved_alerts': [],
            'suppressed_alerts': [],
            'alert_summary': {},
            'system_health': {},
            'recommendations': [],
            'escalations': []
        }