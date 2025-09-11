"""
Aplicación Streamlit para Remote IoT Agent con Groq API
======================================================

Aplicación web para desplegar el agente IoT en Streamlit Cloud
usando Groq como proveedor de LLM (100% gratuito).
"""

import streamlit as st
import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar configuración para cloud
try:
    import config_cloud  # Configuración automática para Streamlit Cloud
except ImportError:
    pass  # No hay problema si no existe en desarrollo local

# Cargar variables de entorno
load_dotenv()

# Agregar path del proyecto
sys.path.append(os.path.abspath('.'))

try:
    from modules.agents.cloud_iot_agent import create_cloud_iot_agent
except ImportError as e:
    st.error(f"Error importando módulos: {e}")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="Remote IoT Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #D4F6CC;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
        margin: 1rem 0;
    }
    .metric-container {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Inicializar variables de sesión"""
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'agent_initialized' not in st.session_state:
        st.session_state.agent_initialized = False
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

async def initialize_agent():
    """Inicializar el agente IoT"""
    try:
        if st.session_state.agent is None:
            with st.spinner("🚀 Inicializando Remote IoT Agent..."):
                st.session_state.agent = create_cloud_iot_agent(
                    groq_model="llama-3.1-8b-instant"
                )
                
                # Inicializar agente
                success = await st.session_state.agent.initialize()
                
                if success:
                    st.session_state.agent_initialized = True
                    return True
                else:
                    st.error("Error inicializando el agente")
                    return False
        return st.session_state.agent_initialized
    except Exception as e:
        st.error(f"Error durante la inicialización: {e}")
        return False

async def process_query(user_input: str):
    """Procesar consulta del usuario"""
    try:
        if not st.session_state.agent_initialized:
            st.warning("El agente no está inicializado. Reinicia la aplicación.")
            return None
        
        with st.spinner("🤖 Procesando consulta..."):
            response = await st.session_state.agent.process_query(user_input)
            return response
    except Exception as e:
        st.error(f"Error procesando la consulta: {e}")
        return None

def display_response(response_data: dict):
    """Mostrar la respuesta del agente"""
    if not response_data:
        return
    
    if response_data.get('success'):
        # Respuesta principal
        st.markdown("### 🤖 Respuesta del Agente")
        st.markdown(response_data['response'])
        
        # Métricas en columnas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📊 Registros Procesados",
                value=response_data['data_summary']['total_records']
            )
        
        with col2:
            st.metric(
                label="🔧 Sensores Detectados",
                value=len(response_data['data_summary']['sensors'])
            )
        
        with col3:
            st.metric(
                label="📱 Dispositivos Activos",
                value=len(response_data['data_summary']['devices'])
            )
        
        with col4:
            verification = response_data.get('verification', {})
            confidence = verification.get('confidence', 0) * 100
            st.metric(
                label="✅ Confianza",
                value=f"{confidence:.0f}%"
            )
        
        # Detalles técnicos en expander
        with st.expander("🔍 Detalles Técnicos"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Datos del Sistema:**")
                st.json({
                    "modelo_usado": response_data.get('model_used'),
                    "status_ejecucion": response_data.get('execution_status'),
                    "timestamp": response_data.get('timestamp')
                })
            
            with col2:
                st.markdown("**Sensores Detectados:**")
                sensors = response_data['data_summary']['sensors']
                for sensor in sensors:
                    st.markdown(f"• {sensor}")
                
                st.markdown("**Dispositivos:**")
                devices = response_data['data_summary']['devices']
                for device in devices:
                    st.markdown(f"• {device}")
    else:
        st.error(f"❌ Error: {response_data.get('error', 'Error desconocido')}")

def display_sidebar():
    """Mostrar información en la barra lateral"""
    with st.sidebar:
        st.markdown("## ⚙️ Configuración")
        
        # Estado del sistema
        st.markdown("### 🔍 Estado del Sistema")
        
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key:
            st.success(f"✅ Groq API: Configurada")
        else:
            st.warning("⚠️ Groq API: Modo fallback")
        
        jetson_url = os.getenv('JETSON_API_URL', 'Default')
        st.info(f"📡 Jetson API: {jetson_url[:30]}...")
        
        if st.session_state.agent_initialized:
            st.success("🤖 Agente: Inicializado")
        else:
            st.warning("🤖 Agente: No inicializado")
        
        # Información del proyecto
        st.markdown("### 📋 Información")
        st.markdown("""
        **Remote IoT Agent**
        - 🔗 Conecta con sensores reales via Jetson API
        - 🤖 Usa Groq API (100% gratuito)
        - 📊 Análisis inteligente de datos IoT
        - ✅ Verificación anti-alucinaciones
        """)
        
        # Ejemplos de consultas
        st.markdown("### 💡 Consultas de Ejemplo")
        example_queries = [
            "¿Cuál es la temperatura actual?",
            "Dame un resumen de todos los sensores",
            "¿Hay valores anormales?",
            "Muestra los últimos datos de temperatura",
            "Estado de los dispositivos conectados"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{hash(query)}"):
                st.session_state.selected_query = query

async def display_health_status():
    """Mostrar estado de salud del sistema"""
    if st.session_state.agent and st.session_state.agent_initialized:
        try:
            health = await st.session_state.agent.health_check()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status = health.get('overall_status', 'unknown')
                if status == 'healthy':
                    st.success(f"🟢 Sistema: {status.title()}")
                else:
                    st.warning(f"🟡 Sistema: {status.title()}")
            
            with col2:
                groq_status = health.get('groq_status', 'unknown')
                if groq_status == 'success':
                    st.success(f"🤖 Groq: Activo")
                else:
                    st.info(f"🤖 Groq: Fallback")
            
            with col3:
                jetson_status = health.get('jetson_status', 'unknown')
                if jetson_status == 'healthy':
                    st.success(f"📡 Jetson: Conectado")
                else:
                    st.info(f"📡 Jetson: Demo")
                    
        except Exception as e:
            st.error(f"Error verificando estado: {e}")

def main():
    """Función principal de la aplicación"""
    initialize_session_state()
    
    # Header principal
    st.markdown('<h1 class="main-header">🤖 Remote IoT Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Agente inteligente para análisis de datos IoT en tiempo real</p>', unsafe_allow_html=True)
    
    # Sidebar
    display_sidebar()
    
    # Inicialización del agente
    if not st.session_state.agent_initialized:
        st.markdown('<div class="info-box">🚀 <strong>Inicializando sistema...</strong> El agente se está configurando para conectar con los sensores remotos.</div>', unsafe_allow_html=True)
        
        # Inicializar agente de forma asíncrona
        if asyncio.run(initialize_agent()):
            st.markdown('<div class="success-box">✅ <strong>Sistema inicializado correctamente!</strong> Ya puedes hacer consultas sobre los datos de sensores.</div>', unsafe_allow_html=True)
            st.rerun()
        else:
            st.error("❌ Error inicializando el sistema. Verifica la configuración.")
            st.stop()
    
    # Estado del sistema
    st.markdown("### 📊 Estado del Sistema")
    asyncio.run(display_health_status())
    
    # Interfaz de consulta
    st.markdown("### 💬 Consulta al Agente")
    
    # Manejar consulta desde sidebar
    user_input = ""
    if 'selected_query' in st.session_state:
        user_input = st.session_state.selected_query
        del st.session_state.selected_query
    
    # Input de consulta
    user_query = st.text_input(
        "Escribe tu consulta sobre los sensores IoT:",
        value=user_input,
        placeholder="Ej: ¿Cuál es la temperatura actual de los sensores?"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        submit_button = st.button("🚀 Consultar", type="primary")
    
    with col2:
        clear_button = st.button("🗑️ Limpiar Historial")
    
    if clear_button:
        st.session_state.conversation_history = []
        st.rerun()
    
    # Procesar consulta
    if submit_button and user_query:
        # Agregar consulta al historial
        st.session_state.conversation_history.append({
            "tipo": "usuario",
            "mensaje": user_query,
            "timestamp": datetime.now()
        })
        
        # Procesar consulta
        response = asyncio.run(process_query(user_query))
        
        if response:
            # Agregar respuesta al historial
            st.session_state.conversation_history.append({
                "tipo": "agente",
                "respuesta": response,
                "timestamp": datetime.now()
            })
    
    # Mostrar historial de conversación
    if st.session_state.conversation_history:
        st.markdown("### 📝 Historial de Conversación")
        
        for i, entry in enumerate(reversed(st.session_state.conversation_history[-10:])):  # Últimas 10
            if entry["tipo"] == "usuario":
                st.markdown(f"**🧑 Usuario ({entry['timestamp'].strftime('%H:%M:%S')}):**")
                st.markdown(f"> {entry['mensaje']}")
                
            elif entry["tipo"] == "agente":
                st.markdown(f"**🤖 Agente ({entry['timestamp'].strftime('%H:%M:%S')}):**")
                display_response(entry["respuesta"])
                
            st.markdown("---")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Error en la aplicación: {e}")
        st.markdown("**🔧 Solución:** Verifica que todas las dependencias estén instaladas y la configuración sea correcta.")
