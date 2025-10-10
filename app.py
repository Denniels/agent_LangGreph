"""
🤖 AGENTE IoT REMOTO - STREAMLIT CLOUD SIMPLIFICADO
=================================================

Punto de entrada PRINCIPAL para Streamlit Cloud.
Versión SIMPLIFICADA sin complejidades innecesarias.
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
    os.environ['JETSON_API_URL'] = 'https://respect-craps-lit-aged.trycloudflare.com'

# EJECUTAR APLICACIÓN SIMPLIFICADA
if __name__ == "__main__":
    try:
        # Usar app simplificada sin semáforo complejo
        exec(open('streamlit_app/app_final_simplified.py').read())
    except Exception as e:
        print(f"Error: {e}")
        import streamlit as st
        st.error("Error de carga. Contacte al administrador.")
