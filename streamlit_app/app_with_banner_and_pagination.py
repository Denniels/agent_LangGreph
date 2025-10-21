"""
🎯 STREAMLIT APP CON BANNER PROFESIONAL Y PAGINACIÓN
Demostración de sistema IoT con capacidades empresariales
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from modules.utils.professional_banner import display_complete_banner
from modules.agents.direct_api_agent import DirectAPIAgent
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timezone
import json

# Configuración de página
st.set_page_config(
    page_title="🏭 Sistema IoT Industrial", 
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Aplicación principal con banner profesional"""
    
    # Mostrar banner profesional completo
    display_complete_banner()
    
    # Sidebar para configuración
    with st.sidebar:
        st.header("⚙️ Configuración de Análisis")
        
        # Selector de rango temporal con paginación automática
        time_range = st.selectbox(
            "📅 Rango Temporal",
            options=[
                ("3h", "3 horas (Tiempo Real)"),
                ("6h", "6 horas (Reciente)"),
                ("12h", "12 horas (Paginado)"),
                ("24h", "24 horas (1 día)"),
                ("48h", "48 horas (2 días)"),
                ("168h", "168 horas (1 semana)")
            ],
            format_func=lambda x: x[1],
            index=0
        )
        
        hours = float(time_range[0][:-1])  # Extraer número de horas
        
        # Información sobre la consulta
        if hours <= 6:
            st.success("⚡ Consulta rápida - Respuesta inmediata")
        else:
            st.info("📚 Consulta extensa - Usando paginación avanzada")
        
        st.markdown("---")
        
        # Configuración de visualización
        show_individual_sensors = st.checkbox("🔍 Mostrar sensores individuales", value=True)
        show_statistics = st.checkbox("📊 Mostrar estadísticas avanzadas", value=True)
        
        # Información técnica
        with st.expander("🔧 Info Técnica"):
            st.markdown(f"""
            **Configuración Actual:**
            - Rango: {hours} horas
            - Método: {'Paginado' if hours > 6 else 'Estándar'}
            - Máx. Registros: {min(2000, int(hours * 50)) if hours > 6 else 200}
            """)
    
    # Botón principal para obtener datos
    if st.button("📡 Obtener Datos del Sistema IoT", type="primary", use_container_width=True):
        
        with st.spinner(f"🔄 Obteniendo datos de {hours}h usando {'paginación' if hours > 6 else 'método estándar'}..."):
            
            try:
                # Conectar al agente
                base_url = "https://plain-state-refers-nutritional.trycloudflare.com"
                agent = DirectAPIAgent(base_url=base_url)
                
                # Obtener datos con paginación automática
                start_time = datetime.now()
                result = agent.get_all_recent_data(hours=hours)
                end_time = datetime.now()
                
                duration = (end_time - start_time).total_seconds()
                
                if result.get('status') == 'success':
                    
                    # Métricas principales
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "📈 Registros Obtenidos",
                            result.get('total_records', 0),
                            delta=f"Método: {result.get('method', 'unknown')}"
                        )
                    
                    with col2:
                        st.metric(
                            "🖥️ Dispositivos Activos",
                            result.get('active_devices', 0),
                            delta="En línea"
                        )
                    
                    with col3:
                        st.metric(
                            "⏱️ Tiempo de Respuesta",
                            f"{duration:.2f}s",
                            delta="Optimizado"
                        )
                    
                    with col4:
                        records_per_hour = result.get('total_records', 0) / hours if hours > 0 else 0
                        st.metric(
                            "📊 Densidad de Datos",
                            f"{records_per_hour:.1f} rec/h",
                            delta="Calidad Alta"
                        )
                    
                    # Procesar datos para visualización
                    sensor_data = result.get('sensor_data', [])
                    
                    if sensor_data:
                        
                        # Convertir a DataFrame
                        df = pd.DataFrame(sensor_data)
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                        
                        # Gráfico principal - Temperatura
                        st.subheader("🌡️ Análisis de Temperatura")
                        
                        temp_data = df[df['sensor_type'].str.contains('temperature', na=False, case=False)]
                        
                        if not temp_data.empty:
                            fig_temp = px.line(
                                temp_data, 
                                x='timestamp', 
                                y='value', 
                                color='device_id',
                                facet_col='sensor_type',
                                title=f"Evolución de Temperatura ({hours}h)",
                                labels={'value': 'Temperatura (°C)', 'timestamp': 'Tiempo'}
                            )
                            fig_temp.update_layout(height=400)
                            st.plotly_chart(fig_temp, use_container_width=True)
                        
                        # Gráfico de luminosidad
                        st.subheader("💡 Análisis de Luminosidad")
                        
                        ldr_data = df[df['sensor_type'] == 'ldr']
                        
                        if not ldr_data.empty:
                            fig_ldr = px.scatter(
                                ldr_data,
                                x='timestamp',
                                y='value',
                                color='device_id',
                                title=f"Niveles de Luminosidad ({hours}h)",
                                labels={'value': 'Luminosidad', 'timestamp': 'Tiempo'}
                            )
                            fig_ldr.update_layout(height=400)
                            st.plotly_chart(fig_ldr, use_container_width=True)
                        
                        # Estadísticas por dispositivo
                        if show_statistics:
                            st.subheader("📊 Estadísticas por Dispositivo")
                            
                            stats_data = []
                            for device in result.get('data', {}).get('devices', []):
                                device_id = device.get('device_id')
                                records = device.get('records', [])
                                
                                if records:
                                    device_df = pd.DataFrame(records)
                                    device_df['value'] = pd.to_numeric(device_df['value'], errors='coerce')
                                    
                                    stats_data.append({
                                        'Dispositivo': device_id,
                                        'Registros': len(records),
                                        'Temp Promedio': device_df[device_df['sensor_type'].str.contains('temperature', na=False)]['value'].mean(),
                                        'Temp Máxima': device_df[device_df['sensor_type'].str.contains('temperature', na=False)]['value'].max(),
                                        'Temp Mínima': device_df[device_df['sensor_type'].str.contains('temperature', na=False)]['value'].min(),
                                    })
                            
                            if stats_data:
                                stats_df = pd.DataFrame(stats_data)
                                st.dataframe(stats_df, use_container_width=True)
                        
                        # Mostrar datos individuales si se solicita
                        if show_individual_sensors:
                            with st.expander("🔍 Datos Detallados por Sensor"):
                                sensor_types = df['sensor_type'].unique()
                                
                                for sensor_type in sensor_types:
                                    st.write(f"**{sensor_type.upper()}**")
                                    sensor_subset = df[df['sensor_type'] == sensor_type]
                                    st.dataframe(sensor_subset[['timestamp', 'device_id', 'value']].head(10))
                        
                        # Información de la consulta
                        with st.expander("ℹ️ Información de la Consulta"):
                            query_info = {
                                "Rango Temporal": f"{hours} horas",
                                "Método Utilizado": result.get('method', 'unknown'),
                                "Tiempo de Respuesta": f"{duration:.2f} segundos",
                                "Registros Totales": result.get('total_records', 0),
                                "Dispositivos Activos": result.get('active_devices', 0),
                                "Timestamp": datetime.now(timezone.utc).isoformat()
                            }
                            
                            st.json(query_info)
                    
                    else:
                        st.warning("⚠️ No se encontraron datos de sensores en el rango especificado")
                
                else:
                    st.error(f"❌ Error obteniendo datos: {result.get('message', 'Error desconocido')}")
                    
            except Exception as e:
                st.error(f"💥 Error de conexión: {str(e)}")
                st.info("🔧 Verifique que el sistema IoT esté en línea y la URL sea correcta")

if __name__ == "__main__":
    main()