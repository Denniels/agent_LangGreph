"""
Generador de Visualizaciones Modernas para Reportes IoT
======================================================

Crea dashboards atractivos y tarjetas modernas usando Altair y Plotly
con diseños tipo Material Design para reportes ejecutivos.

Autor: IoT Agent System
Fecha: 29 de octubre de 2025
"""

import altair as alt
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
import io
from typing import Dict, List, Optional, Any
import logging

class ModernVisualizationEngine:
    """Motor de visualizaciones modernas para dashboards IoT"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configurar Altair para mejores visualizaciones
        alt.data_transformers.enable('json')
        
        # Paleta de colores moderna tipo Material Design
        self.modern_colors = {
            'primary': '#1976D2',      # Azul Material
            'secondary': '#FF6F00',    # Naranja vibrante
            'success': '#388E3C',      # Verde
            'danger': '#D32F2F',       # Rojo
            'warning': '#F57C00',      # Amarillo/naranja
            'info': '#0288D1',         # Azul claro
            'purple': '#7B1FA2',       # Púrpura
            'teal': '#00796B'          # Verde azulado
        }
        
        self.gradient_colors = [
            '#667eea', '#764ba2', '#f093fb', '#f5576c', 
            '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'
        ]

    async def create_sensor_dashboard_cards(self, df: pd.DataFrame) -> Dict[str, str]:
        """Crear tarjetas de dashboard modernas para cada sensor"""
        try:
            if df.empty:
                return {}
            
            # Preparar datos
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['numeric_value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df.dropna(subset=['numeric_value'])
            
            cards = {}
            sensors = df['sensor_type'].unique()
            
            for i, sensor in enumerate(sensors):
                sensor_data = df[df['sensor_type'] == sensor].copy()
                
                if len(sensor_data) == 0:
                    continue
                
                # Crear tarjeta moderna para este sensor
                card_html = await self._create_altair_sensor_card(sensor, sensor_data, i)
                
                if card_html:
                    cards[f"sensor_{sensor}"] = card_html
            
            return cards
            
        except Exception as e:
            self.logger.error(f"Error creando dashboard cards: {e}")
            return {}

    async def _create_altair_sensor_card(self, sensor_name: str, data: pd.DataFrame, color_index: int) -> str:
        """Crear tarjeta individual usando Altair con diseño moderno"""
        try:
            # Estadísticas
            stats = {
                'mean': data['numeric_value'].mean(),
                'std': data['numeric_value'].std(),
                'min': data['numeric_value'].min(),
                'max': data['numeric_value'].max(),
                'count': len(data),
                'trend': self._calculate_trend(data['numeric_value'])
            }
            
            # Determinar unidad
            unit = self._get_sensor_unit(sensor_name)
            color = list(self.modern_colors.values())[color_index % len(self.modern_colors)]
            
            # Crear gráfico principal con Altair
            base_chart = alt.Chart(data).add_selection(
                alt.selection_interval(bind='scales')
            )
            
            # Gráfico de línea principal
            line_chart = base_chart.mark_line(
                color=color,
                strokeWidth=3,
                point=alt.OverlayMarkDef(
                    color=color,
                    size=50,
                    opacity=0.8
                )
            ).encode(
                x=alt.X('timestamp:T', 
                       axis=alt.Axis(title='', labels=False, ticks=False)),
                y=alt.Y('numeric_value:Q',
                       axis=alt.Axis(title='', labels=True, tickCount=5)),
                tooltip=[
                    alt.Tooltip('timestamp:T', title='Tiempo'),
                    alt.Tooltip('numeric_value:Q', title=f'Valor ({unit})', format='.2f'),
                    alt.Tooltip('device_id:N', title='Dispositivo')
                ]
            ).properties(
                width=350,
                height=120
            )
            
            # Área de relleno
            area_chart = base_chart.mark_area(
                color=color,
                opacity=0.2
            ).encode(
                x='timestamp:T',
                y='numeric_value:Q'
            )
            
            # Línea de promedio
            mean_line = alt.Chart(pd.DataFrame({
                'mean': [stats['mean']], 
                'label': [f"Promedio: {stats['mean']:.1f}{unit}"]
            })).mark_rule(
                color='red',
                strokeDash=[5, 5],
                strokeWidth=2
            ).encode(
                y='mean:Q',
                tooltip='label:N'
            )
            
            # Combinar gráficos
            combined_chart = (area_chart + line_chart + mean_line).resolve_scale(
                color='independent'
            )
            
            # Convertir a HTML
            chart_html = combined_chart.to_html()
            
            # Crear tarjeta HTML moderna completa
            card_html = f"""
            <div style="
                background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
                border-radius: 20px;
                box-shadow: 
                    0 10px 25px -5px rgba(0, 0, 0, 0.1),
                    0 10px 10px -5px rgba(0, 0, 0, 0.04);
                border: 1px solid rgba(229, 231, 235, 0.8);
                padding: 28px;
                margin: 20px;
                max-width: 420px;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            " onmouseover="this.style.transform='translateY(-8px)'; this.style.boxShadow='0 25px 50px -12px rgba(0, 0, 0, 0.25)';" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)';">
               
                <!-- Decoración de gradiente superior -->
                <div style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                    background: linear-gradient(90deg, {color} 0%, {self.gradient_colors[color_index % len(self.gradient_colors)]} 100%);
                "></div>
                
                <!-- Header elegante -->
                <div style="display: flex; align-items: center; margin-bottom: 24px;">
                    <div style="
                        width: 20px;
                        height: 20px;
                        background: linear-gradient(135deg, {color} 0%, {self.gradient_colors[color_index % len(self.gradient_colors)]} 100%);
                        border-radius: 50%;
                        margin-right: 16px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    "></div>
                    <div>
                        <h3 style="
                            margin: 0;
                            font-size: 20px;
                            font-weight: 700;
                            color: #1f2937;
                            text-transform: capitalize;
                            letter-spacing: -0.025em;
                        ">{sensor_name.replace('_', ' ')}</h3>
                        <p style="
                            margin: 2px 0 0 0;
                            font-size: 13px;
                            color: #6b7280;
                            font-weight: 500;
                        ">Sensor IoT - Tiempo Real</p>
                    </div>
                </div>
                
                <!-- KPIs principales -->
                <div style="
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 16px;
                    margin-bottom: 24px;
                ">
                    <div style="
                        text-align: center;
                        padding: 20px 16px;
                        background: linear-gradient(135deg, {color}15 0%, {color}08 100%);
                        border-radius: 16px;
                        border: 1px solid {color}20;
                    ">
                        <div style="
                            font-size: 32px;
                            font-weight: 800;
                            color: {color};
                            line-height: 1;
                            margin-bottom: 4px;
                        ">{stats['mean']:.1f}</div>
                        <div style="
                            font-size: 11px;
                            color: #6b7280;
                            font-weight: 600;
                            text-transform: uppercase;
                            letter-spacing: 0.05em;
                        ">Promedio {unit}</div>
                    </div>
                    
                    <div style="
                        text-align: center;
                        padding: 20px 16px;
                        background: linear-gradient(135deg, #10b98115 0%, #10b98108 100%);
                        border-radius: 16px;
                        border: 1px solid #10b98120;
                    ">
                        <div style="
                            font-size: 32px;
                            font-weight: 800;
                            color: #10b981;
                            line-height: 1;
                            margin-bottom: 4px;
                        ">{stats['count']}</div>
                        <div style="
                            font-size: 11px;
                            color: #6b7280;
                            font-weight: 600;
                            text-transform: uppercase;
                            letter-spacing: 0.05em;
                        ">Registros</div>
                    </div>
                </div>
                
                <!-- Estadísticas detalladas -->
                <div style="
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 12px;
                    margin-bottom: 24px;
                    padding: 16px;
                    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                    border-radius: 12px;
                    border: 1px solid #e2e8f0;
                ">
                    <div style="text-align: center;">
                        <div style="font-size: 16px; font-weight: 700; color: #374151;">{stats['min']:.1f}</div>
                        <div style="font-size: 10px; color: #9ca3af; font-weight: 600;">MÍNIMO</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 16px; font-weight: 700; color: #374151;">{stats['std']:.1f}</div>
                        <div style="font-size: 10px; color: #9ca3af; font-weight: 600;">DESV. EST.</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 16px; font-weight: 700; color: #374151;">{stats['max']:.1f}</div>
                        <div style="font-size: 10px; color: #9ca3af; font-weight: 600;">MÁXIMO</div>
                    </div>
                </div>
                
                <!-- Gráfico temporal -->
                <div style="
                    margin-bottom: 20px;
                    border-radius: 12px;
                    overflow: hidden;
                    border: 1px solid #e5e7eb;
                    background: white;
                ">
                    {chart_html}
                </div>
                
                <!-- Badge de tendencia -->
                <div style="
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 12px 16px;
                    background: linear-gradient(90deg, {color}20 0%, {color}10 100%);
                    border-radius: 10px;
                    border-left: 4px solid {color};
                ">
                    <span style="
                        font-size: 13px;
                        color: #374151;
                        font-weight: 600;
                    ">
                        📈 Tendencia: {stats['trend']} | Variabilidad: {(stats['std']/stats['mean']*100):.1f}%
                    </span>
                </div>
            </div>
            """
            
            return card_html
            
        except Exception as e:
            self.logger.error(f"Error creando tarjeta Altair para {sensor_name}: {e}")
            return ""

    def _get_sensor_unit(self, sensor_name: str) -> str:
        """Obtener unidad apropiada para el sensor"""
        sensor_lower = sensor_name.lower()
        
        if "temperature" in sensor_lower or "ntc" in sensor_lower:
            return "°C"
        elif "ldr" in sensor_lower:
            return " lux"
        elif "humidity" in sensor_lower:
            return "%"
        elif "pressure" in sensor_lower:
            return " hPa"
        else:
            return ""

    def _calculate_trend(self, values: pd.Series) -> str:
        """Calcular tendencia simple de los valores"""
        if len(values) < 2:
            return "Insuficiente"
        
        first_half = values[:len(values)//2].mean()
        second_half = values[len(values)//2:].mean()
        
        diff_percent = ((second_half - first_half) / first_half) * 100
        
        if abs(diff_percent) < 2:
            return "Estable"
        elif diff_percent > 0:
            return f"Ascendente (+{diff_percent:.1f}%)"
        else:
            return f"Descendente ({diff_percent:.1f}%)"

    async def create_summary_dashboard(self, df: pd.DataFrame) -> str:
        """Crear dashboard resumen usando Plotly con diseño moderno"""
        try:
            if df.empty:
                return ""
            
            # Preparar datos
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['numeric_value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df.dropna(subset=['numeric_value'])
            
            # Crear subplots con diseño moderno
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('📊 Distribución por Sensor', '📈 Tendencias Temporales', 
                               '🔥 Mapa de Calor por Hora', '📋 Estadísticas por Dispositivo'),
                specs=[[{"type": "bar"}, {"type": "scatter"}],
                       [{"type": "heatmap"}, {"type": "bar"}]],
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            # 1. Distribución por sensor (Box Plot moderno)
            sensors = df['sensor_type'].unique()
            for i, sensor in enumerate(sensors):
                sensor_data = df[df['sensor_type'] == sensor]
                
                fig.add_trace(go.Box(
                    y=sensor_data['numeric_value'],
                    name=sensor,
                    boxpoints='outliers',
                    marker=dict(color=self.gradient_colors[i % len(self.gradient_colors)]),
                    line=dict(width=2)
                ), row=1, col=1)
            
            # 2. Tendencias temporales agrupadas
            for i, sensor in enumerate(sensors):
                sensor_data = df[df['sensor_type'] == sensor].sort_values('timestamp')
                
                fig.add_trace(go.Scatter(
                    x=sensor_data['timestamp'],
                    y=sensor_data['numeric_value'],
                    mode='lines+markers',
                    name=f'{sensor}',
                    line=dict(width=3, color=self.gradient_colors[i % len(self.gradient_colors)]),
                    marker=dict(size=6)
                ), row=1, col=2)
            
            # 3. Mapa de calor por hora y sensor
            df['hour'] = df['timestamp'].dt.hour
            heatmap_data = df.groupby(['hour', 'sensor_type'])['numeric_value'].mean().unstack(fill_value=0)
            
            fig.add_trace(go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale='Viridis',
                showscale=True
            ), row=2, col=1)
            
            # 4. Estadísticas por dispositivo
            device_stats = df.groupby('device_id')['numeric_value'].agg(['count', 'mean']).reset_index()
            
            fig.add_trace(go.Bar(
                x=device_stats['device_id'],
                y=device_stats['count'],
                name='Registros',
                marker=dict(color='rgba(55, 126, 184, 0.8)'),
                yaxis='y4'
            ), row=2, col=2)
            
            # Configurar layout moderno
            fig.update_layout(
                height=800,
                title=dict(
                    text="🚀 Dashboard IoT - Análisis Ejecutivo",
                    x=0.5,
                    font=dict(size=24, family="Arial Black")
                ),
                template="plotly_white",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                font=dict(family="Arial, sans-serif", size=12)
            )
            
            # Convertir a base64
            img_bytes = fig.to_image(format="png", width=1200, height=800)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            self.logger.error(f"Error creando dashboard resumen: {e}")
            return ""