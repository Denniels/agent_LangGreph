"""
Sistema Avanzado de Generación de Reportes IoT
=============================================

Generador de reportes inteligente que combina análisis estadístico profundo,
visualizaciones sofisticadas, correlaciones automáticas y insights accionables.

Este sistema transforma datos básicos en reportes ejecutivos profesionales.
"""

import logging
import asyncio
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import json
import base64
from io import BytesIO

# Optional imports for enhanced visualizations
try:
    import seaborn as sns
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Imports para PDF avanzado
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.units import inch

# Imports locales
from modules.intelligence.smart_analyzer import SmartAnalyzer, SensorInsight, SystemInsight
from modules.intelligence.dynamic_sensor_detector import DynamicSensorDetector

logger = logging.getLogger(__name__)

@dataclass
class ReportSection:
    """Sección individual de un reporte"""
    title: str
    content: str
    visualizations: List[str] = None  # Base64 encoded images
    insights: List[str] = None
    recommendations: List[str] = None
    priority: int = 1  # 1=highest, 5=lowest
    data_summary: Dict[str, Any] = None

@dataclass
class AdvancedReport:
    """Reporte completo con metadatos"""
    title: str
    subtitle: str
    generated_at: datetime
    analysis_period: str
    executive_summary: str
    sections: List[ReportSection]
    health_score: float
    confidence_level: float
    total_devices: int
    total_sensors: int
    data_points: int
    key_insights: List[str]
    urgent_actions: List[str]
    attachments: Dict[str, bytes] = None  # Files to include
    metadata: Dict[str, Any] = None

