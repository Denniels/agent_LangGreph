#!/usr/bin/env python3
"""
APLICACIÓN STREAMLIT COMPLETA Y OPTIMIZADA - VERSIÓN DEFINITIVA
=============================================================

✅ INCLUYE TODAS LAS FUNCIONALIDADES:
- Chat IoT Agent con gráficos integrados
- Generador de Reportes completo  
- Visualizaciones matplotlib nativas
- Carga súper optimizada
- Sin pérdida de funcionalidades

🚀 OPTIMIZADA PARA STREAMLIT CLOUD
"""

# IMPORTS MÍNIMOS AL INICIO para carga rápida
import streamlit as st
import os

# Configuración MÍNIMA
st.set_page_config(
    page_title="🤖 Agente IoT Completo",
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Variables de entorno
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
JETSON_API_URL = "https://couples-mario-repository-alive.trycloudflare.com"

# CACHE AGRESIVO para módulos pesados
@st.cache_resource(show_spinner="🔄 Cargando módulos...")
def load_project_modules():
    """Cargar TODOS los módulos del proyecto de forma optimizada y robusta"""
    import sys
    from datetime import datetime, timedelta
    import traceback
    
    # Agregar path del proyecto
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.append(project_root)
    
    try:
        # Imports principales (críticos)
        from modules.agents.cloud_iot_agent import CloudIoTAgent
        from modules.tools.jetson_api_connector import JetsonAPIConnector
        from modules.utils.usage_tracker import usage_tracker
        
        # Imports para reportes (con manejo de errores)
        try:
            from modules.agents.reporting import ReportGenerator
            report_generator_available = True
        except Exception as e:
            st.warning(f"⚠️ Sistema de reportes no disponible: {str(e)}")
            ReportGenerator = None
            report_generator_available = False
        
        # Imports para UI de uso (con fallback robusto)
        try:
            from modules.utils.streamlit_usage_display import (
                display_usage_metrics, 
                display_usage_alert,
                display_model_limits_info
            )
            usage_display_available = True
        except Exception as e:
            st.warning(f"⚠️ Displays de uso no disponibles: {str(e)}")
            # Crear funciones fallback
            def display_usage_metrics(*args, **kwargs):
                st.info("📊 Métricas de uso no disponibles")
            def display_usage_alert(*args, **kwargs):
                pass
            def display_model_limits_info(*args, **kwargs):
                st.info("ℹ️ Información de límites no disponible")
            usage_display_available = False
        
        return {
            'CloudIoTAgent': CloudIoTAgent,
            'JetsonAPIConnector': JetsonAPIConnector, 
            'ReportGenerator': ReportGenerator,
            'usage_tracker': usage_tracker,
            'display_usage_metrics': display_usage_metrics,
            'display_usage_alert': display_usage_alert,
            'display_model_limits_info': display_model_limits_info,
            'datetime': datetime,
            'timedelta': timedelta,
            'traceback': traceback,
            'report_generator_available': report_generator_available,
            'usage_display_available': usage_display_available
        }
    except Exception as e:
        st.error(f"❌ Error crítico cargando módulos: {str(e)}")
        st.error("🔧 Verifique que todas las dependencias estén instaladas en Streamlit Cloud")
        return None

@st.cache_resource(show_spinner="🔧 Inicializando servicios...")
def initialize_services():
    """Inicializar servicios con verificación robusta"""
    modules = load_project_modules()
    if not modules:
        return None, None, None
    
    try:
        # Crear conector de Jetson
        jetson_connector = modules['JetsonAPIConnector'](JETSON_API_URL)
        
        # Verificar conectividad
        devices = jetson_connector.get_devices()
        
        # Crear agente IoT completo
        cloud_agent = modules['CloudIoTAgent']()
        
        # Crear generador de reportes (si está disponible)
        if modules.get('report_generator_available', False) and modules['ReportGenerator']:
            try:
                report_generator = modules['ReportGenerator'](jetson_connector=jetson_connector)
            except Exception as e:
                st.warning(f"⚠️ Error inicializando reportes: {str(e)}")
                report_generator = None
        else:
            report_generator = None
        
        return cloud_agent, jetson_connector, report_generator
        
    except Exception as e:
        st.error(f"❌ Error inicializando servicios: {str(e)}")
        st.error("🔧 Intente recargar la página o verificar la configuración de Streamlit Cloud")
        return None, None, None

def create_matplotlib_chart(data, query_type="time_series"):
    """Crear gráficos matplotlib directamente en Streamlit"""
    modules = load_project_modules()
    if not modules or not data:
        return None
    
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
        import numpy as np
        
        # Configurar matplotlib para Streamlit
        plt.style.use('default')
        
        if query_type == "time_series":
            # Gráfico de series temporales
            fig, ax = plt.subplots(figsize=(12, 6))
            
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Agrupar por dispositivo y sensor
            for device_id in df['device_id'].unique():
                device_data = df[df['device_id'] == device_id]
                
                for sensor_type in device_data['sensor_type'].unique():
                    sensor_data = device_data[device_data['sensor_type'] == sensor_type]
                    
                    if len(sensor_data) > 0:
                        label = f"{device_id} - {sensor_type}"
                        ax.plot(sensor_data['timestamp'], sensor_data['value'], 
                               marker='o', label=label, linewidth=2, markersize=4)
            
            ax.set_title("📈 Series Temporales de Sensores", fontsize=14, fontweight='bold')
            ax.set_xlabel("Tiempo")
            ax.set_ylabel("Valor del Sensor")
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Rotar etiquetas de fecha
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            return fig
            
        elif query_type == "statistics":
            # Gráfico de estadísticas
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            df = pd.DataFrame(data)
            
            # Gráfico de barras por dispositivo
            device_counts = df['device_id'].value_counts()
            ax1.bar(device_counts.index, device_counts.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
            ax1.set_title("📊 Registros por Dispositivo")
            ax1.set_ylabel("Número de Registros")
            
            # Gráfico de distribución de valores por sensor
            for i, sensor_type in enumerate(df['sensor_type'].unique()):
                sensor_data = df[df['sensor_type'] == sensor_type]
                ax2.hist(sensor_data['value'], alpha=0.7, label=sensor_type, bins=10)
            
            ax2.set_title("📊 Distribución de Valores por Sensor")
            ax2.set_xlabel("Valor")
            ax2.set_ylabel("Frecuencia")
            ax2.legend()
            
            plt.tight_layout()
            return fig
    
    except Exception as e:
        st.error(f"Error creando gráfico: {e}")
        return None

def display_chat_interface():
    """Interfaz de chat con gráficos integrados"""
    st.title("🤖 Chat con Agente IoT")
    
    if not GROQ_API_KEY:
        st.error("❌ Configure GROQ_API_KEY en las variables de entorno")
        return
    
    # Cargar servicios
    cloud_agent, jetson_connector, _ = initialize_services()
    
    if not cloud_agent or not jetson_connector:
        st.error("❌ No se pudieron inicializar los servicios")
        return
    
    # Información de dispositivos compacta
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
            st.error(f"Error: {e}")
    
    # Historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Mostrar mensajes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Mostrar gráficos si los hay
            if "charts" in message and message["charts"]:
                for chart_fig in message["charts"]:
                    st.pyplot(chart_fig)
    
    # Input del usuario
    if prompt := st.chat_input("💬 Escribe tu consulta sobre sensores IoT..."):
        # Mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Respuesta del agente
        with st.chat_message("assistant"):
            with st.spinner("🤖 Procesando consulta..."):
                try:
                    # Procesar con el agente (USANDO FUNCIÓN SÍNCRONA)
                    if hasattr(cloud_agent, 'process_query_sync'):
                        # Usar la función síncrona optimizada
                        response_text = cloud_agent.process_query_sync(prompt)
                    else:
                        # Fallback al método async si es necesario
                        import asyncio
                        import nest_asyncio
                        nest_asyncio.apply()
                        
                        response = asyncio.run(cloud_agent.process_query(prompt))
                        response_text = response.get('response', str(response)) if isinstance(response, dict) else str(response)
                    
                    # Mostrar respuesta textual
                    st.markdown(response_text)
                    
                    # GENERAR Y MOSTRAR GRÁFICOS SI SE SOLICITAN
                    charts_generated = []
                    
                    # Detectar si se solicitan gráficos
                    chart_keywords = ['grafica', 'gráfica', 'grafico', 'gráfico', 'visualizar', 'chart', 'plot']
                    needs_charts = any(keyword in prompt.lower() for keyword in chart_keywords)
                    
                    if needs_charts:
                        st.info("📊 Generando gráficos...")
                        
                        try:
                            # Obtener datos recientes para gráficos
                            all_chart_data = []
                            devices = jetson_connector.get_devices()
                            
                            for device in devices:
                                device_id = device.get('device_id')
                                if device_id:
                                    # Obtener más datos para gráficos
                                    device_data = jetson_connector.get_sensor_data(
                                        device_id=device_id, 
                                        limit=50  # Más datos para gráficos mejores
                                    )
                                    if device_data:
                                        all_chart_data.extend(device_data)
                            
                            if all_chart_data:
                                # Generar gráfico de series temporales
                                time_series_fig = create_matplotlib_chart(all_chart_data, "time_series")
                                if time_series_fig:
                                    st.subheader("📈 Series Temporales")
                                    st.pyplot(time_series_fig)
                                    charts_generated.append(time_series_fig)
                                
                                # Generar gráfico de estadísticas  
                                stats_fig = create_matplotlib_chart(all_chart_data, "statistics")
                                if stats_fig:
                                    st.subheader("📊 Estadísticas")
                                    st.pyplot(stats_fig)
                                    charts_generated.append(stats_fig)
                                
                                if charts_generated:
                                    st.success(f"✅ Generados {len(charts_generated)} gráficos")
                                else:
                                    st.warning("⚠️ No se pudieron generar gráficos")
                            else:
                                st.warning("⚠️ No hay datos suficientes para generar gráficos")
                                
                        except Exception as chart_error:
                            st.error(f"❌ Error generando gráficos: {chart_error}")
                    
                    # Agregar al historial
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response_text,  # Usar response_text en lugar de response
                        "charts": charts_generated
                    })
                    
                except Exception as e:
                    modules = load_project_modules()
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    if modules and 'traceback' in modules:
                        st.code(modules['traceback'].format_exc())
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

