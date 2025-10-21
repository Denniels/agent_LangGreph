"""
Herramientas de Análisis
========================

Herramientas para analizar datos IoT y generar insights.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from modules.utils.logger import setup_logger

logger = setup_logger(__name__)


class AnalysisTools:
    """
    Herramientas para análisis de datos IoT.
    """
    
    def analyze_sensor_trends(self, sensor_data: List[Dict[str, Any]], 
                            time_window: int = 24) -> Dict[str, Any]:
        """
        Analiza tendencias en los datos de sensores.
        
        Args:
            sensor_data: Lista de datos de sensores
            time_window: Ventana de tiempo en horas
            
        Returns:
            Análisis de tendencias
        """
        if not sensor_data:
            return {"error": "No hay datos para analizar", "total_readings": 0}
        
        try:
            df = pd.DataFrame(sensor_data)
            # Validar columnas mínimas
            required_cols = {"device_id", "sensor_type", "value", "timestamp"}
            missing = required_cols - set(df.columns)
            if missing:
                logger.warning(f"Datos insuficientes para análisis, faltan columnas: {missing}")
                # Devolver estructura mínima para que el agente no falle
                return {
                    "error": "Datos incompletos para análisis",
                    "missing_columns": list(missing),
                    "total_readings": len(df)
                }
            
            # Convertir timestamp si es necesario
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
                df = df.sort_values('timestamp')
            
            # Filtrar por ventana de tiempo
            cutoff_time = pd.Timestamp(datetime.now(), tz='UTC') - timedelta(hours=time_window)
            df_filtered = df[df['timestamp'] >= cutoff_time]
            
            analysis = {
                "total_readings": len(df_filtered),
                "devices_analyzed": df_filtered['device_id'].nunique(),
                "sensor_types": df_filtered['sensor_type'].unique().tolist(),
                "time_range": {
                    "start": df_filtered['timestamp'].min().isoformat() if len(df_filtered) > 0 else None,
                    "end": df_filtered['timestamp'].max().isoformat() if len(df_filtered) > 0 else None
                }
            }
            
            # Análisis por tipo de sensor
            sensor_analysis = {}
            for sensor_type in df_filtered['sensor_type'].unique():
                sensor_df = df_filtered[df_filtered['sensor_type'] == sensor_type]
                if sensor_df.empty:
                    continue
                try:
                    sensor_analysis[sensor_type] = {
                        "count": len(sensor_df),
                        "avg_value": float(sensor_df['value'].mean()),
                        "min_value": float(sensor_df['value'].min()),
                        "max_value": float(sensor_df['value'].max()),
                        "std_deviation": float(sensor_df['value'].std()) if len(sensor_df) > 1 else 0.0,
                        "trend": self._calculate_trend(sensor_df['value'].tolist())
                    }
                except Exception as inner:
                    logger.error(f"Error analizando sensor_type {sensor_type}: {inner}")
                    sensor_analysis[sensor_type] = {"error": str(inner), "count": len(sensor_df)}
            
            analysis["by_sensor_type"] = sensor_analysis
            
            logger.info(f"Análisis completado para {len(df_filtered)} lecturas")
            return analysis
            
        except Exception as e:
            logger.error(f"Error en análisis de tendencias: {e}")
            return {"error": f"Error en análisis: {str(e)}"}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """
        Calcula la tendencia básica de una serie de valores.
        
        Args:
            values: Lista de valores numéricos
            
        Returns:
            Tendencia: 'increasing', 'decreasing', 'stable'
        """
        if len(values) < 2:
            return "insufficient_data"
        
        # Calcular pendiente usando regresión linear simple
        x = np.arange(len(values))
        y = np.array(values)
        
        slope = np.corrcoef(x, y)[0, 1] * (np.std(y) / np.std(x))
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def detect_anomalies(self, sensor_data: List[Dict[str, Any]], 
                        threshold_factor: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detecta anomalías en los datos de sensores usando desviación estándar.
        
        Args:
            sensor_data: Lista de datos de sensores
            threshold_factor: Factor de desviación estándar para considerar anomalía
            
        Returns:
            Lista de anomalías detectadas
        """
        if not sensor_data:
            return []
        
        try:
            df = pd.DataFrame(sensor_data)
            anomalies = []
            
            # Detectar anomalías por tipo de sensor
            for sensor_type in df['sensor_type'].unique():
                sensor_df = df[df['sensor_type'] == sensor_type]
                
                mean_val = sensor_df['value'].mean()
                std_val = sensor_df['value'].std()
                
                if std_val == 0:  # Si no hay variación, no hay anomalías
                    continue
                
                threshold_upper = mean_val + (threshold_factor * std_val)
                threshold_lower = mean_val - (threshold_factor * std_val)
                
                # Encontrar valores anómalos
                anomalous_data = sensor_df[
                    (sensor_df['value'] > threshold_upper) | 
                    (sensor_df['value'] < threshold_lower)
                ]
                
                for _, row in anomalous_data.iterrows():
                    anomalies.append({
                        "device_id": row['device_id'],
                        "sensor_type": row['sensor_type'],
                        "value": row['value'],
                        "timestamp": row['timestamp'].isoformat() if isinstance(row['timestamp'], datetime) else row['timestamp'],
                        "expected_range": {
                            "min": threshold_lower,
                            "max": threshold_upper
                        },
                        "severity": "high" if abs(row['value'] - mean_val) > 3 * std_val else "medium"
                    })
            
            logger.info(f"Detectadas {len(anomalies)} anomalías")
            return {
                "anomalies_found": len(anomalies),
                "anomalies": anomalies,
                "threshold_used": {
                    "method": "statistical",
                    "sigma_multiplier": 2
                }
            }
            
        except Exception as e:
            logger.error(f"Error detectando anomalías: {e}")
            return {
                "anomalies_found": 0,
                "anomalies": [],
                "error": str(e)
            }
    
    def generate_summary_report(self, sensor_data: List[Dict[str, Any]], 
                              alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Genera un reporte resumen del estado del sistema IoT.
        
        Args:
            sensor_data: Datos de sensores
            alerts: Alertas activas
            
        Returns:
            Reporte resumen
        """
        try:
            # Análisis de datos de sensores
            sensor_analysis = self.analyze_sensor_trends(sensor_data)
            
            # Análisis de alertas
            alerts_by_severity = {}
            alerts_by_device = {}
            
            for alert in alerts:
                # Manejar el caso donde alert puede ser un string o dict
                if isinstance(alert, dict):
                    severity = alert.get('severity', 'unknown')
                    device_id = alert.get('device_id', 'unknown')
                else:
                    # Si es un string, asumir severidad media
                    severity = 'medium'
                    device_id = 'unknown'
                
                alerts_by_severity[severity] = alerts_by_severity.get(severity, 0) + 1
                alerts_by_device[device_id] = alerts_by_device.get(device_id, 0) + 1
            
            # Detectar anomalías
            anomalies = self.detect_anomalies(sensor_data)
            
            # Extraer la lista de anomalías del resultado
            anomalies_list = anomalies.get('anomalies', []) if isinstance(anomalies, dict) else []
            
            report = {
                "generated_at": datetime.now().isoformat(),
                "summary": f"Análisis de {len(sensor_data)} lecturas de sensores y {len(alerts)} eventos",
                "sensor_summary": sensor_analysis,
                "alerts_summary": {
                    "total_active_alerts": len(alerts),
                    "by_severity": alerts_by_severity,
                    "devices_with_alerts": len(alerts_by_device),
                    "most_problematic_device": max(alerts_by_device.items(), key=lambda x: x[1])[0] if alerts_by_device else None
                },
                "anomalies_summary": {
                    "total_anomalies": len(anomalies_list),
                    "anomalies_by_severity": {
                        "high": len([a for a in anomalies_list if a.get('severity') == 'high']),
                        "medium": len([a for a in anomalies_list if a.get('severity') == 'medium'])
                    }
                },
                "recommendations": self._generate_recommendations(sensor_analysis, alerts, anomalies_list)
            }
            
            logger.info("Reporte resumen generado exitosamente")
            return report
            
        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
            return {"error": f"Error generando reporte: {str(e)}"}
    
    def _generate_recommendations(self, sensor_analysis: Dict[str, Any], 
                                alerts: List[Dict[str, Any]], 
                                anomalies: List[Dict[str, Any]]) -> List[str]:
        """
        Genera recomendaciones basadas en el análisis de datos.
        
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        # Recomendaciones basadas en alertas
        if len(alerts) > 5:
            recommendations.append("Alto número de alertas activas. Revisar dispositivos con múltiples alertas.")
        
        # Recomendaciones basadas en anomalías
        high_severity_anomalies = len([a for a in anomalies if a.get('severity') == 'high'])
        if high_severity_anomalies > 0:
            recommendations.append(f"Se detectaron {high_severity_anomalies} anomalías de alta severidad. Investigar inmediatamente.")
        
        # Recomendaciones basadas en tendencias
        if 'by_sensor_type' in sensor_analysis:
            for sensor_type, analysis in sensor_analysis['by_sensor_type'].items():
                if analysis.get('trend') == 'increasing' and sensor_type in ['temperature', 'ldr']:
                    recommendations.append(f"Tendencia creciente en {sensor_type}. Monitorear de cerca.")
        
        if not recommendations:
            recommendations.append("Sistema funcionando dentro de parámetros normales.")
        
        return recommendations
