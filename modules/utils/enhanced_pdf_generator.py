#!/usr/bin/env python3
"""
Enhanced PDF Report Generator - Generador de Reportes PDF Enriquecidos
====================================================================

Sistema mejorado que genera reportes PDF con:
- Gráficas explicativas de hallazgos
- Muestra visual de datos
- Insights graficados
- Análisis estadístico visual
- Tablas de datos formateadas

Optimizado para funcionar en Streamlit Cloud.
"""

import logging
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import base64
from io import BytesIO
import seaborn as sns
import matplotlib.pyplot as plt

# Imports para PDF avanzado
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.units import inch, cm

logger = logging.getLogger(__name__)

class EnhancedPDFReportGenerator:
    """
    Generador mejorado de reportes PDF con gráficas y visualizaciones avanzadas.
    """
    
    def __init__(self):
        self.logger = logger
        
        # Configurar matplotlib para Streamlit Cloud
        plt.switch_backend('Agg')
        plt.ioff()
        
        # Configurar seaborn
        sns.set_style("whitegrid")
        sns.set_palette("husl")
        
        # Configurar plotly para exportar imágenes
        pio.kaleido.scope.default_format = "png"
        pio.kaleido.scope.default_width = 800
        pio.kaleido.scope.default_height = 600
        
        self.logger.info("📊 EnhancedPDFReportGenerator inicializado")
    
    def create_sensor_insights_chart(self, insights: List, data: pd.DataFrame) -> str:
        """
        Crear gráfico de insights de sensores.
        
        Args:
            insights: Lista de insights del SmartAnalyzer
            data: DataFrame con datos de sensores
            
        Returns:
            Imagen en base64
        """
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('📊 Análisis de Insights de Sensores', fontsize=16, fontweight='bold')
            
            # 1. Distribución de severidad de insights
            if insights:
                severity_counts = {}
                for insight in insights:
                    severity = getattr(insight, 'severity', 'unknown')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                colors_map = {'critical': '#d62728', 'warning': '#ff7f0e', 'info': '#2ca02c', 'unknown': '#7f7f7f'}
                ax1.pie(severity_counts.values(), labels=severity_counts.keys(), autopct='%1.1f%%',
                       colors=[colors_map.get(k, '#7f7f7f') for k in severity_counts.keys()])
                ax1.set_title('Distribución de Severidad')
            else:
                ax1.text(0.5, 0.5, 'No hay insights disponibles', ha='center', va='center', transform=ax1.transAxes)
                ax1.set_title('Distribución de Severidad')
            
            # 2. Valores por sensor a lo largo del tiempo
            if not data.empty and 'timestamp' in data.columns and 'sensor_type' in data.columns:
                # Tomar una muestra de datos para el gráfico
                sample_data = data.groupby(['sensor_type', pd.Grouper(key='timestamp', freq='1H')])['value'].mean().reset_index()
                
                for sensor in sample_data['sensor_type'].unique()[:4]:  # Máximo 4 sensores
                    sensor_data = sample_data[sample_data['sensor_type'] == sensor]
                    ax2.plot(sensor_data['timestamp'], sensor_data['value'], marker='o', label=sensor, alpha=0.7)
                
                ax2.set_title('Tendencias Temporales por Sensor')
                ax2.set_xlabel('Tiempo')
                ax2.set_ylabel('Valor')
                ax2.legend()
                ax2.tick_params(axis='x', rotation=45)
            else:
                ax2.text(0.5, 0.5, 'Datos insuficientes', ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Tendencias Temporales por Sensor')
            
            # 3. Distribución de valores por sensor
            if not data.empty and 'sensor_type' in data.columns and 'value' in data.columns:
                sensors = data['sensor_type'].unique()[:4]  # Máximo 4 sensores
                sensor_values = [data[data['sensor_type'] == sensor]['value'].values for sensor in sensors]
                
                ax3.boxplot(sensor_values, labels=sensors)
                ax3.set_title('Distribución de Valores por Sensor')
                ax3.set_ylabel('Valor')
                ax3.tick_params(axis='x', rotation=45)
            else:
                ax3.text(0.5, 0.5, 'Datos insuficientes', ha='center', va='center', transform=ax3.transAxes)
                ax3.set_title('Distribución de Valores por Sensor')
            
            # 4. Heatmap de correlaciones
            if not data.empty and len(data['sensor_type'].unique()) > 1:
                # Crear matriz de correlación
                pivot_data = data.pivot_table(values='value', index='timestamp', columns='sensor_type', aggfunc='mean')
                correlation_matrix = pivot_data.corr()
                
                im = ax4.imshow(correlation_matrix.values, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
                ax4.set_xticks(range(len(correlation_matrix.columns)))
                ax4.set_yticks(range(len(correlation_matrix.index)))
                ax4.set_xticklabels(correlation_matrix.columns, rotation=45)
                ax4.set_yticklabels(correlation_matrix.index)
                ax4.set_title('Correlaciones entre Sensores')
                
                # Agregar valores en las celdas
                for i in range(len(correlation_matrix.index)):
                    for j in range(len(correlation_matrix.columns)):
                        ax4.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}', 
                                ha='center', va='center', color='white', fontweight='bold')
            else:
                ax4.text(0.5, 0.5, 'Datos insuficientes\npara correlaciones', ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Correlaciones entre Sensores')
            
            plt.tight_layout()
            
            # Convertir a base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            self.logger.error(f"❌ Error creando gráfico de insights: {e}")
            return None
    
    def create_data_sample_table(self, data: pd.DataFrame, max_rows: int = 10) -> str:
        """
        Crear tabla HTML con muestra de datos.
        
        Args:
            data: DataFrame con datos
            max_rows: Número máximo de filas a mostrar
            
        Returns:
            HTML de la tabla
        """
        try:
            if data.empty:
                return "<p>No hay datos disponibles para mostrar.</p>"
            
            # Tomar muestra de datos
            sample_data = data.head(max_rows).copy()
            
            # Formatear timestamp si existe
            if 'timestamp' in sample_data.columns:
                sample_data['timestamp'] = pd.to_datetime(sample_data['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Formatear valores numéricos
            for col in sample_data.columns:
                if sample_data[col].dtype in ['float64', 'float32']:
                    sample_data[col] = sample_data[col].round(2)
            
            # Crear tabla HTML con estilo
            html = f"""
            <div style="font-family: Arial, sans-serif; margin: 20px 0;">
                <h3 style="color: #2E86AB; margin-bottom: 10px;">📋 Muestra de Datos ({len(sample_data)} de {len(data)} registros)</h3>
                <div style="overflow-x: auto;">
                    {sample_data.to_html(index=False, classes='data-table', table_id='sample-data')}
                </div>
                <p style="color: #666; font-size: 12px; margin-top: 10px;">
                    Total de registros: {len(data):,} | 
                    Columnas: {len(data.columns)} | 
                    Período: {data['timestamp'].min() if 'timestamp' in data.columns else 'N/A'} - 
                    {data['timestamp'].max() if 'timestamp' in data.columns else 'N/A'}
                </p>
            </div>
            """
            
            return html
            
        except Exception as e:
            self.logger.error(f"❌ Error creando tabla de datos: {e}")
            return "<p>Error generando tabla de datos.</p>"
    
    def create_insights_visualization_chart(self, insights: List, title: str = "💡 Insights del Sistema") -> str:
        """
        Crear visualización específica de insights con gráficos explicativos.
        
        Args:
            insights: Lista de insights
            title: Título del gráfico
            
        Returns:
            Imagen en base64
        """
        try:
            if not insights:
                # Crear gráfico vacío informativo
                fig, ax = plt.subplots(1, 1, figsize=(10, 6))
                ax.text(0.5, 0.5, '📊 No hay insights disponibles para mostrar', 
                       ha='center', va='center', transform=ax.transAxes, 
                       fontsize=14, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
                ax.set_title(title)
                ax.axis('off')
            else:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
                fig.suptitle(title, fontsize=16, fontweight='bold')
                
                # 1. Gráfico de barras de insights por tipo
                insight_types = {}
                severities = {}
                
                for insight in insights:
                    insight_type = getattr(insight, 'insight_type', 'general')
                    severity = getattr(insight, 'severity', 'unknown')
                    
                    insight_types[insight_type] = insight_types.get(insight_type, 0) + 1
                    severities[severity] = severities.get(severity, 0) + 1
                
                # Gráfico de tipos de insights
                ax1.bar(insight_types.keys(), insight_types.values(), color='skyblue', alpha=0.7)
                ax1.set_title('📊 Insights por Tipo')
                ax1.set_ylabel('Cantidad')
                ax1.tick_params(axis='x', rotation=45)
                
                # Gráfico de severidad
                severity_colors = {'critical': '#d62728', 'warning': '#ff7f0e', 'info': '#2ca02c', 'unknown': '#7f7f7f'}
                colors_list = [severity_colors.get(k, '#7f7f7f') for k in severities.keys()]
                
                ax2.bar(severities.keys(), severities.values(), color=colors_list, alpha=0.7)
                ax2.set_title('⚠️ Insights por Severidad')
                ax2.set_ylabel('Cantidad')
                
                # Agregar valores en las barras
                for ax in [ax1, ax2]:
                    for i, (label, value) in enumerate(zip(ax.get_xticklabels(), 
                                                         [bar.get_height() for bar in ax.patches])):
                        ax.text(i, value + 0.05, str(int(value)), ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            
            # Convertir a base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            self.logger.error(f"❌ Error creando visualización de insights: {e}")
            return None
    
    def create_system_health_chart(self, health_data: Dict) -> str:
        """
        Crear gráfico de salud del sistema.
        
        Args:
            health_data: Datos de salud del sistema
            
        Returns:
            Imagen en base64
        """
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('🏥 Salud del Sistema IoT', fontsize=16, fontweight='bold')
            
            # 1. Medidor de salud general
            health_score = health_data.get('overall_score', 0)
            colors_gauge = ['#d62728' if health_score < 50 else '#ff7f0e' if health_score < 80 else '#2ca02c']
            
            wedges, texts, autotexts = ax1.pie([health_score, 100-health_score], 
                                               labels=['Salud', 'Restante'],
                                               colors=[colors_gauge[0], '#f0f0f0'],
                                               startangle=90,
                                               counterclock=False,
                                               wedgeprops=dict(width=0.3))
            
            ax1.text(0, 0, f'{health_score:.1f}%', ha='center', va='center', fontsize=20, fontweight='bold')
            ax1.set_title('🎯 Score General de Salud')
            
            # 2. Issues por severidad
            issues = health_data.get('issues_summary', {})
            if issues:
                severities = list(issues.keys())
                counts = list(issues.values())
                colors_bars = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4'][:len(severities)]
                
                bars = ax2.bar(severities, counts, color=colors_bars, alpha=0.7)
                ax2.set_title('⚠️ Issues por Severidad')
                ax2.set_ylabel('Cantidad')
                
                # Agregar valores en las barras
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                            f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            else:
                ax2.text(0.5, 0.5, 'No hay issues registrados', ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('⚠️ Issues por Severidad')
            
            # 3. Métricas clave
            metrics = health_data.get('key_metrics', {})
            if metrics:
                metric_names = list(metrics.keys())
                metric_values = list(metrics.values())
                
                ax3.barh(metric_names, metric_values, color='lightblue', alpha=0.7)
                ax3.set_title('📊 Métricas Clave')
                ax3.set_xlabel('Valores')
                
                # Agregar valores
                for i, v in enumerate(metric_values):
                    ax3.text(v + max(metric_values) * 0.01, i, f'{v}', va='center', fontweight='bold')
            else:
                ax3.text(0.5, 0.5, 'Métricas no disponibles', ha='center', va='center', transform=ax3.transAxes)
                ax3.set_title('📊 Métricas Clave')
            
            # 4. Timeline de confianza
            confidence = health_data.get('confidence_level', 0)
            predictions_available = health_data.get('predictions_available', False)
            
            # Crear gráfico de estado
            status_data = {
                'Confianza': confidence * 100,
                'Predicciones': 100 if predictions_available else 0,
                'Completitud': health_score
            }
            
            ax4.bar(status_data.keys(), status_data.values(), color=['#ff7f0e', '#2ca02c', '#1f77b4'], alpha=0.7)
            ax4.set_title('📈 Estado del Sistema')
            ax4.set_ylabel('Porcentaje (%)')
            ax4.set_ylim(0, 100)
            
            # Agregar valores
            for i, (name, value) in enumerate(status_data.items()):
                ax4.text(i, value + 2, f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            
            # Convertir a base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            self.logger.error(f"❌ Error creando gráfico de salud: {e}")
            return None
    
    def generate_enhanced_pdf_report(self, 
                                   analysis_results: Dict, 
                                   raw_data: pd.DataFrame,
                                   title: str = "📊 Reporte IoT Avanzado") -> bytes:
        """
        Generar reporte PDF mejorado con gráficas y visualizaciones.
        
        Args:
            analysis_results: Resultados del análisis del SmartAnalyzer
            raw_data: DataFrame con datos originales
            title: Título del reporte
            
        Returns:
            Bytes del PDF generado
        """
        try:
            self.logger.info("📄 Generando reporte PDF mejorado...")
            
            # Crear buffer para PDF
            buffer = BytesIO()
            
            # Configurar documento
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Estilos personalizados
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2E86AB')
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=15,
                textColor=colors.HexColor('#A23B72')
            )
            
            # 1. PORTADA
            story.append(Paragraph(title, title_style))
            story.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 30))
            
            # Información del sistema
            system_info = f"""
            <b>📊 Resumen del Sistema:</b><br/>
            • Registros procesados: {len(raw_data):,}<br/>
            • Dispositivos: {raw_data['device_id'].nunique() if 'device_id' in raw_data.columns else 'N/A'}<br/>
            • Sensores: {raw_data['sensor_type'].nunique() if 'sensor_type' in raw_data.columns else 'N/A'}<br/>
            • Período: {raw_data['timestamp'].min() if 'timestamp' in raw_data.columns else 'N/A'} - {raw_data['timestamp'].max() if 'timestamp' in raw_data.columns else 'N/A'}<br/>
            """
            
            if 'smart_analysis' in analysis_results:
                smart_analysis = analysis_results['smart_analysis']
                health_score = smart_analysis.get('health_score', 0)
                system_info += f"• Score de salud: {health_score:.1f}%<br/>"
                system_info += f"• Insights generados: {len(smart_analysis.get('sensor_insights', []))}<br/>"
            
            story.append(Paragraph(system_info, styles['Normal']))
            story.append(PageBreak())
            
            # 2. GRÁFICOS DE INSIGHTS
            if 'smart_analysis' in analysis_results:
                smart_analysis = analysis_results['smart_analysis']
                insights = smart_analysis.get('sensor_insights', [])
                
                story.append(Paragraph("💡 Análisis de Insights", subtitle_style))
                
                # Crear gráfico de insights
                insights_chart = self.create_insights_visualization_chart(insights)
                if insights_chart:
                    # Crear imagen temporal
                    image_buffer = BytesIO(base64.b64decode(insights_chart))
                    story.append(Image(image_buffer, width=6*inch, height=3*inch))
                    story.append(Spacer(1, 15))
                
                # Lista de insights
                if insights:
                    story.append(Paragraph("<b>Insights Detectados:</b>", styles['Normal']))
                    for i, insight in enumerate(insights[:10], 1):  # Máximo 10 insights
                        insight_text = f"{i}. <b>{getattr(insight, 'title', 'Insight sin título')}</b> "
                        insight_text += f"({getattr(insight, 'severity', 'unknown').upper()})<br/>"
                        insight_text += f"   {getattr(insight, 'description', 'Sin descripción')}<br/>"
                        story.append(Paragraph(insight_text, styles['Normal']))
                        story.append(Spacer(1, 5))
                
                story.append(PageBreak())
            
            # 3. GRÁFICO DE SALUD DEL SISTEMA
            if 'smart_analysis' in analysis_results:
                story.append(Paragraph("🏥 Salud del Sistema", subtitle_style))
                
                health_chart = self.create_system_health_chart(analysis_results['smart_analysis'])
                if health_chart:
                    image_buffer = BytesIO(base64.b64decode(health_chart))
                    story.append(Image(image_buffer, width=7*inch, height=5*inch))
                    story.append(Spacer(1, 15))
                
                story.append(PageBreak())
            
            # 4. ANÁLISIS DETALLADO DE SENSORES
            story.append(Paragraph("📊 Análisis Detallado de Sensores", subtitle_style))
            
            sensor_chart = self.create_sensor_insights_chart(
                analysis_results.get('smart_analysis', {}).get('sensor_insights', []),
                raw_data
            )
            if sensor_chart:
                image_buffer = BytesIO(base64.b64decode(sensor_chart))
                story.append(Image(image_buffer, width=7*inch, height=6*inch))
                story.append(Spacer(1, 15))
            
            story.append(PageBreak())
            
            # 5. MUESTRA DE DATOS
            story.append(Paragraph("📋 Muestra de Datos del Sistema", subtitle_style))
            
            # Crear tabla con muestra de datos
            if not raw_data.empty:
                # Tomar muestra representativa
                sample_size = min(15, len(raw_data))
                sample_data = raw_data.sample(n=sample_size) if len(raw_data) > sample_size else raw_data
                
                # Preparar datos para tabla
                table_data = []
                headers = list(sample_data.columns)[:6]  # Máximo 6 columnas
                table_data.append(headers)
                
                for _, row in sample_data.iterrows():
                    row_data = []
                    for col in headers:
                        value = row[col]
                        # Formatear valores
                        if pd.isna(value):
                            row_data.append('N/A')
                        elif isinstance(value, (int, float)):
                            if isinstance(value, float):
                                row_data.append(f'{value:.2f}')
                            else:
                                row_data.append(str(value))
                        elif pd.api.types.is_datetime64_any_dtype(pd.Series([value])):
                            row_data.append(pd.to_datetime(value).strftime('%Y-%m-%d %H:%M'))
                        else:
                            row_data.append(str(value)[:20])  # Truncar strings largos
                    table_data.append(row_data)
                
                # Crear tabla
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
                story.append(Spacer(1, 10))
                
                # Estadísticas de los datos
                stats_text = f"<b>Estadísticas de los datos:</b><br/>"
                stats_text += f"• Total de registros: {len(raw_data):,}<br/>"
                if 'value' in raw_data.columns:
                    stats_text += f"• Valor promedio: {raw_data['value'].mean():.2f}<br/>"
                    stats_text += f"• Valor mínimo: {raw_data['value'].min():.2f}<br/>"
                    stats_text += f"• Valor máximo: {raw_data['value'].max():.2f}<br/>"
                
                story.append(Paragraph(stats_text, styles['Normal']))
            
            # 6. PIE DE PÁGINA
            story.append(PageBreak())
            story.append(Paragraph("📋 Resumen Final", subtitle_style))
            
            summary_text = """
            Este reporte ha sido generado automáticamente por el sistema de análisis inteligente IoT.
            Las gráficas y análisis presentados proporcionan una visión integral del estado actual
            del sistema y los insights detectados por los algoritmos de machine learning.
            
            Para consultas técnicas o interpretación de resultados, contacte al equipo de desarrollo.
            """
            story.append(Paragraph(summary_text, styles['Normal']))
            
            # Construir PDF
            doc.build(story)
            
            # Obtener bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            self.logger.info(f"✅ Reporte PDF mejorado generado: {len(pdf_bytes):,} bytes")
            return pdf_bytes
            
        except Exception as e:
            self.logger.error(f"❌ Error generando reporte PDF mejorado: {e}")
            raise


# Instancia global
_enhanced_generator = None

def get_enhanced_pdf_generator():
    """Obtener instancia del generador mejorado."""
    global _enhanced_generator
    if _enhanced_generator is None:
        _enhanced_generator = EnhancedPDFReportGenerator()
    return _enhanced_generator


if __name__ == "__main__":
    # Test del generador mejorado
    print("🧪 PRUEBA DEL ENHANCED PDF REPORT GENERATOR")
    print("=" * 60)
    
    generator = EnhancedPDFReportGenerator()
    
    # Crear datos de prueba
    test_data = pd.DataFrame({
        'timestamp': pd.date_range('2025-01-01', periods=100, freq='1H'),
        'device_id': ['device_1', 'device_2'] * 50,
        'sensor_type': ['temperature', 'humidity', 'pressure'] * 33 + ['temperature'],
        'value': np.random.normal(25, 5, 100)
    })
    
    test_analysis = {
        'smart_analysis': {
            'health_score': 75.5,
            'sensor_insights': [],
            'issues_summary': {'critical': 2, 'warning': 5, 'info': 3},
            'key_metrics': {'devices': 2, 'sensors': 3, 'data_points': 100}
        }
    }
    
    print("📊 Generando reporte de prueba...")
    pdf_bytes = generator.generate_enhanced_pdf_report(test_analysis, test_data)
    
    print(f"✅ Reporte generado: {len(pdf_bytes):,} bytes")
    
    # Guardar archivo de prueba
    with open('test_enhanced_report.pdf', 'wb') as f:
        f.write(pdf_bytes)
    
    print("💾 Reporte guardado como 'test_enhanced_report.pdf'")