class AdvancedReportGenerator:
    """
    Generador avanzado de reportes IoT con capacidades de análisis profundo.
    
    Características:
    - Análisis estadístico multivariable
    - Visualizaciones interactivas y estáticas
    - Detección automática de correlaciones
    - Insights predictivos
    - Exportación a múltiples formatos
    - Personalización por audiencia
    """
    
    def __init__(self, jetson_api_url: str):
        self.jetson_api_url = jetson_api_url
        self.logger = logging.getLogger(__name__)
        
        # Inicializar componentes de análisis
        self.smart_analyzer = SmartAnalyzer()
        self.sensor_detector = DynamicSensorDetector(jetson_api_url)
        
        # Configuración de visualizaciones
        self.color_palette = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3D5A80', '#98C1D9']
        self.figure_width = 800
        self.figure_height = 500
        
        # Templates de reportes por audiencia
        self.report_templates = {
            'executive': {
                'focus': 'high_level_insights',
                'sections': ['executive_summary', 'key_metrics', 'critical_issues', 'recommendations'],
                'detail_level': 'summary'
            },
            'technical': {
                'focus': 'detailed_analysis',
                'sections': ['system_overview', 'sensor_analysis', 'anomalies', 'correlations', 'predictions', 'maintenance'],
                'detail_level': 'comprehensive'
            },
            'operational': {
                'focus': 'actionable_insights',
                'sections': ['status_overview', 'alerts', 'performance', 'actions_required'],
                'detail_level': 'focused'
            }
        }
        
        # Configurar matplotlib para reportes (si está disponible)
        if MATPLOTLIB_AVAILABLE:
            plt.style.use('default')
            sns.set_palette(self.color_palette)
    
    async def generate_comprehensive_report(self, 
                                          analysis_hours: float = 24.0,
                                          report_type: str = 'technical',
                                          include_predictions: bool = True,
                                          include_correlations: bool = True,
                                          custom_title: Optional[str] = None) -> AdvancedReport:
        """
        Genera reporte comprehensivo con análisis avanzado.
        
        Args:
            analysis_hours: Horas de datos a analizar
            report_type: Tipo de reporte ('executive', 'technical', 'operational')  
            include_predictions: Incluir análisis predictivo
            include_correlations: Incluir análisis de correlaciones
            custom_title: Título personalizado del reporte
            
        Returns:
            AdvancedReport completo con todos los análisis
        """
        try:
            self.logger.info(f"🚀 Generando reporte comprehensivo tipo '{report_type}' para {analysis_hours}h")
            
            # 1. OBTENER Y VALIDAR DATOS
            raw_data = await self._fetch_comprehensive_data(analysis_hours)
            
            if not raw_data:
                return self._create_empty_report("No hay datos disponibles para el análisis")
            
            # 2. ANÁLISIS INTELIGENTE COMPLETO
            smart_analysis = self.smart_analyzer.analyze_comprehensive(raw_data, analysis_hours)
            
            # 3. DESCUBRIMIENTO DINÁMICO DE SENSORES
            sensor_inventory = await self.sensor_detector.discover_all_sensors()
            
            # 4. GENERAR VISUALIZACIONES AVANZADAS
            visualizations = await self._generate_advanced_visualizations(
                raw_data, smart_analysis, include_correlations
            )
            
            # 5. CREAR SECCIONES DEL REPORTE
            report_sections = await self._create_report_sections(
                raw_data, smart_analysis, sensor_inventory, visualizations, report_type
            )
            
            # 6. GENERAR RESUMEN EJECUTIVO INTELIGENTE
            executive_summary = self._generate_executive_summary(smart_analysis, report_type)
            
            # 7. CREAR REPORTE FINAL
            report = AdvancedReport(
                title=custom_title or f"Reporte IoT {report_type.title()}",
                subtitle=f"Análisis de {analysis_hours} horas - {len(raw_data)} registros",
                generated_at=datetime.now(),
                analysis_period=f"{analysis_hours}h",
                executive_summary=executive_summary,
                sections=report_sections,
                health_score=smart_analysis.get('health_score', 0),
                confidence_level=smart_analysis.get('confidence_level', 0),
                total_devices=len(smart_analysis.get('devices_analyzed', [])),
                total_sensors=len(smart_analysis.get('sensors_analyzed', [])),
                data_points=len(raw_data),
                key_insights=smart_analysis.get('summary', {}).get('top_insights', []),
                urgent_actions=smart_analysis.get('summary', {}).get('urgent_actions', []),
                metadata={
                    'analysis_timestamp': datetime.now().isoformat(),
                    'report_type': report_type,
                    'analysis_hours': analysis_hours,
                    'smart_analysis_version': '2.0',
                    'visualization_count': len(visualizations)
                }
            )
            
            self.logger.info(f"✅ Reporte generado: {len(report_sections)} secciones, "
                           f"salud {report.health_score:.1f}%, confianza {report.confidence_level:.1%}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error generando reporte comprehensivo: {e}")
            return self._create_empty_report(f"Error: {str(e)}")
    
    async def export_to_pdf(self, report: AdvancedReport, filename: Optional[str] = None) -> bytes:
        """
        Exporta reporte a PDF profesional con gráficos embebidos.
        
        Args:
            report: Reporte a exportar
            filename: Nombre del archivo (opcional)
            
        Returns:
            Bytes del PDF generado
        """
        try:
            self.logger.info("📄 Exportando reporte a PDF...")
            
            # Crear buffer para PDF
            buffer = BytesIO()
            
            # Configurar documento
            if not filename:
                filename = f"reporte_iot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Crear documento con márgenes personalizados
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Construir contenido del PDF
            story = []
            styles = getSampleStyleSheet()
            
            # Estilo personalizado para títulos
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2E86AB')
            )
            
            # Estilo para subtítulos
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=20,
                textColor=colors.HexColor('#A23B72')
            )
            
            # 1. PORTADA
            story.append(Paragraph(report.title, title_style))
            story.append(Paragraph(report.subtitle, styles['Heading3']))
            story.append(Spacer(1, 20))
            
            # Información del reporte
            report_info = f"""
            <b>Generado:</b> {report.generated_at.strftime('%d/%m/%Y %H:%M:%S')}<br/>
            <b>Período de análisis:</b> {report.analysis_period}<br/>
            <b>Dispositivos analizados:</b> {report.total_devices}<br/>
            <b>Sensores activos:</b> {report.total_sensors}<br/>
            <b>Registros procesados:</b> {report.data_points:,}<br/>
            <b>Puntuación de salud:</b> {report.health_score:.1f}%<br/>
            <b>Nivel de confianza:</b> {report.confidence_level:.1%}
            """
            story.append(Paragraph(report_info, styles['Normal']))
            story.append(PageBreak())
            
            # 2. RESUMEN EJECUTIVO
            story.append(Paragraph("Resumen Ejecutivo", title_style))
            story.append(Paragraph(report.executive_summary, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # 3. INSIGHTS CLAVE
            if report.key_insights:
                story.append(Paragraph("Insights Clave", subtitle_style))
                for insight in report.key_insights:
                    story.append(Paragraph(f"• {insight}", styles['Normal']))
                story.append(Spacer(1, 15))
            
            # 4. ACCIONES URGENTES
            if report.urgent_actions:
                story.append(Paragraph("Acciones Urgentes", subtitle_style))
                for action in report.urgent_actions:
                    story.append(Paragraph(f"⚠️ {action}", styles['Normal']))
                story.append(PageBreak())
            
            # 5. SECCIONES DETALLADAS
            for section in sorted(report.sections, key=lambda x: x.priority):
                story.append(Paragraph(section.title, subtitle_style))
                story.append(Paragraph(section.content, styles['Normal']))
                
                # Agregar visualizaciones si existen
                if section.visualizations:
                    story.append(Spacer(1, 10))
                    for viz_base64 in section.visualizations:
                        try:
                            # Decodificar imagen base64
                            image_data = base64.b64decode(viz_base64)
                            image_buffer = BytesIO(image_data)
                            
                            # Agregar imagen al PDF
                            img = Image(image_buffer, width=6*inch, height=4*inch)
                            story.append(img)
                            story.append(Spacer(1, 10))
                        except Exception as img_error:
                            self.logger.warning(f"⚠️ Error agregando imagen: {img_error}")
                
                # Agregar insights de la sección
                if section.insights:
                    story.append(Paragraph("<b>Insights:</b>", styles['Normal']))
                    for insight in section.insights:
                        story.append(Paragraph(f"💡 {insight}", styles['Normal']))
                
                # Agregar recomendaciones de la sección
                if section.recommendations:
                    story.append(Paragraph("<b>Recomendaciones:</b>", styles['Normal']))
                    for rec in section.recommendations:
                        story.append(Paragraph(f"🎯 {rec}", styles['Normal']))
                
                story.append(PageBreak())
            
            # Construir PDF
            doc.build(story)
            
            # Obtener bytes del PDF
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            self.logger.info(f"✅ PDF exportado: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            self.logger.error(f"❌ Error exportando PDF: {e}")
            return b""
    
    async def export_to_excel(self, report: AdvancedReport, raw_data: List[Dict]) -> bytes:
        """
        Exporta reporte a Excel con múltiples hojas y análisis.
        
        Args:
            report: Reporte a exportar
            raw_data: Datos originales
            
        Returns:
            Bytes del archivo Excel
        """
        try:
            self.logger.info("📊 Exportando reporte a Excel...")
            
            buffer = BytesIO()
            
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # 1. HOJA DE RESUMEN
                summary_data = {
                    'Métrica': [
                        'Título del Reporte',
                        'Fecha de Generación', 
                        'Período de Análisis',
                        'Total Dispositivos',
                        'Total Sensores',
                        'Registros Procesados',
                        'Puntuación de Salud (%)',
                        'Nivel de Confianza (%)'
                    ],
                    'Valor': [
                        report.title,
                        report.generated_at.strftime('%d/%m/%Y %H:%M:%S'),
                        report.analysis_period,
                        report.total_devices,
                        report.total_sensors,
                        report.data_points,
                        f"{report.health_score:.1f}%",
                        f"{report.confidence_level:.1%}"
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Resumen', index=False)
                
                # 2. HOJA DE DATOS ORIGINALES
                if raw_data:
                    data_df = pd.DataFrame(raw_data)
                    data_df.to_excel(writer, sheet_name='Datos Originales', index=False)
                
                # 3. HOJAS POR SECCIÓN
                for i, section in enumerate(report.sections):
                    sheet_name = f"Seccion_{i+1}_{section.title[:20]}"
                    
                    section_data = {
                        'Elemento': ['Título', 'Contenido', 'Prioridad'],
                        'Valor': [section.title, section.content[:1000], section.priority]
                    }
                    
                    if section.insights:
                        for j, insight in enumerate(section.insights):
                            section_data['Elemento'].append(f'Insight {j+1}')
                            section_data['Valor'].append(insight)
                    
                    if section.recommendations:
                        for j, rec in enumerate(section.recommendations):
                            section_data['Elemento'].append(f'Recomendación {j+1}')
                            section_data['Valor'].append(rec)
                    
                    section_df = pd.DataFrame(section_data)
                    section_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # 4. HOJA DE INSIGHTS CLAVE
                if report.key_insights:
                    insights_df = pd.DataFrame({
                        'Insight': report.key_insights,
                        'Tipo': ['Clave'] * len(report.key_insights)
                    })
                    insights_df.to_excel(writer, sheet_name='Insights Clave', index=False)
                
                # 5. HOJA DE ACCIONES URGENTES
                if report.urgent_actions:
                    actions_df = pd.DataFrame({
                        'Acción': report.urgent_actions,
                        'Urgencia': ['Alta'] * len(report.urgent_actions)
                    })
                    actions_df.to_excel(writer, sheet_name='Acciones Urgentes', index=False)
            
            excel_bytes = buffer.getvalue()
            buffer.close()
            
            self.logger.info(f"✅ Excel exportado: {len(excel_bytes)} bytes")
            return excel_bytes
            
        except Exception as e:
            self.logger.error(f"❌ Error exportando Excel: {e}")
            return b""
    
    async def generate_interactive_dashboard(self, report: AdvancedReport, raw_data: List[Dict]) -> str:
        """
        Genera dashboard HTML interactivo con Plotly.
        
        Args:
            report: Reporte base
            raw_data: Datos para gráficos interactivos
            
        Returns:
            HTML string del dashboard
        """
        try:
            self.logger.info("🌐 Generando dashboard interactivo...")
            
            if not raw_data:
                return "<html><body><h1>No hay datos disponibles</h1></body></html>"
            
            df = pd.DataFrame(raw_data)
            
            # Crear figura combinada con subplots
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=('Tendencias Temporales', 'Distribución por Dispositivo',
                              'Análisis por Sensor', 'Correlaciones',
                              'Métricas de Salud', 'Predicciones'),
                specs=[[{"secondary_y": True}, {"type": "pie"}],
                       [{"colspan": 2}, None],
                       [{"type": "indicator"}, {"type": "scatter"}]]
            )
            
            # 1. Tendencias temporales
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                for i, device in enumerate(df['device_id'].unique()[:3]):  # Máximo 3 dispositivos
                    device_data = df[df['device_id'] == device]
                    fig.add_trace(
                        go.Scatter(
                            x=device_data['timestamp'],
                            y=device_data['value'],
                            name=f'Dispositivo {device}',
                            line=dict(color=self.color_palette[i % len(self.color_palette)])
                        ),
                        row=1, col=1
                    )
            
            # 2. Distribución por dispositivo
            device_counts = df['device_id'].value_counts()
            fig.add_trace(
                go.Pie(
                    labels=device_counts.index,
                    values=device_counts.values,
                    name="Dispositivos"
                ),
                row=1, col=2
            )
            
            # 3. Análisis por sensor
            sensor_stats = df.groupby('sensor_type')['value'].agg(['mean', 'std']).reset_index()
            fig.add_trace(
                go.Bar(
                    x=sensor_stats['sensor_type'],
                    y=sensor_stats['mean'],
                    name='Promedio',
                    error_y=dict(type='data', array=sensor_stats['std'])
                ),
                row=2, col=1
            )
            
            # 4. Indicador de salud
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=report.health_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Salud del Sistema (%)"},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "gray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ),
                row=3, col=1
            )
            
            # Configurar layout
            fig.update_layout(
                height=1000,
                showlegend=True,
                title_text=f"Dashboard Interactivo - {report.title}",
                title_x=0.5
            )
            
            # Convertir a HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{report.title} - Dashboard Interactivo</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .summary {{ background: #f0f0f0; padding: 20px; border-radius: 10px; margin-bottom: 30px; }}
                    .insights {{ background: #e8f4f8; padding: 15px; border-left: 5px solid #2E86AB; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{report.title}</h1>
                    <h3>{report.subtitle}</h3>
                    <p>Generado: {report.generated_at.strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
                
                <div class="summary">
                    <h2>Resumen Ejecutivo</h2>
                    <p>{report.executive_summary}</p>
                    <div style="display: flex; justify-content: space-around; margin-top: 20px;">
                        <div><strong>Salud:</strong> {report.health_score:.1f}%</div>
                        <div><strong>Confianza:</strong> {report.confidence_level:.1%}</div>
                        <div><strong>Dispositivos:</strong> {report.total_devices}</div>
                        <div><strong>Sensores:</strong> {report.total_sensors}</div>
                    </div>
                </div>
                
                <div id="dashboard-plot" style="width:100%;height:1000px;"></div>
                
                <script>
                    var graphDiv = document.getElementById('dashboard-plot');
                    var plotData = {fig.to_json()};
                    Plotly.newPlot(graphDiv, plotData.data, plotData.layout);
                </script>
                
                <div class="insights">
                    <h2>Insights Clave</h2>
                    <ul>
            """
            
            for insight in report.key_insights:
                html_content += f"<li>{insight}</li>"
            
            html_content += """
                    </ul>
                </div>
                
                <div class="insights">
                    <h2>Acciones Urgentes</h2>
                    <ul>
            """
            
            for action in report.urgent_actions:
                html_content += f"<li><strong>{action}</strong></li>"
            
            html_content += """
                    </ul>
                </div>
            </body>
            </html>
            """
            
            self.logger.info("✅ Dashboard HTML generado exitosamente")
            return html_content
            
        except Exception as e:
            self.logger.error(f"❌ Error generando dashboard: {e}")
            return f"<html><body><h1>Error generando dashboard: {str(e)}</h1></body></html>"
    
    # MÉTODOS PRIVADOS
    
    async def _fetch_comprehensive_data(self, hours: float) -> List[Dict[str, Any]]:
        """Obtiene datos comprehensivos para análisis"""
        try:
            # Usar el endpoint estándar de la API
            import requests
            
            url = f"{self.jetson_api_url}/api/get_recent_data"
            params = {'hours': hours}
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    sensor_data = data.get('sensor_data', [])
                    self.logger.info(f"✅ Obtenidos {len(sensor_data)} registros para reporte")
                    return sensor_data
                else:
                    self.logger.warning(f"⚠️ API retornó estado: {data.get('status')}")
                    return []
            else:
                self.logger.error(f"❌ Error HTTP {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo datos: {e}")
            return []
    
    async def _generate_advanced_visualizations(self, raw_data: List[Dict], 
                                              smart_analysis: Dict, 
                                              include_correlations: bool) -> Dict[str, str]:
        """Genera visualizaciones avanzadas en base64"""
        visualizations = {}
        
        try:
            if not raw_data:
                return visualizations
            
            df = pd.DataFrame(raw_data)
            
            # 1. GRÁFICO DE TENDENCIAS TEMPORALES
            if 'timestamp' in df.columns:
                temporal_viz = await self._create_temporal_trends_chart(df)
                if temporal_viz:
                    visualizations['temporal_trends'] = temporal_viz
            
            # 2. ANÁLISIS ESTADÍSTICO POR SENSOR
            statistical_viz = await self._create_statistical_analysis_chart(df)
            if statistical_viz:
                visualizations['statistical_analysis'] = statistical_viz
            
            # 3. MATRIZ DE CORRELACIONES (si se solicita)
            if include_correlations:
                correlation_viz = await self._create_correlation_matrix(df)
                if correlation_viz:
                    visualizations['correlations'] = correlation_viz
            
            # 4. DISTRIBUCIÓN DE VALORES POR DISPOSITIVO
            distribution_viz = await self._create_distribution_chart(df)
            if distribution_viz:
                visualizations['distributions'] = distribution_viz
            
            # 5. HEATMAP DE ACTIVIDAD
            heatmap_viz = await self._create_activity_heatmap(df)
            if heatmap_viz:
                visualizations['activity_heatmap'] = heatmap_viz
            
            self.logger.info(f"✅ Generadas {len(visualizations)} visualizaciones avanzadas")
            
        except Exception as e:
            self.logger.error(f"❌ Error generando visualizaciones: {e}")
        
        return visualizations
    
    async def _create_temporal_trends_chart(self, df: pd.DataFrame) -> Optional[str]:
        """Crea gráfico de tendencias temporales"""
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Tendencias por Dispositivo', 'Variabilidad Temporal'),
                shared_xaxes=True
            )
            
            # Tendencias por dispositivo
            for i, device in enumerate(df['device_id'].unique()):
                device_data = df[df['device_id'] == device].sort_values('timestamp')
                
                fig.add_trace(
                    go.Scatter(
                        x=device_data['timestamp'],
                        y=device_data['value'],
                        name=f'Dispositivo {device}',
                        line=dict(color=self.color_palette[i % len(self.color_palette)]),
                        mode='lines+markers'
                    ),
                    row=1, col=1
                )
            
            # Variabilidad por hora
            df['hour'] = df['timestamp'].dt.hour
            hourly_stats = df.groupby('hour')['value'].agg(['mean', 'std']).reset_index()
            
            fig.add_trace(
                go.Scatter(
                    x=hourly_stats['hour'],
                    y=hourly_stats['mean'],
                    error_y=dict(type='data', array=hourly_stats['std']),
                    name='Promedio Horario',
                    line=dict(color='red', width=3)
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                height=800,
                title_text="Análisis de Tendencias Temporales",
                showlegend=True
            )
            
            # Convertir a base64
            img_bytes = pio.to_image(fig, format="png", width=self.figure_width, height=800)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return img_base64
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error creando gráfico temporal: {e}")
            return None
    
    async def _create_statistical_analysis_chart(self, df: pd.DataFrame) -> Optional[str]:
        """Crea gráfico de análisis estadístico"""
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Box Plot por Sensor', 'Histograma de Valores',
                              'Scatter Plot Multivariable', 'Estadísticas por Dispositivo')
            )
            
            # Box plot por sensor
            for i, sensor in enumerate(df['sensor_type'].unique()):
                sensor_data = df[df['sensor_type'] == sensor]
                
                fig.add_trace(
                    go.Box(
                        y=sensor_data['value'],
                        name=sensor,
                        boxpoints='outliers'
                    ),
                    row=1, col=1
                )
            
            # Histograma general
            fig.add_trace(
                go.Histogram(
                    x=df['value'],
                    nbinsx=30,
                    name='Distribución de Valores'
                ),
                row=1, col=2
            )
            
            # Scatter plot si hay múltiples sensores
            sensor_types = df['sensor_type'].unique()
            if len(sensor_types) >= 2:
                pivot_df = df.pivot_table(
                    values='value',
                    index='timestamp',
                    columns='sensor_type',
                    aggfunc='mean'
                ).fillna(method='ffill')
                
                if pivot_df.shape[1] >= 2:
                    x_col, y_col = pivot_df.columns[:2]
                    
                    fig.add_trace(
                        go.Scatter(
                            x=pivot_df[x_col],
                            y=pivot_df[y_col],
                            mode='markers',
                            name=f'{x_col} vs {y_col}',
                            marker=dict(
                                color=pivot_df.index.hour if hasattr(pivot_df.index, 'hour') else 'blue',
                                colorscale='viridis',
                                showscale=True
                            )
                        ),
                        row=2, col=1
                    )
            
            # Estadísticas por dispositivo
            device_stats = df.groupby('device_id')['value'].agg(['mean', 'std']).reset_index()
            
            fig.add_trace(
                go.Bar(
                    x=device_stats['device_id'],
                    y=device_stats['mean'],
                    error_y=dict(type='data', array=device_stats['std']),
                    name='Promedio ± STD'
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                height=800,
                title_text="Análisis Estadístico Avanzado",
                showlegend=True
            )
            
            # Convertir a base64
            img_bytes = pio.to_image(fig, format="png", width=self.figure_width, height=800)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return img_base64
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error creando análisis estadístico: {e}")
            return None
    
    async def _create_correlation_matrix(self, df: pd.DataFrame) -> Optional[str]:
        """Crea matriz de correlaciones"""
        try:
            # Crear pivot table para correlaciones
            pivot_df = df.pivot_table(
                values='value',
                index='timestamp',
                columns=['device_id', 'sensor_type'],
                aggfunc='mean'
            ).fillna(method='ffill').fillna(method='bfill')
            
            if pivot_df.shape[1] < 2:
                return None
            
            # Calcular correlaciones
            corr_matrix = pivot_df.corr()
            
            # Crear heatmap con Plotly
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=np.round(corr_matrix.values, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title="Matriz de Correlaciones entre Sensores",
                width=self.figure_width,
                height=self.figure_height
            )
            
            # Convertir a base64
            img_bytes = pio.to_image(fig, format="png", width=self.figure_width, height=self.figure_height)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return img_base64
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error creando matriz de correlaciones: {e}")
            return None
    
    async def _create_distribution_chart(self, df: pd.DataFrame) -> Optional[str]:
        """Crea gráfico de distribuciones"""
        try:
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Distribución por Dispositivo', 'Distribución por Sensor')
            )
            
            # Distribución por dispositivo
            for i, device in enumerate(df['device_id'].unique()):
                device_data = df[df['device_id'] == device]
                
                fig.add_trace(
                    go.Violin(
                        y=device_data['value'],
                        name=device,
                        box_visible=True,
                        meanline_visible=True
                    ),
                    row=1, col=1
                )
            
            # Distribución por sensor
            for i, sensor in enumerate(df['sensor_type'].unique()):
                sensor_data = df[df['sensor_type'] == sensor]
                
                fig.add_trace(
                    go.Violin(
                        y=sensor_data['value'],
                        name=sensor,
                        box_visible=True,
                        meanline_visible=True
                    ),
                    row=1, col=2
                )
            
            fig.update_layout(
                height=500,
                title_text="Análisis de Distribuciones",
                showlegend=False
            )
            
            # Convertir a base64
            img_bytes = pio.to_image(fig, format="png", width=self.figure_width, height=500)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return img_base64
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error creando distribuciones: {e}")
            return None
    
    async def _create_activity_heatmap(self, df: pd.DataFrame) -> Optional[str]:
        """Crea heatmap de actividad por hora/día"""
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day'] = df['timestamp'].dt.day_name()
            
            # Crear matriz de actividad
            activity_matrix = df.groupby(['day', 'hour']).size().unstack(fill_value=0)
            
            fig = go.Figure(data=go.Heatmap(
                z=activity_matrix.values,
                x=activity_matrix.columns,
                y=activity_matrix.index,
                colorscale='Blues',
                colorbar=dict(title="Cantidad de Registros")
            ))
            
            fig.update_layout(
                title="Heatmap de Actividad (Día vs Hora)",
                xaxis_title="Hora del Día",
                yaxis_title="Día de la Semana",
                width=self.figure_width,
                height=self.figure_height
            )
            
            # Convertir a base64
            img_bytes = pio.to_image(fig, format="png", width=self.figure_width, height=self.figure_height)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return img_base64
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error creando heatmap de actividad: {e}")
            return None
    
    async def _create_report_sections(self, raw_data: List[Dict], 
                                    smart_analysis: Dict, 
                                    sensor_inventory: Dict,
                                    visualizations: Dict,
                                    report_type: str) -> List[ReportSection]:
        """Crea secciones del reporte basadas en template"""
        sections = []
        
        try:
            template = self.report_templates.get(report_type, self.report_templates['technical'])
            
            for section_name in template['sections']:
                section = await self._create_section(
                    section_name, raw_data, smart_analysis, sensor_inventory, visualizations, template
                )
                if section:
                    sections.append(section)
        
        except Exception as e:
            self.logger.error(f"❌ Error creando secciones: {e}")
        
        return sections
    
    async def _create_section(self, section_name: str, raw_data: List[Dict], 
                            smart_analysis: Dict, sensor_inventory: Dict,
                            visualizations: Dict, template: Dict) -> Optional[ReportSection]:
        """Crea una sección específica del reporte"""
        
        if section_name == 'executive_summary':
            return ReportSection(
                title="Resumen Ejecutivo",
                content=self._generate_executive_summary(smart_analysis, template.get('detail_level', 'summary')),
                priority=1,
                insights=smart_analysis.get('summary', {}).get('top_insights', [])[:3],
                recommendations=smart_analysis.get('summary', {}).get('urgent_actions', [])[:3]
            )
        
        elif section_name == 'system_overview':
            content = f"""
            El sistema IoT monitoreado cuenta con {len(smart_analysis.get('devices_analyzed', []))} dispositivos activos 
            y {len(smart_analysis.get('sensors_analyzed', []))} tipos de sensores diferentes.
            
            Durante el período de análisis de {smart_analysis.get('analysis_period_hours', 0)} horas, 
            se procesaron {smart_analysis.get('total_data_points', 0)} registros de datos.
            
            **Estado General del Sistema:**
            - Puntuación de salud: {smart_analysis.get('health_score', 0):.1f}%
            - Nivel de confianza del análisis: {smart_analysis.get('confidence_level', 0):.1%}
            
            **Dispositivos Monitoreados:**
            """
            
            for device_id in smart_analysis.get('devices_analyzed', []):
                device_info = sensor_inventory.get(device_id)
                if device_info:
                    content += f"\n- {device_id}: {len(device_info.sensors)} sensores activos"
            
            return ReportSection(
                title="Panorama General del Sistema",
                content=content,
                visualizations=[visualizations.get('temporal_trends')] if 'temporal_trends' in visualizations else None,
                priority=2,
                data_summary={
                    'devices': len(smart_analysis.get('devices_analyzed', [])),
                    'sensors': len(smart_analysis.get('sensors_analyzed', [])),
                    'data_points': smart_analysis.get('total_data_points', 0)
                }
            )
        
        elif section_name == 'sensor_analysis':
            sensor_insights = smart_analysis.get('sensor_insights', [])
            
            content = f"**Análisis Detallado de Sensores**\n\n"
            content += f"Se detectaron {len(sensor_insights)} insights específicos de sensores durante el análisis.\n\n"
            
            # Agrupar insights por severidad
            critical_insights = [s for s in sensor_insights if s.severity == 'critical']
            warning_insights = [s for s in sensor_insights if s.severity == 'warning']
            info_insights = [s for s in sensor_insights if s.severity == 'info']
            
            if critical_insights:
                content += f"**⚠️ Problemas Críticos ({len(critical_insights)}):**\n"
                for insight in critical_insights[:5]:  # Máximo 5
                    content += f"- {insight.title}: {insight.description}\n"
                content += "\n"
            
            if warning_insights:
                content += f"**🟡 Advertencias ({len(warning_insights)}):**\n"
                for insight in warning_insights[:5]:
                    content += f"- {insight.title}: {insight.description}\n"
                content += "\n"
            
            insights = [s.title for s in sensor_insights[:10]]
            recommendations = [s.suggested_action for s in sensor_insights if s.suggested_action][:5]
            
            return ReportSection(
                title="Análisis de Sensores",
                content=content,
                visualizations=[visualizations.get('statistical_analysis')] if 'statistical_analysis' in visualizations else None,
                insights=insights,
                recommendations=recommendations,
                priority=3
            )
        
        elif section_name == 'anomalies':
            anomalies = smart_analysis.get('anomalies', [])
            
            content = f"**Detección de Anomalías**\n\n"
            content += f"Se detectaron {len(anomalies)} anomalías durante el período de análisis.\n\n"
            
            if anomalies:
                # Agrupar por severidad
                critical_anomalies = [a for a in anomalies if a.get('severity') == 'critical']
                warning_anomalies = [a for a in anomalies if a.get('severity') == 'warning']
                
                if critical_anomalies:
                    content += f"**🚨 Anomalías Críticas ({len(critical_anomalies)}):**\n"
                    for anomaly in critical_anomalies[:5]:
                        content += f"- Dispositivo {anomaly.get('device_id')}, Sensor {anomaly.get('sensor_type')}: "
                        content += f"Valor {anomaly.get('value'):.2f} fuera del rango esperado\n"
                    content += "\n"
                
                if warning_anomalies:
                    content += f"**⚠️ Anomalías de Advertencia ({len(warning_anomalies)}):**\n"
                    for anomaly in warning_anomalies[:5]:
                        content += f"- Dispositivo {anomaly.get('device_id')}, Sensor {anomaly.get('sensor_type')}: "
                        content += f"Valor {anomaly.get('value'):.2f} requiere atención\n"
            else:
                content += "✅ No se detectaron anomalías significativas en el período analizado."
            
            return ReportSection(
                title="Detección de Anomalías",
                content=content,
                priority=2,
                insights=[f"Total de anomalías: {len(anomalies)}"],
                recommendations=["Investigar anomalías críticas inmediatamente", 
                               "Establecer alertas automáticas para detección temprana"] if anomalies else []
            )
        
        elif section_name == 'correlations':
            content = "**Análisis de Correlaciones**\n\n"
            
            system_insights = smart_analysis.get('system_insights', [])
            correlation_insights = [s for s in system_insights if s.insight_type == 'correlation']
            
            if correlation_insights:
                content += f"Se encontraron {len(correlation_insights)} correlaciones significativas entre sensores.\n\n"
                for insight in correlation_insights:
                    content += f"- {insight.title}: {insight.description}\n"
            else:
                content += "No se detectaron correlaciones significativas entre sensores en este período."
            
            return ReportSection(
                title="Análisis de Correlaciones",
                content=content,
                visualizations=[visualizations.get('correlations')] if 'correlations' in visualizations else None,
                priority=4,
                insights=[s.title for s in correlation_insights]
            )
        
        # Agregar más secciones según necesidad...
        
        return None
    
    def _generate_executive_summary(self, smart_analysis: Dict, report_type: str) -> str:
        """Genera resumen ejecutivo inteligente"""
        try:
            summary = smart_analysis.get('summary', {})
            
            overall_status = summary.get('overall_status', 'Desconocido')
            health_score = smart_analysis.get('health_score', 0)
            devices_count = len(smart_analysis.get('devices_analyzed', []))
            sensors_count = len(smart_analysis.get('sensors_analyzed', []))
            data_points = smart_analysis.get('total_data_points', 0)
            
            exec_summary = f"""
            **Estado General:** {summary.get('status_emoji', '⚪')} {overall_status}
            
            El sistema IoT presenta una puntuación de salud de {health_score:.1f}% basada en el análisis 
            de {data_points:,} registros de {devices_count} dispositivos con {sensors_count} tipos de sensores diferentes.
            
            **Puntos Destacados:**
            """
            
            # Agregar insights clave
            top_insights = summary.get('top_insights', [])
            for insight in top_insights[:3]:
                exec_summary += f"\n• {insight}"
            
            # Agregar acciones urgentes si existen
            urgent_actions = summary.get('urgent_actions', [])
            if urgent_actions:
                exec_summary += f"\n\n**Acciones Requeridas:**"
                for action in urgent_actions[:3]:
                    exec_summary += f"\n🎯 {action}"
            
            # Conclusión adaptada por tipo de reporte
            if report_type == 'executive':
                exec_summary += f"\n\nEl sistema requiere {'atención inmediata' if health_score < 70 else 'monitoreo continuo' if health_score < 90 else 'mantenimiento rutinario'}."
            elif report_type == 'technical':
                exec_summary += f"\n\nAnálisis técnico detallado disponible en las secciones siguientes con {smart_analysis.get('confidence_level', 0):.1%} de confianza."
            else:
                exec_summary += f"\n\nSe recomienda revisar las recomendaciones operativas para optimizar el rendimiento del sistema."
            
            return exec_summary.strip()
            
        except Exception as e:
            self.logger.error(f"❌ Error generando resumen ejecutivo: {e}")
            return "Error generando resumen ejecutivo del sistema IoT."
    
    def _create_empty_report(self, reason: str) -> AdvancedReport:
        """Crea reporte vacío con razón"""
        return AdvancedReport(
            title="Reporte IoT - Sin Datos",
            subtitle=reason,
            generated_at=datetime.now(),
            analysis_period="0h",
            executive_summary=f"No se pudo generar el reporte: {reason}",
            sections=[],
            health_score=0.0,
            confidence_level=0.0,
            total_devices=0,
            total_sensors=0,
            data_points=0,
            key_insights=[],
            urgent_actions=[],
            metadata={'error': reason}
        )