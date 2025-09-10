"""
Aplicación Streamlit para el Agente IoT Conversacional con Ollama
================================================================

Interfaz web para interactuar con el agente IoT usando Ollama como modelo de lenguaje.
"""

import streamlit as st
import asyncio
import json
import threading
from datetime import datetime
import sys
from pathlib import Path

# Configurar event loop para Streamlit
import nest_asyncio
nest_asyncio.apply()

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.agents.iot_agent_ollama import IoTAgent
from modules.utils.logger import logger


# Configuración de la página
st.set_page_config(
    page_title="🤖 Agente IoT Conversacional",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .status-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
    }
    
    .status-healthy {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
    
    .status-error {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_agent():
    """Inicializa el agente IoT."""
    try:
        agent = IoTAgent()
        logger.info("Agente IoT inicializado exitosamente")
        return agent
    except Exception as e:
        logger.error(f"Error al inicializar agente: {e}")
        st.error(f"Error al inicializar agente: {e}")
        return None


def display_header():
    """Muestra el encabezado principal."""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Agente IoT Conversacional</h1>
        <p>Asistente inteligente para monitoreo y análisis de sistemas IoT</p>
        <small>Powered by Ollama + PostgreSQL</small>
    </div>
    """, unsafe_allow_html=True)


async def test_agent_health(agent):
    """Prueba la salud del agente."""
    if agent:
        return await agent.test_system_health()
    return {"overall_status": "error", "error": "Agente no inicializado"}


def display_system_status(agent):
    """Muestra el estado del sistema en la barra lateral."""
    with st.sidebar:
        st.header("🔧 Estado del Sistema")
        
        # Ejecutar prueba de salud
        health_report = asyncio.run(test_agent_health(agent))
        
        # Estado general
        if health_report["overall_status"] == "healthy":
            st.markdown("""
            <div class="status-card status-healthy">
                <strong>✅ Sistema Saludable</strong><br>
                Todos los componentes funcionando correctamente
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-card status-error">
                <strong>❌ Sistema con Problemas</strong><br>
                Algunos componentes requieren atención
            </div>
            """, unsafe_allow_html=True)
        
        # Detalles de componentes
        if "components" in health_report:
            st.subheader("Componentes")
            
            for component, status in health_report["components"].items():
                status_icon = "✅" if status["status"] == "healthy" else "❌"
                st.write(f"{status_icon} **{component.title()}**: {status['status']}")
                
                if "model" in status:
                    st.write(f"   📦 Modelo: {status['model']}")
                if "error" in status:
                    st.write(f"   ⚠️ Error: {status['error']}")
        
        # Información del agente
        if agent:
            summary = agent.get_conversation_summary()
            st.subheader("📊 Estadísticas")
            st.write(f"**Intercambios**: {summary['model_info']['total_exchanges']}")
            st.write(f"**Modelo**: {summary['model_info']['model_used']}")
            st.write(f"**Estado**: {summary['agent_status']}")


def display_conversation_history():
    """Muestra el historial de conversación."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Mostrar mensajes
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 Usuario:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 Asistente:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)


async def process_user_input(agent, user_input):
    """Procesa la entrada del usuario."""
    if agent and user_input:
        try:
            # Mostrar spinner mientras se procesa
            with st.spinner("🤔 Procesando tu consulta..."):
                response = await agent.process_message(user_input)
            
            # Agregar mensajes al historial
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            error_msg = f"❌ Error al procesar la consulta: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            return error_msg
    
    return None


def main():
    """Función principal de la aplicación."""
    # Mostrar encabezado
    display_header()
    
    # Inicializar agente
    agent = initialize_agent()
    
    # Crear columnas para el layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Conversación")
        
        # Mostrar historial de conversación
        display_conversation_history()
        
        # Input del usuario
        user_input = st.chat_input("Escribe tu consulta sobre el sistema IoT...")
        
        if user_input:
            # Procesar entrada del usuario
            response = asyncio.run(process_user_input(agent, user_input))
            
            # Rerun para actualizar la interfaz
            st.rerun()
    
    with col2:
        # Estado del sistema
        display_system_status(agent)
        
        # Botones de acción
        st.header("🎛️ Controles")
        
        if st.button("🗑️ Limpiar Conversación"):
            if agent:
                agent.clear_conversation_history()
            st.session_state.messages = []
            st.success("Conversación limpiada")
            st.rerun()
        
        if st.button("🔄 Actualizar Estado"):
            st.rerun()
        
        # Consultas de ejemplo
        st.subheader("💡 Consultas de Ejemplo")
        
        example_queries = [
            "¿Cuál es el estado actual de los sensores?",
            "Muéstrame los datos de temperatura recientes",
            "¿Hay alguna alerta activa en el sistema?",
            "Analiza las tendencias de los sensores",
            "¿Qué dispositivos están conectados?",
            "Genera un reporte del sistema"
        ]
        
        for query in example_queries:
            if st.button(f"📝 {query}", key=f"example_{hash(query)}"):
                # Procesar consulta de ejemplo
                response = asyncio.run(process_user_input(agent, query))
                st.rerun()
    
    # Información adicional en el pie
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🌡️ **Sensores Monitoreados**\nTemperatura, Humedad, Luz, Conectividad")
    
    with col2:
        st.info("📱 **Dispositivos IoT**\nESP32, Arduino, Dispositivos de Red")
    
    with col3:
        st.info("🔍 **Capacidades IA**\nAnálisis, Detección de Anomalías, Reportes")


if __name__ == "__main__":
    main()
