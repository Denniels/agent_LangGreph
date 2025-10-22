"""
🤖 AGENTE IoT REMOTO - STREAMLIT CLOUD OPTIMIZED - VERSION CORREGIDA
=================================================================

Punto de entrada PRINCIPAL para Streamlit Cloud.
Versión limpia sin errores de indentación.
"""

# Configuración CRÍTICA para Streamlit Cloud
import os
import sys

# ASEGURAR PATH CORRECTO para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# VARIABLES DE ENTORNO para Streamlit Cloud
if not os.getenv('GROQ_API_KEY'):
    print("⚠️ GROQ_API_KEY debe configurarse en Streamlit Cloud Secrets")

if not os.getenv('JETSON_API_URL'):
    os.environ['JETSON_API_URL'] = 'https://replica-subscriber-permission-restricted.trycloudflare.com'

# EJECUTAR APLICACIÓN PRINCIPAL
if __name__ == "__main__":
    try:
        # Ejecutar app optimizada desde streamlit_app
        with open('streamlit_app/app_groq_cloud.py', 'r', encoding='utf-8') as f:
            app_code = f.read()
        exec(app_code)
    except Exception as e:
        print(f"Error ejecutando app principal: {e}")
        # Fallback simple
        import streamlit as st
        st.error("Error de carga. Verifique la configuración.")