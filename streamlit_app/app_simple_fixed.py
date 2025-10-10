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

def initialize_services():
    """Inicializar servicios del sistema"""
    try:
        # Importar módulos necesarios
        from modules.agents.cloud_iot_agent import CloudIoTAgent
        from modules.tools.jetson_api_connector import JetsonAPIConnector
        
        # Crear instancias
        cloud_agent = CloudIoTAgent()
        jetson_connector = JetsonAPIConnector(base_url=JETSON_API_URL)
        
        return cloud_agent, jetson_connector
    except Exception as e:
        st.error(f"❌ Error inicializando servicios: {e}")
        return None, None

def process_user_query(prompt, cloud_agent, jetson_connector):
    """Procesar consulta del usuario con IA y gráficos"""
    response_text = "❌ Error procesando consulta"
    charts_generated = None
    
    try:
        # Obtener configuración temporal
        analysis_hours = getattr(st.session_state, 'analysis_hours', 3.0)
        
        # MÉTODO 1: Intentar con el agente principal
        if cloud_agent:
            try:
                response_text = cloud_agent.process_query_sync(prompt, "cloud-session", analysis_hours)
                method_used = "principal"
            except Exception as main_error:
                st.warning(f"⚠️ Agente principal no disponible: {main_error}")
                response_text = None
        
        # MÉTODO 2: FALLBACK con agente simple
        if not response_text or "Error" in response_text or len(response_text.strip()) < 10:
            try:
                st.info("🚀 Activando sistema de respaldo...")
                
                from modules.agents.ultra_simple_agent import create_ultra_simple_agent
                ultra_agent = create_ultra_simple_agent(jetson_connector)
                response_text = ultra_agent.process_query(prompt)
                
                st.success("✅ Respuesta generada con sistema de respaldo")
                
            except Exception as fallback_error:
                response_text = f"❌ Error: Sistema temporalmente no disponible. Intente más tarde."
        
        # GENERAR GRÁFICOS AUTOMÁTICAMENTE
        charts_generated = generate_charts_if_needed(prompt, response_text, analysis_hours)
        
    except Exception as e:
        response_text = f"❌ Error procesando consulta: {str(e)}"
    
    return response_text, charts_generated

def generate_charts_if_needed(prompt, response_text, analysis_hours):
    """Generar gráficos si la consulta lo amerita"""
    try:
        # Detectar si se necesitan gráficos
        chart_keywords = [
            'grafica', 'gráfica', 'grafico', 'gráfico', 'visualizar', 'chart', 'plot',
            'estadistica', 'estadística', 'analisis', 'análisis', 'tendencia', 'evolution',
            'temperatura', 'luminosidad', 'sensor', 'datos', 'registros', 'ultimas', 'últimas',
            'avanzada', 'detallado', 'completo', 'resumen', 'metrica', 'métrica'
        ]
        
        needs_charts = any(keyword in prompt.lower() for keyword in chart_keywords)
        
        # También generar si la respuesta contiene análisis detallado
        detailed_indicators = [
            'Promedio de temperatura', 'Temperaturas:', 'Luminosidad:', 'Dispositivo',
            'Tendencias observadas', 'Métricas clave', 'temperatura_', 'ntc_', 'ldr'
        ]
        has_detailed_analysis = any(indicator in response_text for indicator in detailed_indicators)
        
        if needs_charts or has_detailed_analysis:
            st.info("📊 Generando visualización automática...")
            
            # Obtener datos usando DirectAPIAgent
            from modules.agents.direct_api_agent import DirectAPIAgent
            direct_agent = DirectAPIAgent(base_url=JETSON_API_URL)
            
            data_result = direct_agent.get_all_recent_data(hours=analysis_hours)
            
            if data_result.get('status') == 'success':
                all_chart_data = data_result.get('sensor_data', [])
                
                if all_chart_data:
                    chart_fig = create_simple_chart(all_chart_data)
                    if chart_fig:
                        st.success("✅ Gráfico generado exitosamente")
                        return chart_fig
            
            st.warning("⚠️ No hay datos suficientes para gráficos")
    
    except Exception as e:
        st.warning(f"⚠️ Error generando gráficos: {e}")
    
    return None

def create_simple_chart(data):
    """Crear gráfico simple y robusto"""
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
        
        # Convertir a DataFrame
        df = pd.DataFrame(data)
        
        # Validar datos
        if df.empty or not all(col in df.columns for col in ['timestamp', 'device_id', 'sensor_type', 'value']):
            return None
        
        # Limpiar datos
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.dropna(subset=['timestamp', 'value'])
        
        if df.empty:
            return None
        
        # Crear gráfico
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
        color_idx = 0
        
        # Plotear por dispositivo y sensor
        for device_id in df['device_id'].unique():
            device_data = df[df['device_id'] == device_id]
            
            for sensor_type in device_data['sensor_type'].unique():
                sensor_data = device_data[device_data['sensor_type'] == sensor_type]
                
                if len(sensor_data) > 0:
                    sensor_data = sensor_data.sort_values('timestamp')
                    label = f"{device_id}-{sensor_type}"
                    
                    ax.plot(sensor_data['timestamp'], sensor_data['value'], 
                           marker='o', label=label, 
                           color=colors[color_idx % len(colors)],
                           linewidth=2, markersize=4)
                    
                    color_idx += 1
        
        ax.set_title("📈 Evolución Temporal de Sensores IoT", fontsize=14, fontweight='bold')
        ax.set_xlabel("Tiempo")
        ax.set_ylabel("Valor del Sensor")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
        
    except Exception as e:
        return None

