"""
Módulo de Generación de Reportes Ejecutivos
==========================================

Genera reportes personalizados en múltiples formatos (PDF, CSV, XLSX, PNG, HTML)
basados en consultas de usuario y datos de sensores IoT.
"""

import re
import json
import logging
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
    
    def __init__(self):
        self.supported_formats = ["pdf", "csv", "xlsx", "png", "html"]
        self.chart_types = ["line", "bar", "area", "scatter", "heatmap"]
        self.max_data_points = 1000  # Límite para evitar archivos enormes
    
    def parse_user_request_to_spec(self, user_text: str, context_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convierte una solicitud en lenguaje natural a especificación estructurada.
        
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
        
        spec = {
            "title": "Reporte Ejecutivo IoT",
            "device_id": None,
            "sensor": None,
            "time_range": {"from": None, "to": None, "description": "últimas 24 horas"},
            "chart": {"type": "line", "sample_points": 200, "y_label": "Valor"},
            "sections": ["summary", "metrics", "chart"],
            "format": "pdf",
            "language": "es",
            "meta": {"timestamp": datetime.now().isoformat()}
        }
        
        # Extraer dispositivo
        available_devices = context_metadata.get("data_summary", {}).get("devices", [])
        for device in available_devices:
            if device.lower() in user_lower:
                spec["device_id"] = device
                break
        
        # Si no se especifica dispositivo, usar el primero disponible
        if not spec["device_id"] and available_devices:
            spec["device_id"] = available_devices[0]
        
        # Extraer sensor
        available_sensors = context_metadata.get("data_summary", {}).get("sensors", [])
        for sensor in available_sensors:
            if sensor.lower() in user_lower:
                spec["sensor"] = sensor
                break
        
        # Si no se especifica sensor, usar el primero disponible
        if not spec["sensor"] and available_sensors:
            spec["sensor"] = available_sensors[0]
        
        # Extraer tipo de gráfico
        for chart_type in self.chart_types:
            if chart_type in user_lower:
                spec["chart"]["type"] = chart_type
                break
        
        # Extraer formato
        if "csv" in user_lower:
            spec["format"] = "csv"
            spec["sections"] = ["table"]
        elif "excel" in user_lower or "xlsx" in user_lower:
            spec["format"] = "xlsx"
            spec["sections"] = ["table"]
        elif "png" in user_lower or "imagen" in user_lower:
            spec["format"] = "png"
            spec["sections"] = ["chart"]
        elif "html" in user_lower:
            spec["format"] = "html"
        
        # Extraer rango temporal
        if "48 horas" in user_lower or "2 días" in user_lower:
            spec["time_range"]["description"] = "últimas 48 horas"
        elif "72 horas" in user_lower or "3 días" in user_lower:
            spec["time_range"]["description"] = "últimas 72 horas"
        elif "semana" in user_lower:
            spec["time_range"]["description"] = "última semana"
        
        # Generar título dinámico
        if spec["device_id"] and spec["sensor"]:
            spec["title"] = f"Reporte Ejecutivo - {spec['device_id']} / {spec['sensor']}"
        
        return spec
    
    def fetch_series_from_metadata(self, device_id: str, sensor: str, 
                                 context_metadata: Dict[str, Any], 
                                 sample_points: int = 200) -> List[Dict[str, Any]]:
        """
        Extrae series temporales de los datos disponibles en metadata.
        
        Args:
            device_id: ID del dispositivo
            sensor: Nombre del sensor
            context_metadata: Metadata con datos históricos
            sample_points: Número máximo de puntos a retornar
            
        Returns:
            Lista de puntos temporales {"t": timestamp, "v": value}
        """
        try:
            # Buscar datos en la verificación del contexto
            verification = context_metadata.get("verification", {})
            
            # Generar datos sintéticos basados en metadata para demo
            # En una implementación real, esto vendría de la base de datos
            data_points = []
            base_timestamp = datetime.now()
            
            # Usar valores de referencia del contexto si están disponibles
            base_value = 25.0  # Valor por defecto
            if "ntc" in sensor.lower():
                base_value = 30.0 + (hash(device_id) % 20)  # Temperatura base
            elif "ldr" in sensor.lower():
                base_value = 400.0 + (hash(device_id) % 400)  # Luz base
            
            # Generar serie temporal sintética
            for i in range(min(sample_points, 100)):
                timestamp = base_timestamp - timedelta(hours=i)
                # Agregar variación realista
                variation = (hash(f"{device_id}_{sensor}_{i}") % 100) / 50.0 - 1.0
                value = base_value + variation * (base_value * 0.1)
                
                data_points.append({
                    "t": timestamp.isoformat(),
                    "v": round(value, 2)
                })
            
            return data_points[:sample_points]
            
        except Exception as e:
            logger.error(f"Error fetching series: {e}")
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
            fig.add_trace(go.Bar(
                x=x_data, y=values,
                name=y_label,
                marker_color='#F18F01'
            ))
        elif chart_type == "scatter":
            fig.add_trace(go.Scatter(
                x=x_data, y=values,
                mode='markers',
                name=y_label,
                marker=dict(size=8, color='#C73E1D')
            ))
        
        # Configurar layout
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
        """Exporta figura Plotly a PNG usando kaleido"""
        try:
            img_bytes = pio.to_image(fig, format="png", width=width, height=height, scale=2)
            return img_bytes
        except Exception as e:
            logger.error(f"Error exporting figure to PNG: {e}")
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
        
        Args:
            spec: Especificación del reporte
            context_metadata: Metadata del contexto
            summary_text: Texto del resumen
            
        Returns:
            Tupla de (bytes_del_archivo, nombre_archivo)
        """
        try:
            # Extraer datos
            data_points = self.fetch_series_from_metadata(
                spec.get('device_id', ''), 
                spec.get('sensor', ''), 
                context_metadata,
                spec.get('chart', {}).get('sample_points', 200)
            )
            
            # Preparar métricas
            metrics = {
                'total_registros': len(data_points),
                'dispositivo': spec.get('device_id', 'N/A'),
                'sensor': spec.get('sensor', 'N/A'),
                'periodo': spec.get('time_range', {}).get('description', 'N/A'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Generar según formato
            format_type = spec.get('format', 'pdf')
            
            if format_type == 'csv':
                file_bytes = self.export_csv_from_table(
                    data_points, spec.get('device_id', ''), spec.get('sensor', '')
                )
                filename = f"reporte_{spec.get('device_id', 'device')}_{spec.get('sensor', 'sensor')}.csv"
                
            elif format_type == 'xlsx':
                file_bytes = self.export_xlsx_from_table(
                    data_points, spec.get('device_id', ''), spec.get('sensor', '')
                )
                filename = f"reporte_{spec.get('device_id', 'device')}_{spec.get('sensor', 'sensor')}.xlsx"
                
            elif format_type == 'png':
                if data_points:
                    timestamps = [point['t'] for point in data_points]
                    values = [point['v'] for point in data_points]
                    fig = self.build_plotly_figure(
                        timestamps, values, 
                        spec.get('chart', {}).get('type', 'line'),
                        spec.get('title', 'Gráfico IoT'),
                        spec.get('chart', {}).get('y_label', 'Valor')
                    )
                    file_bytes = self.export_figure_png(fig)
                else:
                    file_bytes = b""
                filename = f"grafico_{spec.get('device_id', 'device')}_{spec.get('sensor', 'sensor')}.png"
                
            elif format_type == 'html':
                fig_html = ""
                if data_points:
                    timestamps = [point['t'] for point in data_points]
                    values = [point['v'] for point in data_points]
                    fig = self.build_plotly_figure(
                        timestamps, values, 
                        spec.get('chart', {}).get('type', 'line'),
                        spec.get('title', 'Gráfico IoT'),
                        spec.get('chart', {}).get('y_label', 'Valor')
                    )
                    fig_html = fig.to_html(include_plotlyjs='cdn')
                
                file_bytes = self.export_html_report(spec, summary_text, metrics, fig_html)
                filename = f"reporte_{spec.get('device_id', 'device')}_{spec.get('sensor', 'sensor')}.html"
                
            else:  # PDF por defecto
                fig = None
                if data_points and "chart" in spec.get('sections', []):
                    timestamps = [point['t'] for point in data_points]
                    values = [point['v'] for point in data_points]
                    fig = self.build_plotly_figure(
                        timestamps, values, 
                        spec.get('chart', {}).get('type', 'line'),
                        spec.get('title', 'Gráfico IoT'),
                        spec.get('chart', {}).get('y_label', 'Valor')
                    )
                
                file_bytes = self.generate_pdf_from_spec(spec, summary_text, metrics, fig)
                filename = f"reporte_{spec.get('device_id', 'device')}_{spec.get('sensor', 'sensor')}.pdf"
            
            return file_bytes, filename
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return b"", "error.txt"


# Factory function
def create_report_generator() -> ReportGenerator:
    """Crea una instancia del generador de reportes"""
    return ReportGenerator()
