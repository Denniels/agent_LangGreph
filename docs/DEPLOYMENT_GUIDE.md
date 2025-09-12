# 🚀 Guía de Despliegue en Streamlit Cloud

## 📋 Resumen
Esta guía te ayudará a desplegar el **Remote IoT Agent** en Streamlit Cloud usando la API gratuita de Groq.

## ⚡ Requisitos Previos
- ✅ Cuenta de GitHub
- ✅ Cuenta de Streamlit Cloud (gratuita): [share.streamlit.io](https://share.streamlit.io)
- ✅ API Key de Groq (100% gratuita): [console.groq.com](https://console.groq.com)

## 🔑 Configuración de API Keys

### 1. Obtener API Key de Groq (GRATIS)
1. Ve a: https://console.groq.com/
2. Regístrate con tu email (NO requiere tarjeta de crédito)
3. Ve a "API Keys" en el menú
4. Crea una nueva API key
5. Copia la clave (formato: `gsk_xxxxxxxxxx`)

### 2. Configurar Secrets en Streamlit Cloud

En la configuración de tu app en Streamlit Cloud, ve a **"Advanced settings"** → **"Secrets"** y pega lo siguiente:

```toml
# OBLIGATORIO: API Key de Groq (100% gratuita)
GROQ_API_KEY = "tu_nueva_api_key_de_groq_aqui"

# OPCIONAL: URL de la API Jetson (usa default si no se especifica)
JETSON_API_URL = "https://dpi-opportunity-hybrid-manufacturer.trycloudflare.com"

# OPCIONAL: Configuraciones adicionales
ENVIRONMENT = "production"
DEBUG_MODE = false
LOG_LEVEL = "INFO"
```

> ⚠️ **IMPORTANTE**: Reemplaza `tu_nueva_api_key_de_groq_aqui` con tu API key real de Groq.

## 🛠️ Configuración del Deployment

### Datos para Streamlit Cloud:
- **Repository**: `Denniels/agent_LangGreph`
- **Branch**: `main`
- **Main file path**: `app.py`
- **Python version**: `3.11` (recomendado)

### Archivos Clave:
- 📄 `app.py` - Punto de entrada principal
- 📄 `streamlit_app/app_groq_cloud.py` - Aplicación optimizada para cloud
- 📄 `requirements.txt` - Dependencias (incluye groq==0.31.1)
- 📄 `.streamlit/config.toml` - Configuración de Streamlit

## 🔒 Seguridad y Secrets

### ⚠️ NUNCA subas al repositorio:
- ❌ `.env` (variables de entorno locales)
- ❌ `.streamlit/secrets.toml` (secrets locales)
- ❌ API keys o tokens en código
- ❌ Credenciales de base de datos

### ✅ Solo configura secrets en:
- 🔐 Streamlit Cloud → Advanced Settings → Secrets
- 🔐 Variables de entorno del sistema local

## 📦 Dependencias Incluidas

El `requirements.txt` incluye todas las dependencias necesarias:

```pip
# Core LangGraph y Streamlit
langgraph==0.0.69
streamlit==1.35.0
langchain==0.1.20

# Groq API (100% gratuita)
groq==0.31.1

# Utilidades
python-dotenv==1.0.1
requests==2.31.0
httpx==0.27.0
pandas==2.2.2
plotly==5.22.0

# Y muchas más...
```

## 🎯 Características del Sistema Desplegado

- 🤖 **Agent IoT Remoto** con LangGraph (5 nodos)
- 📡 **Datos reales** desde Jetson Nano vía Cloudflare tunnel
- 🧠 **Groq LLM** (llama-3.1-8b-instant) - 100% gratuito
- 🔍 **Anti-alucinaciones** con verificación de datos
- 📊 **40+ registros** de sensores por consulta
- 🎨 **Interfaz moderna** con chat y métricas

## 🚀 Pasos de Despliegue

1. **Conecta GitHub**: Autoriza Streamlit Cloud a acceder a tu repo
2. **Selecciona repo**: `Denniels/agent_LangGreph`
3. **Configura**:
   - Branch: `main`
   - Main file: `app.py`
4. **Agrega Secrets**: Copia la configuración de secrets de arriba
5. **Deploy**: Haz clic en "Deploy"
6. **Espera**: 2-3 minutos para el build
7. **Prueba**: Accede a tu URL pública

## ✅ Verificación Post-Despliegue

### Pruebas recomendadas:
1. **Inicializar agente**: Click en "🚀 Inicializar Agente Cloud"
2. **Consulta básica**: "¿Cuál es la temperatura actual?"
3. **Consulta específica**: "Dame estadísticas del ESP32"
4. **Verificar métricas**: Tab "📊 Métricas"

### Respuesta esperada:
- ✅ 40+ registros procesados
- ✅ 6 tipos de sensores detectados
- ✅ 2 dispositivos activos
- ✅ 90%+ de confianza en verificación

## 🆘 Solución de Problemas

### Error: "Module not found"
- Verifica que `requirements.txt` esté actualizado
- Redeploy la aplicación

### Error: "Groq API key not found"
- Verifica que `GROQ_API_KEY` esté en Secrets
- Asegúrate de que no tenga espacios extra

### Error: "No data from Jetson"
- Normal si Jetson está offline
- El sistema funcionará en modo demo

### App muy lenta
- Groq es rápido, verifica tu conexión
- Revisa logs en Streamlit Cloud

## 📞 Soporte

- 📧 **Groq Support**: [console.groq.com/docs](https://console.groq.com/docs)
- 📧 **Streamlit Support**: [docs.streamlit.io](https://docs.streamlit.io)
- 🐛 **Issues**: Crea un issue en el repositorio GitHub

## 🎉 ¡Éxito!

Una vez desplegado, tendrás una **aplicación IoT completa en la nube** que:
- Procesa datos reales de sensores
- Usa IA avanzada (Groq) completamente gratis
- Funciona 24/7 sin costos de hosting
- Escala automáticamente con usuarios

**URL de tu aplicación**: `https://tu-app-name.streamlit.app`

---

*Última actualización: Septiembre 2025*
*Version: 1.0 - Remote IoT Agent con Groq*
