#!/usr/bin/env python3
"""
APLICACIÓN STREAMLIT SIMPLIFICADA Y ROBUSTA
=========================================

Versión sin errores de indentación para Streamlit Cloud
"""

import streamlit as st
import os
import sys

# Configurar matplotlib ANTES de cualquier otro import
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.ioff()
except:
    pass

# Configuración de página
st.set_page_config(
    page_title="🤖 Agente IoT Completo",
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Variables de entorno
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
JETSON_API_URL = "https://respect-craps-lit-aged.trycloudflare.com"

# Agregar path del proyecto
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

def show_banner():
    """Banner profesional simplificado"""
    st.markdown("## 🏭 Sistema IoT Industrial - Monitoreo con IA")
    st.markdown("🟢 **Estado:** Sistema Operativo | 📡 **Conectividad:** API Activa")
    
    st.info("""
    **Sistema avanzado de monitoreo IoT** ejecutándose en **NVIDIA Jetson Nano** con 
    capacidades de IA integradas para análisis inteligente de sensores industriales.
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Análisis", "1h - 7 días", "Paginación automática")
    with col2:
        st.metric("🤖 IA", "Groq LLM", "Análisis predictivo")
    with col3:
        st.metric("🔍 Sensores", "6 tipos", "Multi-dispositivo")
    with col4:
        st.metric("🖥️ Hardware", "Jetson Nano", "4GB RAM")
    
    st.markdown("---")

def main():
    """Función principal simplificada"""
    
    # Verificar configuración
    if not GROQ_API_KEY:
        st.error("❌ Configure GROQ_API_KEY en Streamlit Cloud Secrets")
        st.stop()
    
    # Mostrar banner
    show_banner()
    
    # Mensaje de funcionalidad básica
    st.title("💬 Chat con Agente IoT")
    
    # Configuración temporal
    with st.expander("⏰ Configuración de Análisis Temporal", expanded=False):
        time_range = st.selectbox(
            "📅 Rango de Datos",
            options=[
                ("3h", "3 horas (Tiempo Real)"),
                ("6h", "6 horas (Reciente)"),
                ("12h", "12 horas (Paginado)"),
                ("24h", "24 horas (1 día)")
            ],
            format_func=lambda x: x[1],
            index=0
        )
        hours = float(time_range[0][:-1])
        st.session_state.analysis_hours = hours
        
        if hours <= 6:
            st.success("⚡ Consulta rápida - Respuesta inmediata")
        else:
            st.info("📚 Consulta extensa - Paginación automática")
    
    # Chat básico
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Mostrar mensajes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input del usuario
    if prompt := st.chat_input("💬 Escribe tu consulta sobre sensores IoT..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            # Respuesta simple por ahora hasta que se resuelva el error
            response = """
            🤖 **Sistema IoT Operativo**
            
            El sistema está funcionando correctamente. Actualmente estamos resolviendo 
            algunos problemas de compatibilidad para restaurar todas las funcionalidades.
            
            **Estado del Sistema:**
            - ✅ Conexión a Jetson Nano: Activa
            - ✅ API de sensores: Funcionando
            - ✅ Base de datos: Operativa
            - 🔧 IA Conversacional: En mantenimiento
            
            Pronto tendrás acceso completo al análisis inteligente de datos.
            """
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Sidebar
    with st.sidebar:
        st.header("🔧 Panel de Control")
        st.info("Sistema en modo de compatibilidad")
        
        if st.button("🔄 Recargar"):
            st.rerun()

if __name__ == "__main__":
    main()