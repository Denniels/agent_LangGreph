"""
📊 Módulo de Visualización Inteligente para IoT
===============================================

Sistema de gráficos que solo se activa cuando:
1. El usuario lo solicita EXPLÍCITAMENTE
2. Es NECESARIO para análisis complejos

NO se usa para consultas simples como "listame X registros"
"""

# Configurar matplotlib para entornos sin display (Streamlit Cloud)
import matplotlib
matplotlib.use('Agg')  # Backend sin display para cloud deployment

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import io
import base64
import logging
import os
import tempfile

import warnings
warnings.filterwarnings('ignore')

# Configurar logging
logger = logging.getLogger(__name__)

# Configurar scikit-learn con manejo de errores para cloud
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("⚠️ scikit-learn no disponible - predicciones ML deshabilitadas")

class IoTVisualizationEngine:
    """
    Motor de visualización inteligente para datos IoT.
    Solo genera gráficos cuando es explícitamente solicitado o necesario.
    """
    
    def __init__(self):
        """Inicializar el motor de visualización"""
        self.supported_chart_types = [
            'time_series', 'statistics', 'comparison', 'prediction', 
            'distribution', 'correlation', 'anomaly_detection'
        ]
        
        # Configurar directorio para gráficos (compatible con Streamlit Cloud)
        self.charts_dir = self._setup_charts_directory()
        
        # Configurar estilo de gráficos
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
    
    def _setup_charts_directory(self) -> str:
        """
        Configurar directorio para gráficos compatible con Streamlit Cloud.
        Usa directorio temporal si no se puede escribir en charts/.
        """
        try:
            # Intentar usar directorio charts/ local
            charts_dir = os.path.join(os.getcwd(), "charts")
            if not os.path.exists(charts_dir):
                os.makedirs(charts_dir, exist_ok=True)
                
            # Probar escribir un archivo de prueba
            test_file = os.path.join(charts_dir, "test.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            
            logger.info(f"📊 Directorio de gráficos: {charts_dir}")
            return charts_dir
            
        except (PermissionError, OSError) as e:
            # Usar directorio temporal en cloud
            charts_dir = tempfile.mkdtemp(prefix="iot_charts_")
            logger.info(f"📊 Directorio temporal para gráficos: {charts_dir}")
            return charts_dir
    
    def should_generate_charts(self, user_query: str, analysis_type: str = "simple") -> bool:
        """
        Determinar si se deben generar gráficos basado en la consulta del usuario.
        
        Args:
            user_query: Consulta del usuario
            analysis_type: Tipo de análisis (simple, advanced, prediction)
            
        Returns:
            True si se deben generar gráficos, False caso contrario
        """
        query_lower = user_query.lower()
        
        # PALABRAS CLAVE EXPLÍCITAS para gráficos
        explicit_chart_keywords = [
            'gráfico', 'grafico', 'gráfica', 'grafica', 'graficar', 
            'visualizar', 'visualización', 'visualizacion',
            'chart', 'plot', 'mostrar gráfico', 'mostrar grafico',
            'con gráfico', 'con grafico', 'graficamente', 'gráficamente'
        ]
        
        # PALABRAS CLAVE que implican análisis avanzado (requieren gráficos)
        advanced_analysis_keywords = [
            'estadísticas avanzadas', 'análisis completo', 'análisis avanzado',
            'tendencias', 'predicción', 'pronóstico', 'comportamiento temporal',
            'evolución', 'patrón', 'patrones', 'correlación', 'distribución',
            'anomalías', 'estadística descriptiva completa'
        ]
        
        # NO graficar para consultas simples
        simple_query_keywords = [
            'listame', 'muestra', 'dame', 'cuáles son', 'qué datos',
            'últimos registros', 'registros de'
        ]
        
        # 1. Si solicita EXPLÍCITAMENTE gráficos
        if any(keyword in query_lower for keyword in explicit_chart_keywords):
            logger.info("🎨 Gráficos solicitados EXPLÍCITAMENTE")
            return True
        
        # 2. Si es análisis avanzado (requiere gráficos por necesidad)
        if any(keyword in query_lower for keyword in advanced_analysis_keywords):
            logger.info("📊 Gráficos NECESARIOS para análisis avanzado")
            return True
        
        # 3. Si es consulta simple, NO graficar
        if any(keyword in query_lower for keyword in simple_query_keywords):
            logger.info("📋 Consulta simple - SIN gráficos")
            return False
        
        # 4. Para tipos de análisis específicos
        if analysis_type in ['prediction', 'advanced_statistics', 'trend_analysis']:
            logger.info(f"📈 Gráficos necesarios para {analysis_type}")
            return True
        
        # Por defecto, NO generar gráficos
        logger.info("🚫 No se requieren gráficos")
        return False
    
    def generate_time_series_chart(self, data: List[Dict], title: str = "Serie Temporal") -> Optional[str]:
        """
        Generar gráfico de serie temporal para datos IoT.
        
        Args:
            data: Lista de registros con timestamp, device_id, sensor_type, value
            title: Título del gráfico
            
        Returns:
            String base64 del gráfico o None si hay error
        """
        try:
            if not data:
                return None
            
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Agrupar por dispositivo y tipo de sensor
            for device_id in df['device_id'].unique():
                device_data = df[df['device_id'] == device_id]
                
                for sensor_type in device_data['sensor_type'].unique():
                    sensor_data = device_data[device_data['sensor_type'] == sensor_type]
                    
                    if len(sensor_data) > 0:
                        label = f"{device_id} - {sensor_type}"
                        ax.plot(sensor_data['timestamp'], sensor_data['value'], 
                               marker='o', markersize=4, linewidth=2, label=label, alpha=0.8)
            
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Tiempo', fontsize=12)
            ax.set_ylabel('Valor del Sensor', fontsize=12)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True, alpha=0.3)
            
            # Formato de fechas en eje X
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # Convertir a base64 para mostrar directamente en Streamlit
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            logger.info(f"✅ Gráfico de serie temporal generado (base64)")
            return chart_base64
            
        except Exception as e:
            logger.error(f"Error generando gráfico de serie temporal: {e}")
            return None
    
    def generate_statistics_chart(self, data: List[Dict], title: str = "Estadísticas por Sensor") -> Optional[str]:
        """
        Generar gráfico de estadísticas (barras con estadísticas descriptivas).
        """
        try:
            if not data:
                return None
            
            df = pd.DataFrame(data)
            
            # Calcular estadísticas por sensor y dispositivo
            stats = df.groupby(['device_id', 'sensor_type'])['value'].agg([
                'count', 'mean', 'std', 'min', 'max'
            ]).reset_index()
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # Gráfico 1: Promedio por sensor
            sensor_groups = stats.groupby('sensor_type')['mean'].mean().sort_values(ascending=False)
            ax1.bar(range(len(sensor_groups)), sensor_groups.values, color='skyblue', alpha=0.8)
            ax1.set_title('Valor Promedio por Tipo de Sensor', fontweight='bold')
            ax1.set_xticks(range(len(sensor_groups)))
            ax1.set_xticklabels(sensor_groups.index, rotation=45)
            ax1.set_ylabel('Valor Promedio')
            
            # Gráfico 2: Cantidad de registros por dispositivo
            device_counts = df['device_id'].value_counts()
            ax2.pie(device_counts.values, labels=device_counts.index, autopct='%1.1f%%', 
                   colors=['lightcoral', 'lightblue', 'lightgreen', 'lightyellow'])
            ax2.set_title('Distribución de Registros por Dispositivo', fontweight='bold')
            
            # Gráfico 3: Rango de valores (min-max) por sensor
            x_pos = range(len(stats))
            ax3.errorbar(x_pos, stats['mean'], 
                        yerr=[stats['mean'] - stats['min'], stats['max'] - stats['mean']], 
                        fmt='o', capsize=5, capthick=2, alpha=0.8)
            ax3.set_title('Rango de Valores por Sensor', fontweight='bold')
            ax3.set_xticks(x_pos)
            ax3.set_xticklabels([f"{row['device_id']}\n{row['sensor_type']}" 
                               for _, row in stats.iterrows()], rotation=45)
            ax3.set_ylabel('Valor')
            
            # Gráfico 4: Desviación estándar
            ax4.bar(x_pos, stats['std'], color='orange', alpha=0.7)
            ax4.set_title('Desviación Estándar por Sensor', fontweight='bold')
            ax4.set_xticks(x_pos)
            ax4.set_xticklabels([f"{row['device_id']}\n{row['sensor_type']}" 
                               for _, row in stats.iterrows()], rotation=45)
            ax4.set_ylabel('Desviación Estándar')
            
            plt.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
            plt.tight_layout()
            
            # Convertir a base64 para mostrar directamente en Streamlit
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            logger.info(f"✅ Gráfico de estadísticas generado (base64)")
            return chart_base64
            
        except Exception as e:
            logger.error(f"Error generando gráfico de estadísticas: {e}")
            return None
    
    def generate_prediction_chart(self, data: List[Dict], hours_ahead: int = 24, 
                                title: str = "Predicción de Sensores") -> Optional[str]:
        """
        Generar gráfico de predicción usando regresión polinomial simple.
        Requiere scikit-learn.
        """
        try:
            if not SKLEARN_AVAILABLE:
                logger.warning("📊 Predicciones no disponibles - scikit-learn no instalado")
                return None
                
            if not data or len(data) < 10:
                return None
            
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            axes = axes.flatten()
            
            plot_count = 0
            max_plots = 4
            
            for device_id in df['device_id'].unique():
                if plot_count >= max_plots:
                    break
                    
                device_data = df[df['device_id'] == device_id]
                
                for sensor_type in device_data['sensor_type'].unique():
                    if plot_count >= max_plots:
                        break
                    
                    sensor_data = device_data[device_data['sensor_type'] == sensor_type]
                    
                    if len(sensor_data) < 5:
                        continue
                    
                    # Preparar datos para predicción
                    sensor_data = sensor_data.copy()
                    sensor_data['time_numeric'] = (sensor_data['timestamp'] - sensor_data['timestamp'].min()).dt.total_seconds() / 3600
                    
                    X = sensor_data['time_numeric'].values.reshape(-1, 1)
                    y = sensor_data['value'].values
                    
                    # Crear modelo polinomial simple
                    poly_features = PolynomialFeatures(degree=2)
                    X_poly = poly_features.fit_transform(X)
                    
                    model = LinearRegression()
                    model.fit(X_poly, y)
                    
                    # Generar predicción
                    last_time = sensor_data['time_numeric'].max()
                    future_times = np.linspace(last_time, last_time + hours_ahead, 50)
                    future_X_poly = poly_features.transform(future_times.reshape(-1, 1))
                    future_predictions = model.predict(future_X_poly)
                    
                    # Crear timestamps futuros
                    future_timestamps = [sensor_data['timestamp'].max() + timedelta(hours=h) 
                                       for h in (future_times - last_time)]
                    
                    ax = axes[plot_count]
                    
                    # Plotear datos históricos
                    ax.plot(sensor_data['timestamp'], sensor_data['value'], 
                           'o-', label='Datos Históricos', linewidth=2, markersize=4)
                    
                    # Plotear predicción
                    ax.plot(future_timestamps, future_predictions, 
                           '--', label=f'Predicción {hours_ahead}h', linewidth=2, alpha=0.8, color='red')
                    
                    ax.set_title(f'{device_id} - {sensor_type}', fontweight='bold')
                    ax.set_xlabel('Tiempo')
                    ax.set_ylabel('Valor')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    
                    # Formato de fechas
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
                    
                    plot_count += 1
            
            # Ocultar subplots no utilizados
            for i in range(plot_count, max_plots):
                axes[i].set_visible(False)
            
            plt.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
            plt.tight_layout()
            
            # Convertir a base64 para mostrar directamente en Streamlit
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            logger.info(f"📊 Gráfico de predicción generado (base64)")
            return chart_base64
            
        except Exception as e:
            logger.error(f"Error generando gráfico de predicción: {e}")
            return None
    
    def generate_comprehensive_analysis(self, data: List[Dict], analysis_hours: int = 24) -> Dict[str, Any]:
        """
        Generar análisis completo con múltiples gráficos cuando es necesario.
        
        Args:
            data: Datos de sensores
            analysis_hours: Horas de análisis
            
        Returns:
            Dict con gráficos y estadísticas
        """
        try:
            results = {
                'charts': {},
                'statistics': {},
                'insights': []
            }
            
            if not data:
                return results
            
            # 1. Gráfico de serie temporal
            time_series_chart = self.generate_time_series_chart(
                data, f"Serie Temporal - Últimas {analysis_hours} Horas"
            )
            if time_series_chart:
                results['charts']['time_series'] = time_series_chart
            
            # 2. Gráfico de estadísticas
            stats_chart = self.generate_statistics_chart(
                data, f"Estadísticas Descriptivas - {analysis_hours}h"
            )
            if stats_chart:
                results['charts']['statistics'] = stats_chart
            
            # 3. Gráfico de predicción
            prediction_chart = self.generate_prediction_chart(
                data, hours_ahead=24, title="Predicción para las Próximas 24 Horas"
            )
            if prediction_chart:
                results['charts']['prediction'] = prediction_chart
            
            # 4. Calcular estadísticas numéricas
            df = pd.DataFrame(data)
            
            # Estadísticas por sensor
            sensor_stats = {}
            for device_id in df['device_id'].unique():
                device_data = df[df['device_id'] == device_id]
                sensor_stats[device_id] = {}
                
                for sensor_type in device_data['sensor_type'].unique():
                    sensor_data = device_data[device_data['sensor_type'] == sensor_type]
                    
                    sensor_stats[device_id][sensor_type] = {
                        'count': len(sensor_data),
                        'mean': float(sensor_data['value'].mean()),
                        'std': float(sensor_data['value'].std()),
                        'min': float(sensor_data['value'].min()),
                        'max': float(sensor_data['value'].max()),
                        'range': float(sensor_data['value'].max() - sensor_data['value'].min())
                    }
            
            results['statistics'] = sensor_stats
            
            # 5. Generar insights automáticos
            insights = []
            
            # Insight sobre cantidad de datos
            total_records = len(df)
            devices_count = df['device_id'].nunique()
            sensors_count = df['sensor_type'].nunique()
            
            insights.append(f"📊 Se analizaron {total_records} registros de {devices_count} dispositivos y {sensors_count} tipos de sensores")
            
            # Insight sobre dispositivo más activo
            most_active_device = df['device_id'].value_counts().index[0]
            most_active_count = df['device_id'].value_counts().iloc[0]
            insights.append(f"📱 Dispositivo más activo: {most_active_device} con {most_active_count} registros")
            
            # Insight sobre rangos de temperatura
            temp_sensors = ['temperature_1', 'temperature_2', 'temperature_avg', 'ntc_entrada', 'ntc_salida']
            temp_data = df[df['sensor_type'].isin(temp_sensors)]
            if not temp_data.empty:
                temp_mean = temp_data['value'].mean()
                temp_std = temp_data['value'].std()
                insights.append(f"🌡️ Temperatura promedio: {temp_mean:.1f}°C (±{temp_std:.1f}°C)")
            
            results['insights'] = insights
            
            return results
            
        except Exception as e:
            logger.error(f"Error en análisis completo: {e}")
            return {'charts': {}, 'statistics': {}, 'insights': []}
    
    def generate_charts(self, data: str, user_query: str = "") -> List[str]:
        """
        Método principal para generar gráficos desde el agente.
        
        Args:
            data: Datos formateados como string JSON o lista
            user_query: Consulta del usuario para contexto
            
        Returns:
            Lista de rutas de archivos de gráficos generados
        """
        try:
            # Convertir datos de string a lista si es necesario
            if isinstance(data, str):
                import json
                try:
                    # Intentar parsear como JSON
                    data_list = json.loads(data) if data.strip().startswith('[') else []
                except json.JSONDecodeError:
                    logger.warning("No se pudo parsear los datos como JSON")
                    return []
            else:
                data_list = data
            
            if not data_list:
                logger.warning("No hay datos válidos para generar gráficos")
                return []
            
            logger.info(f"📊 Generando gráficos para {len(data_list)} registros")
            
            # Generar análisis completo
            analysis = self.generate_comprehensive_analysis(data_list)
            
            # Extraer rutas de gráficos del resultado
            charts_dict = analysis.get("charts", {})
            chart_paths = []
            
            for chart_type, path in charts_dict.items():
                if path and isinstance(path, str):
                    chart_paths.append(path)
            
            logger.info(f"✅ Generados {len(chart_paths)} gráficos exitosamente")
            return chart_paths
            
        except Exception as e:
            logger.error(f"Error generando gráficos: {e}")
            return []


def create_visualization_engine() -> IoTVisualizationEngine:
    """Crear instancia del motor de visualización"""
    return IoTVisualizationEngine()

# Alias para compatibilidad
VisualizationEngine = IoTVisualizationEngine