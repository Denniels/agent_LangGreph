#!/usr/bin/env python3
"""
APLICACIÓN STREAMLIT ROBUSTA CON PESTAÑAS SEPARADAS
==================================================

Versión mejorada que separa funcionalidades:
- Pestaña 1: Chat IoT Agent
- Pestaña 2: Generador de Reportes

Esto resuelve los conflictos de estado y garantiza funcionalidad independiente.
"""

import streamlit as st
import sys
import os
import uuid
from datetime import datetime, timedelta
import traceback

# Configuración de página
st.set_page_config(
    page_title="Agente IoT Avanzado - Sistema Completo",
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
    from modules.agents.reporting import ReportGenerator
    from modules.utils.usage_tracker import usage_tracker
    from modules.utils.streamlit_usage_display import (
        display_usage_metrics, 
        display_usage_alert,
        display_model_limits_info
    )
    
    # Variables de configuración
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    JETSON_API_URL = "https://integrate-del-peers-jefferson.trycloudflare.com"
    
except ImportError as e:
    st.error(f"❌ Error importando módulos: {str(e)}")
    st.stop()

# Función para inicializar servicios
@st.cache_resource
def initialize_services():
    """Inicializar servicios globales con conexiones correctas"""
    try:
        # Crear conector de Jetson
        jetson_connector = JetsonAPIConnector(JETSON_API_URL)
        
        # Crear agente completo (no solo Groq)
        cloud_agent = CloudIoTAgent()
        
        # Crear generador de reportes CON conexión a Jetson
        report_generator = ReportGenerator(jetson_connector=jetson_connector)
        
        return cloud_agent, jetson_connector, report_generator
    except Exception as e:
        st.error(f"❌ Error inicializando servicios: {str(e)}")
        return None, None, None

# Función de procesamiento de consultas (compartida)
async def process_user_query(query: str):
    """Procesar consulta del usuario usando CloudIoTAgent completo"""
    try:
        cloud_agent, jetson_connector, _ = initialize_services()
        
        if not cloud_agent:
            return {"success": False, "error": "Agente IoT no disponible"}
        
        # Usar CloudIoTAgent completo (NO solo Groq)
        response = await cloud_agent.process_query(query)
        
        return response
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "execution_status": "failed"
        }

# ===============================
# PESTAÑA 1: CHAT IoT AGENT
# ===============================

def render_chat_tab():
    """Renderizar pestaña de chat"""
    
    st.header("💬 Chat con Agente IoT")
    st.markdown("Consulta datos de sensores en tiempo real y obtén análisis inteligentes.")
    
    # Inicializar historial de chat
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Mostrar historial de chat
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Mostrar metadata si existe
            if "metadata" in message:
                with st.expander("📊 Detalles técnicos"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Registros procesados",
                            message["metadata"].get("data_summary", {}).get("total_records", 0)
                        )
                    
                    with col2:
                        st.metric(
                            "Sensores activos",
                            len(message["metadata"].get("data_summary", {}).get("sensors", []))
                        )
                    
                    with col3:
                        st.metric(
                            "Dispositivos conectados",
                            len(message["metadata"].get("data_summary", {}).get("devices", []))
                        )
    
    # Input de chat
    if prompt := st.chat_input("Escribe tu consulta sobre sensores IoT..."):
        
        # Agregar mensaje del usuario
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.write(prompt)
        
        # Procesar consulta
        with st.chat_message("assistant"):
            with st.spinner("🤖 Analizando sensores..."):
                import asyncio
                try:
                    # Ejecutar función async en Streamlit
                    response = asyncio.run(process_user_query(prompt))
                except Exception as e:
                    response = {"success": False, "error": str(e)}
            
            if response.get("success", False):
                response_text = response.get("response", "No se pudo generar respuesta")
                st.write(response_text)
                
                # Agregar mensaje del asistente con metadata
                st.session_state.chat_messages.append({
                    "role": "assistant", 
                    "content": response_text,
                    "metadata": response
                })
                
                # Verificar si es solicitud de reporte
                report_keywords = ["reporte", "informe", "ejecutivo", "descarga", "pdf", "csv", "excel", "exporta"]
                is_report_request = any(keyword.lower() in prompt.lower() for keyword in report_keywords)
                
                if is_report_request:
                    st.info("📊 **¿Necesitas un reporte descargable?** Ve a la pestaña '📊 Generador de Reportes' para crear reportes en PDF, CSV o Excel.")
                
            else:
                error_msg = f"❌ Error: {response.get('error', 'Error desconocido')}"
                st.error(error_msg)
                st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})