def display_reports_interface():
    """Interfaz de generación de reportes - RESTAURADA COMPLETAMENTE"""
    st.title("📊 Generador de Reportes IoT")
    
    # Cargar servicios
    cloud_agent, jetson_connector, report_generator = initialize_services()
    modules = load_project_modules()
    
    if not report_generator or not modules:
        st.error("❌ Servicios de reportes no disponibles")
        return
    
    # Configuración del reporte
    st.subheader("⚙️ Configuración del Reporte")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Selección de dispositivos
        try:
            devices = jetson_connector.get_devices()
            device_options = [d.get('device_id', 'N/A') for d in devices]
            selected_devices = st.multiselect(
                "📱 Seleccionar Dispositivos:",
                device_options,
                default=device_options
            )
        except:
            st.error("Error obteniendo dispositivos")
            selected_devices = []
    
    with col2:
        # Rango de tiempo
        date_range = st.selectbox(
            "📅 Rango de Tiempo:",
            ["Última hora", "Últimas 6 horas", "Últimas 24 horas", "Últimos 7 días"]
        )
    
    # Tipo de reporte
    report_type = st.selectbox(
        "📄 Tipo de Reporte:",
        ["Resumen Ejecutivo", "Análisis Técnico Completo", "Reporte de Tendencias"]
    )
    
    # Generar reporte
    if st.button("🚀 Generar Reporte", type="primary"):
        if selected_devices:
            with st.spinner("📝 Generando reporte..."):
                try:
                    # Configurar parámetros del reporte
                    hours_map = {
                        "Última hora": 1,
                        "Últimas 6 horas": 6, 
                        "Últimas 24 horas": 24,
                        "Últimos 7 días": 168
                    }
                    
                    hours = hours_map.get(date_range, 24)
                    
                    # Generar reporte usando el generador
                    report_result = report_generator.generate_comprehensive_report(
                        device_ids=selected_devices,
                        hours_back=hours,
                        report_type=report_type.lower().replace(" ", "_")
                    )
                    
                    if report_result and "success" in report_result:
                        st.success("✅ Reporte generado exitosamente!")
                        
                        # Mostrar reporte
                        if "report_content" in report_result:
                            st.markdown("### 📋 Contenido del Reporte")
                            st.markdown(report_result["report_content"])
                        
                        # Mostrar archivos generados
                        if "files_generated" in report_result:
                            st.markdown("### 📁 Archivos Generados")
                            for file_info in report_result["files_generated"]:
                                st.write(f"- **{file_info['type']}**: {file_info['filename']}")
                        
                        # Botón de descarga si está disponible
                        if "download_url" in report_result:
                            st.download_button(
                                "📥 Descargar Reporte PDF",
                                data=report_result.get("pdf_content", ""),
                                file_name=f"reporte_iot_{modules['datetime'].now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf"
                            )
                    else:
                        st.error("❌ Error generando reporte")
                        if "error" in report_result:
                            st.error(report_result["error"])
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    if modules and 'traceback' in modules:
                        st.code(modules['traceback'].format_exc())
        else:
            st.warning("⚠️ Seleccione al menos un dispositivo")

