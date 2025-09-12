#!/usr/bin/env python3
"""
Versión simplificada y robusta del manejo de reportes para Streamlit
"""

def render_report_section(prompt, response, response_text, conversation_id):
    """
    Renderiza la sección de reportes de manera robusta
    """
    import streamlit as st
    
    # Verificar si es una solicitud de reporte
    report_keywords = ["reporte", "informe", "ejecutivo", "descarga", "pdf", "csv", "excel", "exporta"]
    is_report_request = any(keyword.lower() in prompt.lower() for keyword in report_keywords)
    
    if not is_report_request:
        return
    
    st.markdown("---")
    st.markdown("### 📊 Generar Reporte Descargable")
    
    # Detectar especificación del reporte con manejo de errores
    try:
        report_spec = st.session_state.report_generator.parse_user_request_to_spec(prompt, response)
    except Exception as e:
        st.error(f"❌ Error parseando solicitud: {str(e)}")
        return
    
    if not report_spec:
        st.warning("⚠️ No se pudo interpretar la solicitud de reporte.")
        return
    
    # Mostrar información del reporte
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info(f"🎯 **Reporte detectado:** {report_spec.get('title', 'Reporte IoT')}")
        st.write(f"📱 **Dispositivo:** {report_spec.get('device_id', 'N/A')}")
        st.write(f"🔬 **Sensor:** {report_spec.get('sensor', 'N/A')}")
        st.write(f"📈 **Gráfico:** {report_spec.get('chart', {}).get('type', 'line')}")
        st.write(f"📄 **Formato:** {report_spec.get('format', 'pdf').upper()}")
    
    with col2:
        # Estado del reporte para esta conversación
        report_state_key = f"report_state_{conversation_id}"
        if report_state_key not in st.session_state:
            st.session_state[report_state_key] = "ready"  # ready, generating, completed, error
        
        report_state = st.session_state[report_state_key]
        
        # Botón de generar
        if report_state == "ready":
            if st.button("📥 Generar y Descargar", type="primary", key=f"generate_{conversation_id}"):
                st.session_state[report_state_key] = "generating"
                st.rerun()
        
        elif report_state == "generating":
            # Mostrar progreso y generar reporte
            with st.spinner("Generando reporte..."):
                try:
                    st.info("🔧 Iniciando generación...")
                    
                    # Generar el reporte
                    file_bytes, filename = st.session_state.report_generator.generate_report(
                        report_spec, response, response_text
                    )
                    
                    if file_bytes and len(file_bytes) > 0:
                        # Determinar MIME type
                        mime_types = {
                            'pdf': 'application/pdf',
                            'csv': 'text/csv',
                            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            'png': 'image/png',
                            'html': 'text/html'
                        }
                        mime_type = mime_types.get(report_spec.get('format', 'pdf'), 'application/octet-stream')
                        
                        # Guardar en session state
                        st.session_state[f'report_data_{conversation_id}'] = {
                            'bytes': file_bytes,
                            'filename': filename,
                            'mime_type': mime_type
                        }
                        
                        # Cambiar estado a completado
                        st.session_state[report_state_key] = "completed"
                        st.success(f"✅ Reporte generado: {filename}")
                        st.rerun()
                    else:
                        st.session_state[report_state_key] = "error"
                        st.error("❌ Error: Archivo vacío generado")
                        st.rerun()
                        
                except Exception as e:
                    st.session_state[report_state_key] = "error"
                    st.error(f"❌ Error: {str(e)}")
                    st.rerun()
        
        elif report_state == "error":
            st.error("❌ Error en generación")
            if st.button("🔄 Reintentar", key=f"retry_{conversation_id}"):
                st.session_state[report_state_key] = "ready"
                st.rerun()
        
        elif report_state == "completed":
            st.success("✅ Reporte completado")
    
    # Mostrar botón de descarga si el reporte existe
    report_key = f'report_data_{conversation_id}'
    if report_key in st.session_state:
        report_data = st.session_state[report_key]
        
        st.markdown("---")
        st.markdown("### 📥 **Descarga Disponible**")
        
        col_info, col_download = st.columns([2, 1])
        
        with col_info:
            st.success("✅ **Reporte listo para descarga**")
            st.write(f"📄 **Archivo:** {report_data['filename']}")
            st.write(f"📊 **Tamaño:** {len(report_data['bytes']):,} bytes")
        
        with col_download:
            st.download_button(
                label="⬇️ **DESCARGAR**",
                data=report_data['bytes'],
                file_name=report_data['filename'],
                mime=report_data['mime_type'],
                use_container_width=True,
                key=f"download_{conversation_id}",
                type="primary"
            )