# ===============================
# PESTAÑA 2: GENERADOR DE REPORTES
# ===============================

def render_reports_tab():
    """Renderizar pestaña de generación de reportes"""
    
    st.header("📊 Generador de Reportes IoT")
    st.markdown("Crea reportes ejecutivos profesionales con gráficos y análisis detallados.")
    
    # Inicializar servicios
    groq_agent, jetson_connector, report_generator = initialize_services()
    
    if not report_generator:
        st.error("❌ Error: No se pudo inicializar el generador de reportes")
        st.stop()
    
    # Sección de configuración del reporte
    st.subheader("🔧 Configuración del Reporte")
    
    with st.form("report_config"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📱 Dispositivos**")
            device_esp32 = st.checkbox("ESP32 WiFi 001 (192.168.0.105)", value=True, 
                                       help="Sensores: ntc_entrada, ntc_salida, ldr")
            device_arduino = st.checkbox("Arduino Ethernet 001 (192.168.0.106)", value=True,
                                         help="Sensores: t1, t2, avg (SOLO temperatura)")
            
            st.markdown("**🔬 Sensores**")
            sensor_temperature = st.checkbox("Temperatura", value=True, 
                                             help="Disponible en ambos dispositivos")
            
            # Solo mostrar LDR si ESP32 está seleccionado
            if device_esp32:
                sensor_ldr = st.checkbox("LDR (Luz)", value=True, 
                                         help="SOLO disponible en ESP32 WiFi")
            else:
                sensor_ldr = False
                st.info("ℹ️ LDR solo disponible con ESP32 WiFi")
                if device_arduino and not device_esp32:
                    st.info("ℹ️ Arduino Ethernet SOLO tiene sensores de temperatura (t1, t2, avg)")
        
        with col2:
            st.markdown("**📈 Tipos de Gráficos**")
            temp_chart = st.selectbox("Gráfico para Temperatura", ["pie", "bar", "line"], index=0)
            ldr_chart = st.selectbox("Gráfico para LDR", ["bar", "pie", "line"], index=0)
            
            st.markdown("**📄 Configuración**")
            report_format = st.selectbox("Formato de salida", ["pdf", "csv", "xlsx", "html"], index=0)
            time_range = st.selectbox("Período de tiempo", ["24 horas", "48 horas", "7 días"], index=1)
        
        # Área de texto para solicitud personalizada
        st.markdown("**💬 Solicitud Personalizada (Opcional)**")
        custom_request = st.text_area(
            "Describe qué tipo de reporte necesitas:",
            value="genera un informe ejecutivo con los datos del esp32y del arduino ethernet de los registros de las ultimas 48 horas, usa graficos de torta para las temperaturas y de barra para la ldr",
            height=100
        )
        
        # Botón de generación
        generate_button = st.form_submit_button("🚀 Generar Reporte", type="primary", use_container_width=True)
    
    # Procesar generación de reporte
    if generate_button:
        
        # Crear configuración basada en selecciones
        selected_devices = []
        if device_esp32:
            selected_devices.append("esp32_wifi_001")
        if device_arduino:
            selected_devices.append("arduino_eth_001")
        
        selected_sensors = []
        if sensor_temperature:
            selected_sensors.append("temperature")
        if sensor_ldr:
            selected_sensors.append("ldr")
        
        chart_types = {}
        if sensor_temperature:
            chart_types["temperature"] = temp_chart
        if sensor_ldr:
            chart_types["ldr"] = ldr_chart
        
        # Validar configuración
        if not selected_devices:
            st.error("❌ Debes seleccionar al menos un dispositivo")
            st.stop()
        
        if not selected_sensors:
            st.error("❌ Debes seleccionar al menos un sensor")
            st.stop()
        
        # Crear especificación del reporte
        report_spec = {
            "title": "Reporte Ejecutivo IoT - Múltiples Dispositivos",
            "devices": selected_devices,
            "sensors": selected_sensors,
            "chart_types": chart_types,
            "format": report_format,
            "time_range": {
                "description": time_range,
                "hours": 48 if time_range == "48 horas" else (24 if time_range == "24 horas" else 168)
            }
        }
        
        # Obtener datos reales del Jetson API
        try:
            status_text = st.empty()
            status_text.text("🔍 Obteniendo datos reales de sensores...")
            
            # Obtener datos reales usando el conector (función síncrona)
            real_data_result = jetson_connector.get_sensor_data(limit=100)
            
            if real_data_result and len(real_data_result) > 0:
                sensor_data = real_data_result
                
                # Filtrar datos según dispositivos seleccionados
                filtered_data = []
                for record in sensor_data:
                    if record.get("device_id") in selected_devices:
                        filtered_data.append(record)
                
                # Crear metadata con datos reales
                metadata = {
                    "data_summary": {
                        "total_records": len(filtered_data),
                        "sensors": selected_sensors,
                        "devices": selected_devices,
                        "real_data": True,
                        "latest_readings": {}
                    },
                    "model_used": "llama-3.1-8b-instant",
                    "execution_status": "completed"
                }
                
                # Obtener últimas lecturas por dispositivo
                device_latest = {}
                for record in filtered_data:
                    device_id = record.get("device_id")
                    if device_id not in device_latest:
                        device_latest[device_id] = record
                    elif record.get("timestamp", "") > device_latest[device_id].get("timestamp", ""):
                        device_latest[device_id] = record
                
                # Construir summary con datos reales
                summary_parts = [
                    f"ANÁLISIS EJECUTIVO DE SENSORES IOT - {time_range.upper()}",
                    "",
                    f"Dispositivos monitoreados: {', '.join(selected_devices)}",
                    f"Sensores analizados: {', '.join(selected_sensors)}",
                    f"Total de registros procesados: {len(filtered_data)}",
                    "",
                    f"Durante el período de {time_range} se monitorearon los dispositivos seleccionados:",
                    ""
                ]
                
                # Agregar información específica por dispositivo
                for device_id, latest in device_latest.items():
                    if device_id == "esp32_wifi_001" and device_esp32:
                        summary_parts.append(f"ESP32 WiFi 001 (192.168.0.105): {len([r for r in filtered_data if r.get('device_id') == device_id])} registros")
                        if latest:
                            summary_parts.append(f"  • Última lectura: {latest.get('timestamp', 'N/A')}")
                            if 'ntc_entrada' in latest:
                                summary_parts.append(f"  • NTC entrada: {latest['ntc_entrada']}°C")
                            if 'ntc_salida' in latest:
                                summary_parts.append(f"  • NTC salida: {latest['ntc_salida']}°C")
                            if 'ldr' in latest:
                                summary_parts.append(f"  • LDR: {latest['ldr']}")
                    
                    elif device_id == "arduino_eth_001" and device_arduino:
                        summary_parts.append(f"Arduino Ethernet 001 (192.168.0.106): {len([r for r in filtered_data if r.get('device_id') == device_id])} registros")
                        if latest:
                            summary_parts.append(f"  • Última lectura: {latest.get('timestamp', 'N/A')}")
                            if 't1' in latest:
                                summary_parts.append(f"  • Temperatura T1: {latest['t1']}°C")
                            if 't2' in latest:
                                summary_parts.append(f"  • Temperatura T2: {latest['t2']}°C")
                            if 'avg' in latest:
                                summary_parts.append(f"  • Promedio: {latest['avg']}°C")
                
                summary_parts.extend([
                    "",
                    "RECOMENDACIONES:",
                    "• Continuar monitoreo automático",
                    "• Revisar tendencias identificadas",
                    "• Mantener calibración de sensores"
                ])
                
                summary_text = "\n".join(summary_parts)
                
            else:
                # Fallback a datos simulados si no hay datos reales
                st.warning("⚠️ No se pudieron obtener datos reales, usando configuración básica")
                metadata = {
                    "data_summary": {
                        "total_records": 0,
                        "sensors": selected_sensors,
                        "devices": selected_devices,
                        "real_data": False
                    },
                    "model_used": "llama-3.1-8b-instant",
                    "execution_status": "no_data"
                }
                
                summary_text = f"""
                ANÁLISIS EJECUTIVO DE SENSORES IOT - {time_range.upper()}
                
                Dispositivos configurados: {', '.join(selected_devices)}
                Sensores configurados: {', '.join(selected_sensors)}
                
                ⚠️ No se encontraron datos en el período especificado.
                
                CONFIGURACIÓN DE DISPOSITIVOS:
                """ + ("• ESP32 WiFi 001 (192.168.0.105): ntc_entrada, ntc_salida, ldr\n" if device_esp32 else "") + \
                      ("• Arduino Ethernet 001 (192.168.0.106): t1, t2, avg (SOLO temperatura)\n" if device_arduino 
                       else "") + """
                
                RECOMENDACIONES:
                • Verificar conectividad de dispositivos
                • Revisar configuración de red
                • Confirmar funcionamiento de sensores
                """
                
        except Exception as e:
            st.error(f"❌ Error obteniendo datos reales: {str(e)}")
            # Fallback a configuración básica
            metadata = {
                "data_summary": {
                    "total_records": 0,
                    "sensors": selected_sensors,
                    "devices": selected_devices,
                    "real_data": False,
                    "error": str(e)
                },
                "model_used": "llama-3.1-8b-instant",
                "execution_status": "error"
            }
        
        # Mostrar progreso
        with st.container():
            st.markdown("---")
            st.subheader("🔄 Generando Reporte...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Paso 1: Parsing
                status_text.text("📋 Parseando configuración...")
                progress_bar.progress(20)
                
                # Paso 2: Generación de datos
                status_text.text("📊 Generando datos del reporte...")
                progress_bar.progress(40)
                
                # Paso 3: Creación de gráficos
                status_text.text("📈 Creando gráficos...")
                progress_bar.progress(60)
                
                # Paso 4: Generación del archivo
                status_text.text("📄 Generando archivo final...")
                progress_bar.progress(80)
                
                # Generar reporte
                file_bytes, filename = report_generator.generate_report(
                    report_spec, metadata, summary_text
                )
                
                progress_bar.progress(100)
                status_text.text("✅ ¡Reporte generado exitosamente!")
                
                # Mostrar resultados
                st.success(f"🎉 **¡Reporte generado exitosamente!**")
                
                # Información del archivo
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📄 Archivo", filename)
                
                with col2:
                    st.metric("📊 Tamaño", f"{len(file_bytes):,} bytes")
                
                with col3:
                    st.metric("🗂️ Formato", report_format.upper())
                
                # Botón de descarga
                st.markdown("---")
                
                # Determinar MIME type
                mime_types = {
                    'pdf': 'application/pdf',
                    'csv': 'text/csv',
                    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'html': 'text/html'
                }
                mime_type = mime_types.get(report_format, 'application/octet-stream')
                
                st.download_button(
                    label="⬇️ **DESCARGAR REPORTE**",
                    data=file_bytes,
                    file_name=filename,
                    mime=mime_type,
                    use_container_width=True,
                    type="primary"
                )
                
                # Detalles técnicos
                with st.expander("🔍 Detalles Técnicos del Reporte"):
                    st.json({
                        "especificacion": report_spec,
                        "dispositivos": selected_devices,
                        "sensores": selected_sensors,
                        "graficos": chart_types,
                        "archivo": {
                            "nombre": filename,
                            "tamaño_bytes": len(file_bytes),
                            "formato": report_format,
                            "mime_type": mime_type
                        }
                    })
                
            except Exception as e:
                st.error(f"❌ **Error generando reporte:** {str(e)}")
                st.error("🔍 **Detalles del error:**")
                st.code(traceback.format_exc())

# ===============================
# PESTAÑA 3: USO DE API
# ===============================

def render_usage_tab():
    """Renderizar pestaña de uso de API"""
    
    st.header("📈 Seguimiento de Uso de API")
    st.markdown("Monitorea tu uso diario de las APIs de Groq y evita sobrepasar los límites.")
    
    try:
        # Obtener modelo actual del agente
        cloud_agent, _, _ = initialize_services()
        current_model = "llama-3.1-8b-instant"  # Modelo por defecto
        
        if cloud_agent:
            current_model = cloud_agent.groq_model
        
        # Obtener información de uso del modelo actual
        usage_info = usage_tracker.get_usage_info(current_model)
        
        # Mostrar alerta si es necesaria
        display_usage_alert(usage_info)
        
        # Mostrar métricas principales
        display_usage_metrics(usage_info, "main_usage")
        
        st.markdown("---")
        
        # Sección de resumen diario
        st.subheader("📊 Resumen Diario")
        
        daily_summary = usage_tracker.get_daily_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🔥 Total Consultas Hoy",
                f"{daily_summary['total_requests_today']:,}",
                help="Total de consultas realizadas hoy"
            )
        
        with col2:
            st.metric(
                "🎯 Total Tokens Hoy",
                f"{daily_summary['total_tokens_today']:,}",
                help="Total de tokens utilizados hoy"
            )
        
        with col3:
            st.metric(
                "🤖 Modelos Usados",
                daily_summary['models_used_today'],
                help="Número de modelos diferentes utilizados"
            )
        
        with col4:
            from modules.utils.streamlit_usage_display import get_time_until_reset
            st.metric(
                "⏰ Reset en",
                get_time_until_reset(),
                help="Tiempo hasta el próximo reset diario"
            )
        
        # Sección de todos los modelos
        st.markdown("---")
        st.subheader("🤖 Uso por Modelo")
        
        all_models_usage = usage_tracker.get_all_models_usage()
        
        # Crear tabla de modelos
        model_data = []
        for model_id, model_info in all_models_usage.items():
            model_data.append({
                "Modelo": model_info["model_description"],
                "Consultas": f"{model_info['requests_used']:,}/{model_info['requests_limit']:,}",
                "Tokens": f"{model_info['tokens_used']:,}/{model_info['tokens_limit']:,}",
                "Uso %": f"{model_info['requests_percentage']:.1f}%",
                "Estado": {
                    "normal": "✅ Normal",
                    "warning": "⚠️ Advertencia", 
                    "critical": "🚨 Crítico"
                }.get(model_info["status"], "❓ Desconocido"),
                "Disponible": "Sí" if model_info["can_make_request"] else "No"
            })
        
        if model_data:
            import pandas as pd
            df = pd.DataFrame(model_data)
            st.dataframe(df, use_container_width=True)
        
        # Información de límites
        st.markdown("---")
        display_model_limits_info()
        
        # Botones de control
        st.markdown("---")
        st.subheader("🔧 Controles")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Actualizar Datos", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("📊 Health Check", use_container_width=True):
                with st.spinner("Verificando estado..."):
                    import asyncio
                    health = asyncio.run(cloud_agent.health_check()) if cloud_agent else {}
                    
                    if health.get("overall_status") == "healthy":
                        st.success("✅ Sistema saludable")
                    else:
                        st.warning("⚠️ Sistema con problemas")
                    
                    with st.expander("Detalles de Health Check"):
                        st.json(health)
        
        with col3:
            # Botón de reset solo para desarrollo/testing
            if st.button("🚨 Reset Contadores (Dev)", use_container_width=True, help="Solo para desarrollo - no usar en producción"):
                if st.button("⚠️ Confirmar Reset", type="secondary"):
                    usage_tracker.force_reset()
                    st.success("✅ Contadores reseteados")
                    st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error mostrando información de uso: {str(e)}")
        st.write("**Detalles del error:**")
        st.code(traceback.format_exc())

# ===============================
# SIDEBAR Y NAVEGACIÓN PRINCIPAL
# ===============================

def render_sidebar():
    """Renderizar sidebar con información del sistema"""
    
    with st.sidebar:
        st.title("🤖 Agente IoT Avanzado")
        st.markdown("---")
        
        # Estado del sistema
        st.subheader("📊 Estado del Sistema")
        
        # Verificar servicios
        groq_agent, jetson_connector, report_generator = initialize_services()
        
        if groq_agent:
            st.success("✅ Agente Groq")
        else:
            st.error("❌ Agente Groq")
            
        if jetson_connector:
            st.success("✅ API Jetson")
        else:
            st.error("❌ API Jetson")
            
        if report_generator:
            st.success("✅ Generador de Reportes")
        else:
            st.error("❌ Generador de Reportes")
        
        st.markdown("---")
        
        # Información de configuración
        st.subheader("⚙️ Configuración")
        st.info(f"**API URL:** {JETSON_API_URL}")
        st.info(f"**Modelo:** llama-3.1-8b-instant")
        st.info(f"**Versión:** Pestañas Separadas v1.0")
        
        st.markdown("---")
        
        # Información de uso de API
        st.subheader("📊 Uso de API")
        try:
            current_model = "llama-3.1-8b-instant"
            if groq_agent:
                current_model = groq_agent.groq_model
            
            usage_info = usage_tracker.get_usage_info(current_model)
            
            # Mostrar métricas compactas
            st.metric(
                "🔥 Consultas",
                f"{usage_info['requests_used']}/{usage_info['requests_limit']}",
                delta=f"{usage_info['requests_percentage']:.1f}% usado"
            )
            
            # Estado visual
            status = usage_info.get("status", "normal")
            if status == "critical":
                st.error("🚨 Uso crítico")
            elif status == "warning":
                st.warning("⚠️ Uso alto")
            else:
                st.success("✅ Uso normal")
                
            # Enlace a pestaña de detalles
            st.caption("👆 Ve a la pestaña 'Uso de API' para más detalles")
            
        except Exception as e:
            st.error("❌ Error cargando uso de API")
        
        st.markdown("---")
        
        # Estadísticas de sesión
        st.subheader("📈 Estadísticas")
        
        if "chat_messages" in st.session_state:
            st.metric("💬 Mensajes de Chat", len(st.session_state.chat_messages))
        else:
            st.metric("💬 Mensajes de Chat", 0)
        
        st.metric("⏰ Sesión Iniciada", datetime.now().strftime("%H:%M"))
        
        # Botón de reset
        if st.button("🔄 Reiniciar Sesión", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ===============================
# APLICACIÓN PRINCIPAL
# ===============================

def main():
    """Función principal de la aplicación"""
    
    # Renderizar sidebar
    render_sidebar()
    
    # Título principal
    st.title("🤖 Agente IoT Avanzado - Sistema Completo")
    st.markdown("**Análisis inteligente de sensores IoT con generación de reportes profesionales**")
    
    # Crear pestañas
    tab1, tab2, tab3 = st.tabs(["💬 Chat IoT Agent", "📊 Generador de Reportes", "📈 Uso de API"])
    
    with tab1:
        render_chat_tab()
    
    with tab2:
        render_reports_tab()
    
    with tab3:
        render_usage_tab()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "🤖 Agente IoT Avanzado - Sistema de pestañas separadas para máxima robustez"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()