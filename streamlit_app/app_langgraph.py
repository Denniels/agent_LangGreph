"""
Aplicación Streamlit con LangGraph StateGraph Completo
======================================================

Interfaz de usuario que utiliza el agente IoT con LangGraph StateGraph.
"""

import streamlit as st
import asyncio
import time
import sys
import os
from datetime import datetime

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.agents.iot_agent_langgraph import langgraph_agent
from modules.utils.logger import setup_logger

logger = setup_logger(__name__)

# Configuración de la página
st.set_page_config(
    page_title="🤖 Agente IoT LangGraph",
    page_icon="🔗", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-card {
        background: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success-card {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-card {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def run_async(coro):
    """Ejecuta una corrutina de forma segura en Streamlit."""
    try:
        return asyncio.run(coro)
    except Exception as e:
        logger.error(f"Error ejecutando corrutina: {e}")
        return None

async def initialize_agent():
    """Inicializa el agente LangGraph si no está inicializado."""
    try:
        if not langgraph_agent.graph:
            await langgraph_agent.initialize()
        return True
    except Exception as e:
        st.error(f"❌ Error inicializando agente: {e}")
        return False

def main():
    """Función principal de la aplicación Streamlit."""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Agente IoT con LangGraph StateGraph</h1>
        <p>Sistema avanzado de consulta IoT con nodos especializados y flujo condicional</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar con información del sistema
    with st.sidebar:
        st.header("🔧 Estado del Sistema")
        
        # Botón para inicializar/verificar agente
        if st.button("🔄 Verificar Agente"):
            with st.spinner("Inicializando agente..."):
                success = run_async(initialize_agent())
                if success:
                    st.success("✅ Agente inicializado")
                else:
                    st.error("❌ Error en inicialización")
        
        # Estado del agente
        try:
            agent_status = run_async(langgraph_agent.get_agent_status())
            
            if agent_status and agent_status.get("agent_initialized", False):
                st.markdown('<div class="success-card">🟢 Agente Activo</div>', unsafe_allow_html=True)
                
                # Métricas del agente
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Nodos", agent_status.get("graph_nodes", 0))
                with col2:
                    st.metric("Sesiones", agent_status.get("active_sessions", 0))
                
                # Características del grafo
                if "graph_features" in agent_status:
                    st.subheader("🔗 Características LangGraph")
                    for feature in agent_status["graph_features"]:
                        st.write(f"• {feature}")
                        
            else:
                st.markdown('<div class="error-card">🔴 Agente No Inicializado</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error obteniendo estado: {e}")
            logger.error(f"Error en get_agent_status: {e}")
        
        # Visualización del grafo
        st.subheader("📊 Grafo LangGraph")
        if st.button("Ver Estructura"):
            try:
                graph_viz = run_async(langgraph_agent.get_graph_visualization())
                
                if "nodes" in graph_viz:
                    st.subheader("🔗 Nodos del Grafo")
                    for node in graph_viz["nodes"]:
                        st.write(f"**{node['label']}**")
                        st.write(f"_{node['description']}_")
                        st.write("---")
                        
                if "features" in graph_viz:
                    st.subheader("⚡ Capacidades")
                    for feature in graph_viz["features"]:
                        st.write(f"✓ {feature}")
                        
            except Exception as e:
                st.error(f"Error visualizando grafo: {e}")
    
    # Área principal de consulta
    st.header("💬 Consulta al Agente IoT")
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Consulta", "📊 Capacidades", "📈 Historial", "🔧 Debug"])
    
    with tab1:
        # Formulario de consulta
        with st.form("query_form"):
            st.subheader("Ingresa tu consulta")
            
            # Ejemplos de consultas
            st.write("**Ejemplos de consultas:**")
            examples = [
                "¿Cuántos registros de sensores hay en total?",
                "Muestra los datos de sensores más recientes",
                "¿Qué dispositivos están activos?",
                "Analiza las tendencias de temperatura",
                "Detecta anomalías en los datos",
            ]
            
            selected_example = st.selectbox("Selecciona un ejemplo:", [""] + examples)
            
            user_query = st.text_area(
                "Tu consulta:",
                value=selected_example,
                height=100,
                placeholder="Ejemplo: ¿Cuántos sensores están enviando datos?"
            )
            
            # Opciones avanzadas
            with st.expander("⚙️ Opciones Avanzadas"):
                user_id = st.text_input("ID Usuario", value="streamlit_user")
                session_id = st.text_input("ID Sesión (opcional)", value="")
                show_metadata = st.checkbox("Mostrar metadatos de ejecución", value=True)
            
            submitted = st.form_submit_button("🚀 Enviar Consulta")
        
        # Procesar consulta
        if submitted and user_query.strip():
            with st.spinner("🔄 Procesando consulta con LangGraph..."):
                start_time = time.time()
                
                try:
                    # Procesar usando el agente LangGraph
                    result = run_async(langgraph_agent.process_query(
                        user_query=user_query,
                        user_id=user_id,
                        session_id=session_id if session_id else None
                    ))
                    
                    processing_time = time.time() - start_time
                    
                    # Mostrar respuesta
                    if result.get("status") == "success":
                        st.markdown('<div class="success-card">✅ Consulta Procesada Exitosamente</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-card">⚠️ Consulta Procesada con Advertencias</div>', unsafe_allow_html=True)
                    
                    # Respuesta principal
                    st.subheader("📋 Respuesta:")
                    st.write(result.get("response", "No se generó respuesta"))
                    
                    # Métricas de ejecución
                    if show_metadata:
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("⏱️ Tiempo", f"{processing_time:.2f}s")
                        
                        with col2:
                            intent = result.get("query_intent", "unknown")
                            st.metric("🎯 Intención", intent)
                        
                        with col3:
                            tools_count = len(result.get("tools_used", []))
                            st.metric("🛠️ Herramientas", tools_count)
                        
                        with col4:
                            status = result.get("status", "unknown")
                            st.metric("📊 Estado", status)
                        
                        # Detalles de ejecución
                        with st.expander("🔍 Detalles de Ejecución"):
                            st.json(result.get("execution_metadata", {}))
                            
                            if result.get("tools_used"):
                                st.write("**Herramientas utilizadas:**")
                                for tool in result["tools_used"]:
                                    st.write(f"• {tool}")
                
                except Exception as e:
                    st.error(f"❌ Error procesando consulta: {e}")
                    logger.error(f"Error en consulta Streamlit: {e}")
    
    with tab2:
        st.subheader("🚀 Capacidades del Agente LangGraph")
        
        try:
            capabilities = run_async(langgraph_agent.get_available_capabilities())
            
            if capabilities:
                # Características del grafo
                st.write("### 🔗 Características LangGraph")
                for feature in capabilities.get("graph_features", []):
                    st.write(f"✓ {feature}")
                
                # Tipos de consultas soportadas
                st.write("### 🔍 Consultas Soportadas")
                for query_type in capabilities.get("supported_queries", []):
                    st.write(f"• {query_type}")
                
                # Herramientas disponibles
                st.write("### 🛠️ Herramientas Disponibles")
                for tool in capabilities.get("available_tools", []):
                    st.write(f"• {tool}")
                
                # Características avanzadas
                st.write("### ⚡ Características Avanzadas")
                for feature in capabilities.get("advanced_features", []):
                    st.write(f"• {feature}")
            else:
                st.warning("No se pudieron obtener las capacidades del agente")
                
        except Exception as e:
            st.error(f"Error obteniendo capacidades: {e}")
            logger.error(f"Error en get_available_capabilities: {e}")
    
    with tab3:
        st.subheader("📈 Historial de Sesiones")
        
        # Input para ID de sesión
        session_lookup = st.text_input("Buscar por ID de sesión:")
        
        if st.button("🔍 Buscar Historial") and session_lookup:
            try:
                history = run_async(langgraph_agent.get_session_history(session_lookup))
                
                if history:
                    st.write(f"**Encontradas {len(history)} interacciones:**")
                    
                    for i, interaction in enumerate(reversed(history[-10:])):  # Últimas 10
                        with st.expander(f"Interacción {len(history)-i} - {interaction.get('timestamp', '')}"):
                            st.write(f"**Consulta:** {interaction.get('user_query', '')}")
                            st.write(f"**Respuesta:** {interaction.get('response', '')}")
                            st.write(f"**Estado:** {interaction.get('status', '')}")
                            st.write(f"**Intención:** {interaction.get('query_intent', '')}")
                            st.write(f"**Herramientas:** {', '.join(interaction.get('tools_used', []))}")
                else:
                    st.info("No se encontró historial para esta sesión")
                    
            except Exception as e:
                st.error(f"Error buscando historial: {e}")
    
    with tab4:
        st.subheader("🔧 Información de Debug")
        
        # Estado detallado del agente
        if st.button("🔄 Actualizar Estado"):
            try:
                agent_status = run_async(langgraph_agent.get_agent_status())
                st.json(agent_status)
                
            except Exception as e:
                st.error(f"Error obteniendo estado: {e}")
        
        # Reiniciar sesión
        st.write("### 🔄 Reiniciar Sesión")
        session_to_reset = st.text_input("ID de sesión a reiniciar:")
        
        if st.button("🗑️ Reiniciar Sesión") and session_to_reset:
            try:
                result = run_async(langgraph_agent.reset_session(session_to_reset))
                
                if result.get("success"):
                    st.success(f"✅ {result.get('message')}")
                else:
                    st.error(f"❌ {result.get('error')}")
                    
            except Exception as e:
                st.error(f"Error reiniciando sesión: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        🤖 Agente IoT LangGraph | StateGraph con nodos especializados y flujo condicional
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
