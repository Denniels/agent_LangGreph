"""
Remote IoT Agent - Aplicación Principal para Streamlit Cloud
==========================================================

Punto de entrada principal para el despliegue en Streamlit Cloud.
Usa Groq API (100% gratuito) para análisis inteligente de datos IoT.
"""

# Configurar el entorno antes de cualquier import
import os
import sys

# Configurar path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar variables de entorno para cloud
if not os.getenv('GROQ_API_KEY'):
    # En Streamlit Cloud, se configura en Secrets
    pass

if not os.getenv('JETSON_API_URL'):
    os.environ['JETSON_API_URL'] = 'https://dpi-opportunity-hybrid-manufacturer.trycloudflare.com'

# Ejecutar la aplicación principal
from streamlit_app.app_groq import main

if __name__ == "__main__":
    main()
