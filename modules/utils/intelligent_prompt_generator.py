"""
Módulo de análisis inteligente para el CloudIoTAgent
====================================================

Contiene métodos auxiliares para análisis específico por tipo de consulta
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def create_intelligent_prompt(user_query: str, intelligent_response: str, 
                               comprehensive_analysis: Dict, statistical_analysis: Dict, 
                               raw_data: List) -> str:
    """
    Crear prompt inteligente específico según el tipo de consulta del usuario
    """
    query_lower = user_query.lower()
    
    # DETERMINAR TIPO DE CONSULTA
    is_statistical = any(word in query_lower for word in [
        'promedio', 'media', 'estadística', 'estadisticas', 'cálculo', 'calculos',
        'máximo', 'mínimo', 'desviación', 'varianza', 'suma', 'total'
    ])
    
    is_temporal = any(word in query_lower for word in [
        'últimas', 'ultimas', '24 horas', 'hoy', 'ayer', 'reciente', 'actual'
    ])
    
    is_visualization = any(word in query_lower for word in [
        'gráfico', 'grafico', 'gráfica', 'grafica', 'visualiza', 'chart', 'plot'
    ])
    
    # FILTRAR DATOS SI ES CONSULTA TEMPORAL
    filtered_data = raw_data
    if is_temporal and raw_data:
        filtered_data = filter_data_by_time(raw_data, user_query)
    
    # CALCULAR ESTADÍSTICAS ESPECÍFICAS SI ES CONSULTA ESTADÍSTICA
    specific_calculations = {}
    if is_statistical and filtered_data:
        specific_calculations = calculate_specific_statistics(filtered_data, user_query)
    
    # CREAR PROMPT SEGÚN TIPO DE CONSULTA
    if is_statistical:
        return create_statistical_prompt(user_query, intelligent_response, 
                                         specific_calculations, comprehensive_analysis)
    elif is_temporal:
        return create_temporal_prompt(user_query, intelligent_response, 
                                      filtered_data, comprehensive_analysis)
    elif is_visualization:
        return create_visualization_prompt(user_query, intelligent_response, 
                                           comprehensive_analysis)
    else:
        return create_general_prompt(user_query, intelligent_response, 
                                     comprehensive_analysis, statistical_analysis)

def filter_data_by_time(raw_data: List, user_query: str) -> List:
    """Filtrar datos según el período de tiempo solicitado"""
    try:        
        # Determinar período basado en la consulta
        if '24 horas' in user_query.lower() or 'últimas 24' in user_query.lower():
            cutoff_time = datetime.now() - timedelta(hours=24)
        elif 'hoy' in user_query.lower():
            cutoff_time = datetime.now().replace(hour=0, minute=0, second=0)
        else:
            cutoff_time = datetime.now() - timedelta(hours=24)  # Default
        
        filtered = []
        for record in raw_data:
            try:
                timestamp_str = record.get('timestamp', '')
                if timestamp_str:
                    # Intentar parsear diferentes formatos de timestamp
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                        try:
                            record_time = datetime.strptime(timestamp_str.split('.')[0].replace('T', ' '), fmt)
                            if record_time >= cutoff_time:
                                filtered.append(record)
                            break
                        except:
                            continue
            except:
                continue
        
        logger.info(f"🕒 Datos filtrados: {len(raw_data)} → {len(filtered)} registros para período solicitado")
        return filtered if filtered else raw_data  # Fallback a todos los datos
        
    except Exception as e:
        logger.warning(f"⚠️ Error filtrando datos por tiempo: {e}")
        return raw_data

def calculate_specific_statistics(data: List, user_query: str) -> Dict:
    """Calcular estadísticas específicas solicitadas por el usuario"""
    try:
        if not data:
            return {}
        
        import pandas as pd
        import numpy as np
        
        # Convertir a DataFrame para análisis
        df = pd.DataFrame(data)
        
        calculations = {}
        query_lower = user_query.lower()
        
        # Identificar sensores en la consulta
        sensor_keywords = {
            'temperatura': ['temperature', 'temp', 'temperatura', 'ntc'],
            'temperature': ['temperature', 'temp', 'temperatura', 'ntc'],
            'luz': ['ldr', 'light', 'luz'],
            'ldr': ['ldr', 'light', 'luz'],
            'light': ['ldr', 'light', 'luz']
        }
        
        requested_sensor_types = []
        for word in query_lower.split():
            for sensor_key, sensor_aliases in sensor_keywords.items():
                if word in sensor_key or sensor_key in word:
                    requested_sensor_types.extend(sensor_aliases)
                    break
        
        # Eliminar duplicados
        requested_sensor_types = list(set(requested_sensor_types))
        
        for column in df.columns:
            if column in ['timestamp', 'device_id']:
                continue
                
            # Solo calcular para sensores solicitados o todos si no se especifica
            column_lower = column.lower()
            if requested_sensor_types:
                # Verificar si algún tipo de sensor está en el nombre de la columna
                should_include = any(sensor_type in column_lower for sensor_type in requested_sensor_types)
                if not should_include:
                    continue
            
            try:
                numeric_data = pd.to_numeric(df[column], errors='coerce').dropna()
                if len(numeric_data) > 0:
                    sensor_stats = {}
                    
                    if 'promedio' in query_lower or 'media' in query_lower:
                        sensor_stats['promedio'] = float(numeric_data.mean())
                    
                    if 'máximo' in query_lower or 'maximo' in query_lower:
                        sensor_stats['máximo'] = float(numeric_data.max())
                    
                    if 'mínimo' in query_lower or 'minimo' in query_lower:
                        sensor_stats['mínimo'] = float(numeric_data.min())
                    
                    if 'desviación' in query_lower:
                        sensor_stats['desviación_estándar'] = float(numeric_data.std())
                    
                    if 'suma' in query_lower or 'total' in query_lower:
                        sensor_stats['suma_total'] = float(numeric_data.sum())
                    
                    # Siempre incluir estadísticas básicas
                    sensor_stats.update({
                        'count': len(numeric_data),
                        'promedio': float(numeric_data.mean()),
                        'mediana': float(numeric_data.median()),
                        'mínimo': float(numeric_data.min()),
                        'máximo': float(numeric_data.max())
                    })
                    
                    calculations[column] = sensor_stats
            except:
                continue
        
        logger.info(f"📊 Cálculos específicos realizados para {len(calculations)} sensores")
        return calculations
        
    except Exception as e:
        logger.warning(f"⚠️ Error calculando estadísticas específicas: {e}")
        return {}

def create_statistical_prompt(user_query: str, intelligent_response: str, 
                              calculations: Dict, comprehensive_analysis: Dict) -> str:
    """Crear prompt especializado para consultas estadísticas"""
    
    calculations_text = ""
    if calculations:
        calculations_text = "\n🧮 **CÁLCULOS ESPECÍFICOS SOLICITADOS:**\n"
        for sensor, stats in calculations.items():
            calculations_text += f"• **{sensor}**:\n"
            for stat_name, value in stats.items():
                if isinstance(value, float):
                    calculations_text += f"  - {stat_name}: {value:.2f}\n"
                else:
                    calculations_text += f"  - {stat_name}: {value}\n"
    
    return f"""
