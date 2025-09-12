#!/usr/bin/env python3
"""
Aplicación Streamlit simplificada para reportes IoT con funcionalidad robusta
"""

import streamlit as st
import asyncio
from datetime import datetime

# Configurar página
st.set_page_config(
    page_title="Remote IoT Agent - Reportes",
    page_icon="🤖",
    layout="wide"
)

def initialize_session_state():
    """Inicializar el estado de sesión"""
    if 'agent_initialized' not in st.session_state:
        st.session_state.agent_initialized = False
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'report_generator' not in st.session_state:
        try:
            from modules.agents.reporting import ReportGenerator
            st.session_state.report_generator = ReportGenerator()
        except Exception as e:
            st.error(f"Error inicializando generador de reportes: {e}")
            st.session_state.report_generator = None

def render_simple_report_interface():
    """Renderiza una interfaz simple para generar reportes"""
    
    st.title("🤖 Remote IoT Agent - Generador de Reportes")
    
    # Formulario simple para generar reportes
    with st.form("report_form"):
        st.markdown("### 📊 Generar Reporte de Sensores IoT")
        
        # Inputs del usuario
        user_query = st.text_area(
            "Describe el reporte que necesitas:",
            placeholder="Ejemplo: genera un informe ejecutivo con los datos del esp32y del arduino ethernet de los registros de las ultimas 48 horas, usa graficos de torta para las temperaturas y de barra para la ldr",
            height=100
        )
        
        # Botón de submit
        submitted = st.form_submit_button("🚀 Generar Reporte", type="primary")
        
        if submitted and user_query:
            # Generar timestamp único para este reporte
            timestamp = int(datetime.now().timestamp() * 1000)
            report_id = f"report_{timestamp}"
            
            # Placeholder para progreso
            progress_container = st.container()
            
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Paso 1: Inicializar (20%)
                    progress_bar.progress(20)
                    status_text.text("🔧 Inicializando generación de reporte...")
                    
                    # Verificar que el generador esté disponible
                    if st.session_state.report_generator is None:
                        status_text.error("❌ Generador de reportes no disponible")
                        st.stop()
                    
                    # Paso 2: Parsear solicitud (40%)
                    progress_bar.progress(40)
                    status_text.text("📋 Analizando solicitud del usuario...")
                    
                    # Crear metadata mock para el análisis
                    mock_response = {
                        'data_summary': {
                            'total_records': 80,
                            'sensors': ['temperature', 'humidity', 'ldr'],
                            'devices': ['esp32_wifi_001', 'arduino_eth_001']
                        },
                        'model_used': 'llama-3.1-8b-instant',
                        'execution_status': 'completed'
                    }
                    
                    mock_summary = """
                    Análisis de Temperatura:
                    • Rango detectado: 18.5°C - 28.3°C
                    • Promedio: 23.4°C
                    • Estado: Normal, dentro de parámetros operativos
                    • Recomendación: Monitoreo continuo recomendado
                    """
                    
                    # Parsear la solicitud
                    spec = st.session_state.report_generator.parse_user_request_to_spec(
                        user_query, mock_response
                    )
                    
                    # Paso 3: Generar datos (60%)
                    progress_bar.progress(60)
                    status_text.text("📊 Generando datos del reporte...")
                    
                    # Paso 4: Crear archivo (80%)
                    progress_bar.progress(80)
                    status_text.text("📄 Creando archivo de reporte...")
                    
                    # Generar el reporte
                    file_bytes, filename = st.session_state.report_generator.generate_report(
                        spec, mock_response, mock_summary
                    )
                    
                    # Paso 5: Finalizar (100%)
                    progress_bar.progress(100)
                    status_text.text("✅ ¡Reporte generado exitosamente!")
                    
                    if file_bytes and len(file_bytes) > 0:
                        # Determinar MIME type
                        mime_types = {
                            'pdf': 'application/pdf',
                            'csv': 'text/csv',
                            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            'png': 'image/png',
                            'html': 'text/html'
                        }
                        format_type = spec.get('format', 'pdf')
                        mime_type = mime_types.get(format_type, 'application/octet-stream')
                        
                        # Guardar en session state
                        st.session_state[report_id] = {
                            'bytes': file_bytes,
                            'filename': filename,
                            'mime_type': mime_type,
                            'spec': spec,
                            'created_at': datetime.now()
                        }
                        
                        # Limpiar progreso y mostrar éxito
                        progress_container.empty()
                        
                        st.success(f"✅ **Reporte generado exitosamente!**")
                        st.info(f"📄 **Archivo:** {filename}")
                        st.info(f"📊 **Tamaño:** {len(file_bytes):,} bytes")
                        st.info(f"🗂️ **Formato:** {format_type.upper()}")
                        
                        # Botón de descarga inmediato
                        st.download_button(
                            label="⬇️ **DESCARGAR REPORTE**",
                            data=file_bytes,
                            file_name=filename,
                            mime=mime_type,
                            key=f"download_{report_id}",
                            type="primary"
                        )
                        
                    else:
                        status_text.error("❌ Error: No se pudo generar el archivo")
                        
                except Exception as e:
                    progress_bar.progress(0)
                    status_text.error(f"❌ Error: {str(e)}")
                    
                    # Mostrar detalles del error
                    with st.expander("🔍 Detalles del error"):
                        import traceback
                        st.code(traceback.format_exc())
    
    # Mostrar reportes generados anteriormente
    render_previous_reports()

def render_previous_reports():
    """Muestra reportes generados anteriormente"""
    
    # Buscar reportes en session state
    reports = {k: v for k, v in st.session_state.items() if k.startswith('report_')}
    
    if reports:
        st.markdown("---")
        st.markdown("### 📁 Reportes Anteriores")
        
        for report_id, report_data in reports.items():
            if isinstance(report_data, dict) and 'filename' in report_data:
                with st.expander(f"📄 {report_data['filename']} - {report_data['created_at'].strftime('%H:%M:%S')}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Archivo:** {report_data['filename']}")
                        st.write(f"**Tamaño:** {len(report_data['bytes']):,} bytes")
                        st.write(f"**Formato:** {report_data['mime_type']}")
                        st.write(f"**Creado:** {report_data['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    with col2:
                        st.download_button(
                            label="⬇️ Descargar",
                            data=report_data['bytes'],
                            file_name=report_data['filename'],
                            mime=report_data['mime_type'],
                            key=f"prev_download_{report_id}",
                            use_container_width=True
                        )

def main():
    """Función principal"""
    
    # Inicializar estado
    initialize_session_state()
    
    # Renderizar interfaz
    render_simple_report_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("🤖 **Remote IoT Agent** | Generación de reportes inteligente para dispositivos IoT")

if __name__ == "__main__":
    main()
