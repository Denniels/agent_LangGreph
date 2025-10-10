"""
Streamlit App para Cloud IoT Agent con HuggingFace
=================================================

Aplicación web optimizada para despliegue en Streamlit Cloud.
"""

import streamlit as st
import asyncio
import os
import logging
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any, List

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Imports del proyecto
try:
    from modules.agents.cloud_iot_agent import CloudIoTAgent
    from modules.tools.jetson_api_connector import JetsonAPIConnector
except ImportError as e:
    st.error(f"Error importando módulos: {e}")
    st.info("Asegúrate de que todos los módulos estén disponibles en el entorno cloud.")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="🌐 Cloud IoT Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .status-healthy {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    
    .chat-message {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    .response-message {
        background: #e7f3ff;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #007bff;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitCloudApp:
    """Aplicación Streamlit para Cloud IoT Agent."""
    
    def __init__(self):
        """Inicializar la aplicación."""
        self.agent = None
        self.jetson_connector = None
        self.session_initialized = False
        
        # Configurar session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'agent_initialized' not in st.session_state:
            st.session_state.agent_initialized = False
        if 'health_status' not in st.session_state:
            st.session_state.health_status = {}
        if 'last_data' not in st.session_state:
            st.session_state.last_data = []
    
    def check_environment(self) -> Dict[str, Any]:
        """
        Verificar variables de entorno necesarias.
        
        Returns:
            Dict con el estado de las variables
        """
        env_status = {
            "huggingface_token": bool(os.getenv("HUGGINGFACE_API_TOKEN")),
            "jetson_url": bool(os.getenv("JETSON_API_URL")),
            "all_ready": False
        }
        
        env_status["all_ready"] = env_status["huggingface_token"]
        
        return env_status
    
    def render_header(self):
        """Renderizar header de la aplicación."""
        st.markdown("""
        <div class="main-header">
            <h1>🌐 Cloud IoT Agent</h1>
            <p>Agente IoT inteligente con HuggingFace | Desplegado en Streamlit Cloud</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Renderizar sidebar con configuración y estado."""
        with st.sidebar:
            st.header("⚙️ Configuración")
            
            # Verificar entorno
            env_status = self.check_environment()
            
            st.subheader("🔐 Variables de Entorno")
            
            # HuggingFace Token
            if env_status["huggingface_token"]:
                st.success("✅ HUGGINGFACE_API_TOKEN configurado")
            else:
                st.error("❌ HUGGINGFACE_API_TOKEN faltante")
                st.info("Configura tu token de HuggingFace en Streamlit Cloud Secrets")
            
            # Jetson URL
            jetson_url = os.getenv("JETSON_API_URL", "https://respect-craps-lit-aged.trycloudflare.com")
            st.info(f"🔗 Jetson API: {jetson_url}")
            
            # Modelo de HuggingFace
            st.subheader("🤖 Configuración del Modelo")
            
            model_options = [
                "microsoft/DialoGPT-large",
                "microsoft/DialoGPT-medium",
                "facebook/blenderbot-400M-distill",
                "microsoft/GODEL-v1_1-base-seq2seq"
            ]
            
            selected_model = st.selectbox(
                "Modelo HuggingFace:",
                model_options,
                index=0,
                help="Selecciona el modelo de HuggingFace para generar respuestas"
            )
            
            # Botón de inicialización
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🚀 Inicializar Agente", disabled=not env_status["huggingface_token"]):
                    if not env_status["huggingface_token"]:
                        st.error("Token de HuggingFace requerido")
                    else:
                        with st.spinner("Inicializando agente..."):
                            success = asyncio.run(self.initialize_agent(selected_model))
                            if success:
                                st.session_state.agent_initialized = True
                                st.success("✅ Agente inicializado")
                            else:
                                st.error("❌ Error inicializando agente")
            
            with col2:
                if st.button("🔄 Health Check"):
                    if self.agent:
                        with st.spinner("Verificando estado..."):
                            health = asyncio.run(self.agent.health_check())
                            st.session_state.health_status = health
                            st.rerun()
            
            # Estado del agente
            st.subheader("📊 Estado del Sistema")
            
            if st.session_state.health_status:
                health = st.session_state.health_status
                
                overall_status = health.get("overall_status", "unknown")
                if overall_status == "healthy":
                    st.markdown('<p class="status-healthy">🟢 Sistema Saludable</p>', unsafe_allow_html=True)
                elif overall_status == "degraded":
                    st.markdown('<p class="status-warning">🟡 Sistema Degradado</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p class="status-error">🔴 Sistema con Errores</p>', unsafe_allow_html=True)
                
                # Detalles de componentes
                st.caption("**Componentes:**")
                
                # HuggingFace
                hf_status = health.get("huggingface_status", "unknown")
                hf_icon = "🟢" if hf_status == "success" else "🔴"
                st.caption(f"{hf_icon} HuggingFace: {hf_status}")
                
                # Jetson
                jetson_status = health.get("jetson_status", "unknown")
                jetson_icon = "🟢" if jetson_status == "healthy" else "🟡" if jetson_status == "not_configured" else "🔴"
                st.caption(f"{jetson_icon} Jetson API: {jetson_status}")
            
            # Información adicional
            st.subheader("ℹ️ Información")
            st.info("""
            **Cloud IoT Agent** usa:
            - 🤖 HuggingFace para generación de respuestas
            - 📡 Jetson API para datos IoT en tiempo real
            - 🧠 LangGraph para flujo de procesamiento
            - ☁️ Streamlit Cloud para despliegue
            """)
    
    async def initialize_agent(self, model_name: str) -> bool:
        """
        Inicializar el agente de forma asíncrona.
        
        Args:
            model_name: Nombre del modelo de HuggingFace
            
        Returns:
            True si la inicialización fue exitosa
        """
        try:
            self.agent = CloudIoTAgent(huggingface_model=model_name)
            success = await self.agent.initialize()
            
            if success:
                # Obtener estado inicial
                health = await self.agent.health_check()
                st.session_state.health_status = health
            
            return success
            
        except Exception as e:
            logger.error(f"Error inicializando agente: {e}")
            st.error(f"Error: {e}")
            return False
    
    def render_chat_interface(self):
        """Renderizar interfaz de chat."""
        st.header("💬 Chat con IoT Agent")
        
        if not st.session_state.agent_initialized:
            st.warning("⚠️ Inicializa el agente en la barra lateral antes de consultar")
            return
        
        # Mostrar historial de chat
        if st.session_state.chat_history:
            st.subheader("📝 Historial de Conversación")
            
            for i, exchange in enumerate(st.session_state.chat_history):
                # Mensaje del usuario
                st.markdown(f"""
                <div class="chat-message">
                    <strong>👤 Usuario:</strong><br>
                    {exchange['user_message']}
                    <br><small>🕐 {exchange['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Respuesta del agente
                st.markdown(f"""
                <div class="response-message">
                    <strong>🤖 Agente:</strong><br>
                    {exchange['agent_response']}
                    <br><small>🤖 {exchange.get('model_used', 'Unknown')} | ⏱️ {exchange.get('response_time', 'N/A')}s</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar gráficos si existen
                if exchange.get('chart_base64_list'):
                    st.markdown("**📊 Gráficos Generados:**")
                    chart_list = exchange['chart_base64_list']
                    
                    # Mostrar cada gráfico
                    for idx, chart_base64 in enumerate(chart_list):
                        if chart_base64:  # Verificar que no sea None o vacío
                            try:
                                import base64
                                from io import BytesIO
                                
                                # Convertir base64 a imagen para Streamlit
                                chart_data = base64.b64decode(chart_base64)
                                st.image(chart_data, caption=f"Gráfico {idx + 1}", use_column_width=True)
                                
                            except Exception as e:
                                st.error(f"Error mostrando gráfico {idx + 1}: {str(e)}")
                
                # Métricas de la respuesta
                if exchange.get('data_summary'):
                    data_summary = exchange['data_summary']
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("📊 Registros", data_summary.get('total_records', 0))
                    with col2:
                        st.metric("🔌 Dispositivos", len(data_summary.get('devices', [])))
                    with col3:
                        st.metric("📡 Sensores", len(data_summary.get('sensors', [])))
                
                st.divider()
        
        # Nueva consulta
        st.subheader("✨ Nueva Consulta")
        
        # Sugerencias de consultas
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_input = st.text_input(
                "Escribe tu consulta sobre sensores IoT:",
                placeholder="Ej: ¿Cuál es la temperatura actual?",
                key="user_input"
            )
        
        with col2:
            st.caption("💡 **Sugerencias:**")
            suggestions = [
                "¿Cuál es la temperatura actual?",
                "Muestra datos de todos los sensores",
                "¿Qué dispositivos están activos?",
                "Análisis de temperaturas recientes"
            ]
            
            for suggestion in suggestions:
                if st.button(suggestion, key=f"sug_{hash(suggestion)}", help="Click para usar esta consulta"):
                    st.session_state.user_input = suggestion
                    st.rerun()
        
        # Botón de envío
        if st.button("🚀 Consultar Agente", disabled=not user_input):
            if user_input:
                self.process_user_query(user_input)
    
    def process_user_query(self, user_query: str):
        """
        Procesar consulta del usuario.
        
        Args:
            user_query: Consulta del usuario
        """
        try:
            with st.spinner("🤖 Procesando consulta con Cloud IoT Agent..."):
                # Medir tiempo de respuesta
                start_time = datetime.now()
                
                # Procesar consulta
                response = asyncio.run(self.agent.process_query(user_query))
                
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                # Guardar en historial
                chat_entry = {
                    "user_message": user_query,
                    "agent_response": response.get("response", "No se pudo generar respuesta"),
                    "timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "response_time": round(response_time, 2),
                    "model_used": response.get("model_used", "Unknown"),
                    "data_summary": response.get("data_summary", {}),
                    "verification": response.get("verification", {}),
                    "success": response.get("success", False),
                    "chart_base64_list": response.get("chart_base64_list", [])  # Gráficos base64
                }
                
                st.session_state.chat_history.append(chat_entry)
                
                # Actualizar datos
                if response.get("success") and response.get("data_summary"):
                    st.session_state.last_data = response.get("data_summary", {})
                
                # Limpiar input
                st.session_state.user_input = ""
                
                # Recargar página para mostrar respuesta
                st.rerun()
                
        except Exception as e:
            logger.error(f"Error procesando consulta: {e}")
            st.error(f"Error procesando la consulta: {e}")
    
    def render_data_dashboard(self):
        """Renderizar dashboard de datos."""
        st.header("📊 Dashboard de Datos IoT")
        
        if not st.session_state.last_data:
            st.info("💡 Realiza una consulta para ver datos en el dashboard")
            return
        
        data_summary = st.session_state.last_data
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📊 Total Registros",
                data_summary.get('total_records', 0),
                help="Número total de registros procesados"
            )
        
        with col2:
            devices = data_summary.get('devices', [])
            st.metric(
                "🔌 Dispositivos",
                len(devices),
                help=f"Dispositivos: {', '.join(devices)}"
            )
        
        with col3:
            sensors = data_summary.get('sensors', [])
            st.metric(
                "📡 Tipos de Sensores",
                len(sensors),
                help=f"Sensores: {', '.join(sensors)}"
            )
        
        with col4:
            last_update = datetime.now().strftime("%H:%M:%S")
            st.metric(
                "🕐 Última Actualización",
                last_update,
                help="Hora de la última consulta procesada"
            )
        
        # Gráficos (datos demo si no hay reales)
        if data_summary.get('total_records', 0) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Distribución por Dispositivo")
                
                # Crear gráfico de pie para dispositivos
                devices = data_summary.get('devices', [])
                if devices:
                    device_counts = {device: 1 for device in devices}  # Demo data
                    
                    fig_pie = px.pie(
                        values=list(device_counts.values()),
                        names=list(device_counts.keys()),
                        title="Distribución de Dispositivos"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.subheader("🌡️ Tipos de Sensores")
                
                # Crear gráfico de barras para sensores
                sensors = data_summary.get('sensors', [])
                if sensors:
                    sensor_counts = {sensor: 1 for sensor in sensors}  # Demo data
                    
                    fig_bar = px.bar(
                        x=list(sensor_counts.keys()),
                        y=list(sensor_counts.values()),
                        title="Distribución de Tipos de Sensores",
                        labels={'x': 'Tipo de Sensor', 'y': 'Cantidad'}
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
        
        # Información adicional
        st.subheader("ℹ️ Información Técnica")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **Fuente de Datos:**
            - 📡 API remota de Jetson Nano
            - 🌐 Cloudflare tunnel
            - 🔄 Tiempo real
            """)
        
        with col2:
            st.info("""
            **Procesamiento:**
            - 🤖 HuggingFace AI
            - 🧠 LangGraph workflow
            - ✅ Verificación de calidad
            """)
    
    def render_settings(self):
        """Renderizar página de configuración."""
        st.header("⚙️ Configuración Avanzada")
        
        # Configuración de modelo
        st.subheader("🤖 Configuración del Modelo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input(
                "Token HuggingFace:",
                value="●●●●●●●●" if os.getenv("HUGGINGFACE_API_TOKEN") else "",
                disabled=True,
                help="Configurado en Streamlit Cloud Secrets"
            )
        
        with col2:
            current_model = "microsoft/DialoGPT-large"  # Default
            st.text_input(
                "Modelo actual:",
                value=current_model,
                disabled=True,
                help="Modelo de HuggingFace en uso"
            )
        
        # Configuración de conexión
        st.subheader("🔗 Configuración de Conexión")
        
        jetson_url = os.getenv("JETSON_API_URL", "https://respect-craps-lit-aged.trycloudflare.com")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input(
                "URL de Jetson API:",
                value=jetson_url,
                disabled=True,
                help="URL de la API remota de Jetson"
            )
        
        with col2:
            timeout = st.number_input(
                "Timeout (segundos):",
                min_value=10,
                max_value=120,
                value=30,
                help="Tiempo límite para conexiones"
            )
        
        # Configuración de chat
        st.subheader("💬 Configuración de Chat")
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_history = st.number_input(
                "Máximo historial:",
                min_value=5,
                max_value=50,
                value=20,
                help="Número máximo de intercambios en historial"
            )
        
        with col2:
            max_tokens = st.number_input(
                "Máximo tokens:",
                min_value=100,
                max_value=1000,
                value=512,
                help="Número máximo de tokens por respuesta"
            )
        
        # Acciones
        st.subheader("🔧 Acciones del Sistema")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Limpiar Historial"):
                st.session_state.chat_history = []
                st.success("Historial limpiado")
                st.rerun()
        
        with col2:
            if st.button("🔄 Reiniciar Agente"):
                st.session_state.agent_initialized = False
                st.session_state.health_status = {}
                self.agent = None
                st.success("Agente reiniciado")
                st.rerun()
        
        with col3:
            if st.button("📥 Exportar Logs"):
                if st.session_state.chat_history:
                    # Crear CSV con historial
                    import pandas as pd
                    
                    df = pd.DataFrame(st.session_state.chat_history)
                    csv = df.to_csv(index=False)
                    
                    st.download_button(
                        label="📥 Descargar CSV",
                        data=csv,
                        file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No hay historial para exportar")
    
    def run(self):
        """Ejecutar la aplicación principal."""
        # Header
        self.render_header()
        
        # Sidebar
        self.render_sidebar()
        
        # Navegación por tabs
        tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Dashboard", "⚙️ Configuración"])
        
        with tab1:
            self.render_chat_interface()
        
        with tab2:
            self.render_data_dashboard()
        
        with tab3:
            self.render_settings()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem;">
            🌐 <strong>Cloud IoT Agent</strong> | 
            Powered by <strong>HuggingFace</strong> & <strong>Streamlit Cloud</strong> | 
            Real-time IoT Data Analysis
        </div>
        """, unsafe_allow_html=True)


# Función principal
def main():
    """Función principal de la aplicación."""
    try:
        app = StreamlitCloudApp()
        app.run()
    except Exception as e:
        st.error(f"Error crítico en la aplicación: {e}")
        logger.error(f"Error crítico: {e}")


if __name__ == "__main__":
    main()
