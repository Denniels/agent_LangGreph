"""
Remote IoT Agent - App Simplificada para Streamlit Cloud
======================================================

Aplicación simplificada sin dependencias complejas.
"""

import streamlit as st
import asyncio
import os
import sys
from datetime import datetime

# Configurar path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import del agente simplificado
from modules.agents.simple_cloud_agent import create_simple_cloud_iot_agent

# Configuración de la página
st.set_page_config(
    page_title="🤖 Remote IoT Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .status-card {
        background: linear-gradient(90deg, #e3f2fd 0%, #f3e5f5 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado de la sesión
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'agent_initialized' not in st.session_state:
    st.session_state.agent_initialized = False

@st.cache_resource
def get_agent():
    """Obtener instancia del agente (cached)."""
    return create_simple_cloud_iot_agent()

async def initialize_agent_async():
    """Inicializar agente de forma asíncrona."""
    if st.session_state.agent is None:
        st.session_state.agent = get_agent()
    
    if not st.session_state.agent_initialized:
        success = await st.session_state.agent.initialize()
        st.session_state.agent_initialized = success
        return success
    return True

def main():
    """Función principal de la aplicación."""
    
    # Header principal
    st.markdown('<h1 class="main-header">🤖 Remote IoT Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Análisis inteligente de datos IoT con Groq AI (100% Gratuito)</p>', unsafe_allow_html=True)
    
    # Sidebar con información del sistema
    with st.sidebar:
        st.markdown("## 🔧 Estado del Sistema")
        
        # Verificar configuración
        groq_configured = bool(os.getenv('GROQ_API_KEY'))
        jetson_url = os.getenv('JETSON_API_URL', 'No configurado')
        
        if groq_configured:
            st.success("✅ Groq API Configurada")
        else:
            st.warning("⚠️ Modo Demo (Sin Groq API)")
        
        st.info(f"🌐 Jetson API: {jetson_url[:30]}...")
        
        # Métricas del sistema
        st.markdown("### 📊 Métricas")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Consultas", len(st.session_state.chat_history))
        with col2:
            st.metric("Estado", "🟢 Online")
        
        # Información del proyecto
        st.markdown("---")
        st.markdown("### ℹ️ Acerca de")
        st.markdown("""
        **Remote IoT Agent v2.0**
        - 🤖 LangGraph Workflow
        - ⚡ Groq AI (Gratuito)
        - 🌐 Jetson API Connection
        - 📊 Análisis en Tiempo Real
        """)
        
        if st.button("🔄 Reiniciar Sistema"):
            st.session_state.clear()
            st.rerun()
    
    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 💬 Chat con el Agente IoT")
        
        # Área de chat
        chat_container = st.container()
        
        # Mostrar historial de chat
        with chat_container:
            for i, (query, response, timestamp) in enumerate(st.session_state.chat_history):
                with st.chat_message("user"):
                    st.write(f"**{timestamp}**")
                    st.write(query)
                
                with st.chat_message("assistant"):
                    st.write(response)
        
        # Input para nueva consulta
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area(
                "Tu consulta sobre sensores IoT:",
                placeholder="Ejemplo: ¿Cuál es la temperatura actual de los sensores?",
                height=100,
                key="user_input"
            )
            
            col_submit, col_example = st.columns([1, 2])
            with col_submit:
                submitted = st.form_submit_button("🚀 Enviar", use_container_width=True)
            
            with col_example:
                if st.form_submit_button("💡 Consulta de Ejemplo", use_container_width=True):
                    user_input = "¿Cuál es la temperatura actual de los sensores ESP32 y Arduino?"
                    submitted = True
        
        # Procesar consulta
        if submitted and user_input.strip():
            process_query(user_input.strip())
    
    with col2:
        st.markdown("## 🎯 Ejemplos de Consultas")
        
        examples = [
            "¿Cuál es la temperatura actual?",
            "Dame estadísticas de los sensores",
            "¿Hay algún sensor con valores anómalos?",
            "Analiza las tendencias de temperatura",
            "¿Qué dispositivos están conectados?",
            "Muestra el estado de todos los sensores"
        ]
        
        for i, example in enumerate(examples):
            if st.button(f"📝 {example}", key=f"example_{i}", use_container_width=True):
                process_query(example)
        
        st.markdown("---")
        st.markdown("### 🔍 Información Técnica")
        
        st.markdown("""
        **Sensores Soportados:**
        - 🌡️ Temperatura (NTC)
        - 💡 Luminosidad (LDR)
        - 📊 Múltiples dispositivos
        
        **Dispositivos:**
        - ESP32 WiFi
        - Arduino Ethernet
        - Jetson Nano
        """)

def process_query(user_input: str):
    """Procesar consulta del usuario."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    with st.spinner("🤖 Analizando sensores IoT..."):
        try:
            # Inicializar agente si es necesario
            agent_ready = asyncio.run(initialize_agent_async())
            
            if not agent_ready:
                st.error("❌ Error inicializando agente IoT")
                return
            
            # Procesar consulta
            response = asyncio.run(st.session_state.agent.process_query(user_input))
            
            # Agregar al historial
            st.session_state.chat_history.append((user_input, response, timestamp))
            
            # Rerun para mostrar el resultado
            st.rerun()
            
        except Exception as e:
            error_msg = f"❌ Error procesando consulta: {str(e)}"
            st.session_state.chat_history.append((user_input, error_msg, timestamp))
            st.error(error_msg)
            st.rerun()

if __name__ == "__main__":
    main()
