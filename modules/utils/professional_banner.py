"""
📢 COMPONENTE DE BANNER PROFESIONAL PARA STREAMLIT
Banner informativo sobre capacidades y limitaciones del sistema IoT
"""

import streamlit as st
from datetime import datetime
import time

def show_professional_banner():
    """
    Mostrar banner profesional con información del sistema IoT
    """
    
    # CSS personalizado para el banner
    st.markdown("""
    <style>
    .professional-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .banner-header {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .banner-content {
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 15px;
    }
    
    .capabilities-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 15px;
        margin: 15px 0;
    }
    
    .capability-item {
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
    }
    
    .limitation-item {
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #FF9800;
    }
    
    .tech-specs {
        background: rgba(255,255,255,0.08);
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
        font-size: 14px;
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-active {
        background-color: #4CAF50;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Banner principal
    st.markdown(f"""
    <div class="professional-banner">
        <div class="banner-header">
            <span class="status-indicator status-active"></span>
            🏭 Sistema IoT Industrial - Monitoreo en Tiempo Real
        </div>
        
        <div class="banner-content">
            Bienvenido al sistema de monitoreo IoT ejecutándose en <strong>NVIDIA Jetson Nano</strong>. 
            Este sistema proporciona análisis inteligente de datos de sensores industriales con 
            capacidades de IA integradas para optimización de procesos.
        </div>
        
        <div class="capabilities-grid">
            <div class="capability-item">
                <strong>📊 Análisis Temporal</strong><br>
                • Datos en tiempo real (últimas 3-6 horas)<br>
                • Análisis histórico (hasta 1 semana)<br>
                • Tendencias y patrones automáticos
            </div>
            
            <div class="capability-item">
                <strong>🤖 IA Integrada</strong><br>
                • Procesamiento con Groq LLM<br>
                • Análisis predictivo<br>
                • Recomendaciones automáticas
            </div>
            
            <div class="capability-item">
                <strong>🔍 Monitoreo Multi-Sensor</strong><br>
                • Temperatura (múltiples puntos)<br>
                • Luminosidad (LDR)<br>
                • Sensores NTC especializados
            </div>
            
            <div class="limitation-item">
                <strong>⚙️ Consideraciones Técnicas</strong><br>
                • Procesamiento optimizado para Jetson Nano<br>
                • Consultas extensas pueden requerir tiempo adicional<br>
                • Datos limitados por capacidad de hardware embebido
            </div>
        </div>
        
        <div class="tech-specs">
            <strong>🔧 Especificaciones Técnicas:</strong>
            Jetson Nano 4GB | API REST optimizada | Base de datos SQLite | 
            Procesamiento IA con Groq | Interfaz Streamlit Cloud
            <br><br>
            <strong>📈 Capacidad Actual:</strong>
            Hasta 2,000 registros por consulta | 6 tipos de sensores | 
            Análisis temporal hasta 7 días | Respuesta sub-segundo para consultas recientes
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_system_status():
    """
    Mostrar estado actual del sistema
    """
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🟢 Estado Sistema",
            value="Operativo",
            delta="Online"
        )
    
    with col2:
        st.metric(
            label="📡 Conectividad",
            value="Estable",
            delta="API Activa"
        )
    
    with col3:
        st.metric(
            label="🔋 Hardware",
            value="Jetson Nano",
            delta="4GB RAM"
        )
    
    with col4:
        current_time = datetime.now().strftime("%H:%M:%S")
        st.metric(
            label="⏰ Última Actualización",
            value=current_time,
            delta="Tiempo Real"
        )

def show_data_capacity_info():
    """
    Mostrar información sobre capacidades de datos
    """
    
    with st.expander("📊 Información sobre Capacidades de Datos", expanded=False):
        st.markdown("""
        ### 🎯 Capacidades del Sistema
        
        **Consultas Rápidas (Recomendado):**
        - ⚡ **1-6 horas**: Respuesta instantánea (~200 registros)
        - 🔍 **Ideal para**: Monitoreo en tiempo real, análisis inmediato
        
        **Consultas Extensas (Avanzado):**
        - 📚 **6-48 horas**: Análisis con paginación (~1,000-2,000 registros)
        - 📈 **Hasta 7 días**: Análisis histórico completo
        - 🔍 **Ideal para**: Tendencias semanales, análisis profundo
        
        ### ⚙️ Optimización Técnica
        
        **¿Por qué estas limitaciones?**
        - 🖥️ **Hardware Embebido**: Jetson Nano optimizado para eficiencia
        - 📊 **Calidad vs Cantidad**: Priorizamos análisis precisos
        - ⚡ **Velocidad**: Respuestas rápidas para decisiones inmediatas
        
        **💡 Recomendación Profesional:**
        Para análisis de tendencias complejas, combine múltiples consultas 
        de períodos más cortos para obtener la mejor experiencia de usuario.
        """)

def show_technical_disclaimer():
    """
    Mostrar disclaimer técnico profesional
    """
    
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; margin-top: 20px;">
        <h4 style="color: #007bff; margin-bottom: 10px;">🔬 Nota Técnica</h4>
        <p style="margin-bottom: 8px; color: #666;">
            Este sistema está optimizado para demostrar capacidades de IoT + IA en hardware embebido. 
            Para implementaciones de producción a gran escala, se recomienda infraestructura cloud dedicada.
        </p>
        <small style="color: #888;">
            Sistema desarrollado para demostración de capacidades técnicas | 
            Hardware: NVIDIA Jetson Nano | Framework: Streamlit + FastAPI + Groq AI
        </small>
    </div>
    """, unsafe_allow_html=True)

# Función principal para mostrar todo el banner
def display_complete_banner():
    """
    Mostrar el banner completo con todos los componentes
    """
    show_professional_banner()
    show_system_status()
    show_data_capacity_info()
    show_technical_disclaimer()

if __name__ == "__main__":
    # Demo del banner
    st.set_page_config(
        page_title="Sistema IoT Demo", 
        page_icon="🏭",
        layout="wide"
    )
    
    display_complete_banner()
    
    st.markdown("### 🧪 Vista Previa del Banner")
    st.info("Este es el banner que aparecerá en la aplicación principal.")