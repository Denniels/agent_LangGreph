"""
Módulo de Generación de Reportes Ejecutivos
==========================================

Genera reportes personalizados en múltiples formatos (PDF, CSV, XLSX, PNG, HTML)
basados en consultas de usuario y datos de sensores IoT.
"""

import re
import json
import math
import logging
import statistics
from io import BytesIO
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd

# Imports para gráficos y exportación
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

# Imports para PDF
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm, inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT

logger = logging.getLogger(__name__)

# Configurar kaleido para exportar gráficos
pio.kaleido.scope.default_format = "png"

class ReportGenerator:
    """Generador de reportes ejecutivos flexible"""
    
    def __init__(self, jetson_connector=None):
        self.supported_formats = ["pdf", "csv", "xlsx", "png", "html"]
        self.chart_types = ["line", "bar", "area", "scatter", "heatmap"]
        self.max_data_points = 1000  # Límite para evitar archivos enormes
        
        # Conector para obtener datos reales (NO GENERAR DATOS FICTICIOS)
        self.jetson_connector = jetson_connector
        if not jetson_connector:
            logger.warning("🚨 ReportGenerator inicializado sin conexión a Jetson - solo reportes de error disponibles")
    
    def parse_user_request_to_spec(self, user_text: str, context_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convierte una solicitud en lenguaje natural a especificación estructurada.
        MEJORADO para manejar múltiples dispositivos y sensores.
        
        Args:
            user_text: Texto del usuario pidiendo reporte
            context_metadata: Metadata del agente con dispositivos y sensores disponibles
            
        Returns:
            Especificación del reporte estructurada
        """
        user_lower = user_text.lower()
        
        # Detectar si es una solicitud de reporte
        report_keywords = ["reporte", "informe", "ejecutivo", "descarga", "pdf", "csv", "excel"]
        is_report_request = any(keyword in user_lower for keyword in report_keywords)
        
        if not is_report_request:
            return None
        
        # Detectar múltiples dispositivos
        devices = []
        if any(word in user_lower for word in ['esp32', 'esp']):
            devices.append('esp32_wifi_001')
        if any(word in user_lower for word in ['arduino', 'ethernet']):
            devices.append('arduino_eth_001')
        
        # Si no se detecta ninguno, usar los disponibles
        if not devices:
            available_devices = context_metadata.get("data_summary", {}).get("devices", [])
            devices = available_devices[:2]  # Máximo 2 dispositivos
        
        # Detectar múltiples sensores (SOLO sensores reales disponibles)
        sensors = []
        if any(word in user_lower for word in ['temperatura', 'temp']):
            sensors.append('temperature')
        if any(word in user_lower for word in ['ldr', 'luz', 'light']):
            sensors.append('ldr')
        
        # Si no se detecta ninguno, usar solo sensores reales disponibles
        if not sensors:
            # Solo sensores que realmente existen en nuestro sistema
            real_sensors = ['temperature', 'ldr']  # Solo estos existen
            available_sensors = context_metadata.get("data_summary", {}).get("sensors", real_sensors)
            # Filtrar para asegurar que solo usamos sensores reales
            sensors = [s for s in available_sensors if s in real_sensors][:2]
        
        # Detectar tipos de gráficos específicos por sensor
        chart_types = {}
        if any(word in user_lower for word in ['torta', 'pie', 'circular']):
            if 'temperatura' in user_lower or 'temp' in user_lower:
                chart_types['temperature'] = 'pie'
        if any(word in user_lower for word in ['barra', 'bar']):
            if 'ldr' in user_lower:
                chart_types['ldr'] = 'bar'
        
        # Valores por defecto para sensores sin tipo específico
        for sensor in sensors:
            if sensor not in chart_types:
                chart_types[sensor] = 'line'
        
        spec = {
            "title": "Reporte Ejecutivo IoT - Múltiples Dispositivos",
            "devices": devices,  # Lista de dispositivos
            "sensors": sensors,  # Lista de sensores  
            "chart_types": chart_types,  # Tipo específico por sensor
            "time_range": {"from": None, "to": None, "description": "últimas 24 horas"},
            "chart": {"type": "multiple", "sample_points": 200, "y_label": "Valor"},
            "sections": ["summary", "metrics", "charts"],  # charts en plural
            "format": "pdf",
            "language": "es",
            "meta": {"timestamp": datetime.now().isoformat()}
        }
        
        # Extraer formato
        if "csv" in user_lower:
            spec["format"] = "csv"
            spec["sections"] = ["table"]
        elif "excel" in user_lower or "xlsx" in user_lower:
            spec["format"] = "xlsx"
            spec["sections"] = ["table"]
        elif "png" in user_lower or "imagen" in user_lower:
            spec["format"] = "png"
            spec["sections"] = ["charts"]
        elif "html" in user_lower:
            spec["format"] = "html"
        
        # Extraer rango temporal
        if "48 horas" in user_lower or "2 días" in user_lower:
            spec["time_range"]["description"] = "últimas 48 horas"
        elif "72 horas" in user_lower or "3 días" in user_lower:
            spec["time_range"]["description"] = "últimas 72 horas"
        elif "semana" in user_lower:
            spec["time_range"]["description"] = "última semana"
        
        logger.info(f"Spec generado: dispositivos={devices}, sensores={sensors}, gráficos={chart_types}")
        
        return spec
    
    def _get_valid_device_sensors(self) -> Dict[str, List[str]]:
        """
        Retorna la configuración real de sensores por dispositivo.
        
        Returns:
            Diccionario con dispositivos como claves y lista de sensores como valores
        """
        return {
            "arduino_eth_001": ["t1", "t2", "avg"],  # Solo temperatura (2 sondas + promedio)
            "esp32_wifi_001": ["ntc_entrada", "ntc_salida", "ldr"]  # Temperatura + LDR
        }
    
    def _expand_sensors_for_device(self, device_id: str, logical_sensors: List[str]) -> List[Dict[str, str]]:
        """
        Expande sensores lógicos (como 'temperature') a sensores físicos específicos del dispositivo.
        
        Args:
            device_id: ID del dispositivo
            logical_sensors: Lista de sensores lógicos (ej: ['temperature', 'ldr'])
            
        Returns:
            Lista de diccionarios con mapeo de sensor lógico a físico
        """
        expanded = []
        device_sensors = self._get_valid_device_sensors()
        
        # Normalizar nombre del dispositivo
        normalized_device = device_id.lower()
        if "arduino" in normalized_device and "eth" in normalized_device:
            device_key = "arduino_eth_001"
        elif "esp32" in normalized_device and "wifi" in normalized_device:
            device_key = "esp32_wifi_001"
        else:
            device_key = device_id
        
        physical_sensors = device_sensors.get(device_key, [])
        
        for logical_sensor in logical_sensors:
            if logical_sensor.lower() == 'temperature':
                # Mapear temperatura a sensores físicos de temperatura
                for sensor in physical_sensors:
                    if sensor.lower() in ['t1', 't2', 'avg', 'ntc_entrada', 'ntc_salida']:
                        expanded.append({
                            'logical_sensor': 'temperature',
                            'physical_sensor': sensor
                        })
            elif logical_sensor.lower() == 'ldr':
                # Mapear LDR solo si el dispositivo lo tiene
                if 'ldr' in physical_sensors:
                    expanded.append({
                        'logical_sensor': 'ldr',
                        'physical_sensor': 'ldr'
                    })
            else:
                # Para otros sensores, mapeo directo si existe
                if logical_sensor in physical_sensors:
                    expanded.append({
                        'logical_sensor': logical_sensor,
                        'physical_sensor': logical_sensor
                    })
        
        return expanded
    
    def _is_valid_device_sensor_combination(self, device_id: str, sensor: str) -> bool:
        """
        Valida si un dispositivo específico tiene un sensor específico.
        
        Args:
            device_id: ID del dispositivo
            sensor: Nombre del sensor
            
        Returns:
            True si la combinación es válida, False en caso contrario
        """
        valid_combinations = self._get_valid_device_sensors()
        
        # Normalizar nombres de dispositivos
        normalized_device = device_id.lower()
        if "arduino" in normalized_device and "eth" in normalized_device:
            device_key = "arduino_eth_001"
        elif "esp32" in normalized_device and "wifi" in normalized_device:
            device_key = "esp32_wifi_001"
        else:
            # Para otros dispositivos, permitir todos los sensores (compatibilidad hacia atrás)
            return True
        
        return sensor.lower() in [s.lower() for s in valid_combinations.get(device_key, [])]

    def _get_real_sensor_data(self, device_id: str, sensor: str) -> List[Dict[str, Any]]:
        """
        Obtener datos reales de sensores desde la Jetson API.
        NO genera datos ficticios.
        
        Args:
            device_id: ID del dispositivo
            sensor: Nombre del sensor
            
        Returns:
            Lista de puntos temporales reales o lista vacía si no hay datos
        """
        try:
            if not hasattr(self, 'jetson_connector') or not self.jetson_connector:
                logger.warning(f"🚨 No hay conexión con Jetson API para obtener datos de {device_id}/{sensor}")
                return []
            
            # Intentar obtener datos reales de la Jetson
            real_data = self.jetson_connector.get_sensor_data(
                device_id=device_id,
                sensor_type=sensor,
                limit=200
            )
            
            if not real_data:
                logger.warning(f"📭 No hay datos disponibles para {device_id}/{sensor}")
                return []
            
            # Formatear datos reales para el gráfico
            data_points = []
            for record in real_data:
                timestamp = record.get('timestamp')
                value = record.get('value')
                
                if timestamp and value is not None:
                    data_points.append({
                        "t": timestamp,
                        "v": value
                    })
            
            logger.info(f"✅ Obtenidos {len(data_points)} puntos reales para {device_id}/{sensor}")
            return data_points
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos reales para {device_id}/{sensor}: {e}")
            return []
    
    def build_plotly_figure(self, timestamps: List[str], values: List[float], 
                          chart_type: str = "line", title: str = "Sensor Data", 
                          y_label: str = "Valor") -> go.Figure:
        """
        Construye figura de Plotly basada en datos y tipo de gráfico.
        
        Args:
            timestamps: Lista de timestamps en formato ISO
            values: Lista de valores numéricos
            chart_type: Tipo de gráfico (line, bar, area, scatter)
            title: Título del gráfico
            y_label: Etiqueta del eje Y
            
        Returns:
            Figura de Plotly
        """
        fig = go.Figure()
        
        # Convertir timestamps a datetime si es necesario
        try:
            x_data = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps]
        except:
            x_data = timestamps
        
        if chart_type == "line":
            fig.add_trace(go.Scatter(
                x=x_data, y=values, 
                mode='lines+markers',
                name=y_label,
                line=dict(color='#2E86AB', width=3),
                marker=dict(size=6)
            ))
        elif chart_type == "area":
            fig.add_trace(go.Scatter(
                x=x_data, y=values,
                fill='tozeroy',
                mode='lines',
                name=y_label,
                line=dict(color='#A23B72', width=2),
                fillcolor='rgba(162, 59, 114, 0.3)'
            ))
        elif chart_type == "bar":
            # Mejorar barras especialmente para datos LDR
            if "ldr" in title.lower() or "luz" in title.lower() or "light" in title.lower():
                # Análisis específico para datos de luminosidad
                color_scale = []
                for value in values:
                    if value < 100:
                        color_scale.append('#2c3e50')  # Muy oscuro
                    elif value < 300:
                        color_scale.append('#34495e')  # Oscuro
                    elif value < 500:
                        color_scale.append('#7f8c8d')  # Medio
                    elif value < 700:
                        color_scale.append('#f39c12')  # Claro
                    else:
                        color_scale.append('#f1c40f')  # Muy claro
                
                fig.add_trace(go.Bar(
                    x=x_data, y=values,
                    name=y_label,
                    marker=dict(
                        color=color_scale,
                        line=dict(color='rgba(255,255,255,0.8)', width=1),
                        opacity=0.8
                    ),
                    text=[f'{v:.0f}' for v in values],
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>' +
                                'Luminosidad: %{y:.0f}<br>' +
                                '<extra></extra>'
                ))
            else:
                # Barras estándar con gradiente de colores
                fig.add_trace(go.Bar(
                    x=x_data, y=values,
                    name=y_label,
                    marker=dict(
                        color=values,
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title=y_label),
                        line=dict(color='rgba(255,255,255,0.6)', width=1),
                        opacity=0.8
                    ),
                    text=[f'{v:.1f}' for v in values],
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>' +
                                f'{y_label}: %{{y:.1f}}<br>' +
                                '<extra></extra>'
                ))
        elif chart_type == "scatter":
            fig.add_trace(go.Scatter(
                x=x_data, y=values,
                mode='markers',
                name=y_label,
                marker=dict(size=8, color='#C73E1D')
            ))
        elif chart_type == "pie":
            # Para gráficos de torta, agregar distribución de rangos de temperatura
            if "temperatura" in title.lower() or "temperature" in title.lower():
                # Crear rangos de temperatura
                ranges = {
                    "Muy Frío (< 15°C)": 0,
                    "Frío (15-20°C)": 0,
                    "Templado (20-25°C)": 0,
                    "Cálido (25-30°C)": 0,
                    "Caliente (> 30°C)": 0
                }
                
                for value in values:
                    if value < 15:
                        ranges["Muy Frío (< 15°C)"] += 1
                    elif value < 20:
                        ranges["Frío (15-20°C)"] += 1
                    elif value < 25:
                        ranges["Templado (20-25°C)"] += 1
                    elif value < 30:
                        ranges["Cálido (25-30°C)"] += 1
                    else:
                        ranges["Caliente (> 30°C)"] += 1
                
                # Filtrar rangos con datos
                filtered_ranges = {k: v for k, v in ranges.items() if v > 0}
                
                if filtered_ranges:
                    fig.add_trace(go.Pie(
                        labels=list(filtered_ranges.keys()),
                        values=list(filtered_ranges.values()),
                        hole=0.3,  # Donut style
                        marker=dict(
                            colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
                            line=dict(color='#FFFFFF', width=2)
                        ),
                        textinfo='label+percent+value',
                        textposition='auto'
                    ))
                else:
                    # Fallback si no hay datos
                    fig.add_trace(go.Pie(
                        labels=["Sin datos"],
                        values=[1],
                        marker=dict(colors=['#cccccc'])
                    ))
            else:
                # Para otros tipos de datos en pie chart
                # Agrupar por rangos generales de valores
                if len(values) > 0:
                    min_val, max_val = min(values), max(values)
                    range_size = (max_val - min_val) / 4 if max_val != min_val else 1
                    
                    ranges = {
                        f"Bajo ({min_val:.1f}-{min_val + range_size:.1f})": 0,
                        f"Medio-Bajo ({min_val + range_size:.1f}-{min_val + 2*range_size:.1f})": 0,
                        f"Medio-Alto ({min_val + 2*range_size:.1f}-{min_val + 3*range_size:.1f})": 0,
                        f"Alto ({min_val + 3*range_size:.1f}-{max_val:.1f})": 0
                    }
                    
                    for value in values:
                        if value <= min_val + range_size:
                            ranges[f"Bajo ({min_val:.1f}-{min_val + range_size:.1f})"] += 1
                        elif value <= min_val + 2*range_size:
                            ranges[f"Medio-Bajo ({min_val + range_size:.1f}-{min_val + 2*range_size:.1f})"] += 1
                        elif value <= min_val + 3*range_size:
                            ranges[f"Medio-Alto ({min_val + 2*range_size:.1f}-{min_val + 3*range_size:.1f})"] += 1
                        else:
                            ranges[f"Alto ({min_val + 3*range_size:.1f}-{max_val:.1f})"] += 1
                    
                    # Filtrar rangos con datos
                    filtered_ranges = {k: v for k, v in ranges.items() if v > 0}
                    
                    fig.add_trace(go.Pie(
                        labels=list(filtered_ranges.keys()),
                        values=list(filtered_ranges.values()),
                        hole=0.3,
                        marker=dict(
                            colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'],
                            line=dict(color='#FFFFFF', width=2)
                        ),
                        textinfo='label+percent+value',
                        textposition='auto'
                    ))
        
        # Configurar layout
        if chart_type == "pie":
            # Layout específico para gráficos de torta
            fig.update_layout(
                title={
                    'text': title,
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 16, 'family': 'Arial, sans-serif', 'color': '#2c3e50'}
                },
                template="plotly_white",
                margin=dict(l=20, r=20, t=80, b=20),
                height=500,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.02,
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor='rgba(0,0,0,0.1)',
                    borderwidth=1
                ),
                annotations=[
                    dict(
                        text=f"Total: {len(values)} mediciones",
                        showarrow=False,
                        x=0.5, y=-0.1,
                        font=dict(size=12, color='#7f8c8d'),
                        xref="paper", yref="paper"
                    )
                ]
            )
        else:
            # Layout para otros tipos de gráficos
            fig.update_layout(
                title={
                    'text': title,
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 16, 'family': 'Arial, sans-serif'}
                },
                xaxis_title="Tiempo",
                yaxis_title=y_label,
                template="plotly_white",
                margin=dict(l=60, r=60, t=80, b=60),
                height=400,
                showlegend=True,
                legend=dict(x=0, y=1, bgcolor='rgba(255,255,255,0.8)')
            )
        
        return fig
    
    def export_figure_png(self, fig: go.Figure, width: int = 1200, height: int = 600) -> bytes:
        """Exporta figura Plotly a PNG usando kaleido con fallback robusto"""
        try:
            logger.info(f"Intentando exportar figura a PNG - width: {width}, height: {height}")
            
            # Método 1: Intentar con kaleido
            try:
                # Configurar kaleido explícitamente
                pio.kaleido.scope.default_width = width
                pio.kaleido.scope.default_height = height
                pio.kaleido.scope.default_scale = 1
                
                # Intentar exportar
                img_bytes = pio.to_image(fig, format="png", width=width, height=height, scale=1)
                
                if img_bytes and len(img_bytes) > 1000:  # Al menos 1KB para ser válido
                    logger.info(f"✅ Figura exportada con kaleido - tamaño: {len(img_bytes)} bytes")
                    return img_bytes
                else:
                    logger.warning("Kaleido devolvió imagen muy pequeña, intentando método alternativo")
                    raise Exception("Imagen kaleido muy pequeña")
                    
            except Exception as kaleido_error:
                logger.warning(f"Kaleido falló: {kaleido_error}, intentando método alternativo")
                
                # Método 2: Usar plotly con orca (si está disponible)
                try:
                    img_bytes = pio.to_image(fig, format="png", width=width, height=height, engine="orca")
                    if img_bytes and len(img_bytes) > 1000:
                        logger.info(f"✅ Figura exportada con orca - tamaño: {len(img_bytes)} bytes")
                        return img_bytes
                except:
                    pass
                
                # Método 3: Fallback a matplotlib
                return self._create_matplotlib_chart(fig, width, height)
                
        except Exception as e:
            logger.error(f"Error exporting figure to PNG: {e}")
            logger.error(f"Tipo de error: {type(e).__name__}")
            return self._create_fallback_image()
    
    def _create_matplotlib_chart(self, fig: go.Figure, width: int, height: int) -> bytes:
        """Convierte figura plotly a matplotlib y exporta"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # Backend sin GUI
            
            logger.info("Generando gráfico con matplotlib como fallback")
            
            # Extraer datos de la figura plotly
            trace = fig.data[0] if fig.data else None
            if not trace:
                return self._create_fallback_image()
            
            plt.figure(figsize=(width/100, height/100))
            
            if hasattr(trace, 'type'):
                if trace.type == 'scatter':
                    if hasattr(trace, 'mode') and 'lines' in trace.mode:
                        plt.plot(trace.x, trace.y, marker='o' if 'markers' in trace.mode else '', linewidth=2)
                    else:
                        plt.scatter(trace.x, trace.y)
                elif trace.type == 'bar':
                    plt.bar(range(len(trace.y)), trace.y)
                    if hasattr(trace, 'x') and trace.x:
                        plt.xticks(range(len(trace.x)), [str(x)[:10] for x in trace.x], rotation=45)
                elif trace.type == 'pie':
                    plt.pie(trace.values, labels=trace.labels, autopct='%1.1f%%')
                else:
                    # Gráfico genérico
                    plt.plot(trace.y)
            
            # Configurar estilo
            plt.title(fig.layout.title.text if fig.layout.title else "Gráfico de Sensores IoT")
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Exportar
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            buffer.seek(0)
            
            img_bytes = buffer.read()
            logger.info(f"✅ Figura generada con matplotlib - tamaño: {len(img_bytes)} bytes")
            return img_bytes
            
        except Exception as e:
            logger.error(f"Error creando gráfico con matplotlib: {e}")
            return self._create_fallback_image()
    
    def _create_fallback_image(self) -> bytes:
        """Crea una imagen de respaldo usando matplotlib si todo falla"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # Backend sin GUI
            
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.text(0.5, 0.5, '📊 Gráfico IoT\n\n(Datos disponibles en tabla)', 
                   ha='center', va='center', fontsize=14,
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.set_facecolor('white')
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close(fig)
            buffer.seek(0)
            return buffer.read()
            
        except Exception as e:
            logger.error(f"Error creando imagen de respaldo: {e}")
            # Crear imagen mínima si todo falla
            return b""
    
    def generate_pdf_from_spec(self, spec: Dict[str, Any], summary_text: str, 
                             metrics: Dict[str, Any], fig: Optional[go.Figure] = None) -> bytes:
        """
        Genera PDF ejecutivo basado en especificación.
        
        Args:
            spec: Especificación del reporte
            summary_text: Texto resumen ejecutivo
            metrics: Métricas clave del sistema
            fig: Figura de Plotly opcional
            
        Returns:
            Bytes del PDF generado
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                  topMargin=20*mm, bottomMargin=20*mm,
                                  leftMargin=20*mm, rightMargin=20*mm)
            
            story = []
            styles = getSampleStyleSheet()
            
            # Estilo personalizado para título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#2E86AB'),
                spaceAfter=20,
                alignment=TA_CENTER
            )
            
            # Título
            story.append(Paragraph(spec.get('title', 'Reporte Ejecutivo IoT'), title_style))
            story.append(Spacer(1, 10*mm))
            
            # Metadata del reporte
            meta_data = [
                ['Dispositivo:', spec.get('device_id', 'N/A')],
                ['Sensor:', spec.get('sensor', 'N/A')],
                ['Periodo:', spec.get('time_range', {}).get('description', 'N/A')],
                ['Generado:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            ]
            
            meta_table = Table(meta_data, colWidths=[40*mm, 80*mm])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(meta_table)
            story.append(Spacer(1, 10*mm))
            
            # Resumen ejecutivo
            if "summary" in spec.get('sections', []):
                story.append(Paragraph("Resumen Ejecutivo", styles['Heading2']))
                story.append(Paragraph(summary_text, styles['Normal']))
                story.append(Spacer(1, 8*mm))
            
            # Métricas clave
            if "metrics" in spec.get('sections', []):
                story.append(Paragraph("Métricas Clave", styles['Heading2']))
                
                metrics_data = [['Métrica', 'Valor']]
                for key, value in metrics.items():
                    metrics_data.append([str(key).replace('_', ' ').title(), str(value)])
                
                metrics_table = Table(metrics_data, colWidths=[60*mm, 60*mm])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                story.append(metrics_table)
                story.append(Spacer(1, 8*mm))
            
            # Gráfico
            if "chart" in spec.get('sections', []) and fig is not None:
                story.append(Paragraph("Análisis Gráfico", styles['Heading2']))
                
                # Convertir figura a imagen
                img_bytes = self.export_figure_png(fig, width=800, height=400)
                if img_bytes:
                    img_buffer = BytesIO(img_bytes)
                    img = Image(img_buffer, width=160*mm, height=80*mm)
                    story.append(img)
                    story.append(Spacer(1, 5*mm))
            
            # Footer
            story.append(Spacer(1, 10*mm))
            footer_text = f"Generado por Remote IoT Agent • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            story.append(Paragraph(footer_text, styles['Normal']))
            
            # Construir PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.read()
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return b""
    
    def export_csv_from_table(self, data_points: List[Dict[str, Any]], 
                            device_id: str, sensor: str) -> bytes:
        """Exporta datos a CSV"""
        try:
            df = pd.DataFrame(data_points)
            if not df.empty:
                df['device_id'] = device_id
                df['sensor'] = sensor
                # Reordenar columnas
                cols = ['device_id', 'sensor', 't', 'v']
                df = df[cols]
                df.columns = ['Dispositivo', 'Sensor', 'Timestamp', 'Valor']
            
            buffer = BytesIO()
            df.to_csv(buffer, index=False, encoding='utf-8')
            buffer.seek(0)
            return buffer.read()
            
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            return b""
    
    def export_xlsx_from_table(self, data_points: List[Dict[str, Any]], 
                             device_id: str, sensor: str) -> bytes:
        """Exporta datos a Excel"""
        try:
            df = pd.DataFrame(data_points)
            if not df.empty:
                df['device_id'] = device_id
                df['sensor'] = sensor
                cols = ['device_id', 'sensor', 't', 'v']
                df = df[cols]
                df.columns = ['Dispositivo', 'Sensor', 'Timestamp', 'Valor']
            
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Datos IoT', index=False)
            
            buffer.seek(0)
            return buffer.read()
            
        except Exception as e:
            logger.error(f"Error exporting XLSX: {e}")
            return b""
    
    def export_html_report(self, spec: Dict[str, Any], summary_text: str, 
                         metrics: Dict[str, Any], fig_html: str = "") -> bytes:
        """Genera reporte en formato HTML"""
        try:
            html_template = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{spec.get('title', 'Reporte IoT')}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ text-align: center; color: #2E86AB; margin-bottom: 30px; }}
                    .metadata {{ background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
                    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
                    .metric-card {{ background: #e8f4f8; padding: 15px; border-radius: 8px; text-align: center; }}
                    .chart-container {{ margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{spec.get('title', 'Reporte Ejecutivo IoT')}</h1>
                    <p>Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="metadata">
                    <h3>Información del Reporte</h3>
                    <p><strong>Dispositivo:</strong> {spec.get('device_id', 'N/A')}</p>
                    <p><strong>Sensor:</strong> {spec.get('sensor', 'N/A')}</p>
                    <p><strong>Periodo:</strong> {spec.get('time_range', {}).get('description', 'N/A')}</p>
                </div>
                
                <div class="summary">
                    <h3>Resumen Ejecutivo</h3>
                    <p>{summary_text}</p>
                </div>
                
                <div class="metrics">
                    <h3>Métricas Clave</h3>
                    {''.join([f'<div class="metric-card"><h4>{k.replace("_", " ").title()}</h4><p>{v}</p></div>' for k, v in metrics.items()])}
                </div>
                
                <div class="chart-container">
                    <h3>Análisis Gráfico</h3>
                    {fig_html}
                </div>
            </body>
            </html>
            """
            
            return html_template.encode('utf-8')
            
        except Exception as e:
            logger.error(f"Error generating HTML: {e}")
            return b""
    
    def generate_report(self, spec: Dict[str, Any], context_metadata: Dict[str, Any], 
                       summary_text: str) -> Tuple[bytes, str]:
        """
        Función principal para generar reporte en cualquier formato.
        MEJORADO para manejar múltiples dispositivos y sensores.
        
        Args:
            spec: Especificación del reporte
            context_metadata: Metadata del contexto
            summary_text: Texto del resumen
            
        Returns:
            Tupla de (bytes_del_archivo, nombre_archivo)
        """
        try:
            # Obtener listas de dispositivos y sensores
            devices = spec.get('devices', [])
            sensors = spec.get('sensors', [])
            chart_types = spec.get('chart_types', {})
            
            # Si está usando formato legacy, convertir
            if not devices and spec.get('device_id'):
                devices = [spec.get('device_id')]
            if not sensors and spec.get('sensor'):
                sensors = [spec.get('sensor')]
            
            # Generar datos para todas las combinaciones dispositivo-sensor
            all_data = {}
            metrics = {
                'total_registros': 0,
                'dispositivos': devices,
                'sensores': sensors,
                'periodo': spec.get('time_range', {}).get('description', 'N/A'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Expandir sensores lógicos a sensores físicos por dispositivo
            for device in devices:
                expanded_sensors = self._expand_sensors_for_device(device, sensors)
                
                for sensor_info in expanded_sensors:
                    physical_sensor = sensor_info['physical_sensor']
                    logical_sensor = sensor_info['logical_sensor'] 
                    
                    key = f"{device}_{physical_sensor}"
                    try:
                        data_points = self._get_real_sensor_data(device, physical_sensor)
                        
                        if not data_points:
                            logger.warning(f"🚨 No hay datos reales disponibles para {device}/{physical_sensor}")
                            all_data[key] = {
                                'device': device,
                                'sensor': physical_sensor,
                                'logical_sensor': logical_sensor,
                                'data': [],
                                'error': 'NO_DATA_AVAILABLE',
                                'message': f'No se pudieron obtener datos reales para {device}/{physical_sensor}'
                            }
                        else:
                            all_data[key] = {
                                'device': device,
                                'sensor': physical_sensor,
                                'logical_sensor': logical_sensor,
                                'data': data_points,
                                'chart_type': chart_types.get(logical_sensor, 'line')
                            }
                            metrics['total_registros'] += len(data_points)
                    except Exception as e:
                        logger.error(f"Error obteniendo datos para {device}/{physical_sensor}: {e}")
                        all_data[key] = {
                            'device': device,
                            'sensor': physical_sensor,
                            'logical_sensor': logical_sensor,
                            'data': [],
                            'chart_type': chart_types.get(logical_sensor, 'line')
                        }
            
            # Generar según formato
            format_type = spec.get('format', 'pdf')
            
            if format_type == 'csv':
                # Para CSV, combinar todos los datos
                combined_data = []
                for key, info in all_data.items():
                    for point in info['data']:
                        point_copy = point.copy()
                        point_copy['device'] = info['device']
                        point_copy['sensor'] = info['sensor']
                        combined_data.append(point_copy)
                
                file_bytes = self.export_csv_from_combined_data(combined_data)
                filename = f"reporte_iot_multi_dispositivos.csv"
                
            elif format_type == 'xlsx':
                file_bytes = self.export_xlsx_from_combined_data(all_data)
                filename = f"reporte_iot_multi_dispositivos.xlsx"
                
            elif format_type == 'png':
                # Para PNG, crear gráfico combinado o múltiple
                file_bytes = self.export_multiple_charts_png(all_data, spec)
                filename = f"graficos_iot_multi.png"
                
            elif format_type == 'html':
                file_bytes = self.export_html_multi_report(spec, summary_text, metrics, all_data)
                filename = f"reporte_iot_multi.html"
                
            else:  # PDF por defecto
                file_bytes = self.generate_pdf_multi_device(spec, summary_text, metrics, all_data)
                filename = f"reporte_iot_multi_dispositivos.pdf"
            
            logger.info(f"Reporte generado: {filename} ({len(file_bytes)} bytes)")
            return file_bytes, filename
            
        except Exception as e:
            logger.error(f"Error generating multi-device report: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return b"", "error.txt"

    def generate_data_insights(self, all_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Genera insights analíticos valiosos de los datos de sensores IoT.
        
        Args:
            all_data: Diccionario con datos de todos los dispositivos
            
        Returns:
            Diccionario con insights organizados por tipo de análisis
        """
        insights = {
            "general": "",
            "temperatura": "",
            "ldr": "",
            "tendencias": "",
            "anomalias": "",
            "recomendaciones": ""
        }
        
        try:
            total_readings = 0
            all_temperatures = []
            all_ldr_values = []
            device_count = 0
            devices_found = set()
            
            # Configuración real de dispositivos
            valid_config = self._get_valid_device_sensors()
            
            # Recopilar todos los datos de la nueva estructura
            for key, device_info in all_data.items():
                if isinstance(device_info, dict) and 'device' in device_info and 'sensor' in device_info:
                    device_id = device_info['device']
                    sensor_type = device_info['sensor']
                    data_points = device_info.get('data', [])
                    
                    devices_found.add(device_id)
                    
                    # Validar que es una combinación válida
                    if not self._is_valid_device_sensor_combination(device_id, sensor_type):
                        continue
                    
                    if data_points:
                        values = [point['v'] for point in data_points if 'v' in point]
                        total_readings += len(values)
                        
                        # Clasificar por tipo de sensor
                        if sensor_type.lower() == 'ldr':
                            all_ldr_values.extend(values)
                        elif any(temp_sensor in sensor_type.lower() 
                                for temp_sensor in ['t1', 't2', 'avg', 'ntc_entrada', 'ntc_salida']):
                            all_temperatures.extend(values)
            
            device_count = len(devices_found)
            
            # Análisis general mejorado
            device_status = []
            for device_id in devices_found:
                sensors = valid_config.get(device_id, [])
                if "arduino" in device_id.lower():
                    device_status.append(f"🔧 {device_id}: {len(sensors)} sensores de temperatura")
                elif "esp32" in device_id.lower():
                    device_status.append(f"📡 {device_id}: {len(sensors)} sensores (temp + LDR)")
            
            insights["general"] = f"""
📊 **Resumen Ejecutivo:**
• Dispositivos operativos: {device_count}/2 conectados
• Total de mediciones procesadas: {total_readings:,}
• Configuración validada: ✅ Según especificaciones reales
• Estado del sistema: {'🟢 Operativo' if device_count > 0 else '🔴 Sin datos'}

📋 **Configuración de Dispositivos:**
{chr(10).join(device_status) if device_status else '• Sin dispositivos detectados'}
            """.strip()
            
            # Análisis de temperatura
            if all_temperatures:
                temp_stats = self._calculate_temperature_stats(all_temperatures)
                insights["temperatura"] = f"""
🌡️ **Análisis de Temperatura:**
• Promedio: {temp_stats['avg']:.1f}°C
• Rango: {temp_stats['min']:.1f}°C - {temp_stats['max']:.1f}°C
• Desviación estándar: {temp_stats['std']:.1f}°C
• Condición predominante: {temp_stats['condition']}
• Estabilidad: {temp_stats['stability']}
                """.strip()
            
            # Análisis de luminosidad
            if all_ldr_values:
                ldr_stats = self._calculate_ldr_stats(all_ldr_values)
                insights["ldr"] = f"""
💡 **Análisis de Luminosidad:**
• Promedio: {ldr_stats['avg']:.0f} unidades
• Rango: {ldr_stats['min']:.0f} - {ldr_stats['max']:.0f}
• Condición predominante: {ldr_stats['condition']}
• Variabilidad: {ldr_stats['variability']}
• Ciclo día/noche: {ldr_stats['cycle_detected']}
                """.strip()
            
            # Análisis de tendencias
            trends = self._analyze_trends(all_temperatures, all_ldr_values)
            insights["tendencias"] = f"""
📈 **Tendencias Identificadas:**
• Temperatura: {trends['temperature_trend']}
• Luminosidad: {trends['ldr_trend']}
• Correlación T-L: {trends['correlation']}
• Patrón temporal: {trends['pattern']}
            """.strip()
            
            # Detección de anomalías
            anomalies = self._detect_anomalies(all_temperatures, all_ldr_values)
            insights["anomalias"] = f"""
⚠️ **Anomalías y Alertas:**
• Temperaturas extremas: {anomalies['temp_extremes']}
• Lecturas LDR anómalas: {anomalies['ldr_anomalies']}
• Dispositivos inconsistentes: {anomalies['device_issues']}
• Nivel de alerta: {anomalies['alert_level']}
            """.strip()
            
            # Recomendaciones
            recommendations = self._generate_recommendations(all_temperatures, all_ldr_values, device_count)
            insights["recomendaciones"] = f"""
💡 **Recomendaciones:**
{recommendations}
            """.strip()
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            insights["general"] = "❌ Error en el análisis de datos"
        
        return insights
    
    def _get_analysis_period(self, all_data: Dict[str, Any]) -> str:
        """Determina el período de análisis de los datos"""
        try:
            all_timestamps = []
            for device_data in all_data.values():
                if isinstance(device_data, dict):
                    for sensor_data in device_data.values():
                        if isinstance(sensor_data, dict) and 'timestamps' in sensor_data:
                            all_timestamps.extend(sensor_data['timestamps'])
            
            if all_timestamps:
                from datetime import datetime
                timestamps = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in all_timestamps[:5]]
                if len(timestamps) >= 2:
                    duration = max(timestamps) - min(timestamps)
                    hours = duration.total_seconds() / 3600
                    if hours < 1:
                        return f"{int(duration.total_seconds() / 60)} minutos"
                    elif hours < 24:
                        return f"{hours:.1f} horas"
                    else:
                        return f"{hours/24:.1f} días"
            return "Período no determinado"
        except:
            return "Período no determinado"
    
    def _calculate_temperature_stats(self, temperatures: List[float]) -> Dict[str, Any]:
        """Calcula estadísticas detalladas de temperatura"""
        import statistics
        stats = {
            'avg': statistics.mean(temperatures),
            'min': min(temperatures),
            'max': max(temperatures),
            'std': statistics.stdev(temperatures) if len(temperatures) > 1 else 0,
        }
        
        # Determinar condición predominante
        if stats['avg'] < 18:
            stats['condition'] = "❄️ Frío"
        elif stats['avg'] < 24:
            stats['condition'] = "🌡️ Templado"
        elif stats['avg'] < 28:
            stats['condition'] = "☀️ Cálido"
        else:
            stats['condition'] = "🔥 Caliente"
        
        # Evaluar estabilidad
        if stats['std'] < 2:
            stats['stability'] = "🟢 Muy estable"
        elif stats['std'] < 5:
            stats['stability'] = "🟡 Moderadamente estable"
        else:
            stats['stability'] = "🔴 Inestable"
        
        return stats
    
    def _calculate_ldr_stats(self, ldr_values: List[float]) -> Dict[str, Any]:
        """Calcula estadísticas detalladas de luminosidad"""
        import statistics
        stats = {
            'avg': statistics.mean(ldr_values),
            'min': min(ldr_values),
            'max': max(ldr_values),
        }
        
        # Determinar condición predominante
        if stats['avg'] < 200:
            stats['condition'] = "🌙 Muy oscuro"
        elif stats['avg'] < 400:
            stats['condition'] = "🌆 Oscuro"
        elif stats['avg'] < 600:
            stats['condition'] = "🌤️ Iluminado"
        else:
            stats['condition'] = "☀️ Muy brillante"
        
        # Evaluar variabilidad
        range_val = stats['max'] - stats['min']
        if range_val < 100:
            stats['variability'] = "🟢 Baja variación"
        elif range_val < 300:
            stats['variability'] = "🟡 Variación moderada"
        else:
            stats['variability'] = "🔴 Alta variación"
        
        # Detectar ciclo día/noche
        if range_val > 200 and stats['max'] > 500:
            stats['cycle_detected'] = "✅ Detectado"
        else:
            stats['cycle_detected'] = "❌ No detectado"
        
        return stats
    
    def _analyze_trends(self, temperatures: List[float], ldr_values: List[float]) -> Dict[str, str]:
        """Analiza tendencias en los datos"""
        trends = {}
        
        # Tendencia de temperatura
        if len(temperatures) > 5:
            recent_temps = temperatures[-5:]
            initial_temps = temperatures[:5]
            if statistics.mean(recent_temps) > statistics.mean(initial_temps) + 1:
                trends['temperature_trend'] = "📈 Aumentando"
            elif statistics.mean(recent_temps) < statistics.mean(initial_temps) - 1:
                trends['temperature_trend'] = "📉 Disminuyendo"
            else:
                trends['temperature_trend'] = "➡️ Estable"
        else:
            trends['temperature_trend'] = "➡️ Datos insuficientes"
        
        # Tendencia de LDR
        if len(ldr_values) > 5:
            recent_ldr = ldr_values[-5:]
            initial_ldr = ldr_values[:5]
            if statistics.mean(recent_ldr) > statistics.mean(initial_ldr) + 50:
                trends['ldr_trend'] = "📈 Aumentando"
            elif statistics.mean(recent_ldr) < statistics.mean(initial_ldr) - 50:
                trends['ldr_trend'] = "📉 Disminuyendo"
            else:
                trends['ldr_trend'] = "➡️ Estable"
        else:
            trends['ldr_trend'] = "➡️ Datos insuficientes"
        
        # Correlación simple
        if len(temperatures) > 0 and len(ldr_values) > 0:
            if abs(len(temperatures) - len(ldr_values)) / max(len(temperatures), len(ldr_values)) < 0.3:
                trends['correlation'] = "🔗 Datos correlacionados"
            else:
                trends['correlation'] = "❓ Correlación débil"
        else:
            trends['correlation'] = "❌ Sin correlación"
        
        trends['pattern'] = "📊 Patrón típico de IoT" if len(temperatures) > 10 else "⏳ Recopilando datos"
        
        return trends
    
    def _detect_anomalies(self, temperatures: List[float], ldr_values: List[float]) -> Dict[str, str]:
        """Detecta anomalías en los datos"""
        anomalies = {}
        
        # Temperaturas extremas
        extreme_temps = [t for t in temperatures if t < 0 or t > 50]
        if extreme_temps:
            anomalies['temp_extremes'] = f"⚠️ {len(extreme_temps)} lecturas extremas detectadas"
        else:
            anomalies['temp_extremes'] = "✅ Sin temperaturas extremas"
        
        # LDR anómalas
        if ldr_values:
            anomalous_ldr = [l for l in ldr_values if l < 0 or l > 1023]
            if anomalous_ldr:
                anomalies['ldr_anomalies'] = f"⚠️ {len(anomalous_ldr)} lecturas LDR fuera de rango"
            else:
                anomalies['ldr_anomalies'] = "✅ Lecturas LDR normales"
        else:
            anomalies['ldr_anomalies'] = "❌ Sin datos LDR"
        
        # Dispositivos inconsistentes
        anomalies['device_issues'] = "✅ Dispositivos operando normalmente"
        
        # Nivel de alerta general
        if extreme_temps or (ldr_values and any(l < 0 or l > 1023 for l in ldr_values)):
            anomalies['alert_level'] = "🔴 ALTA - Revisar sistema"
        elif len(temperatures) < 5:
            anomalies['alert_level'] = "🟡 MEDIA - Pocos datos"
        else:
            anomalies['alert_level'] = "🟢 BAJA - Sistema normal"
        
        return anomalies
    
    def _generate_recommendations(self, temperatures: List[float], ldr_values: List[float], device_count: int) -> str:
        """Genera recomendaciones basadas en el análisis y configuración real"""
        recommendations = []
        
        # Recomendaciones específicas por configuración de dispositivos
        if device_count == 0:
            recommendations.append("🚨 CRÍTICO: No se detectaron dispositivos - Verificar conectividad de red")
            recommendations.append("🔌 Verificar que Arduino Ethernet (192.168.0.106) esté conectado")
            recommendations.append("� Verificar que ESP32 WiFi (192.168.0.105) esté conectado")
        elif device_count == 1:
            recommendations.append("⚠️ Solo 1 dispositivo operativo - Verificar el dispositivo faltante")
            recommendations.append("🔄 Configuración objetivo: Arduino Ethernet + ESP32 WiFi")
        
        # Análisis de temperaturas
        if not temperatures:
            recommendations.append("🌡️ Sin lecturas de temperatura - Verificar sensores NTC")
            recommendations.append("🔧 Arduino: Revisar sondas T1 y T2")
            recommendations.append("📊 ESP32: Revisar sensores NTC entrada y salida")
        elif len(temperatures) > 0:
            temp_avg = statistics.mean(temperatures)
            if temp_avg > 40:
                recommendations.append("🔥 Temperaturas elevadas detectadas - Revisar ventilación")
                recommendations.append("❄️ Considerar sistema de enfriamiento para ESP32")
            elif temp_avg < 15:
                recommendations.append("🧊 Temperaturas bajas - Verificar ambiente y calibración")
            
            # Análisis específico por rangos
            high_temps = [t for t in temperatures if t > 35]
            if len(high_temps) > len(temperatures) * 0.3:
                recommendations.append("🌡️ 30%+ lecturas en rango alto - Monitorear térmicamente")
        
        # Análisis de luminosidad (solo ESP32)
        if not ldr_values:
            recommendations.append("💡 Sin lecturas LDR - Verificar sensor de luz en ESP32")
            recommendations.append("🔍 ESP32 debería reportar valores LDR (0-1023)")
        elif len(ldr_values) > 0:
            ldr_avg = statistics.mean(ldr_values)
            recent_ldr = ldr_values[-5:] if len(ldr_values) >= 5 else ldr_values
            
            if all(l < 100 for l in recent_ldr):
                recommendations.append("🌙 Ambiente muy oscuro - Verificar iluminación")
            elif all(l > 800 for l in recent_ldr):
                recommendations.append("☀️ Alta luminosidad constante - Verificar exposición del sensor")
            
            # Detectar ciclo día/noche
            ldr_range = max(ldr_values) - min(ldr_values)
            if ldr_range < 100:
                recommendations.append("� Poca variación en LDR - Verificar posicionamiento del sensor")
        
        # Recomendaciones de optimización
        if len(temperatures) < 20:
            recommendations.append("📈 Pocos datos - Aumentar frecuencia de muestreo")
        
        # Estado óptimo
        if (device_count == 2 and temperatures and ldr_values and 
            len(temperatures) >= 20 and len(ldr_values) >= 10):
            recommendations.append("✅ Configuración completa operativa")
            recommendations.append("📊 Arduino Ethernet: Monitoreo de temperatura dual")
            recommendations.append("🌐 ESP32 WiFi: Monitoreo temperatura + luminosidad")
            recommendations.append("🔄 Considerar análisis predictivo y alertas automáticas")
        
        return "\n• ".join([""] + recommendations)

    def generate_pdf_multi_device(self, spec: Dict[str, Any], summary_text: str,
                                 metrics: Dict[str, Any], all_data: Dict[str, Any]) -> bytes:
        """
        Genera PDF con múltiples dispositivos y sensores.
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
            from io import BytesIO
            import datetime
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=letter,
                leftMargin=0.75*inch,
                rightMargin=0.75*inch,
                topMargin=1*inch,
                bottomMargin=1*inch
            )
            styles = getSampleStyleSheet()
            story = []
            
            # Estilos personalizados mejorados
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.Color(0.1, 0.2, 0.4),  # Azul oscuro
                fontName='Helvetica-Bold'
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceBefore=15,
                spaceAfter=10,
                textColor=colors.Color(0.2, 0.3, 0.5),
                fontName='Helvetica-Bold',
                borderWidth=1,
                borderColor=colors.Color(0.8, 0.8, 0.8),
                borderPadding=5,
                backColor=colors.Color(0.95, 0.97, 1.0)
            )
            
            section_style = ParagraphStyle(
                'SectionStyle',
                parent=styles['Heading3'],
                fontSize=12,
                spaceBefore=10,
                spaceAfter=5,
                textColor=colors.Color(0.3, 0.4, 0.6),
                fontName='Helvetica-Bold'
            )
            
            content_style = ParagraphStyle(
                'ContentStyle',
                parent=styles['Normal'],
                fontSize=10,
                spaceBefore=3,
                spaceAfter=8,
                alignment=TA_JUSTIFY,
                leftIndent=10,
                fontName='Helvetica'
            )
            
            # Encabezado del documento
            header_text = f"""
            <para align="center">
            <font size="24" color="#1a365d"><b>REPORTE EJECUTIVO IoT</b></font><br/>
            <font size="12" color="#4a5568">Sistema de Monitoreo de Sensores</font><br/>
            <font size="10" color="#718096">Generado el {datetime.datetime.now().strftime('%d/%m/%Y a las %H:%M')}</font>
            </para>
            """
            story.append(Paragraph(header_text, styles['Normal']))
            story.append(Spacer(1, 30))
            
            # Línea separadora
            from reportlab.platypus import HRFlowable
            story.append(HRFlowable(width="100%", thickness=2, color=colors.Color(0.2, 0.3, 0.5)))
            story.append(Spacer(1, 20))
            
            # Resumen ejecutivo
            story.append(Paragraph("📋 RESUMEN EJECUTIVO", subtitle_style))
            story.append(Paragraph(summary_text, content_style))
            story.append(Spacer(1, 15))
            
            # Generar y agregar insights analíticos
            insights = self.generate_data_insights(all_data)
            
            # Análisis General
            story.append(Paragraph("🔍 ANÁLISIS DEL SISTEMA", subtitle_style))
            story.append(Paragraph(insights['general'].replace('\n', '<br/>'), content_style))
            story.append(Spacer(1, 15))
            
            # Análisis de Temperatura
            if insights['temperatura']:
                story.append(Paragraph("🌡️ ANÁLISIS DE TEMPERATURA", section_style))
                story.append(Paragraph(insights['temperatura'].replace('\n', '<br/>'), content_style))
                story.append(Spacer(1, 10))
            
            # Análisis de Luminosidad  
            if insights['ldr']:
                story.append(Paragraph("💡 ANÁLISIS DE LUMINOSIDAD", section_style))
                story.append(Paragraph(insights['ldr'].replace('\n', '<br/>'), content_style))
                story.append(Spacer(1, 10))
            
            # Tendencias
            if insights['tendencias']:
                story.append(Paragraph("📈 ANÁLISIS DE TENDENCIAS", section_style))
                story.append(Paragraph(insights['tendencias'].replace('\n', '<br/>'), content_style))
                story.append(Spacer(1, 10))
            
            # Anomalías y Alertas
            if insights['anomalias']:
                story.append(Paragraph("⚠️ ANOMALÍAS Y ALERTAS", section_style))
                story.append(Paragraph(insights['anomalias'].replace('\n', '<br/>'), content_style))
                story.append(Spacer(1, 10))
            
            # Recomendaciones
            if insights['recomendaciones']:
                story.append(Paragraph("💡 RECOMENDACIONES", section_style))
                story.append(Paragraph(insights['recomendaciones'].replace('\n', '<br/>'), content_style))
                story.append(Spacer(1, 15))
            
            # Separador antes de datos técnicos
            story.append(HRFlowable(width="100%", thickness=1, color=colors.Color(0.8, 0.8, 0.8)))
            story.append(Spacer(1, 15))
            
            # Métricas generales
            story.append(Paragraph("📊 MÉTRICAS DEL SISTEMA", subtitle_style))
            metrics_content = f"""
            <b>📈 Total de registros:</b> {metrics['total_registros']:,}<br/>
            <b>🔌 Dispositivos analizados:</b> {', '.join(metrics['dispositivos'])}<br/>
            <b>📡 Sensores monitoreados:</b> {', '.join(metrics['sensores'])}<br/>
            <b>⏰ Período de análisis:</b> {metrics['periodo']}
            """
            story.append(Paragraph(metrics_content, content_style))
            story.append(Spacer(1, 15))
            
            # Análisis por dispositivo y sensor
            story.append(Paragraph("📈 VISUALIZACIONES Y DATOS TÉCNICOS", subtitle_style))
            
            for key, info in all_data.items():
                if info['data']:
                    device = info['device']
                    sensor = info['sensor']  # Sensor físico
                    logical_sensor = info.get('logical_sensor', sensor)  # Sensor lógico
                    data_points = info['data']
                    chart_type = info['chart_type']
                    
                    # Subsección por sensor con estilo mejorado
                    device_header = f"🔌 {device.upper()} - 📡 {sensor.title()}"
                    if logical_sensor != sensor:
                        device_header += f" ({logical_sensor.title()})"
                    story.append(Paragraph(device_header, section_style))
                    
                    # Estadísticas con formato mejorado
                    values = [point['v'] for point in data_points]
                    if values:
                        stats_content = f"""
                        <b>📊 Registros procesados:</b> {len(values):,}<br/>
                        <b>📈 Valor promedio:</b> {sum(values)/len(values):.2f}<br/>
                        <b>📉 Rango:</b> {min(values):.2f} - {max(values):.2f}<br/>
                        <b>🎯 Tipo de visualización:</b> {chart_type.title()}
                        """
                        story.append(Paragraph(stats_content, content_style))
                        story.append(Spacer(1, 8))
                    
                    # Generar gráfico
                    try:
                        timestamps = [point['t'] for point in data_points]
                        
                        # Determinar tipo de gráfico óptimo según sensor LÓGICO
                        optimal_chart_type = chart_type
                        if logical_sensor.lower() == 'temperature' and len(values) > 5:
                            # Para temperatura, usar el tipo solicitado por el usuario
                            optimal_chart_type = chart_type if chart_type in ['pie', 'bar', 'line'] else "pie"
                        elif logical_sensor.lower() == 'ldr' and chart_type != "pie":
                            # Para LDR, usar barras para mejor visualización
                            optimal_chart_type = chart_type if chart_type in ['bar', 'pie', 'line'] else "bar"
                        
                        fig = self.build_plotly_figure(
                            timestamps, values, optimal_chart_type,
                            f"{device} - {sensor}",
                            sensor.title()
                        )
                        
                        # Para sensores de temperatura, generar gráfico según tipo solicitado
                        if logical_sensor.lower() == 'temperature':
                            if optimal_chart_type == "pie":
                                story.append(Paragraph("🥧 <b>Distribución por Rangos de Temperatura</b>", section_style))
                            elif optimal_chart_type == "bar":
                                story.append(Paragraph("📊 <b>Niveles de Temperatura</b>", section_style))
                            else:
                                story.append(Paragraph("📈 <b>Evolución Temporal de la Temperatura</b>", section_style))
                            
                            img_bytes = self.export_figure_png(fig)
                            if img_bytes:
                                img_buffer = BytesIO(img_bytes)
                                img = Image(img_buffer, width=5.5*inch, height=3.5*inch)
                                story.append(img)
                            story.append(Spacer(1, 10))
                        
                        elif logical_sensor.lower() == 'ldr':
                            if optimal_chart_type == "bar":
                                story.append(Paragraph("📊 <b>Niveles de Luminosidad</b>", section_style))
                            elif optimal_chart_type == "pie":
                                story.append(Paragraph("🥧 <b>Distribución de Luminosidad</b>", section_style))
                            else:
                                story.append(Paragraph("📈 <b>Evolución de la Luminosidad</b>", section_style))
                            
                            img_bytes = self.export_figure_png(fig)
                            if img_bytes:
                                img_buffer = BytesIO(img_bytes)
                                img = Image(img_buffer, width=5.5*inch, height=3.5*inch)
                                story.append(img)
                            story.append(Spacer(1, 10))
                        
                        else:
                            # Exportar gráfico genérico
                            img_bytes = self.export_figure_png(fig)
                            if img_bytes:
                                img_buffer = BytesIO(img_bytes)
                                img = Image(img_buffer, width=5*inch, height=3*inch)
                                story.append(img)
                        
                    except Exception as e:
                        logger.warning(f"Error generando gráfico para {key}: {e}")
                        story.append(Paragraph(f"[Gráfico no disponible: {str(e)}]", styles['Normal']))
                    
                    story.append(Spacer(1, 15))
            
            # Pie de página profesional
            story.append(Spacer(1, 30))
            story.append(HRFlowable(width="100%", thickness=2, color=colors.Color(0.2, 0.3, 0.5)))
            story.append(Spacer(1, 15))
            
            footer_content = f"""
            <para align="center">
            <font size="10" color="#4a5568"><b>📋 INFORMACIÓN DEL REPORTE</b></font><br/>
            <font size="8" color="#718096">
            🕒 Generado el: {metrics['timestamp']}<br/>
            🔧 Sistema de Monitoreo IoT v2.0<br/>
            📊 Este reporte contiene análisis automatizado de datos de sensores<br/>
            ⚡ Para soporte técnico: sistema.iot@empresa.com
            </font>
            </para>
            """
            story.append(Paragraph(footer_content, styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Mensaje de confidencialidad
            confidential_style = ParagraphStyle(
                'ConfidentialStyle',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.Color(0.5, 0.5, 0.5),
                fontName='Helvetica-Oblique'
            )
            story.append(Paragraph("🔒 DOCUMENTO CONFIDENCIAL - Para uso interno únicamente", confidential_style))
            
            # Construir PDF
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generating multi-device PDF: {e}")
            return b""
    
    def export_csv_from_combined_data(self, combined_data: List[Dict[str, Any]]) -> bytes:
        """
        Exporta datos combinados de múltiples dispositivos a CSV.
        """
        try:
            import csv
            from io import StringIO
            
            output = StringIO()
            
            if combined_data:
                fieldnames = ['timestamp', 'device', 'sensor', 'value']
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for point in combined_data:
                    writer.writerow({
                        'timestamp': point.get('t', ''),
                        'device': point.get('device', ''),
                        'sensor': point.get('sensor', ''),
                        'value': point.get('v', '')
                    })
            
            return output.getvalue().encode('utf-8')
            
        except Exception as e:
            logger.error(f"Error exporting combined CSV: {e}")
            return b""
    
    def export_xlsx_from_combined_data(self, all_data: Dict[str, Any]) -> bytes:
        """
        Exporta datos de múltiples dispositivos a Excel con múltiples hojas.
        """
        try:
            import pandas as pd
            from io import BytesIO
            
            buffer = BytesIO()
            
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Hoja de resumen
                summary_data = []
                for key, info in all_data.items():
                    values = [point['v'] for point in info['data']]
                    if values:
                        summary_data.append({
                            'Dispositivo': info['device'],
                            'Sensor': info['sensor'],
                            'Registros': len(values),
                            'Promedio': sum(values)/len(values),
                            'Mínimo': min(values),
                            'Máximo': max(values)
                        })
                
                if summary_data:
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Resumen', index=False)
                
                # Hoja por cada combinación dispositivo-sensor
                for key, info in all_data.items():
                    if info['data']:
                        sheet_name = f"{info['device']}_{info['sensor']}"[:31]  # Excel limit
                        data_for_df = [
                            {
                                'Timestamp': point['t'],
                                'Valor': point['v']
                            }
                            for point in info['data']
                        ]
                        df = pd.DataFrame(data_for_df)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error exporting combined XLSX: {e}")
            return b""
    
    def export_html_multi_report(self, spec: Dict[str, Any], summary_text: str, 
                                metrics: Dict[str, Any], all_data: Dict[str, Any]) -> bytes:
        """
        Genera reporte HTML con múltiples gráficos interactivos.
        """
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{spec.get('title', 'Reporte IoT')}</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #2c3e50; }}
                    h2 {{ color: #34495e; }}
                    .metric {{ background: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                    .chart-container {{ margin: 20px 0; }}
                </style>
            </head>
            <body>
                <h1>{spec.get('title', 'Reporte IoT')}</h1>
                
                <h2>Resumen Ejecutivo</h2>
                <p>{summary_text}</p>
                
                <h2>Métricas del Sistema</h2>
                <div class="metric"><b>Total de registros:</b> {metrics['total_registros']}</div>
                <div class="metric"><b>Dispositivos:</b> {', '.join(metrics['dispositivos'])}</div>
                <div class="metric"><b>Sensores:</b> {', '.join(metrics['sensores'])}</div>
                <div class="metric"><b>Período:</b> {metrics['periodo']}</div>
                
                <h2>Gráficos Interactivos</h2>
            """
            
            # Agregar gráficos
            chart_id = 0
            for key, info in all_data.items():
                if info['data']:
                    device = info['device']
                    sensor = info['sensor']
                    chart_type = info['chart_type']
                    
                    timestamps = [point['t'] for point in info['data']]
                    values = [point['v'] for point in info['data']]
                    
                    fig = self.build_plotly_figure(
                        timestamps, values, chart_type,
                        f"{device} - {sensor}",
                        sensor.title()
                    )
                    
                    fig_json = fig.to_json()
                    
                    html_content += f"""
                    <div class="chart-container">
                        <h3>{device.upper()} - {sensor.title()}</h3>
                        <div id="chart{chart_id}"></div>
                        <script>
                            Plotly.newPlot('chart{chart_id}', {fig_json});
                        </script>
                    </div>
                    """
                    chart_id += 1
            
            html_content += f"""
                <hr>
                <p><small>Generado el {metrics['timestamp']}</small></p>
            </body>
            </html>
            """
            
            return html_content.encode('utf-8')
            
        except Exception as e:
            logger.error(f"Error generating HTML multi-report: {e}")
            return b""


# Factory function
def create_report_generator() -> ReportGenerator:
    """Crea una instancia del generador de reportes"""
    return ReportGenerator()
