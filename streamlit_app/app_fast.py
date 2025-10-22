#!/usr/bin/env python3
"""
APLICACIÓN STREAMLIT ULTRA-OPTIMIZADA PARA CARGA RÁPIDA
=====================================================

Versión minimalista optimizada para Streamlit Cloud:
- Imports mínimos al inicio
- Carga diferida de módulos pesados
- Cache agresivo
- UI simplificada para carga rápida
"""

import streamlit as st
import os

# Configuración MÍNIMA para carga rápida
st.set_page_config(
    page_title="🤖 Agente IoT",
    page_icon="🤖",
    layout="wide"
)

# Variables de entorno
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
JETSON_API_URL = "https://replica-subscriber-permission-restricted.trycloudflare.com"

# Cache para imports pesados
@st.cache_resource
def load_modules():
    """Cargar módulos del proyecto de forma diferida"""
    import sys
    
    # Agregar path del proyecto
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.append(project_root)
    
    try:
        from modules.agents.cloud_iot_agent import CloudIoTAgent
        return CloudIoTAgent()
    except Exception as e:
        st.error(f"❌ Error cargando módulos: {str(e)}")
        return None

# Función principal simplificada
def main():
    st.title("🤖 Chat con Agente IoT")
    
    if not GROQ_API_KEY:
        st.error("❌ Configure GROQ_API_KEY en las variables de entorno")
        st.stop()
    
    # Cargar agente (cached)
    with st.spinner("🔄 Inicializando agente..."):
        agent = load_modules()
    
    if not agent:
        st.error("❌ No se pudo cargar el agente")
        st.stop()
    
    st.success("✅ Agente IoT listo!")
    
    # Inicializar historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Mostrar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input del usuario
    if prompt := st.chat_input("Escribe tu consulta sobre sensores IoT..."):
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Respuesta del agente
        with st.chat_message("assistant"):
            with st.spinner("🤖 Procesando consulta..."):
                try:
                    response = agent.process_query(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()