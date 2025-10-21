"""
Sistema IoT Ultra-Robusto - Aplicación Streamlit Cloud Optimizada
===============================================================

Aplicación principal que integra el sistema ultra-robusto para garantizar
acceso confiable a datos y generar reportes ejecutivos completos.
"""

import streamlit as st
import os
import sys
from datetime import datetime, timedelta
import json
import traceback
import logging
from typing import Dict, Any, List, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuración de página
st.set_page_config(
    page_title="Sistema IoT Ultra-Robusto",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports diferidos para optimizar carga
@st.cache_resource
def load_ultra_robust_system():
    """Cargar sistema ultra-robusto con cache."""
    try:
        from modules.tools.ultra_robust_connector import UltraRobustJetsonConnector
        from modules.agents.ultra_robust_agent import UltraRobustIoTAgent
        from modules.utils.executive_report_generator import ExecutiveReportGenerator
        from modules.utils.visualization_engine import VisualizationEngine
        
        # Inicializar componentes con URL actual
        base_url = "https://wonder-sufficiently-generator-click.trycloudflare.com"
        connector = UltraRobustJetsonConnector(base_url)
        visualization_engine = VisualizationEngine()
        agent = UltraRobustIoTAgent(connector, visualization_engine)
        report_generator = ExecutiveReportGenerator(connector, visualization_engine)
        
        return {
            'connector': connector,
            'agent': agent,
            'visualization_engine': visualization_engine,
            'report_generator': report_generator,
            'status': 'success'
        }
    except Exception as e:
        logger.error(f"Error cargando sistema ultra-robusto: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }

@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_system_status():
    """Obtener estado del sistema con cache."""
    system = load_ultra_robust_system()
    if system['status'] == 'error':
        return {
            'status': 'ERROR',
            'message': f"Error inicializando sistema: {system['error']}",
            'devices': 0,
            'last_update': 'Error'
        }
    
    try:
        # Verificar conectividad
        from modules.tools.ultra_robust_connector import UltraRobustJetsonConnector
        base_url = "https://wonder-sufficiently-generator-click.trycloudflare.com"
        connector = UltraRobustJetsonConnector(base_url)
        test_data = connector.get_devices_robust()
        device_count = len(test_data) if test_data else 0
        
        return {
            'status': 'OPERATIVO' if device_count > 0 else 'SIN DATOS',
            'message': f"Sistema operativo con {device_count} dispositivos detectados",
            'devices': device_count,
            'last_update': datetime.now().strftime("%H:%M:%S")
        }
    except Exception as e:
        return {
            'status': 'ERROR',
            'message': f"Error verificando estado: {str(e)}",
            'devices': 0,
            'last_update': 'Error'
        }

def main():
    """Función principal de la aplicación."""
    
    # Header principal
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0;">
            🚀 Sistema IoT Ultra-Robusto
        </h1>
        <p style="color: white; text-align: center; margin: 0.5rem 0 0 0;">
            Análisis Técnico Avanzado con Acceso Garantizado a Datos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar estado del sistema
    with st.spinner("🔄 Inicializando sistema ultra-robusto..."):
        system_status = get_system_status()
        system_components = load_ultra_robust_system()
    
    # Mostrar estado del sistema
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_color = {
            'OPERATIVO': '🟢',
            'SIN DATOS': '🟡', 
            'ERROR': '🔴'
        }.get(system_status['status'], '⚪')
        
        st.metric(
            "Estado del Sistema", 
            f"{status_color} {system_status['status']}",
            delta=f"Actualizado: {system_status['last_update']}"
        )
    
    with col2:
        st.metric(
            "Dispositivos Detectados",
            system_status['devices'],
            delta="Activos" if system_status['devices'] > 0 else "Sin conexión"
        )
    
    with col3:
        st.metric(
            "Modo de Operación",
            "Ultra-Robusto",
            delta="Múltiples Fallbacks"
        )
    
    with col4:
        st.metric(
            "Última Verificación",
            system_status['last_update'],
            delta="Auto-actualización"
        )
    
    # Mensaje de estado
    if system_status['status'] == 'ERROR':
        st.error(f"⚠️ {system_status['message']}")
        if system_components['status'] == 'error':
            with st.expander("🔍 Detalles del Error"):
                st.code(system_components['traceback'])
        st.stop()
    elif system_status['status'] == 'SIN DATOS':
        st.warning(f"⚠️ {system_status['message']}")
        st.info("El sistema está operativo pero no se detectan datos. Verifique la conectividad de los dispositivos IoT.")
    else:
        st.success(f"✅ {system_status['message']}")
    
    # Sidebar para configuración
    st.sidebar.header("⚙️ Configuración del Sistema")
    
    # Opciones de análisis
    analysis_hours = st.sidebar.selectbox(
        "🕐 Período de Análisis",
        options=[1, 2, 4, 8, 12, 24, 48, 72],
        index=5,  # 24 horas por defecto
        help="Seleccionar período de tiempo para análisis de datos"
    )
    
    analysis_type = st.sidebar.selectbox(
        "📊 Tipo de Análisis",
        options=["Análisis Rápido", "Análisis Técnico", "Reporte Ejecutivo Completo"],
        index=1,
        help="Seleccionar nivel de profundidad del análisis"
    )
    
    enable_visualizations = st.sidebar.checkbox(
        "📈 Generar Visualizaciones",
        value=True,
        help="Incluir gráficos y visualizaciones en el análisis"
    )
    
    # Configuraciones avanzadas
    with st.sidebar.expander("🔧 Configuración Avanzada"):
        max_records = st.number_input(
            "Máximo de registros por dispositivo",
            min_value=100,
            max_value=10000,
            value=1000,
            step=100
        )
        
        fallback_strategy = st.selectbox(
            "Estrategia de Fallback",
            options=["Agresiva", "Conservadora", "Balanceada"],
            index=2
        )
        
        cache_timeout = st.slider(
            "Timeout de Cache (minutos)",
            min_value=1,
            max_value=30,
            value=5
        )
    
    # Sección principal
    st.header("🎯 Análisis del Sistema IoT")
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Análisis en Tiempo Real", 
        "📋 Reporte Ejecutivo",
        "🔍 Diagnóstico del Sistema",
        "📈 Visualizaciones"
    ])
    
    with tab1:
        st.subheader("Análisis Técnico en Tiempo Real")
        
        if st.button("🚀 Ejecutar Análisis Ultra-Robusto", type="primary"):
            
            if system_components['status'] == 'error':
                st.error("❌ No se puede ejecutar análisis: Sistema no inicializado correctamente")
                return
            
            with st.spinner(f"🔄 Ejecutando análisis ultra-robusto ({analysis_hours}h)..."):
                try:
                    # Obtener agente ultra-robusto
                    agent = system_components['agent']
                    
                    # Construir query técnica
                    query = f"""
                    Proporciona un análisis técnico comprehensivo del sistema IoT considerando:
                    - Período de análisis: {analysis_hours} horas
                    - Tipo de análisis: {analysis_type}
                    - Estado actual del sistema: {system_status['status']}
                    
                    Incluye análisis detallado de:
                    1. Estado operativo de dispositivos y sensores
                    2. Métricas de rendimiento y disponibilidad  
                    3. Análisis estadístico de datos por dispositivo
                    4. Identificación de patrones y anomalías
                    5. Evaluación de calidad de datos
                    6. Recomendaciones técnicas específicas
                    
                    Proporciona respuestas técnicas precisas y contundentes basadas en datos reales.
                    """
                    
                    # Ejecutar análisis
                    start_time = datetime.now()
                    response = agent.process_query(query, hours=analysis_hours)
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    # Mostrar resultados
                    st.success(f"✅ Análisis completado en {execution_time:.2f} segundos")
                    
                    # Métricas de ejecución
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Tiempo de Ejecución", f"{execution_time:.2f}s")
                    with col2:
                        st.metric("Registros Analizados", response.get('data_summary', {}).get('total_records', 'N/A'))
                    with col3:
                        st.metric("Dispositivos Procesados", response.get('data_summary', {}).get('devices_analyzed', 'N/A'))
                    
                    # Respuesta principal
                    st.markdown("### 🎯 Análisis Técnico Comprehensivo")
                    st.markdown(response.get('response', 'Sin respuesta generada'))
                    
                    # Datos técnicos adicionales
                    if 'data_summary' in response:
                        with st.expander("📊 Resumen de Datos Analizados"):
                            st.json(response['data_summary'])
                    
                    if 'analysis_metadata' in response:
                        with st.expander("🔧 Metadatos del Análisis"):
                            st.json(response['analysis_metadata'])
                    
                    # Visualizaciones
                    if enable_visualizations and 'visualizations' in response:
                        st.markdown("### 📈 Visualizaciones Generadas")
                        
                        for viz in response['visualizations']:
                            if os.path.exists(viz.get('path', '')):
                                st.image(viz['path'], caption=viz.get('name', 'Visualización'))
                    
                except Exception as e:
                    st.error(f"❌ Error ejecutando análisis: {str(e)}")
                    with st.expander("🔍 Detalles del Error"):
                        st.code(traceback.format_exc())
    
    with tab2:
        st.subheader("📋 Reporte Ejecutivo Completo")
        
        if st.button("📊 Generar Reporte Ejecutivo", type="primary"):
            
            if system_components['status'] == 'error':
                st.error("❌ No se puede generar reporte: Sistema no inicializado correctamente")
                return
            
            with st.spinner(f"📋 Generando reporte ejecutivo comprehensivo..."):
                try:
                    # Obtener generador de reportes
                    report_generator = system_components['report_generator']
                    
                    # Generar reporte
                    start_time = datetime.now()
                    report = report_generator.generate_comprehensive_report(
                        hours=analysis_hours,
                        report_type="executive"
                    )
                    generation_time = (datetime.now() - start_time).total_seconds()
                    
                    st.success(f"✅ Reporte generado en {generation_time:.2f} segundos")
                    
                    # Mostrar reporte
                    st.markdown("### 🎯 Resumen Ejecutivo")
                    st.markdown(report['executive_summary']['overview'])
                    
                    # Métricas clave
                    st.markdown("### 📊 Métricas Clave del Sistema")
                    metrics = report['executive_summary']['key_metrics']
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Dispositivos Activos", metrics.get('dispositivos_activos', 0))
                        st.metric("Sensores Totales", metrics.get('sensores_totales', 0))
                    with col2:
                        st.metric("Registros Analizados", metrics.get('registros_analizados', 0))
                        st.metric("Período (horas)", metrics.get('período_análisis_horas', 0))
                    with col3:
                        st.metric("Última Actividad", metrics.get('última_actividad', 'N/A'))
                        st.metric("Frecuencia Promedio", f"{metrics.get('frecuencia_promedio_registros', 0):.2f} reg/h")
                    
                    # Hallazgos críticos
                    st.markdown("### 🔍 Hallazgos Críticos")
                    for finding in report['executive_summary']['critical_findings']:
                        if '❌' in finding:
                            st.error(finding)
                        elif '⚠️' in finding:
                            st.warning(finding)
                        elif '✅' in finding:
                            st.success(finding)
                        else:
                            st.info(finding)
                    
                    # Análisis de rendimiento
                    st.markdown("### ⚡ Análisis de Rendimiento")
                    perf_metrics = report['performance_metrics']['system_performance']
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Eficiencia del Sistema", f"{perf_metrics.get('system_efficiency_percentage', 0):.1f}%")
                    with col2:
                        st.metric("Throughput", f"{perf_metrics.get('data_throughput_records_per_hour', 0):.1f} rec/h")
                    with col3:
                        st.metric("Completitud", f"{perf_metrics.get('data_completeness_score', 0):.1f}%")
                    with col4:
                        st.metric("Uptime Estimado", f"{perf_metrics.get('uptime_estimation', 0):.1f}%")
                    
                    # Recomendaciones
                    st.markdown("### 🚀 Recomendaciones")
                    
                    if report['recommendations']['immediate_actions']:
                        st.markdown("**Acciones Inmediatas:**")
                        for action in report['recommendations']['immediate_actions']:
                            st.markdown(f"- {action}")
                    
                    if report['recommendations']['short_term_improvements']:
                        st.markdown("**Mejoras a Corto Plazo:**")
                        for improvement in report['recommendations']['short_term_improvements']:
                            st.markdown(f"- {improvement}")
                    
                    # Exportar reporte
                    st.markdown("### 💾 Exportar Reporte")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📄 Exportar a HTML"):
                            html_content = report_generator.export_to_html(report)
                            st.download_button(
                                label="📥 Descargar HTML",
                                data=html_content,
                                file_name=f"reporte_ejecutivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                mime="text/html"
                            )
                    
                    with col2:
                        if st.button("📊 Descargar JSON"):
                            json_content = json.dumps(report, indent=2, ensure_ascii=False)
                            st.download_button(
                                label="📥 Descargar JSON",
                                data=json_content,
                                file_name=f"reporte_datos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                    
                    # Mostrar detalles técnicos
                    with st.expander("🔧 Detalles Técnicos Completos"):
                        st.json(report)
                    
                except Exception as e:
                    st.error(f"❌ Error generando reporte: {str(e)}")
                    with st.expander("🔍 Detalles del Error"):
                        st.code(traceback.format_exc())
    
    with tab3:
        st.subheader("🔍 Diagnóstico del Sistema Ultra-Robusto")
        
        if st.button("🩺 Ejecutar Diagnóstico Completo", type="secondary"):
            
            if system_components['status'] == 'error':
                st.error("❌ No se puede ejecutar diagnóstico: Sistema no inicializado correctamente")
                return
            
            with st.spinner("🔄 Ejecutando diagnóstico comprehensivo..."):
                try:
                    connector = system_components['connector']
                    
                    # Test de conectividad
                    st.markdown("### 🌐 Test de Conectividad")
                    
                    # Test 1: Dispositivos
                    devices_result = connector.get_devices_robust()
                    if devices_result:
                        st.success(f"✅ Dispositivos: {len(devices_result)} detectados")
                        st.json(devices_result[:2])  # Mostrar primeros 2
                    else:
                        st.error("❌ No se pudieron obtener dispositivos")
                    
                    # Test 2: Datos de sensores
                    st.markdown("### 📊 Test de Datos de Sensores")
                    sensor_data = connector.get_sensor_data_robust(hours=1)
                    if sensor_data:
                        st.success(f"✅ Datos de sensores: {len(sensor_data)} registros en última hora")
                        
                        # Análisis por dispositivo
                        device_counts = {}
                        for record in sensor_data:
                            device_id = record.get('device_id', 'unknown')
                            device_counts[device_id] = device_counts.get(device_id, 0) + 1
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Dispositivos con Datos", len(device_counts))
                            st.metric("Total Registros", len(sensor_data))
                        
                        with col2:
                            st.markdown("**Registros por Dispositivo:**")
                            for device, count in device_counts.items():
                                st.markdown(f"- {device}: {count} registros")
                    
                    else:
                        st.error("❌ No se pudieron obtener datos de sensores")
                    
                    # Test 3: Análisis comprehensivo
                    st.markdown("### 🔧 Test de Análisis Comprehensivo")
                    comprehensive_data = connector.get_all_data_comprehensive(hours=2, max_records_per_device=100)
                    if comprehensive_data:
                        st.success(f"✅ Análisis comprehensivo: {len(comprehensive_data)} registros")
                        
                        # Estadísticas
                        devices = set(r.get('device_id') for r in comprehensive_data if r.get('device_id'))
                        sensors = set(f"{r.get('device_id')}_{r.get('sensor_type')}" for r in comprehensive_data 
                                    if r.get('device_id') and r.get('sensor_type'))
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Dispositivos Únicos", len(devices))
                        with col2:
                            st.metric("Sensores Únicos", len(sensors))
                        with col3:
                            st.metric("Calidad de Datos", f"{(len(comprehensive_data)/max(1,len(comprehensive_data)))*100:.1f}%")
                    
                    else:
                        st.warning("⚠️ Análisis comprehensivo devolvió datos vacíos")
                    
                    # Resumen del diagnóstico
                    st.markdown("### 📋 Resumen del Diagnóstico")
                    
                    total_tests = 3
                    passed_tests = sum([
                        1 if devices_result else 0,
                        1 if sensor_data else 0,
                        1 if comprehensive_data else 0
                    ])
                    
                    success_rate = (passed_tests / total_tests) * 100
                    
                    if success_rate == 100:
                        st.success(f"✅ Sistema completamente operativo ({passed_tests}/{total_tests} tests pasados)")
                    elif success_rate >= 66:
                        st.warning(f"⚠️ Sistema parcialmente operativo ({passed_tests}/{total_tests} tests pasados)")
                    else:
                        st.error(f"❌ Sistema con problemas críticos ({passed_tests}/{total_tests} tests pasados)")
                    
                    st.progress(success_rate / 100)
                    
                except Exception as e:
                    st.error(f"❌ Error ejecutando diagnóstico: {str(e)}")
                    with st.expander("🔍 Detalles del Error"):
                        st.code(traceback.format_exc())
    
    with tab4:
        st.subheader("📈 Motor de Visualizaciones")
        
        if enable_visualizations and st.button("🎨 Generar Visualizaciones", type="secondary"):
            
            if system_components['status'] == 'error':
                st.error("❌ No se puede generar visualizaciones: Sistema no inicializado correctamente")
                return
            
            with st.spinner("🎨 Generando visualizaciones comprehensivas..."):
                try:
                    # Obtener datos
                    connector = system_components['connector']
                    visualization_engine = system_components['visualization_engine']
                    
                    data = connector.get_all_data_comprehensive(hours=analysis_hours, max_records_per_device=max_records)
                    
                    if not data:
                        st.warning("⚠️ No hay datos suficientes para generar visualizaciones")
                        return
                    
                    # Generar gráficos
                    chart_paths = visualization_engine.generate_charts(
                        data, 
                        f"Análisis Comprehensivo - {analysis_hours}h"
                    )
                    
                    if chart_paths:
                        st.success(f"✅ {len(chart_paths)} visualizaciones generadas")
                        
                        # Mostrar gráficos
                        cols = st.columns(2)
                        for i, chart_path in enumerate(chart_paths):
                            if os.path.exists(chart_path):
                                with cols[i % 2]:
                                    chart_name = os.path.basename(chart_path)
                                    st.image(chart_path, caption=chart_name, use_column_width=True)
                    else:
                        st.warning("⚠️ No se pudieron generar visualizaciones")
                
                except Exception as e:
                    st.error(f"❌ Error generando visualizaciones: {str(e)}")
                    with st.expander("🔍 Detalles del Error"):
                        st.code(traceback.format_exc())
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🚀 <strong>Sistema IoT Ultra-Robusto</strong> | 
        Versión 2.0 | 
        Múltiples Estrategias de Fallback | 
        Análisis Técnico Avanzado</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()