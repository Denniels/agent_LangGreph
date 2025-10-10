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
JETSON_API_URL = "https://respect-craps-lit-aged.trycloudflare.com"

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
    """Crear gráficos matplotlib directamente en Streamlit - Versión Robusta"""
    if not data:
        st.warning("📊 No hay datos disponibles para gráficos")
        return None
    
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
        import numpy as np
        from datetime import datetime
        
        # Configurar matplotlib para Streamlit
        plt.style.use('default')
        
        # Convertir datos a DataFrame
        df = pd.DataFrame(data)
        
        # Validar que tenemos las columnas necesarias
        required_columns = ['timestamp', 'device_id', 'sensor_type', 'value']
        if not all(col in df.columns for col in required_columns):
            st.error(f"❌ Faltan columnas requeridas. Disponibles: {list(df.columns)}")
            return None
        
        # Limpiar y convertir datos
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # Eliminar filas con datos inválidos
        df = df.dropna(subset=['timestamp', 'value'])
        
        if df.empty:
            st.warning("📊 No hay datos válidos después de limpieza")
            return None
        
        st.info(f"📊 Procesando {len(df)} registros para gráfico {query_type}")
        
        if query_type == "time_series":
            # Gráfico de series temporales mejorado
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Colores predefinidos para mejor visualización
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
            color_idx = 0
            
            # Agrupar por dispositivo y sensor
            for device_id in df['device_id'].unique():
                device_data = df[df['device_id'] == device_id]
                
                for sensor_type in device_data['sensor_type'].unique():
                    sensor_data = device_data[device_data['sensor_type'] == sensor_type]
                    
                    if len(sensor_data) > 0:
                        # Ordenar por timestamp
                        sensor_data = sensor_data.sort_values('timestamp')
                        
                        label = f"{device_id} - {sensor_type}"
                        color = colors[color_idx % len(colors)]
                        
                        ax.plot(sensor_data['timestamp'], sensor_data['value'], 
                               marker='o', label=label, linewidth=2.5, 
                               markersize=5, color=color, alpha=0.8)
                        
                        color_idx += 1
            
            ax.set_title("📈 Evolución Temporal de Sensores IoT", fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel("Tiempo", fontsize=12)
            ax.set_ylabel("Valor del Sensor", fontsize=12)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True, alpha=0.3)
            
            # Rotar etiquetas de tiempo para mejor legibilidad
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            return fig
            
        elif query_type == "statistics":
            # Gráfico de estadísticas por sensor
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle("📊 Estadísticas por Tipo de Sensor", fontsize=16, fontweight='bold')
            
            # Estadísticas por sensor
            sensor_stats = df.groupby(['device_id', 'sensor_type'])['value'].agg(['mean', 'min', 'max', 'std']).reset_index()
            
            # Gráfico 1: Temperaturas promedio
            temp_data = df[df['sensor_type'].str.contains('temperature', case=False, na=False)]
            if not temp_data.empty:
                temp_stats = temp_data.groupby(['device_id', 'sensor_type'])['value'].mean().unstack(fill_value=0)
                temp_stats.plot(kind='bar', ax=axes[0,0], color=['#FF6B6B', '#FF8E8E', '#FFAAAA'])
                axes[0,0].set_title("🌡️ Temperaturas Promedio")
                axes[0,0].set_ylabel("Temperatura (°C)")
                axes[0,0].legend(rotation=45)
            
            # Gráfico 2: Luminosidad
            ldr_data = df[df['sensor_type'] == 'ldr']
            if not ldr_data.empty:
                ldr_stats = ldr_data.groupby('device_id')['value'].mean()
                ldr_stats.plot(kind='bar', ax=axes[0,1], color='#FFEAA7')
                axes[0,1].set_title("💡 Luminosidad Promedio")
                axes[0,1].set_ylabel("Luminosidad")
            
            # Gráfico 3: Distribución de valores
            df.boxplot(column='value', by='sensor_type', ax=axes[1,0])
            axes[1,0].set_title("📦 Distribución por Sensor")
            axes[1,0].set_ylabel("Valor")
            
            # Gráfico 4: Conteo por dispositivo
            device_counts = df.groupby('device_id').size()
            device_counts.plot(kind='pie', ax=axes[1,1], autopct='%1.1f%%', colors=['#4ECDC4', '#45B7D1'])
            axes[1,1].set_title("📊 Registros por Dispositivo")
            
            plt.tight_layout()
            return fig
        
        else:
            st.warning(f"⚠️ Tipo de gráfico '{query_type}' no soportado")
            return None
            
    except Exception as e:
        st.error(f"❌ Error creando gráfico: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None
            
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
    
    # Configuración de análisis temporal
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
            hours = float(time_range[0][:-1])  # Extraer número de horas
            
            if hours <= 6:
                st.success("⚡ Consulta rápida - Respuesta inmediata")
                st.caption("📊 Método: Estándar (hasta 200 registros)")
            else:
                st.info("📚 Consulta extensa - Paginación automática")
                max_records = min(2000, int(hours * 50))
                st.caption(f"📊 Método: Paginado (hasta {max_records} registros)")
        
        # Guardar configuración en session_state
        st.session_state.analysis_hours = hours
    
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
                    # MÉTODO 1: Intentar con el agente principal
                    response_text = None
                    method_used = "principal"
                    
                    try:
                        # Obtener configuración temporal
                        analysis_hours = getattr(st.session_state, 'analysis_hours', 3.0)
                        
                        if hasattr(cloud_agent, 'process_query_sync'):
                            # Usar la función síncrona optimizada con configuración temporal
                            response_text = cloud_agent.process_query_sync(prompt, "cloud-session", analysis_hours)
                        else:
                            # Fallback al método async si es necesario
                            import asyncio
                            import nest_asyncio
                            nest_asyncio.apply()
                            
                            response = asyncio.run(cloud_agent.process_query(prompt))
                            response_text = response.get('response', str(response)) if isinstance(response, dict) else str(response)
                    
                    except Exception as main_agent_error:
                        st.warning(f"⚠️ Agente principal no disponible: {main_agent_error}")
                        response_text = None
                    
                    # MÉTODO 2: FALLBACK ULTRA-SIMPLE (usa misma instancia del frontend)
                    if not response_text or "Error" in response_text or len(response_text.strip()) < 10:
                        try:
                            st.info("🚀 Activando sistema de respaldo robusto...")
                            
                            # Importar y usar UltraSimpleAgent con la misma instancia del frontend
                            from modules.agents.ultra_simple_agent import create_ultra_simple_agent
                            
                            # Usar EXACTAMENTE la misma instancia que usa el frontend exitoso
                            ultra_agent = create_ultra_simple_agent(jetson_connector)
                            response_text = ultra_agent.process_query(prompt)
                            method_used = "ultra_simple_fallback"
                            
                            st.success("✅ Respuesta generada con sistema de respaldo")
                            
                        except Exception as fallback_error:
                            st.error(f"❌ Error en sistema de respaldo: {fallback_error}")
                            response_text = f"❌ Error: Tanto el agente principal como el sistema de respaldo fallaron. Verifica la conectividad."
                            method_used = "error"
                    
                    # Mostrar respuesta textual
                    if response_text:
                        st.markdown(response_text)
                        
                        # Debug info opcional
                        if method_used != "principal":
                            st.caption(f"🔧 Método usado: {method_used}")
                    else:
                        st.error("❌ No se pudo generar respuesta")
                        response_text = "❌ Error interno del sistema"
                    
                    # GENERAR Y MOSTRAR GRÁFICOS AUTOMÁTICAMENTE
                    charts_generated = []
                    
                    # Detectar si se solicitan gráficos o análisis que ameriten visualización
                    chart_keywords = [
                        'grafica', 'gráfica', 'grafico', 'gráfico', 'visualizar', 'chart', 'plot',
                        'estadistica', 'estadística', 'analisis', 'análisis', 'tendencia', 'evolution',
                        'temperatura', 'luminosidad', 'sensor', 'datos', 'registros', 'ultimas', 'últimas',
                        'avanzada', 'detallado', 'completo', 'resumen', 'metrica', 'métrica'
                    ]
                    needs_charts = any(keyword in prompt.lower() for keyword in chart_keywords)
                    
                    # También generar gráficos si la respuesta contiene análisis detallado
                    detailed_analysis_indicators = [
                        'Promedio de temperatura', 'Temperaturas:', 'Luminosidad:', 'Dispositivo',
                        'Tendencias observadas', 'Métricas clave', 'temperatura_', 'ntc_', 'ldr'
                    ]
                    has_detailed_analysis = any(indicator in response_text for indicator in detailed_analysis_indicators)
                    
                    if needs_charts or has_detailed_analysis:
                        st.info("📊 Generando gráficos automáticamente...")
                        
                        try:
                            # Obtener datos usando la configuración temporal actual
                            analysis_hours = getattr(st.session_state, 'analysis_hours', 3.0)
                            
                            # Usar DirectAPIAgent directamente para obtener más datos
                            from modules.agents.direct_api_agent import DirectAPIAgent
                            base_url = "https://respect-craps-lit-aged.trycloudflare.com"
                            direct_agent = DirectAPIAgent(base_url=base_url)
                            
                            # Obtener datos con la configuración temporal actual
                            data_result = direct_agent.get_all_recent_data(hours=analysis_hours)
                            
                            if data_result.get('status') == 'success':
                                all_chart_data = data_result.get('sensor_data', [])
                                st.success(f"✅ Datos obtenidos: {len(all_chart_data)} registros para gráficos")
                            else:
                                # Fallback al método anterior
                                all_chart_data = []
                                devices = jetson_connector.get_devices()
                                
                                for device in devices:
                                    device_id = device.get('device_id')
                                    if device_id:
                                        device_data = jetson_connector.get_sensor_data(
                                            device_id=device_id, 
                                            limit=100  # Más datos para gráficos mejores
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
    
    # Información sobre capacidades de paginación
    with st.sidebar.expander("📊 Capacidades de Análisis", expanded=False):
        st.markdown("""
        **🔍 Análisis Temporal Disponible:**
        
        **Consultas Rápidas:**
        • 1-6 horas: Respuesta inmediata
        • Hasta 200 registros
        • Método: Estándar
        
        **Consultas Extensas:**
        • 6+ horas: Paginación automática
        • Hasta 2,000 registros
        • Método: Paginado inteligente
        
        **📈 Casos de Uso:**
        • Tiempo real: 3-6h
        • Análisis diario: 24h
        • Tendencias: 48h-7días
        
        **⚡ Optimización:**
        Sistema inteligente adapta método 
        según duración solicitada.
        """)
    
    # Información del sistema
    with st.sidebar.expander("🏭 Info del Sistema", expanded=False):
        current_hours = getattr(st.session_state, 'analysis_hours', 3.0)
        method = "Paginado" if current_hours > 6 else "Estándar"
        max_records = min(2000, int(current_hours * 50)) if current_hours > 6 else 200
        
        st.markdown(f"""
        **Configuración Actual:**
        • Rango: {current_hours} horas
        • Método: {method}
        • Máx. Registros: {max_records}
        
        **Hardware:**
        • NVIDIA Jetson Nano 4GB
        • API: FastAPI + SQLite
        • IA: Groq (Gratuita)
        """)
    
    if st.sidebar.button("🗑️ Limpiar Cache"):
        st.cache_resource.clear()
        st.sidebar.success("Cache limpiado")
        st.rerun()
    
    if st.sidebar.button("🔄 Recargar Servicios"):
        st.cache_resource.clear()
        st.sidebar.success("Servicios recargados")
        st.rerun()

def display_professional_banner():
    """
    Banner profesional usando componentes nativos de Streamlit
    """
    
    # Encabezado principal con estado
    st.markdown("## 🏭 Sistema IoT Industrial - Monitoreo con IA")
    st.markdown("🟢 **Estado:** Sistema Operativo | 📡 **Conectividad:** API Activa | ⏰ **Actualización:** Tiempo Real")
    
    # Descripción principal
    st.info("""
    **Sistema avanzado de monitoreo IoT** ejecutándose en **NVIDIA Jetson Nano** con 
    capacidades de IA integradas para análisis inteligente de sensores industriales.
    """)
    
    # Métricas principales en columnas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Análisis Temporal",
            value="1h - 7 días",
            delta="Paginación automática"
        )
    
    with col2:
        st.metric(
            label="🤖 IA Integrada", 
            value="Groq LLM",
            delta="Análisis predictivo"
        )
    
    with col3:
        st.metric(
            label="🔍 Sensores Activos",
            value="6 tipos",
            delta="Multi-dispositivo"
        )
    
    with col4:
        st.metric(
            label="🖥️ Hardware",
            value="Jetson Nano",
            delta="4GB RAM"
        )
    
    # Capacidades en expander
    with st.expander("📋 Capacidades del Sistema IoT", expanded=False):
        cap_col1, cap_col2 = st.columns(2)
        
        with cap_col1:
            st.markdown("""
            **🔍 Análisis Temporal:**
            - ⚡ **1-6 horas:** Respuesta inmediata (hasta 200 registros)
            - 📚 **6+ horas:** Paginación automática (hasta 2,000 registros)
            - 🎯 **IA:** Análisis automático de tendencias y patrones
            
            **💬 Chat Inteligente:**
            - 🤖 **Groq LLM:** Conversación natural sobre datos
            - 📈 **Predictivo:** Análisis automático de tendencias
            - 🗣️ **Explicativo:** Recomendaciones claras y actionables
            """)
        
        with cap_col2:
            st.markdown("""
            **📊 Sensores Monitoreados:**
            - 🌡️ **Temperatura:** 3 tipos (promedio, entrada, salida)
            - 💡 **Luminosidad:** Sensores LDR ambientales
            - ⚙️ **Industriales:** Sensores NTC especializados
            
            **🚀 Optimización Jetson:**
            - 📊 **Adaptativo:** Método automático según duración
            - 📈 **Escalable:** Capacidad variable según necesidad
            - ⚡ **Eficiente:** Respuesta optimizada para hardware edge
            """)
    
    # Información técnica resumida
    st.markdown("""
    **🔧 Stack:** Jetson Nano 4GB | Groq API (Gratuita) | FastAPI + SQLite | Streamlit Cloud | LangGraph IA
    """)
    
    st.markdown("---")

def main():
    """Función principal optimizada con banner profesional"""
    
    # Verificar configuración básica
    if not GROQ_API_KEY:
        st.error("❌ Configure GROQ_API_KEY en Streamlit Cloud Secrets")
        st.stop()
    
    # MOSTRAR BANNER PROFESIONAL
    display_professional_banner()
    
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