def show_sidebar():
    """Sidebar con información completa"""
    with st.sidebar:
        st.header("🔧 Panel de Control")
        
        # Estado actual
        current_hours = getattr(st.session_state, 'analysis_hours', 3.0)
        method = "Paginado" if current_hours > 6 else "Estándar"
        max_records = min(2000, int(current_hours * 50)) if current_hours > 6 else 200
        
        st.metric("⚙️ Configuración Actual", f"{current_hours}h", f"Método: {method}")
        
        # Capacidades del sistema
        with st.expander("📊 Capacidades de Análisis", expanded=False):
            st.markdown(f"""
            **🔍 Configuración Actual:**
            - Rango temporal: {current_hours} horas
            - Método: {method}
            - Máx. registros: {max_records}
            
            **⚡ Consultas Rápidas (1-6h):**
            - Respuesta inmediata
            - Hasta 200 registros
            - Ideal para monitoreo en tiempo real
            
            **📚 Consultas Extensas (6h+):**
            - Paginación automática
            - Hasta 2,000 registros
            - Ideal para análisis de tendencias
            
            **🎯 Casos de Uso:**
            - Tiempo real: 3-6h
            - Análisis diario: 24h
            - Tendencias semanales: 168h
            """)
        
        # Información técnica
        with st.expander("🏭 Info del Sistema", expanded=False):
            st.markdown("""
            **🖥️ Hardware:**
            - NVIDIA Jetson Nano 4GB
            - ARM Cortex-A57 Quad-core
            
            **🔧 Software:**
            - API: FastAPI + SQLite
            - IA: Groq API (Gratuita)
            - Frontend: Streamlit Cloud
            
            **📊 Sensores:**
            - 6 tipos monitoreados
            - 2 dispositivos activos
            - Actualización en tiempo real
            """)
        
        # Controles
        if st.button("🗑️ Limpiar Chat"):
            st.session_state.messages = []
            st.rerun()
        
        if st.button("🔄 Recargar Sistema"):
            st.cache_data.clear()
            st.rerun()

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
    """Función principal con todas las funcionalidades restauradas"""
    
    # Verificar configuración
    if not GROQ_API_KEY:
        st.error("❌ Configure GROQ_API_KEY en Streamlit Cloud Secrets")
        st.stop()
    
    # Mostrar banner
    show_banner()
    
    # Título principal
    st.title("💬 Chat con Agente IoT")
    
    # Inicializar servicios
    try:
        cloud_agent, jetson_connector = initialize_services()
        services_available = True
    except Exception as e:
        st.warning(f"⚠️ Inicializando servicios: {str(e)}")
        cloud_agent, jetson_connector = None, None
        services_available = False
    
    # Estado de dispositivos
    if services_available and jetson_connector:
        with st.expander("📱 Estado de Dispositivos", expanded=False):
            try:
                devices = jetson_connector.get_devices()
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("🔌 Dispositivos", len(devices))
                
                device_info = []
                for device in devices:
                    device_id = device.get('device_id', 'N/A')
                    try:
                        recent_data = jetson_connector.get_sensor_data(device_id=device_id, limit=1)
                        status = "🟢 Activo" if recent_data else "🔴 Inactivo"
                        device_info.append(f"**{device_id}**: {status}")
                    except:
                        device_info.append(f"**{device_id}**: ❓ Desconocido")
                
                with col2:
                    for info in device_info[:len(device_info)//2 + 1]:
                        st.write(info)
                
                with col3:
                    for info in device_info[len(device_info)//2 + 1:]:
                        st.write(info)
                        
            except Exception as e:
                st.error(f"Error obteniendo dispositivos: {e}")
    
    # Configuración temporal mejorada
    with st.expander("⏰ Configuración de Análisis Temporal", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            time_range = st.selectbox(
                "📅 Rango de Datos",
                options=[
                    ("3h", "3 horas (Tiempo Real)"),
                    ("6h", "6 horas (Reciente)"),
                    ("12h", "12 horas (Paginado)"),
                    ("24h", "24 horas (1 día)"),
                    ("48h", "48 horas (2 días)"),
                    ("168h", "168 horas (1 semana)")
                ],
                format_func=lambda x: x[1],
                index=0,
                key="time_range_selector"
            )
        
        with col2:
            hours = float(time_range[0][:-1])
            st.session_state.analysis_hours = hours
            
            if hours <= 6:
                st.success("⚡ Consulta rápida - Respuesta inmediata")
                st.caption("📊 Método: Estándar (hasta 200 registros)")
            else:
                st.info("📚 Consulta extensa - Paginación automática")
                max_records = min(2000, int(hours * 50))
                st.caption(f"📊 Método: Paginado (hasta {max_records} registros)")
    
    # Chat con funcionalidad completa
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Mostrar mensajes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Mostrar gráficos si los hay
            if "charts" in message and message["charts"]:
                for chart_fig in message["charts"]:
                    st.pyplot(chart_fig, clear_figure=True)
    
    # Input del usuario con IA completa
    if prompt := st.chat_input("💬 Escribe tu consulta sobre sensores IoT..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤖 Procesando consulta..."):
                response_text, charts_generated = process_user_query(prompt, cloud_agent, jetson_connector)
                
                # Mostrar respuesta
                st.markdown(response_text)
                
                # Mostrar gráficos si se generaron
                if charts_generated:
                    st.pyplot(charts_generated, clear_figure=True)
                
                # Agregar al historial
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_text,
                    "charts": [charts_generated] if charts_generated else []
                })

    # Sidebar con información completa
    show_sidebar()

if __name__ == "__main__":
    main()