Eres un analista de datos IoT especializado en estadísticas. El usuario te solicita cálculos estadísticos específicos.

CONSULTA ESTADÍSTICA: "{user_query}"

{calculations_text}

DATOS DEL SISTEMA:
{intelligent_response}

INSTRUCCIONES ESPECÍFICAS:
1. RESPONDE CON LOS CÁLCULOS EXACTOS mostrados arriba
2. Menciona ÚNICAMENTE los sensores para los que tienes cálculos específicos
3. Usa las cifras EXACTAS de los cálculos realizados
4. Sé preciso y profesional en tu respuesta
5. Si el usuario pidió un cálculo específico (promedio, máximo, etc.), enfócate en eso
6. NO inventes cifras - usa solo los cálculos proporcionados

FORMATO DE RESPUESTA:
- Respuesta directa al cálculo solicitado
- Cifras exactas con 2 decimales
- Contexto breve sobre los datos analizados
- Recomendaciones si es apropiado

RESPONDE DE FORMA TÉCNICA Y PRECISA:
"""

def create_temporal_prompt(user_query: str, intelligent_response: str, 
                          filtered_data: List, comprehensive_analysis: Dict) -> str:
    """Crear prompt especializado para consultas temporales"""
    
    time_info = f"Datos filtrados: {len(filtered_data)} registros para el período solicitado"
    
    return f"""
Eres un analista de tendencias temporales IoT. El usuario solicita información sobre un período específico.

CONSULTA TEMPORAL: "{user_query}"

⏰ **PERÍODO ANALIZADO**: {time_info}

DATOS DEL PERÍODO:
{intelligent_response}

INSTRUCCIONES ESPECÍFICAS:
1. Enfócate en el PERÍODO ESPECÍFICO solicitado (últimas 24 horas, hoy, etc.)
2. Menciona la cantidad exacta de registros analizados
3. Describe tendencias y patrones en ese período
4. Compara con períodos anteriores si es relevante
5. Identifica cambios significativos en el tiempo solicitado

RESPONDE ENFOCÁNDOTE EN EL PERÍODO TEMPORAL:
"""

def create_visualization_prompt(user_query: str, intelligent_response: str, 
                               comprehensive_analysis: Dict) -> str:
    """Crear prompt especializado para consultas de visualización"""
    
    return f"""
Eres un especialista en visualización de datos IoT. El usuario solicita gráficos específicos.

SOLICITUD DE VISUALIZACIÓN: "{user_query}"

