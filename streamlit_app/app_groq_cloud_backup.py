#!/usr/bin/env python3
"""
APLICACIÓN STREAMLIT PARA AGENTE IOT - VERSIÓN CORREGIDA
======================================================

Versión completamente funcional que:
- Ve TODOS los dispositivos
- Genera gráficos cuando se solicita
- Acceso robusto a API
"""

import streamlit as st
import sys
import os
import uuid
import glob
import time
from datetime import datetime, timedelta
import traceback

# Configuración de página
st.set_page_config(
    page_title="🤖 Agente IoT Avanzado",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Agregar path del proyecto
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Importaciones del proyecto
try:
    from modules.agents.cloud_iot_agent import CloudIoTAgent
    from modules.tools.jetson_api_connector import JetsonAPIConnector
    from modules.utils.usage_tracker import usage_tracker
    
    # Variables de configuración
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    JETSON_API_URL = "https://replica-subscriber-permission-restricted.trycloudflare.com"
    
except ImportError as e:
    st.error(f"❌ Error importando módulos: {str(e)}")
    st.code(traceback.format_exc())
    st.stop()

# Cache para servicios
@st.cache_resource
def initialize_services():
    """Inicializar servicios con conexión robusta"""
    try:
        # Crear conector de Jetson
        jetson_connector = JetsonAPIConnector(JETSON_API_URL)
        
        # Verificar conexión
        devices = jetson_connector.get_devices()
        st.success(f"✅ Conectado a API Jetson: {len(devices)} dispositivos detectados")
        
        # Crear agente IoT completo
        cloud_agent = CloudIoTAgent()
        
        return cloud_agent, jetson_connector
        
    except Exception as e:
        st.error(f"❌ Error inicializando servicios: {str(e)}")
        st.code(traceback.format_exc())
        return None, None

def display_chat_interface():
    """Interfaz principal del chat"""
    st.title("🤖 Chat con Agente IoT")
    
    if not GROQ_API_KEY:
        st.error("❌ Configure GROQ_API_KEY en las variables de entorno")
        return
    
    # Inicializar servicios
    cloud_agent, jetson_connector = initialize_services()
    
    if not cloud_agent or not jetson_connector:
        st.error("❌ No se pudieron inicializar los servicios")
        return
    
    # Información de dispositivos disponibles
    with st.expander("📱 Información de Dispositivos", expanded=True):
        try:
            devices = jetson_connector.get_devices()
            st.write(f"**Dispositivos detectados:** {len(devices)}")
            
            for device in devices:
                device_id = device.get('device_id', 'N/A')
                last_seen = device.get('last_seen', 'N/A')
                st.write(f"- **{device_id}**: Último registro {last_seen}")
                
                # Mostrar datos recientes
                try:
                    recent_data = jetson_connector.get_sensor_data(device_id=device_id, limit=5)
                    if recent_data:
                        st.write(f"  - Registros recientes: {len(recent_data)}")
                        latest = recent_data[0] if recent_data else {}
                        sensor_type = latest.get('sensor_type', 'N/A')
                        value = latest.get('value', 'N/A')
                        timestamp = latest.get('timestamp', 'N/A')
                        st.write(f"  - Última lectura: {sensor_type} = {value} ({timestamp})")
                    else:
                        st.write("  - Sin datos recientes")
                except Exception as e:
                    st.write(f"  - Error obteniendo datos: {e}")
                    
        except Exception as e:
            st.error(f"Error obteniendo dispositivos: {e}")
    
    # Historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Mostrar mensajes anteriores
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input del usuario
    if prompt := st.chat_input("Escribe tu consulta sobre sensores IoT..."):
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Procesar consulta
        with st.chat_message("assistant"):
            with st.spinner("🤖 Procesando consulta..."):
                try:
                    # Usar el agente IoT completo
                    response = cloud_agent.process_query(prompt)
                    
                    # Mostrar respuesta
                    st.markdown(response)
                    
                    # VERIFICAR Y MOSTRAR GRÁFICOS SI SE GENERARON
                    try:
                        # Buscar archivos de gráficos recientes
                        import glob
                        import time
                        
                        # Buscar en directorio charts/
                        chart_patterns = [
                            "charts/time_series_*.png",
                            "charts/statistics_*.png", 
                            "charts/prediction_*.png"
                        ]
                        
                        charts_found = []
                        for pattern in chart_patterns:
                            files = glob.glob(pattern)
                            # Filtrar archivos creados en los últimos 30 segundos
                            recent_files = [f for f in files if time.time() - os.path.getmtime(f) < 30]
                            charts_found.extend(recent_files)
                        
                        if charts_found:
                            st.success(f"📊 **GRÁFICOS GENERADOS**: {len(charts_found)} archivos")
                            
                            # Mostrar cada gráfico
                            for chart_path in sorted(charts_found):
                                chart_name = os.path.basename(chart_path)
                                st.subheader(f"📈 {chart_name}")
                                
                                try:
                                    st.image(chart_path, caption=chart_name, use_column_width=True)
                                except Exception as img_error:
                                    st.error(f"Error mostrando {chart_name}: {img_error}")
                                    
                    except Exception as chart_error:
                        # No mostrar error si no hay gráficos, es normal
                        if "grafica" in prompt.lower() or "gráfico" in prompt.lower():
                            st.warning(f"No se encontraron gráficos recientes: {chart_error}")
                    
                    # Agregar al historial
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"❌ Error procesando consulta: {str(e)}"
                    st.error(error_msg)
                    st.code(traceback.format_exc())
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

def display_debug_info():
    """Panel de información de debug"""
    st.sidebar.header("🔧 Información de Debug")
    
    try:
        # Información de uso de API
        current_model = "llama-3.1-70b-versatile"
        usage_info = usage_tracker.get_usage_info(current_model)
        
        st.sidebar.write("**Uso de API Groq:**")
        st.sidebar.write(f"- Requests: {usage_info.get('requests_used', 0)}/{usage_info.get('requests_limit', 0)}")
        st.sidebar.write(f"- Tokens: {usage_info.get('tokens_used', 0)}/{usage_info.get('tokens_limit', 0)}")
        
        # Información de conectividad
        st.sidebar.write("**Conectividad:**")
        st.sidebar.write(f"- API Jetson: {JETSON_API_URL}")
        st.sidebar.write(f"- Groq API: {'✅' if GROQ_API_KEY else '❌'}")
        
        # Test de conectividad
        if st.sidebar.button("🔄 Test Conectividad"):
            with st.sidebar:
                try:
                    connector = JetsonAPIConnector(JETSON_API_URL)
                    devices = connector.get_devices()
                    st.success(f"✅ API OK: {len(devices)} dispositivos")
                    
                    for device in devices:
                        device_id = device.get('device_id')
                        data = connector.get_sensor_data(device_id=device_id, limit=1)
                        st.write(f"- {device_id}: {len(data) if data else 0} registros")
                        
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        # Limpiar caché
        if st.sidebar.button("🗑️ Limpiar Caché"):
            st.cache_resource.clear()
            st.sidebar.success("✅ Caché limpiado")
            
    except Exception as e:
        st.sidebar.error(f"Error en debug: {e}")

def main():
    """Función principal"""
    try:
        # Crear pestañas
        tab1, tab2 = st.tabs(["💬 Chat IoT", "📊 Estado del Sistema"])
        
        with tab1:
            display_chat_interface()
        
        with tab2:
            st.header("📊 Estado del Sistema")
            
            # Información de dispositivos
            try:
                connector = JetsonAPIConnector(JETSON_API_URL)
                devices = connector.get_devices()
                
                st.subheader("📱 Dispositivos Conectados")
                
                for device in devices:
                    device_id = device.get('device_id', 'N/A')
                    
                    with st.expander(f"🔧 {device_id}", expanded=True):
                        # Datos recientes
                        recent_data = connector.get_sensor_data(device_id=device_id, limit=10)
                        
                        if recent_data:
                            st.write(f"**Registros recientes:** {len(recent_data)}")
                            
                            # Mostrar tabla
                            import pandas as pd
                            df = pd.DataFrame(recent_data)
                            st.dataframe(df[['sensor_type', 'value', 'timestamp']].head(5))
                            
                            # Estadísticas
                            sensors = df['sensor_type'].unique()
                            st.write(f"**Sensores activos:** {', '.join(sensors)}")
                            
                            latest_timestamp = df['timestamp'].max()
                            st.write(f"**Última actualización:** {latest_timestamp}")
                        else:
                            st.warning("Sin datos disponibles")
            
            except Exception as e:
                st.error(f"Error obteniendo estado del sistema: {e}")
                st.code(traceback.format_exc())
        
        # Panel lateral de debug
        display_debug_info()
        
    except Exception as e:
        st.error(f"Error en aplicación principal: {e}")
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()