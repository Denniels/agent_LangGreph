# Configuración para Streamlit Cloud
# ===================================

# Variables de entorno requeridas:
# GROQ_API_KEY=tu_nueva_api_key_aqui
# JETSON_API_URL=https://dependent-discussions-venice-filling.trycloudflare.com

# Configuración automática para cloud
import os

# Configurar automáticamente las variables si no están presentes
if not os.getenv('GROQ_API_KEY'):
    # En producción, estas se configuran en Streamlit Cloud Secrets
    # Para desarrollo local, usar .env
    pass

if not os.getenv('JETSON_API_URL'):
    os.environ['JETSON_API_URL'] = 'https://dependent-discussions-venice-filling.trycloudflare.com'

# Configuración de logging para cloud
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
