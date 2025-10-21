"""
Generador de Reportes Ejecutivos Ultra-Completos
==============================================

Sistema avanzado para generar reportes ejecutivos con análisis estadísticos
comprehensivos, visualizaciones y exportación en múltiples formatos.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

class ExecutiveReportGenerator:
    """
    Generador de reportes ejecutivos ultra-completos con análisis estadístico avanzado.
    """
    
    def __init__(self, data_connector, visualization_engine=None):
        self.connector = data_connector
        self.visualization_engine = visualization_engine
        
        # Configuración de reportes
        self.report_config = {
            'include_executive_summary': True,
            'include_technical_analysis': True,
            'include_device_breakdown': True,
            'include_sensor_analysis': True,
            'include_trend_analysis': True,
            'include_performance_metrics': True,
            'include_recommendations': True,
            'include_visualizations': True
        }
        
        logger.info("📊 ExecutiveReportGenerator inicializado")
    
    def generate_comprehensive_report(self, hours: float = 24.0, report_type: str = "executive") -> Dict[str, Any]:
        """
        Generar reporte comprehensivo con análisis ejecutivo completo.
        """
        logger.info(f"📋 Generando reporte comprehensivo ({report_type}, {hours}h)")
        
        # 1. Recolectar datos
        start_time = datetime.now()
        raw_data = self.connector.get_all_data_comprehensive(hours=hours, max_records_per_device=1000)
        data_collection_time = (datetime.now() - start_time).total_seconds()
        
        # 2. Análisis ejecutivo
        executive_analysis = self._generate_executive_analysis(raw_data, hours)
        
        # 3. Análisis técnico detallado
        technical_analysis = self._generate_technical_analysis(raw_data)
        
        # 4. Análisis de rendimiento
        performance_analysis = self._generate_performance_analysis(raw_data, hours)
        
        # 5. Análisis de tendencias
        trend_analysis = self._generate_trend_analysis(raw_data)
        
        # 6. Recomendaciones
        recommendations = self._generate_recommendations(raw_data, performance_analysis)
        
        # 7. Visualizaciones
        visualizations = self._generate_report_visualizations(raw_data)
        
        # 8. Métricas de calidad
        quality_metrics = self._calculate_quality_metrics(raw_data)
        
        # Estructura del reporte
        report = {
            'metadata': {
                'report_id': f"IoT_Executive_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'generated_at': datetime.now().isoformat(),
                'report_type': report_type,
                'time_period_hours': hours,
                'data_collection_time_seconds': data_collection_time,
                'total_records_analyzed': len(raw_data),
                'report_version': '2.0-Ultra'
            },
            
            'executive_summary': {
                'overview': executive_analysis['overview'],
                'key_metrics': executive_analysis['key_metrics'],
                'critical_findings': executive_analysis['critical_findings'],
                'status_assessment': executive_analysis['status']
            },
            
            'technical_analysis': {
                'system_overview': technical_analysis['system_overview'],
                'device_analysis': technical_analysis['device_analysis'],
                'sensor_analysis': technical_analysis['sensor_analysis'],
                'data_quality': quality_metrics
            },
            
            'performance_metrics': {
                'system_performance': performance_analysis['system_metrics'],
                'device_performance': performance_analysis['device_metrics'],
                'sensor_performance': performance_analysis['sensor_metrics'],
                'availability_metrics': performance_analysis['availability']
            },
            
            'trend_analysis': {
                'temporal_patterns': trend_analysis['temporal'],
                'value_trends': trend_analysis['trends'],
                'anomaly_detection': trend_analysis['anomalies'],
                'predictive_insights': trend_analysis['predictions']
            },
            
            'recommendations': {
                'immediate_actions': recommendations['immediate'],
                'short_term_improvements': recommendations['short_term'],
                'long_term_strategy': recommendations['long_term'],
                'technical_optimizations': recommendations['technical']
            },
            
            'visualizations': visualizations,
            
            'appendices': {
                'raw_data_summary': self._generate_data_summary(raw_data),
                'technical_specifications': self._generate_tech_specs(),
                'glossary': self._generate_glossary()
            }
        }
        
        logger.info(f"✅ Reporte comprehensivo generado: {len(raw_data)} registros analizados")
        return report
    
    def _generate_executive_analysis(self, data: List[Dict], hours: float) -> Dict[str, Any]:
        """
        Generar análisis ejecutivo de alto nivel.
        """
        if not data:
            return {
                'overview': 'Sistema IoT sin datos disponibles para el período analizado.',
                'key_metrics': {},
                'critical_findings': ['Sin datos disponibles'],
                'status': 'CRÍTICO'
            }
        
        # Análisis de dispositivos
        devices = set(r.get('device_id') for r in data if r.get('device_id'))
        active_devices = len(devices)
        
        # Análisis temporal
        timestamps = [r.get('timestamp') for r in data if r.get('timestamp')]
        latest_activity = max(timestamps) if timestamps else 'Desconocido'
        
        # Análisis de sensores
        sensors = set(f"{r.get('device_id')}_{r.get('sensor_type')}" for r in data 
                     if r.get('device_id') and r.get('sensor_type'))
        total_sensors = len(sensors)
        
        # Métricas clave
        key_metrics = {
            'dispositivos_activos': active_devices,
            'sensores_totales': total_sensors,
            'registros_analizados': len(data),
            'período_análisis_horas': hours,
            'última_actividad': latest_activity,
            'frecuencia_promedio_registros': len(data) / hours if hours > 0 else 0
        }
        
        # Hallazgos críticos
        critical_findings = []
        
        if active_devices == 0:
            critical_findings.append("❌ No se detectaron dispositivos activos")
        elif active_devices < 2:
            critical_findings.append("⚠️ Solo un dispositivo activo detectado")
        else:
            critical_findings.append(f"✅ {active_devices} dispositivos operativos")
        
        if len(data) < 10:
            critical_findings.append("❌ Volumen de datos insuficiente")
        elif len(data) < 100:
            critical_findings.append("⚠️ Volumen de datos bajo")
        else:
            critical_findings.append(f"✅ Volumen de datos saludable ({len(data)} registros)")
        
        # Evaluación de estado
        if active_devices == 0 or len(data) < 10:
            status = 'CRÍTICO'
        elif active_devices < 2 or len(data) < 100:
            status = 'ATENCIÓN'
        else:
            status = 'OPERATIVO'
        
        overview = f"""
