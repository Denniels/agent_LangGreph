"""
Aplicación Streamlit para el Agente IoT Conversacional con Ollama
================================================================

Interfaz web ULTRA-OPTIMIZADA con gestión robusta de asyncio:
- Event loop completamente aislado para Streamlit
- Pool de conexiones dedicado para base de datos
- Manejo de errores mejorado
- Acceso a datos en tiempo real garantizado

Ejecutar con: streamlit run streamlit_app/app.py --server.port 8502
"""

import streamlit as st
import asyncio
import json
import threading
from datetime import datetime
import sys
from pathlib import Path
import concurrent.futures

# Configurar event loop para Streamlit de forma robusta
import nest_asyncio
nest_asyncio.apply()

# Configuración adicional para evitar conflictos
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.agents.iot_agent_ollama import IoTAgent
from modules.utils.logger import logger


# Configuración de la página
st.set_page_config(
    page_title="🤖 Agente IoT Conversacional (Fixed)",
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
def get_persistent_loop():
    """Crea (una sola vez) un event loop persistente en un hilo dedicado.
    Esto evita recrear loops y pérdidas de pools asyncpg que podrían devolver
    resultados vacíos en la primera consulta."""
    loop = asyncio.new_event_loop()

    def run_loop(l):
        asyncio.set_event_loop(l)
        l.run_forever()

    thread = threading.Thread(target=run_loop, args=(loop,), daemon=True, name="streamlit-iot-loop")
    thread.start()
    logger.info("Event loop persistente iniciado para Streamlit")
    return loop


def run_async(coro):
    """Ejecuta corrutinas en el loop persistente y devuelve el resultado.
    Beneficios:
    - Reutiliza el mismo loop => el pool asyncpg pertenece a un único loop.
    - Evita overhead de crear/cerrar loops por petición.
    - Reduce riesgo de resultados vacíos intermitentes."""
    loop = get_persistent_loop()
    try:
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result(timeout=30)
    except Exception as e:
        logger.error(f"Error ejecutando corrutina en loop persistente: {e}")
        return {"error": str(e)}


# Pool global de agentes para reutilización
@st.cache_resource
def get_agent_pool():
    """Crea un pool de agentes reutilizable"""
    return {"agent": None, "initialized": False}


@st.cache_resource
def initialize_agent():
    """Inicializa el agente IoT de forma ultra-segura."""
    try:
        # Crear agente en thread separado para evitar conflictos
        def create_agent():
            return IoTAgent()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(create_agent)
            agent = future.result(timeout=30)
            
        logger.info("Agente IoT inicializado exitosamente con ThreadPoolExecutor")
        return agent
    except Exception as e:
        logger.error(f"Error al inicializar agente: {e}")
        st.error(f"Error al inicializar agente: {e}")
        return None


def get_safe_agent():
    """Obtiene un agente de forma segura con reintentos"""
    pool = get_agent_pool()
    
    if not pool["initialized"] or pool["agent"] is None:
        with st.spinner("🔄 Inicializando agente IoT..."):
            pool["agent"] = initialize_agent()
            pool["initialized"] = True
    
    return pool["agent"]


def display_header():
    """Muestra el encabezado principal."""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Agente IoT Conversacional (FIXED)</h1>
        <p>Asistente inteligente para monitoreo y análisis de sistemas IoT</p>
        <small>Powered by Ollama + PostgreSQL + Event Loop Fix</small>
    </div>
    """, unsafe_allow_html=True)


def test_agent_health(agent):
    """Prueba la salud del agente de forma síncrona."""
    if agent:
        try:
            return run_async(agent.test_system_health())
        except Exception as e:
            return {"overall_status": "error", "error": str(e)}
    return {"overall_status": "error", "error": "Agente no inicializado"}


def display_system_status(agent):
    """Muestra el estado del sistema en la barra lateral."""
    with st.sidebar:
        st.header("🔧 Estado del Sistema")
        
        # Ejecutar prueba de salud
        with st.spinner("Verificando estado..."):
            health_report = test_agent_health(agent)
        
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


# Inicializar el estado de la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []


def display_conversation_history():
    """Muestra el historial de conversación."""
    for message in st.session_state.messages:
        role_icon = "👤" if message["role"] == "user" else "🤖"
        role_class = "user-message" if message["role"] == "user" else "assistant-message"
        
        st.markdown(f"""
        <div class="chat-message {role_class}">
            <strong>{role_icon} {'Usuario' if message["role"] == "user" else 'Asistente'}:</strong><br>
            {message["content"]}
        </div>
        """, unsafe_allow_html=True)


def process_user_input(agent, user_input):
    """Procesa la entrada del usuario de forma síncrona."""
    if agent and user_input:
        try:
            # Usar run_async para manejar asyncio correctamente
            response = run_async(agent.process_message(user_input))
            
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
    """Función principal de la aplicación ULTRA-OPTIMIZADA."""
    # Mostrar encabezado
    display_header()
    
    # Obtener agente de forma segura
    agent = get_safe_agent()
    
    if not agent:
        st.error("❌ No se pudo inicializar el agente. Revisa los logs para más detalles.")
        st.info("💡 Intenta recargar la página o verifica que Ollama esté ejecutándose")
        return
    
    # Indicador de estado del sistema
    with st.container():
        col_status1, col_status2, col_status3 = st.columns(3)
        
        with col_status1:
            st.metric("🤖 Agente", "✅ Activo")
        with col_status2:
            st.metric("🔗 Ollama", "✅ Conectado")  
        with col_status3:
            st.metric("🗄️ Base de Datos", "✅ Conectada")
    
    # Crear columnas para el layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Conversación")
        
        # Mostrar historial de conversación
        display_conversation_history()
        
        # Input del usuario
        user_input = st.chat_input("Escribe tu consulta sobre el sistema IoT...")
        
        if user_input:
            with st.spinner("🤔 Procesando tu consulta (optimizado)..."):
                start_time = datetime.now()
                response = process_user_input(agent, user_input)
                end_time = datetime.now()
                
                # Mostrar tiempo de respuesta
                response_time = (end_time - start_time).total_seconds()
                st.success(f"⚡ Respuesta generada en {response_time:.2f} segundos")
                
                # Auto-scroll hacia abajo
                st.rerun()
                # Procesar entrada del usuario
                response = process_user_input(agent, user_input)
            
            # Rerun para actualizar la interfaz
            st.rerun()
    
    with col2:
        # Estado del sistema
        display_system_status(agent)
        
        # Botones de acción
        st.header("🎛️ Controles")
        
        if st.button("🗑️ Limpiar Conversación"):
            if agent:
                try:
                    run_async(agent.clear_conversation_history())
                except:
                    pass  # Ignorar errores al limpiar
            st.session_state.messages = []
            st.success("Conversación limpiada")
            st.rerun()
        
        if st.button("🔄 Actualizar Estado"):
            st.cache_resource.clear()
            st.rerun()
        
        # Consultas de ejemplo
        st.subheader("💡 Consultas de Ejemplo")
        
        example_queries = [
            "¿Cuál es el estado actual de los sensores?",
            "Muéstrame los dispositivos conectados",
            "¿Hay alguna alerta activa?",
            "Analiza las tendencias de temperatura",
            "¿Qué dispositivos están offline?"
        ]
        
        for query in example_queries:
            if st.button(f"📝 {query}", key=f"example_{hash(query)}"):
                with st.spinner("🤔 Procesando consulta de ejemplo..."):
                    response = process_user_input(agent, query)
                st.rerun()


# Información adicional en la barra lateral
with st.sidebar:
    st.markdown("---")
    st.subheader("ℹ️ Información")
    st.markdown("""
    **Versión mejorada con:**
    - ✅ Event loop fix para asyncio
    - ✅ Manejo robusto de errores  
    - ✅ Conexión estable a PostgreSQL
    - ✅ Integración optimizada con Ollama
    
    **Base de datos**: PostgreSQL en Jetson Nano  
    **Modelo IA**: Llama 3.2 (2GB) via Ollama  
    **Dispositivos**: ESP32 + Arduino en tiempo real
    """)


if __name__ == "__main__":
    main()