def display_system_status():
    """Panel de estado del sistema optimizado"""
    st.title("⚙️ Estado del Sistema")
    
    cloud_agent, jetson_connector, _ = initialize_services()
    modules = load_project_modules()
    
    if not jetson_connector or not modules:
        st.error("❌ Servicios no disponibles")
        return
    
    # Métricas del sistema
    st.subheader("📊 Métricas del Sistema")
    
    try:
        # Información de conectividad
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🌐 API Jetson", "✅ Conectada" if jetson_connector else "❌ Error")
        
        with col2:
            groq_status = "✅ Configurada" if GROQ_API_KEY else "❌ Faltante"
            st.metric("🤖 Groq API", groq_status)
        
        with col3:
            devices = jetson_connector.get_devices()
            st.metric("📱 Dispositivos", len(devices))
        
        with col4:
            # Contar registros totales
            total_records = 0
            for device in devices:
                try:
                    data = jetson_connector.get_sensor_data(device_id=device.get('device_id'), limit=1000)
                    total_records += len(data) if data else 0
                except:
                    pass
            st.metric("📝 Registros Totales", total_records)
        
        # Detalles de dispositivos
        st.subheader("🔧 Detalles de Dispositivos")
        
        for device in devices:
            device_id = device.get('device_id', 'N/A')
            
            with st.expander(f"📱 {device_id}", expanded=False):
                try:
                    recent_data = jetson_connector.get_sensor_data(device_id=device_id, limit=10)
                    
                    if recent_data:
                        # Convertir a DataFrame para análisis
                        import pandas as pd
                        df = pd.DataFrame(recent_data)
                        
                        # Información básica
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("📊 Registros", len(df))
                        
                        with col2:
                            sensors = df['sensor_type'].nunique()
                            st.metric("🔬 Sensores", sensors)
                        
                        with col3:
                            latest_time = df['timestamp'].max()
                            st.metric("🕐 Última actualización", latest_time)
                        
                        # Tabla de datos recientes
                        st.dataframe(
                            df[['sensor_type', 'value', 'timestamp']].head(5),
                            use_container_width=True
                        )
                    else:
                        st.warning("Sin datos disponibles")
                
                except Exception as e:
                    st.error(f"Error: {e}")
    
    except Exception as e:
        st.error(f"Error obteniendo estado del sistema: {e}")