El sistema IoT ha sido analizado durante un período de {hours} horas, procesando {len(data)} registros 
de {active_devices} dispositivos activos con {total_sensors} sensores en total.

Estado general del sistema: {status}

El análisis revela un sistema {'funcionando correctamente' if status == 'OPERATIVO' 
else 'con problemas que requieren atención' if status == 'ATENCIÓN' 
else 'en estado crítico que requiere intervención inmediata'}.
        """.strip()
        
        return {
            'overview': overview,
            'key_metrics': key_metrics,
            'critical_findings': critical_findings,
            'status': status
        }
    
    def _generate_technical_analysis(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Generar análisis técnico detallado.
        """
        if not data:
            return {
                'system_overview': {},
                'device_analysis': {},
                'sensor_analysis': {}
            }
        
        # Análisis por dispositivo
        device_analysis = {}
        sensor_analysis = {}
        
        for record in data:
            device_id = record.get('device_id', 'unknown')
            sensor_type = record.get('sensor_type', 'unknown')
            value = record.get('value')
            timestamp = record.get('timestamp')
            
            # Análisis de dispositivo
            if device_id not in device_analysis:
                device_analysis[device_id] = {
                    'total_records': 0,
                    'sensors': set(),
                    'values': [],
                    'timestamps': [],
                    'data_quality_score': 0
                }
            
            device_analysis[device_id]['total_records'] += 1
            device_analysis[device_id]['sensors'].add(sensor_type)
            
            if value is not None:
                try:
                    device_analysis[device_id]['values'].append(float(value))
                except:
                    pass
            
            if timestamp:
                device_analysis[device_id]['timestamps'].append(timestamp)
            
            # Análisis de sensor
            sensor_key = f"{device_id}_{sensor_type}"
            if sensor_key not in sensor_analysis:
                sensor_analysis[sensor_key] = {
                    'device_id': device_id,
                    'sensor_type': sensor_type,
                    'values': [],
                    'statistics': {}
                }
            
            if value is not None:
                try:
                    sensor_analysis[sensor_key]['values'].append(float(value))
                except:
                    pass
        
        # Calcular estadísticas
        for device_id, stats in device_analysis.items():
            stats['sensors'] = list(stats['sensors'])
            stats['unique_sensors'] = len(stats['sensors'])
            
            if stats['values']:
                stats['avg_value'] = sum(stats['values']) / len(stats['values'])
                stats['min_value'] = min(stats['values'])
                stats['max_value'] = max(stats['values'])
                stats['value_range'] = stats['max_value'] - stats['min_value']
            
            # Calcular score de calidad
            completeness = len([v for v in stats['values'] if v is not None]) / max(1, stats['total_records'])
            stats['data_quality_score'] = completeness * 100
        
        for sensor_key, stats in sensor_analysis.items():
            if stats['values'] and len(stats['values']) > 0:
                values = stats['values']
                stats['statistics'] = {
                    'count': len(values),
                    'mean': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'range': max(values) - min(values),
                    'std_dev': self._calculate_std_dev(values) if len(values) > 1 else 0
                }
        
        return {
            'system_overview': {
                'total_devices': len(device_analysis),
                'total_sensors': len(sensor_analysis),
                'total_records': len(data)
            },
            'device_analysis': device_analysis,
            'sensor_analysis': sensor_analysis
        }
    
    def _generate_performance_analysis(self, data: List[Dict], hours: float) -> Dict[str, Any]:
        """
        Generar análisis de rendimiento del sistema.
        """
        if not data:
            return {
                'system_metrics': {},
                'device_metrics': {},
                'sensor_metrics': {},
                'availability': {}
            }
        
        # Métricas del sistema
        total_expected_records = hours * 60 * 2  # Asumiendo 1 registro cada 30 segundos por dispositivo
        actual_records = len(data)
        system_efficiency = (actual_records / total_expected_records) * 100 if total_expected_records > 0 else 0
        
        system_metrics = {
            'data_throughput_records_per_hour': len(data) / hours if hours > 0 else 0,
            'system_efficiency_percentage': min(100, system_efficiency),
            'data_completeness_score': self._calculate_completeness_score(data),
            'uptime_estimation': self._estimate_uptime(data, hours)
        }
        
        # Métricas por dispositivo
        device_metrics = {}
        devices = set(r.get('device_id') for r in data if r.get('device_id'))
        
        for device_id in devices:
            device_data = [r for r in data if r.get('device_id') == device_id]
            device_metrics[device_id] = {
                'record_count': len(device_data),
                'records_per_hour': len(device_data) / hours if hours > 0 else 0,
                'data_consistency': self._calculate_consistency_score(device_data),
                'sensor_diversity': len(set(r.get('sensor_type') for r in device_data if r.get('sensor_type')))
            }
        
        return {
            'system_metrics': system_metrics,
            'device_metrics': device_metrics,
            'sensor_metrics': {},  # Expandir si es necesario
            'availability': {
                'system_availability_percentage': min(100, system_efficiency),
                'device_availability': {device: metrics['record_count'] > 0 
                                      for device, metrics in device_metrics.items()}
            }
        }
    
    def _generate_trend_analysis(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Generar análisis de tendencias y patrones.
        """
        if not data:
            return {
                'temporal': {},
                'trends': {},
                'anomalies': {},
                'predictions': {}
            }
        
        # Análisis temporal básico
        timestamps = [r.get('timestamp') for r in data if r.get('timestamp')]
        if timestamps:
            timestamps.sort()
            temporal_analysis = {
                'first_record': timestamps[0],
                'last_record': timestamps[-1],
                'total_timespan': len(timestamps),
                'average_interval': 'variable'  # Simplificado
            }
        else:
            temporal_analysis = {}
        
        # Análisis de tendencias por sensor
        trends = {}
        sensors = set(f"{r.get('device_id')}_{r.get('sensor_type')}" for r in data 
                     if r.get('device_id') and r.get('sensor_type'))
        
        for sensor_key in sensors:
            device_id, sensor_type = sensor_key.split('_', 1)
            sensor_data = [r for r in data if r.get('device_id') == device_id and r.get('sensor_type') == sensor_type]
            
            values = []
            for record in sensor_data:
                try:
                    values.append(float(record.get('value', 0)))
                except:
                    continue
            
            if len(values) > 2:
                # Análisis de tendencia simple
                trend_direction = 'stable'
                if len(values) > 5:
                    first_half = sum(values[:len(values)//2]) / (len(values)//2)
                    second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
                    
                    if second_half > first_half * 1.05:
                        trend_direction = 'increasing'
                    elif second_half < first_half * 0.95:
                        trend_direction = 'decreasing'
                
                trends[sensor_key] = {
                    'direction': trend_direction,
                    'value_count': len(values),
                    'current_avg': sum(values[-5:]) / min(5, len(values)) if values else 0,
                    'overall_avg': sum(values) / len(values) if values else 0
                }
        
        return {
            'temporal': temporal_analysis,
            'trends': trends,
            'anomalies': {},  # Expandir si es necesario
            'predictions': {}  # Expandir si es necesario
        }
    
    def _generate_recommendations(self, data: List[Dict], performance: Dict) -> Dict[str, Any]:
        """
        Generar recomendaciones técnicas y estratégicas.
        """
        immediate = []
        short_term = []
        long_term = []
        technical = []
        
        # Análisis de la situación actual
        devices = set(r.get('device_id') for r in data if r.get('device_id'))
        
        if len(devices) == 0:
            immediate.append("🚨 CRÍTICO: Restaurar conectividad con dispositivos IoT inmediatamente")
            immediate.append("🔧 Verificar configuración de red y túneles Cloudflare")
            technical.append("Revisar logs de conectividad en Jetson Nano")
            
        elif len(devices) < 2:
            immediate.append("⚠️ Solo un dispositivo reportando - verificar conectividad del segundo dispositivo")
            short_term.append("Implementar monitoreo de conectividad automatizado")
            
        if len(data) < 100:
            immediate.append("📊 Volumen de datos bajo - verificar frecuencia de muestreo")
            technical.append("Optimizar intervalos de recolección de datos")
            
        # Recomendaciones basadas en rendimiento
        system_efficiency = performance.get('system_metrics', {}).get('system_efficiency_percentage', 0)
        
        if system_efficiency < 50:
            immediate.append("⚡ Eficiencia del sistema baja - revisar infraestructura")
            short_term.append("Implementar sistema de alertas automáticas")
            
        # Recomendaciones generales
        short_term.append("📈 Implementar dashboard de monitoreo en tiempo real")
        short_term.append("🔔 Configurar alertas automáticas para anomalías")
        
        long_term.append("🤖 Considerar implementación de machine learning para predicciones")
        long_term.append("📊 Expandir capacidades de análisis estadístico")
        long_term.append("🔄 Implementar sistema de backup y redundancia")
        
        technical.append("Optimizar queries de base de datos para mejor rendimiento")
        technical.append("Implementar cache inteligente para reducir latencia")
        technical.append("Considerar migración a base de datos time-series especializada")
        
        return {
            'immediate': immediate,
            'short_term': short_term,
            'long_term': long_term,
            'technical': technical
        }
    
    def _generate_report_visualizations(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Generar visualizaciones para el reporte.
        """
        visualizations = {
            'charts_generated': [],
            'visualization_summary': 'No hay datos suficientes para generar visualizaciones'
        }
        
        if self.visualization_engine and data and len(data) > 10:
            try:
                # Generar gráficos para el reporte
                chart_paths = self.visualization_engine.generate_charts(data, "reporte ejecutivo comprehensivo")
                
                if chart_paths:
                    visualizations['charts_generated'] = [
                        {
                            'name': path.split('\\')[-1],
                            'path': path,
                            'type': 'time_series' if 'time_series' in path else 'statistics'
                        }
                        for path in chart_paths
                    ]
                    visualizations['visualization_summary'] = f"Se generaron {len(chart_paths)} visualizaciones"
                    
            except Exception as e:
                logger.warning(f"Error generando visualizaciones: {e}")
                visualizations['error'] = str(e)
        
        return visualizations
    
    def _calculate_quality_metrics(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Calcular métricas de calidad de datos.
        """
        if not data:
            return {
                'overall_score': 0,
                'completeness': 0,
                'consistency': 0,
                'accuracy': 0,
                'timeliness': 0
            }
        
        # Completitud
        complete_records = 0
        for record in data:
            if all(field in record and record[field] is not None 
                  for field in ['device_id', 'sensor_type', 'value', 'timestamp']):
                complete_records += 1
        
        completeness = (complete_records / len(data)) * 100
        
        # Consistencia (valores en rangos esperados)
        consistent_records = 0
        for record in data:
            value = record.get('value')
            if value is not None:
                try:
                    val = float(value)
                    # Rangos razonables para sensores IoT
                    if -50 <= val <= 200:  # Temperatura, humedad, etc.
                        consistent_records += 1
                except:
                    pass
        
        consistency = (consistent_records / len(data)) * 100 if data else 0
        
        # Puntualidad (datos recientes)
        recent_threshold = datetime.now() - timedelta(hours=2)
        recent_records = 0
        
        for record in data:
            timestamp_str = record.get('timestamp')
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if timestamp >= recent_threshold:
                        recent_records += 1
                except:
                    pass
        
        timeliness = (recent_records / len(data)) * 100 if data else 0
        
        # Score general
        overall_score = (completeness + consistency + timeliness) / 3
        
        return {
            'overall_score': round(overall_score, 2),
            'completeness': round(completeness, 2),
            'consistency': round(consistency, 2),
            'accuracy': 95.0,  # Asumido - requiere validación externa
            'timeliness': round(timeliness, 2),
            'total_records_evaluated': len(data)
        }
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calcular desviación estándar."""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _calculate_completeness_score(self, data: List[Dict]) -> float:
        """Calcular score de completitud."""
        if not data:
            return 0
        
        complete_records = sum(1 for record in data 
                             if all(record.get(field) is not None 
                                   for field in ['device_id', 'sensor_type', 'value']))
        return (complete_records / len(data)) * 100
    
    def _calculate_consistency_score(self, data: List[Dict]) -> float:
        """Calcular score de consistencia."""
        if not data:
            return 0
        
        # Verificar consistencia de tipos de sensores
        sensor_types = set(r.get('sensor_type') for r in data if r.get('sensor_type'))
        if len(sensor_types) > 0:
            return min(100, len(sensor_types) * 20)  # Más diversidad = más consistencia
        return 0
    
    def _estimate_uptime(self, data: List[Dict], hours: float) -> float:
        """Estimar uptime del sistema."""
        if not data or hours == 0:
            return 0
        
        # Análisis simple basado en distribución temporal
        timestamps = [r.get('timestamp') for r in data if r.get('timestamp')]
        if not timestamps:
            return 0
        
        # Si tenemos datos distribuidos a lo largo del período, asumimos buena disponibilidad
        unique_hours = len(set(ts[:13] for ts in timestamps if len(ts) >= 13))  # YYYY-MM-DDTHH
        estimated_uptime = min(100, (unique_hours / max(1, hours)) * 100)
        
        return estimated_uptime
    
    def _generate_data_summary(self, data: List[Dict]) -> Dict[str, Any]:
        """Generar resumen de datos para apéndice."""
        if not data:
            return {'message': 'No hay datos disponibles'}
        
        return {
            'total_records': len(data),
            'date_range': {
                'first': min(r.get('timestamp', '') for r in data if r.get('timestamp')),
                'last': max(r.get('timestamp', '') for r in data if r.get('timestamp'))
            },
            'devices': list(set(r.get('device_id') for r in data if r.get('device_id'))),
            'sensor_types': list(set(r.get('sensor_type') for r in data if r.get('sensor_type'))),
            'sample_records': data[:5]  # Primeros 5 registros como muestra
        }
    
    def _generate_tech_specs(self) -> Dict[str, Any]:
        """Generar especificaciones técnicas."""
        return {
            'system_architecture': 'IoT Data Collection System',
            'data_sources': ['Jetson Nano API', 'ESP32 WiFi Sensors', 'Arduino Ethernet Sensors'],
            'communication_protocols': ['HTTP/HTTPS', 'WiFi', 'Ethernet'],
            'data_format': 'JSON',
            'update_frequency': 'Variable (typically 30-60 seconds)',
            'storage_backend': 'Time-series optimized database'
        }
    
    def _generate_glossary(self) -> Dict[str, str]:
        """Generar glosario de términos técnicos."""
        return {
            'IoT': 'Internet of Things - Red de dispositivos físicos conectados',
            'Sensor': 'Dispositivo que detecta y mide variables físicas',
            'Device ID': 'Identificador único de cada dispositivo en el sistema',
            'Timestamp': 'Marca temporal que indica cuándo se registró un dato',
            'API': 'Application Programming Interface - Interfaz de programación',
            'Uptime': 'Porcentaje de tiempo que el sistema está operativo',
            'Data Quality Score': 'Métrica que evalúa la calidad de los datos',
            'Throughput': 'Cantidad de datos procesados por unidad de tiempo'
        }
    
    def export_to_pdf(self, report: Dict[str, Any]) -> bytes:
        """
        Exportar reporte a PDF (placeholder - requiere implementación de PDF).
        """
        # Esta función requeriría una librería como reportlab o weasyprint
        logger.warning("Exportación PDF no implementada - usar export_to_html")
        return b""
    
    def export_to_html(self, report: Dict[str, Any]) -> str:
        """
        Exportar reporte a HTML formateado.
        """
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reporte Ejecutivo IoT - {report['metadata']['report_id']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; }}
                .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; }}
                .metric {{ background: #ecf0f1; padding: 10px; margin: 5px 0; }}
                .critical {{ color: #e74c3c; font-weight: bold; }}
                .success {{ color: #27ae60; font-weight: bold; }}
                .warning {{ color: #f39c12; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 REPORTE EJECUTIVO IoT</h1>
                <p>Generado: {report['metadata']['generated_at']}</p>
                <p>Período: {report['metadata']['time_period_hours']} horas</p>
            </div>
            
            <div class="section">
                <h2>🎯 RESUMEN EJECUTIVO</h2>
                <p>{report['executive_summary']['overview']}</p>
                
                <h3>Métricas Clave</h3>
                {self._format_metrics_html(report['executive_summary']['key_metrics'])}
                
                <h3>Hallazgos Críticos</h3>
                <ul>
                    {''.join(f'<li>{finding}</li>' for finding in report['executive_summary']['critical_findings'])}
                </ul>
            </div>
            
            <div class="section">
                <h2>🔧 ANÁLISIS TÉCNICO</h2>
                <p>Dispositivos analizados: {report['technical_analysis']['system_overview'].get('total_devices', 0)}</p>
                <p>Sensores totales: {report['technical_analysis']['system_overview'].get('total_sensors', 0)}</p>
                <p>Registros procesados: {report['technical_analysis']['system_overview'].get('total_records', 0)}</p>
            </div>
            
            <div class="section">
                <h2>⚡ MÉTRICAS DE RENDIMIENTO</h2>
                {self._format_performance_html(report['performance_metrics'])}
            </div>
            
            <div class="section">
                <h2>🚀 RECOMENDACIONES</h2>
                
                <h3>Acciones Inmediatas</h3>
                <ul>
                    {''.join(f'<li>{rec}</li>' for rec in report['recommendations']['immediate_actions'])}
                </ul>
                
                <h3>Mejoras a Corto Plazo</h3>
                <ul>
                    {''.join(f'<li>{rec}</li>' for rec in report['recommendations']['short_term_improvements'])}
                </ul>
            </div>
            
        </body>
        </html>
        """
        
        return html_content
    
    def _format_metrics_html(self, metrics: Dict) -> str:
        """Formatear métricas para HTML."""
        html = ""
        for key, value in metrics.items():
            html += f'<div class="metric"><strong>{key.replace("_", " ").title()}:</strong> {value}</div>'
        return html
    
    def _format_performance_html(self, performance: Dict) -> str:
        """Formatear métricas de rendimiento para HTML."""
        html = ""
        system_metrics = performance.get('system_metrics', {})
        for key, value in system_metrics.items():
            html += f'<div class="metric"><strong>{key.replace("_", " ").title()}:</strong> {value}</div>'
        return html