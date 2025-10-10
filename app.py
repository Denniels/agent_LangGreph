"""
🤖 AGENTE IoT REMOTO - STREAMLIT CLOUD OPTIMIZED
===============================================

Punto de entrada PRINCIPAL para Streamlit Cloud.
✅ Gráficos matplotlib nativos
✅ Reportes completos  
✅ Chat IoT inteligente
✅ 100% compatible con Streamlit Cloud

🚀 GROQ API (GRATIS) + LangGraph + Jetson Nano Remoto
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
    # En Streamlit Cloud debe configurarse en Secrets
    print("⚠️ GROQ_API_KEY debe configurarse en Streamlit Cloud Secrets")

if not os.getenv('JETSON_API_URL'):
    os.environ['JETSON_API_URL'] = 'https://respect-craps-lit-aged.trycloudflare.com'

# EJECUTAR APLICACIÓN PRINCIPAL
if __name__ == "__main__":
    # Ejecutar app optimizada desde streamlit_app
    exec(open('streamlit_app/app_groq_cloud.py').read())
