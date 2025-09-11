"""
Aplicación Streamlit Cloud para Remote IoT Agent con Groq
=========================================================

Aplicación web para desplegar en Streamlit Cloud usando Groq API (gratuito).
NO requiere tarjeta de crédito - solo API key gratuita de Groq.
"""

import streamlit as st
import asyncio
import os
import sys
from datetime import datetime
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar path del proyecto
sys.path.append(os.path.abspath('.'))

try:
    from modules.agents.simple_cloud_agent import create_simple_cloud_iot_agent
    from modules.agents.groq_integration import GroqIntegration
except ImportError as e:
    st.error(f"Error importando módulos: {e}")
    st.stop()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la página
st.set_page_config(
    page_title="🤖 Remote IoT Agent - Groq Cloud",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .status-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-card {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .info-card {
        background: #d1ecf1;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
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
    if 'groq_api_key' not in st.session_state:
        st.session_state.groq_api_key = os.getenv('GROQ_API_KEY', '')

async def initialize_agent(groq_api_key: str) -> bool:
    """
    Inicializar el agente IoT cloud
    
    Args:
        groq_api_key: API key de Groq
        
    Returns:
        True si la inicialización fue exitosa
    """
    try:
        # Configurar la API key en el entorno
        os.environ['GROQ_API_KEY'] = groq_api_key
        
        # Crear agente
        agent = create_simple_cloud_iot_agent()
        
        # Inicializar
        success = await agent.initialize()
        
        if success:
            st.session_state.agent = agent
            st.session_state.agent_initialized = True
            return True
        else:
            return False
            
    except Exception as e:
        logger.error(f"Error inicializando agente: {e}")
        return False

def render_header():
    """Renderizar header principal"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Remote IoT Agent</h1>
        <h3>Powered by Groq AI - Completely FREE</h3>
        <p>Análisis inteligente de sensores IoT remotos</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renderizar barra lateral"""
    with st.sidebar:
        st.markdown("## ⚙️ Configuración")
        
        # Configuración de Groq API
        st.markdown("### 🚀 Groq API (Gratuito)")
        
        groq_api_key = st.text_input(
            "API Key de Groq:",
            value=st.session_state.groq_api_key,
            type="password",
            help="Obtén tu API key gratuita en https://console.groq.com/"
        )
        
        if groq_api_key != st.session_state.groq_api_key:
            st.session_state.groq_api_key = groq_api_key
            st.session_state.agent_initialized = False
        
        # Información sobre Groq
        st.markdown("""
        <div class="info-card">
        <strong>🎉 Groq es COMPLETAMENTE GRATUITO</strong><br>
        • Sin tarjeta de crédito requerida<br>
        • 14,400 requests/día gratis<br>
        • Modelos rápidos y eficientes<br>
        • Registro en: <a href="https://console.groq.com/" target="_blank">console.groq.com</a>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón de inicialización
        if st.button("🔄 Inicializar Agente", disabled=not groq_api_key):
            with st.spinner("Inicializando agente..."):
                success = asyncio.run(initialize_agent(groq_api_key))
                
                if success:
                    st.success("✅ Agente inicializado correctamente")
                    st.rerun()
                else:
                    st.error("❌ Error inicializando agente")
        
        # Estado del agente
        st.markdown("### 📊 Estado del Sistema")
        
        if st.session_state.agent_initialized:
            st.markdown("""
            <div class="status-card">
            <strong>✅ Sistema Operativo</strong><br>
            • Groq API: Conectado<br>
            • Jetson API: Activo<br>
            • LangGraph: Funcionando
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="error-card">
            <strong>⚠️ Sistema No Inicializado</strong><br>
            Configura tu API key de Groq e inicializa el agente
            </div>
            """, unsafe_allow_html=True)
        
        # Información adicional
        st.markdown("### 📚 Información")
        with st.expander("ℹ️ Sobre esta aplicación"):
            st.markdown("""
            **Remote IoT Agent** es un sistema inteligente que:
            
            • 🔍 Analiza datos de sensores IoT remotos
            • 🤖 Usa IA para generar insights
            • 📊 Conecta con dispositivos reales via API
            • 🚀 Desplegado en Streamlit Cloud
            • 💰 100% gratuito con Groq API
            
            **Tecnologías utilizadas:**
            - LangGraph para workflows
            - Groq para IA gratuita
            - Jetson API para datos reales
            - Streamlit para interfaz web
            """)

async def process_user_query(query: str) -> dict:
    """
    Procesar consulta del usuario
    
    Args:
        query: Consulta del usuario
        
    Returns:
        Respuesta del agente
    """
    try:
        if not st.session_state.agent_initialized:
            return {
                "success": False,
                "error": "Agente no inicializado",
                "response": "Por favor inicializa el agente primero."
            }
        
        response = await st.session_state.agent.process_query(query)
        
        # El agente simple devuelve string, convertir a formato dict esperado
        return {
            "success": True,
            "response": response,
            "metadata": {
                "confidence": 85,
                "data_source": "jetson_api",
                "processing_time": "< 2s"
            }
        }
        
    except Exception as e:
        logger.error(f"Error procesando consulta: {e}")
        return {
            "success": False,
            "error": str(e),
            "response": f"Error procesando la consulta: {e}"
        }

def render_chat_interface():
    """Renderizar interfaz de chat"""
    st.markdown("## 💬 Chat con el Agente IoT")
    
    # Mostrar historial de conversación
    for i, message in enumerate(st.session_state.conversation_history):
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])
    
    # Input del usuario
    if prompt := st.chat_input("Pregunta sobre los sensores IoT..."):
        if not st.session_state.agent_initialized:
            st.error("⚠️ Por favor inicializa el agente primero en la barra lateral")
            return
        
        # Agregar mensaje del usuario al historial
        st.session_state.conversation_history.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now()
        })
        
        # Mostrar mensaje del usuario
        st.chat_message("user").write(prompt)
        
        # Procesar consulta
        with st.chat_message("assistant"):
            with st.spinner("🤖 Analizando sensores..."):
                response = asyncio.run(process_user_query(prompt))
            
            if response.get("success", False):
                response_text = response.get("response", "No se pudo generar respuesta")
                st.write(response_text)
                
                # Mostrar información adicional
                with st.expander("📊 Detalles técnicos"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Registros procesados",
                            response.get("data_summary", {}).get("total_records", 0)
                        )
                    
                    with col2:
                        st.metric(
                            "Sensores detectados",
                            len(response.get("data_summary", {}).get("sensors", []))
                        )
                    
                    with col3:
                        st.metric(
                            "Dispositivos activos",
                            len(response.get("data_summary", {}).get("devices", []))
                        )
                    
                    st.json({
                        "modelo_usado": response.get("model_used", "N/A"),
                        "estado_ejecucion": response.get("execution_status", "N/A"),
                        "verificacion": response.get("verification", {})
                    })
                
                # Agregar respuesta al historial
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now(),
                    "details": response
                })
            else:
                error_msg = f"❌ Error: {response.get('error', 'Error desconocido')}"
                st.error(error_msg)
                
                # Agregar error al historial
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": error_msg,
                    "timestamp": datetime.now()
                })

def render_examples():
    """Renderizar ejemplos de consultas"""
    st.markdown("## 💡 Ejemplos de Consultas")
    
    examples = [
        "¿Cuál es la temperatura actual de los sensores?",
        "Muestra un resumen de todos los dispositivos IoT",
        "¿Hay alguna anomalía en las lecturas?",
        "¿Cuáles son las últimas mediciones de temperatura?",
        "Analiza las tendencias de los sensores"
    ]
    
    cols = st.columns(2)
    
    for i, example in enumerate(examples):
        col = cols[i % 2]
        
        with col:
            if st.button(f"📝 {example}", key=f"example_{i}"):
                if st.session_state.agent_initialized:
                    # Simular input del usuario
                    st.session_state.conversation_history.append({
                        "role": "user",
                        "content": example,
                        "timestamp": datetime.now()
                    })
                    st.rerun()
                else:
                    st.error("⚠️ Inicializa el agente primero")

def main():
    """Función principal de la aplicación"""
    # Inicializar estado de sesión
    initialize_session_state()
    
    # Renderizar interfaz
    render_header()
    render_sidebar()
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "💡 Ejemplos", "📊 Métricas"])
    
    with tab1:
        render_chat_interface()
    
    with tab2:
        render_examples()
    
    with tab3:
        st.markdown("## 📊 Métricas del Sistema")
        
        if st.session_state.agent_initialized:
            if st.button("🔍 Verificar Estado del Sistema"):
                with st.spinner("Verificando sistema..."):
                    try:
                        health = asyncio.run(st.session_state.agent.health_check())
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            status = health.get("overall_status", "unknown")
                            color = "🟢" if status == "healthy" else "🟡" if status == "degraded" else "🔴"
                            st.metric("Estado General", f"{color} {status.title()}")
                        
                        with col2:
                            groq_status = health.get("groq_status", "unknown")
                            color = "🟢" if groq_status == "success" else "🟡"
                            st.metric("Groq API", f"{color} {groq_status.title()}")
                        
                        with col3:
                            jetson_status = health.get("jetson_status", "unknown")
                            color = "🟢" if jetson_status == "healthy" else "🟡"
                            st.metric("Jetson API", f"{color} {jetson_status.title()}")
                        
                        st.json(health)
                        
                    except Exception as e:
                        st.error(f"Error verificando sistema: {e}")
        else:
            st.info("🔧 Inicializa el agente para ver métricas del sistema")
        
        # Información de uso
        st.markdown("### 📈 Información de Uso")
        
        total_messages = len(st.session_state.conversation_history)
        user_messages = len([m for m in st.session_state.conversation_history if m["role"] == "user"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total de mensajes", total_messages)
        
        with col2:
            st.metric("Consultas del usuario", user_messages)

if __name__ == "__main__":
    main()