def display_sidebar():
    """Sidebar con información optimizada"""
    modules = load_project_modules()
    if not modules:
        return
    
    st.sidebar.header("🔧 Panel de Control")
    
    # Información de uso de API
    try:
        usage_info = modules['usage_tracker'].get_usage_info("llama-3.1-70b-versatile")
        
        st.sidebar.subheader("📊 Uso de API")
        
        # Métricas compactas
        requests_used = usage_info.get('requests_used', 0)
        requests_limit = usage_info.get('requests_limit', 0)
        
        if requests_limit > 0:
            usage_percent = (requests_used / requests_limit) * 100
            st.sidebar.progress(usage_percent / 100)
            st.sidebar.write(f"**Requests**: {requests_used}/{requests_limit} ({usage_percent:.1f}%)")
        
        # Alertas de uso
        modules['display_usage_alert'](usage_info)
        
    except Exception as e:
        st.sidebar.error(f"Error en métricas: {e}")
    
    # Controles del sistema
    st.sidebar.subheader("⚙️ Controles")
    
    if st.sidebar.button("🗑️ Limpiar Cache"):
        st.cache_resource.clear()
        st.sidebar.success("Cache limpiado")
        st.rerun()
    
    if st.sidebar.button("🔄 Recargar Servicios"):
        st.cache_resource.clear()
        st.sidebar.success("Servicios recargados")
        st.rerun()

def main():
    """Función principal optimizada"""
    
    # Verificar configuración básica
    if not GROQ_API_KEY:
        st.error("❌ Configure GROQ_API_KEY en Streamlit Cloud Secrets")
        st.stop()
    
    # Crear pestañas COMPLETAS (sin eliminar funcionalidades)
    tab1, tab2, tab3 = st.tabs([
        "💬 Chat IoT", 
        "📊 Reportes",  # RESTAURADA
        "⚙️ Sistema"
    ])
    
    with tab1:
        display_chat_interface()
    
    with tab2:
        display_reports_interface()  # FUNCIONALIDAD RESTAURADA
    
    with tab3:
        display_system_status()
    
    # Sidebar
    display_sidebar()

if __name__ == "__main__":
    main()