DATOS DISPONIBLES:
{intelligent_response}

INSTRUCCIONES ESPECÍFICAS:
1. Confirma que se generará la visualización solicitada
2. Especifica QUÉ sensores/datos se incluirán en el gráfico
3. Describe brevemente qué mostrará la visualización
4. NO generes gráficos de datos no solicitados
5. Enfócate en responder exactamente lo que se pidió visualizar

RESPONDE CONFIRMANDO LA VISUALIZACIÓN ESPECÍFICA:
"""

def create_general_prompt(user_query: str, intelligent_response: str, 
                         comprehensive_analysis: Dict, statistical_analysis: Dict) -> str:
    """Crear prompt general mejorado"""
    
    insights_text = ""
    if statistical_analysis.get('insights'):
        insights_text = "\n💡 **INSIGHTS INTELIGENTES:**\n"
        for insight in statistical_analysis['insights'][:3]:  # Top 3 insights
            insights_text += f"• {insight.get('title', 'Insight')}: {insight.get('description', '')}\n"
    
    return f"""
Eres un asistente especializado en sistemas IoT con capacidad de análisis avanzado.

CONSULTA: "{user_query}"

DATOS REALES DEL SISTEMA:
{intelligent_response}

{insights_text}

ANÁLISIS DISPONIBLE:
- Dispositivos: {comprehensive_analysis.get('device_analysis', {}).get('total_devices', 0)} activos
- Sensores: {comprehensive_analysis.get('device_analysis', {}).get('total_sensors', 0)} tipos
- Registros: {comprehensive_analysis.get('total_records', 0)} procesados

INSTRUCCIONES:
1. Responde específicamente a la consulta del usuario
2. Usa los datos reales proporcionados
3. Incluye insights relevantes cuando sea apropiado
4. Sé conversacional pero preciso
5. Proporciona recomendaciones si es útil

RESPONDE DE FORMA INTELIGENTE Y ÚTIL:
"""

def should_generate_visualization(user_query: str) -> bool:
    """Determinar si la consulta requiere generar visualizaciones"""
    query_lower = user_query.lower()
    
    # Palabras clave que REQUIEREN visualización
    visualization_keywords = [
        'gráfico', 'grafico', 'gráfica', 'grafica', 'visualiza', 'visualización',
        'chart', 'plot', 'mostrar gráfico', 'generar gráfico', 'hacer gráfico',
        'representar gráficamente', 'plotear', 'diagrama'
    ]
    
    # Palabras clave que NO requieren visualización
    no_visualization_keywords = [
        'promedio', 'media', 'estadística', 'estadisticas', 'cálculo', 'calculos',
        'máximo', 'mínimo', 'suma', 'total', 'contar', 'cuántos', 'cuantos',
        'estado', 'información', 'datos', 'descripción', 'explicar'
    ]
    
    # Verificar si se solicita explícitamente visualización
    explicit_visualization = any(keyword in query_lower for keyword in visualization_keywords)
    
    # Verificar si es consulta que NO requiere visualización
    stats_only = any(keyword in query_lower for keyword in no_visualization_keywords)
    
    # Solo generar si se solicita explícitamente
    if explicit_visualization:
        logger.info(f"🎯 Visualización REQUERIDA para consulta: {user_query}")
        return True
    elif stats_only:
        logger.info(f"📊 Consulta estadística - NO requiere visualización: {user_query}")
        return False
    else:
        # Para consultas generales, NO generar visualización automáticamente
        logger.info(f"💬 Consulta general - NO requiere visualización: {user_query}")
        return False

def filter_visualization_data(raw_data: List, user_query: str) -> List:
    """Filtrar datos específicamente para visualización según la consulta"""
    try:
        # Si se solicita período específico, filtrar
        if any(word in user_query.lower() for word in ['últimas 24', '24 horas', 'hoy', 'reciente']):
            return filter_data_by_time(raw_data, user_query)
        
        # Si se solicitan sensores específicos, filtrar
        requested_sensors = []
        query_lower = user_query.lower()
        
        sensor_types = ['temperatura', 'temperature', 'ldr', 'light', 'ntc']
        for sensor in sensor_types:
            if sensor in query_lower:
                requested_sensors.append(sensor)
        
        if requested_sensors:
            # Filtrar solo registros que contengan los sensores solicitados
            filtered_data = []
            for record in raw_data:
                if any(sensor in str(record).lower() for sensor in requested_sensors):
                    filtered_data.append(record)
            
            logger.info(f"🎯 Datos filtrados para sensores específicos: {len(raw_data)} → {len(filtered_data)}")
            return filtered_data if filtered_data else raw_data
        
        # Si no hay filtros específicos, usar todos los datos pero limitados
        return raw_data[-200:] if len(raw_data) > 200 else raw_data
        
    except Exception as e:
        logger.warning(f"⚠️ Error filtrando datos para visualización: {e}")
        return raw_data