"""
Componente de Streamlit para mostrar el uso de API de manera visual
==================================================================

Proporciona widgets para mostrar el estado de uso de las APIs de Groq
de forma clara y atractiva en la interfaz de Streamlit.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def display_usage_metrics(usage_info: Dict[str, Any], key_prefix: str = "usage"):
    """
    Mostrar métricas de uso de API en Streamlit.
    
    Args:
        usage_info: Información de uso de la API
        key_prefix: Prefijo para las claves de Streamlit
    """
    try:
        # Título de la sección
        st.subheader("📊 Uso de API - Groq")
        
        # Información del modelo
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="🤖 Modelo Actual",
                value=usage_info.get("model_description", "Desconocido"),
                help=f"Modelo: {usage_info.get('model', 'N/A')}"
            )
        
        with col2:
            st.metric(
                label="📅 Fecha de Reset",
                value=usage_info.get("date", "N/A"),
                help="Los límites se resetean diariamente"
            )
        
        # Métricas principales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Requests usados
            requests_used = usage_info.get("requests_used", 0) or 0
            requests_limit = usage_info.get("requests_limit", 1000) or 1000
            requests_remaining = usage_info.get("requests_remaining", 0) or 0
            
            # Color basado en el porcentaje
            usage_percentage = float(usage_info.get("requests_percentage", 0) or 0)
            if usage_percentage >= 90:
                delta_color = "inverse"
            elif usage_percentage >= 75:
                delta_color = "off"
            else:
                delta_color = "normal"
            
            st.metric(
                label="🔥 Consultas Usadas",
                value=f"{requests_used:,}",
                delta=f"-{requests_remaining:,} disponibles",
                delta_color=delta_color,
                help=f"Límite diario: {requests_limit:,}"
            )
        
        with col2:
            # Tokens usados
            tokens_used = usage_info.get("tokens_used", 0) or 0
            tokens_limit = usage_info.get("tokens_limit", 100000) or 100000
            tokens_remaining = usage_info.get("tokens_remaining", 0) or 0
            
            st.metric(
                label="🎯 Tokens Usados",
                value=f"{tokens_used:,}",
                delta=f"-{tokens_remaining:,} disponibles",
                help=f"Límite diario: {tokens_limit:,}"
            )
        
        with col3:
            # Estado general
            status = usage_info.get("status", "normal")
            can_make_request = usage_info.get("can_make_request", True)
            
            status_emoji = {
                "normal": "✅",
                "warning": "⚠️", 
                "critical": "🚨"
            }.get(status, "❓")
            
            status_text = {
                "normal": "Normal",
                "warning": "Advertencia",
                "critical": "Crítico"
            }.get(status, "Desconocido")
            
            st.metric(
                label="🌡️ Estado",
                value=f"{status_emoji} {status_text}",
                delta="Disponible" if can_make_request else "Límite alcanzado",
                delta_color="normal" if can_make_request else "inverse"
            )
        
        # Barra de progreso visual
        display_usage_progress_bar(usage_info, key_prefix)
        
        # Estadísticas adicionales en expandible
        with st.expander("📈 Estadísticas Detalladas"):
            display_detailed_stats(usage_info)
        
    except Exception as e:
        logger.error(f"Error mostrando métricas de uso: {e}")
        st.error("Error mostrando información de uso de API")

def display_usage_progress_bar(usage_info: Dict[str, Any], key_prefix: str):
    """
    Mostrar barra de progreso del uso de API.
    
    Args:
        usage_info: Información de uso
        key_prefix: Prefijo para claves
    """
    try:
        # Configurar datos para la barra de progreso con valores por defecto seguros
        requests_percentage = float(usage_info.get("requests_percentage", 0) or 0)
        tokens_percentage = float(usage_info.get("tokens_percentage", 0) or 0)
        
        # Asegurar que los valores estén en rango válido
        requests_percentage = max(0, min(100, requests_percentage))
        tokens_percentage = max(0, min(100, tokens_percentage))
        
        st.subheader("📊 Progreso de Uso Diario")
        
        # Barra de progreso para requests
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🔥 Consultas (Requests)**")
            
            # Color de la barra basado en el porcentaje
            if requests_percentage >= 90:
                bar_color = "#ff4444"  # Rojo
            elif requests_percentage >= 75:
                bar_color = "#ffaa00"  # Naranja
            else:
                bar_color = "#00aa44"  # Verde
            
            # Crear gráfico de barra con validación de datos
            try:
                fig_requests = go.Figure(go.Bar(
                    x=[requests_percentage],
                    y=["Uso"],
                    orientation='h',
                    marker_color=bar_color,
                    text=f"{requests_percentage:.1f}%",
                    textposition='middle right' if requests_percentage > 5 else 'outside'
                ))
                
                fig_requests.update_layout(
                    xaxis=dict(range=[0, 100], title="Porcentaje"),
                    yaxis=dict(showticklabels=False),
                    height=100,
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=False
                )
                
                st.plotly_chart(fig_requests, use_container_width=True, key=f"{key_prefix}_requests_bar")
                
            except Exception as chart_error:
                # Fallback simple si falla el gráfico
                st.progress(requests_percentage / 100.0)
                st.caption(f"Uso: {requests_percentage:.1f}%")
        
        with col2:
            st.write("**🎯 Tokens**")
            
            # Color de la barra para tokens
            if tokens_percentage >= 90:
                bar_color = "#ff4444"
            elif tokens_percentage >= 75:
                bar_color = "#ffaa00"
            else:
                bar_color = "#0066cc"  # Azul
            
            try:
                fig_tokens = go.Figure(go.Bar(
                    x=[tokens_percentage],
                    y=["Uso"],
                    orientation='h',
                    marker_color=bar_color,
                    text=f"{tokens_percentage:.1f}%",
                    textposition='middle right' if tokens_percentage > 5 else 'outside'
                ))
                
                fig_tokens.update_layout(
                    xaxis=dict(range=[0, 100], title="Porcentaje"),
                    yaxis=dict(showticklabels=False),
                    height=100,
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=False
                )
                
                st.plotly_chart(fig_tokens, use_container_width=True, key=f"{key_prefix}_tokens_bar")
                
            except Exception as chart_error:
                # Fallback simple si falla el gráfico
                st.progress(tokens_percentage / 100.0)
                st.caption(f"Uso: {tokens_percentage:.1f}%")
        
        # Información adicional
        if requests_percentage >= 75 or tokens_percentage >= 75:
            if requests_percentage >= 90 or tokens_percentage >= 90:
                st.error("🚨 **Uso crítico**: Te estás acercando al límite diario")
            else:
                st.warning("⚠️ **Uso alto**: Considera moderar el uso para no agotar el límite")
        elif requests_percentage == 0 and tokens_percentage == 0:
            st.info("💡 **Sin uso registrado**: Haz una consulta para ver el progreso")
        
    except Exception as e:
        logger.error(f"Error mostrando barra de progreso: {e}")
        # Fallback muy simple
        st.write("📊 **Progreso de Uso Diario**")
        col1, col2 = st.columns(2)
        with col1:
            st.write("🔥 **Consultas**: Sin datos disponibles")
        with col2:
            st.write("🎯 **Tokens**: Sin datos disponibles")

def display_detailed_stats(usage_info: Dict[str, Any]):
    """
    Mostrar estadísticas detalladas de uso.
    
    Args:
        usage_info: Información de uso
    """
    try:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📊 Detalles de Requests**")
            st.write(f"• Usados: {usage_info.get('requests_used', 0) or 0:,}")
            st.write(f"• Límite: {usage_info.get('requests_limit', 0) or 0:,}")
            st.write(f"• Disponibles: {usage_info.get('requests_remaining', 0) or 0:,}")
            st.write(f"• Porcentaje: {float(usage_info.get('requests_percentage', 0) or 0):.1f}%")
        
        with col2:
            st.write("**🎯 Detalles de Tokens**")
            st.write(f"• Usados: {usage_info.get('tokens_used', 0) or 0:,}")
            st.write(f"• Límite: {usage_info.get('tokens_limit', 0) or 0:,}")
            st.write(f"• Disponibles: {usage_info.get('tokens_remaining', 0) or 0:,}")
            st.write(f"• Porcentaje: {float(usage_info.get('tokens_percentage', 0) or 0):.1f}%")
        
        # Estadísticas de tiempo
        last_request = usage_info.get("last_request")
        if last_request:
            try:
                last_time = datetime.fromisoformat(last_request.replace('Z', '+00:00'))
                time_diff = datetime.now() - last_time.replace(tzinfo=None)
                st.write(f"**⏰ Última consulta**: hace {time_diff.seconds // 60} minutos")
            except:
                st.write(f"**⏰ Última consulta**: {last_request}")
        
        # Estadísticas de vida útil si están disponibles
        lifetime_stats = usage_info.get("lifetime_stats", {})
        if lifetime_stats:
            st.write("**📈 Estadísticas Totales**")
            st.write(f"• Total requests: {lifetime_stats.get('requests', 0):,}")
            st.write(f"• Total tokens: {lifetime_stats.get('tokens', 0):,}")
            st.write(f"• Días activos: {lifetime_stats.get('days_active', 0)}")
        
    except Exception as e:
        logger.error(f"Error mostrando estadísticas detalladas: {e}")
        st.error("Error mostrando estadísticas detalladas")

def display_usage_alert(usage_info: Dict[str, Any]):
    """
    Mostrar alerta si el uso está cerca del límite.
    
    Args:
        usage_info: Información de uso
    """
    try:
        status = usage_info.get("status", "normal")
        can_make_request = usage_info.get("can_make_request", True)
        
        if not can_make_request:
            st.error("""
            🚨 **LÍMITE DIARIO ALCANZADO**
            
            Has alcanzado el límite diario de consultas para este modelo.
            Los límites se resetean automáticamente cada día a medianoche UTC.
            
            **¿Qué puedes hacer?**
            - ⏰ Esperar al reseteo diario (medianoche UTC)
            - 🔄 Volver mañana cuando se renueven los límites
            - 💡 Usar consultas más específicas para optimizar el uso
            """)
            
        elif status == "critical":
            st.error(f"""
            🚨 **USO CRÍTICO**
            
            Has usado {usage_info.get('requests_percentage', 0):.1f}% de tus consultas diarias.
            Te quedan {usage_info.get('requests_remaining', 0)} consultas.
            
            **Recomendación**: Modera el uso para no agotar el límite.
            """)
            
        elif status == "warning":
            st.warning(f"""
            ⚠️ **USO ALTO**
            
            Has usado {usage_info.get('requests_percentage', 0):.1f}% de tus consultas diarias.
            Te quedan {usage_info.get('requests_remaining', 0)} consultas.
            
            **Sugerencia**: Considera optimizar tus consultas.
            """)
    
    except Exception as e:
        logger.error(f"Error mostrando alerta de uso: {e}")

def display_model_limits_info():
    """
    Mostrar información sobre los límites de los modelos de Groq.
    """
    try:
        st.subheader("📋 Límites por Modelo - Groq")
        
        # Información de límites actualizados (desde usage_tracker)
        from modules.utils.usage_tracker import usage_tracker
        
        # Modelos principales (OFICIALES Sep 2025)
        models_info = [
            ("llama-3.1-8b-instant", "Llama 3.1 8B Instant", "14,400", "1M"),
            ("llama-3.3-70b-versatile", "Llama 3.3 70B Versatile", "1,000", "1M"),
            ("meta-llama/llama-guard-4-12b", "Meta Llama Guard 4 12B", "14,400", "1M"),
            ("groq/compound", "Groq Compound", "250", "1M"),
            ("groq/compound-mini", "Groq Compound Mini", "250", "1M"),
            ("gemma2-9b-it", "Gemma 2 9B IT", "14,400", "1M"),
        ]
        
        # Modelos legacy
        legacy_models_info = [
            ("llama-3.1-70b-versatile", "Llama 3.1 70B Versatile (Legacy)", "1,000", "1M"),
            ("llama3-8b-8192", "Llama 3 8B (Legacy)", "14,400", "1M"),
            ("llama3-70b-8192", "Llama 3 70B (Legacy)", "1,000", "1M"),
            ("mixtral-8x7b-32768", "Mixtral 8x7B", "14,400", "1M"),
            ("gemma-7b-it", "Gemma 7B IT (Legacy)", "14,400", "1M")
        ]
        
        # Mostrar modelos principales
        st.write("### 🔥 Modelos Principales (Oficial)")
        
        # Crear tabla
        for model_id, description, requests, tokens in models_info:
            with st.expander(f"🤖 {description}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("🔥 Requests/día", requests)
                
                with col2:
                    st.metric("🎯 Tokens/día", tokens)
                
                with col3:
                    # Mostrar uso actual si es el modelo activo
                    current_usage = usage_tracker.get_usage_info(model_id)
                    if current_usage["requests_used"] > 0:
                        st.metric(
                            "📊 Uso actual", 
                            f"{current_usage['requests_used']} requests",
                            delta=f"{current_usage['requests_percentage']:.1f}% usado"
                        )
                    else:
                        st.metric("📊 Uso actual", "Sin uso")
        
        # Mostrar modelos legacy
        st.write("### 📦 Modelos Legacy (Compatibilidad)")
        
        for model_id, description, requests, tokens in legacy_models_info:
            with st.expander(f"🤖 {description}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("🔥 Requests/día", requests)
                
                with col2:
                    st.metric("🎯 Tokens/día", tokens)
                
                with col3:
                    # Mostrar uso actual si es el modelo activo
                    current_usage = usage_tracker.get_usage_info(model_id)
                    if current_usage["requests_used"] > 0:
                        st.metric(
                            "📊 Uso actual", 
                            f"{current_usage['requests_used']} requests",
                            delta=f"{current_usage['requests_percentage']:.1f}% usado"
                        )
                    else:
                        st.metric("📊 Uso actual", "Sin uso")
        
        # Información adicional
        st.info("""
        💡 **Información importante**:
        - Los límites se resetean diariamente a medianoche UTC
        - Groq es completamente gratuito - no requiere tarjeta de crédito
        - Los límites nos ayudan a mantener el servicio disponible para todos
        - Puedes cambiar de modelo si alcanzas un límite
        - ⚠️ **ACTUALIZADO Sep 2025**: Límites oficiales de Groq
        """)
    
    except Exception as e:
        logger.error(f"Error mostrando información de límites: {e}")
        st.error("Error mostrando información de límites de modelos")

def get_time_until_reset() -> str:
    """
    Calcular tiempo restante hasta el próximo reset diario.
    
    Returns:
        String con tiempo restante
    """
    try:
        now = datetime.utcnow()
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        time_diff = tomorrow - now
        
        hours = time_diff.seconds // 3600
        minutes = (time_diff.seconds % 3600) // 60
        
        return f"{hours}h {minutes}m"
    
    except Exception:
        return "N/A"