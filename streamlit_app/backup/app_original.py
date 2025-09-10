"""
Aplicación Streamlit para el Agente IoT
=======================================

Interfaz web para interactuar con el agente conversacional IoT.
"""

import streamlit as st
import asyncio
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.agents.iot_agent import IoTAgent
from modules.agents.graph_builder import GraphBuilder
from modules.tools.database_tools import DatabaseTools
from modules.tools.analysis_tools import AnalysisTools
from modules.utils.config import Config
from modules.utils.logger import setup_logger

logger = setup_logger(__name__)

# Configuración de la página
st.set_page_config(
    page_title="Agente IoT Conversacional",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


class StreamlitApp:
    """Aplicación principal de Streamlit."""
    
    def __init__(self):
        self.iot_agent = None
        self.graph_builder = None
        self.db_tools = None
        self.analysis_tools = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Inicializa los componentes del agente."""
        try:
            # Verificar configuración
            if not Config.validate():
                st.error("❌ Configuración incompleta. Verifica las variables de entorno.")
                st.stop()
            
            # Inicializar componentes
            if 'iot_agent' not in st.session_state:
                st.session_state.iot_agent = IoTAgent()
                st.session_state.graph_builder = GraphBuilder()
                st.session_state.db_tools = DatabaseTools()
                st.session_state.analysis_tools = AnalysisTools()
            
            self.iot_agent = st.session_state.iot_agent
            self.graph_builder = st.session_state.graph_builder
            self.db_tools = st.session_state.db_tools
            self.analysis_tools = st.session_state.analysis_tools
            
        except Exception as e:
            st.error(f"❌ Error inicializando la aplicación: {e}")
            st.stop()
    
    def run(self):
        """Ejecuta la aplicación principal."""
        # Header
        st.markdown('<h1 class="main-header">🤖 Agente IoT Conversacional</h1>', 
                   unsafe_allow_html=True)
        
        # Sidebar
        self._render_sidebar()
        
        # Contenido principal
        tab1, tab2, tab3, tab4 = st.tabs([
            "💬 Chat", 
            "📊 Dashboard", 
            "🔔 Alertas", 
            "📈 Análisis"
        ])
        
        with tab1:
            self._render_chat_interface()
        
        with tab2:
            self._render_dashboard()
        
        with tab3:
            self._render_alerts()
        
        with tab4:
            self._render_analysis()
    
    def _render_sidebar(self):
        """Renderiza la barra lateral."""
        with st.sidebar:
            st.header("⚙️ Configuración")
            
            # Estado de conexión
            st.subheader("🔗 Estado del Sistema")
            
            # Verificar estado de la base de datos
            if st.button("🔄 Verificar Conexión DB"):
                try:
                    # Aquí podrías agregar una verificación real de la DB
                    st.success("✅ Base de datos conectada")
                except Exception as e:
                    st.error(f"❌ Error de conexión: {e}")
            
            st.divider()
            
            # Información del sistema
            st.subheader("📋 Información")
            st.write(f"**Aplicación:** {Config.APP_NAME}")
            st.write(f"**Versión:** {Config.APP_VERSION}")
            st.write(f"**Modelo:** {Config.OPENAI_MODEL}")
            
            st.divider()
            
            # Acciones rápidas
            st.subheader("⚡ Acciones Rápidas")
            
            if st.button("🧹 Limpiar Chat"):
                if 'messages' in st.session_state:
                    st.session_state.messages = []
                if self.iot_agent:
                    self.iot_agent.clear_history()
                st.success("Chat limpiado")
                st.rerun()
            
            if st.button("📊 Actualizar Datos"):
                st.cache_data.clear()
                st.success("Cache limpiado")
                st.rerun()
    
    def _render_chat_interface(self):
        """Renderiza la interfaz de chat."""
        st.header("💬 Conversación con el Agente IoT")
        
        # Inicializar historial de mensajes
        if 'messages' not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "¡Hola! Soy tu asistente IoT. Puedo ayudarte a consultar datos de sensores, monitorear dispositivos, gestionar alertas y analizar tendencias. ¿En qué puedo ayudarte hoy?"
                }
            ]
        
        # Mostrar historial de mensajes
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Input del usuario
        if prompt := st.chat_input("Escribe tu mensaje aquí..."):
            # Agregar mensaje del usuario
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generar respuesta del asistente
            with st.chat_message("assistant"):
                with st.spinner("Procesando tu consulta..."):
                    try:
                        # Usar el agente para procesar el mensaje
                        response = asyncio.run(self.iot_agent.process_message(prompt))
                        st.markdown(response)
                        
                        # Agregar respuesta al historial
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response}
                        )
                    except Exception as e:
                        error_msg = f"Lo siento, ocurrió un error: {e}"
                        st.error(error_msg)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": error_msg}
                        )
    
    @st.cache_data(ttl=300)  # Cache por 5 minutos
    def _get_sensor_data(_self):
        """Obtiene datos de sensores con cache."""
        try:
            return asyncio.run(_self.db_tools.get_sensor_data_tool(limit=50))
        except Exception as e:
            logger.error(f"Error obteniendo datos de sensores: {e}")
            return []
    
    @st.cache_data(ttl=300)
    def _get_devices_data(_self):
        """Obtiene datos de dispositivos con cache."""
        try:
            return asyncio.run(_self.db_tools.get_devices_tool())
        except Exception as e:
            logger.error(f"Error obteniendo dispositivos: {e}")
            return []
    
    @st.cache_data(ttl=300)
    def _get_alerts_data(_self):
        """Obtiene datos de alertas con cache."""
        try:
            return asyncio.run(_self.db_tools.get_alerts_tool())
        except Exception as e:
            logger.error(f"Error obteniendo alertas: {e}")
            return []
    
    def _render_dashboard(self):
        """Renderiza el dashboard principal."""
        st.header("📊 Dashboard del Sistema IoT")
        
        # Obtener datos
        sensor_data = self._get_sensor_data()
        devices_data = self._get_devices_data()
        alerts_data = self._get_alerts_data()
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📡 Sensores Activos",
                value=len(set(item['device_id'] for item in sensor_data)) if sensor_data else 0
            )
        
        with col2:
            st.metric(
                label="🔧 Dispositivos",
                value=len(devices_data) if devices_data else 0
            )
        
        with col3:
            st.metric(
                label="🔔 Alertas Activas",
                value=len(alerts_data) if alerts_data else 0
            )
        
        with col4:
            st.metric(
                label="📈 Lecturas Recientes",
                value=len(sensor_data) if sensor_data else 0
            )
        
        st.divider()
        
        # Gráficos
        if sensor_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Tendencias de Sensores")
                df = pd.DataFrame(sensor_data)
                
                if 'timestamp' in df.columns and 'value' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    
                    # Gráfico de líneas por tipo de sensor
                    fig = px.line(
                        df, 
                        x='timestamp', 
                        y='value',
                        color='sensor_type',
                        title="Valores de Sensores en el Tiempo"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📊 Distribución por Tipo")
                sensor_counts = df['sensor_type'].value_counts()
                
                fig = px.pie(
                    values=sensor_counts.values,
                    names=sensor_counts.index,
                    title="Distribución de Tipos de Sensores"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de sensores disponibles.")
    
    def _render_alerts(self):
        """Renderiza la sección de alertas."""
        st.header("🔔 Gestión de Alertas")
        
        alerts_data = self._get_alerts_data()
        
        if alerts_data:
            # Filtros
            col1, col2 = st.columns(2)
            
            with col1:
                severity_filter = st.selectbox(
                    "Filtrar por Severidad",
                    ["Todas"] + list(set(alert.get('severity', 'unknown') for alert in alerts_data))
                )
            
            with col2:
                device_filter = st.selectbox(
                    "Filtrar por Dispositivo",
                    ["Todos"] + list(set(alert.get('device_id', 'unknown') for alert in alerts_data))
                )
            
            # Filtrar datos
            filtered_alerts = alerts_data
            if severity_filter != "Todas":
                filtered_alerts = [a for a in filtered_alerts if a.get('severity') == severity_filter]
            if device_filter != "Todos":
                filtered_alerts = [a for a in filtered_alerts if a.get('device_id') == device_filter]
            
            # Mostrar alertas
            st.subheader(f"📋 Alertas Activas ({len(filtered_alerts)})")
            
            for alert in filtered_alerts:
                severity = alert.get('severity', 'unknown')
                color = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢',
                    'unknown': '⚪'
                }.get(severity, '⚪')
                
                with st.expander(f"{color} {alert.get('alert_type', 'Alerta')} - {alert.get('device_id', 'Unknown')}"):
                    st.write(f"**Mensaje:** {alert.get('message', 'Sin mensaje')}")
                    st.write(f"**Severidad:** {severity}")
                    st.write(f"**Creada:** {alert.get('created_at', 'Fecha desconocida')}")
                    st.write(f"**Estado:** {alert.get('status', 'unknown')}")
        else:
            st.success("🎉 No hay alertas activas en el sistema.")
    
    def _render_analysis(self):
        """Renderiza la sección de análisis."""
        st.header("📈 Análisis Avanzado")
        
        # Obtener datos
        sensor_data = self._get_sensor_data()
        alerts_data = self._get_alerts_data()
        
        if sensor_data:
            # Generar análisis
            with st.spinner("Generando análisis..."):
                trends_analysis = self.analysis_tools.analyze_sensor_trends(sensor_data)
                anomalies = self.analysis_tools.detect_anomalies(sensor_data)
                report = self.analysis_tools.generate_summary_report(sensor_data, alerts_data)
            
            # Mostrar resultados
            tab1, tab2, tab3 = st.tabs(["📊 Tendencias", "⚠️ Anomalías", "📋 Reporte"])
            
            with tab1:
                st.subheader("📊 Análisis de Tendencias")
                
                if 'by_sensor_type' in trends_analysis:
                    for sensor_type, analysis in trends_analysis['by_sensor_type'].items():
                        with st.expander(f"📡 {sensor_type.upper()}"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Promedio", f"{analysis.get('avg_value', 0):.2f}")
                            with col2:
                                st.metric("Máximo", f"{analysis.get('max_value', 0):.2f}")
                            with col3:
                                trend = analysis.get('trend', 'stable')
                                trend_emoji = {'increasing': '📈', 'decreasing': '📉', 'stable': '➡️'}.get(trend, '➡️')
                                st.metric("Tendencia", f"{trend_emoji} {trend}")
            
            with tab2:
                st.subheader("⚠️ Detección de Anomalías")
                
                if anomalies:
                    st.warning(f"Se detectaron {len(anomalies)} anomalías")
                    
                    df_anomalies = pd.DataFrame(anomalies)
                    st.dataframe(df_anomalies, use_container_width=True)
                else:
                    st.success("✅ No se detectaron anomalías en los datos recientes")
            
            with tab3:
                st.subheader("📋 Reporte del Sistema")
                
                if 'recommendations' in report:
                    st.subheader("💡 Recomendaciones")
                    for rec in report['recommendations']:
                        st.write(f"• {rec}")
                
                # Mostrar métricas del reporte
                if 'sensor_summary' in report:
                    st.subheader("📊 Resumen de Sensores")
                    st.json(report['sensor_summary'])
        else:
            st.info("No hay suficientes datos para realizar análisis.")


def main():
    """Función principal."""
    app = StreamlitApp()
    app.run()


if __name__ == "__main__":
    main()
