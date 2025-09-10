"""
Prompts específicos para consultas de datos IoT
"""

SENSOR_DATA_QUERY_PROMPT = """
El usuario está consultando datos de sensores. Analiza la solicitud y:

1. Determina qué tipo de datos necesita (temperatura, humedad, luz, etc.)
2. Identifica el rango temporal solicitado
3. Especifica si necesita datos de dispositivos específicos
4. Obtén los datos usando las herramientas disponibles
5. Presenta un análisis claro y útil

Contexto de dispositivos disponibles:
- esp32_wifi_001: Sensores LDR (luz) y NTC (temperatura)
- arduino_eth_002: Sensores de temperatura
- net_device_*: Monitoreo de red

Respuesta estructurada:
📊 **Datos solicitados**: [Resumen de qué se consultó]
🕐 **Período**: [Rango temporal de los datos]
📈 **Resultados**: [Datos obtenidos con análisis]
💡 **Insights**: [Observaciones importantes]
"""

TREND_ANALYSIS_PROMPT = """
Para análisis de tendencias en datos IoT:

1. **Recolecta datos históricos** del período solicitado
2. **Identifica patrones** temporales (horarios, diarios, etc.)
3. **Calcula estadísticas** (promedio, mínimo, máximo, desviación)
4. **Detecta cambios** significativos en el comportamiento
5. **Predice tendencias** basado en datos históricos

Estructura del análisis:
📊 **Datos analizados**: [Cantidad y tipo de datos]
📈 **Tendencias principales**:
   • Tendencia general: ↗️ Creciente / ↘️ Decreciente / ➡️ Estable
   • Variación: [Rango de valores]
   • Promedio: [Valor promedio del período]

🔍 **Patrones identificados**:
   • Ciclos diarios/horarios
   • Picos y valles
   • Comportamientos anómalos

💡 **Interpretación**:
   • Qué significan estos patrones
   • Factores que pueden influir
   • Recomendaciones basadas en tendencias
"""

ALERT_MANAGEMENT_PROMPT = """
Para gestión de alertas del sistema IoT:

1. **Consulta alertas activas** usando las herramientas disponibles
2. **Clasifica por severidad** (alta, media, baja)
3. **Agrupa por tipo** (temperatura, conectividad, sensor, etc.)
4. **Proporciona contexto** sobre cada alerta
5. **Sugiere acciones** para resolver problemas

Formato de respuesta:
🚨 **Alertas Críticas** (requieren atención inmediata)
⚠️ **Alertas de Advertencia** (requieren monitoreo)
ℹ️ **Alertas Informativas** (solo notificación)

Para cada alerta incluye:
- Dispositivo afectado
- Tipo de problema
- Tiempo desde que se activó
- Acción recomendada
"""

DEVICE_HEALTH_PROMPT = """
Para consultas sobre salud de dispositivos:

1. **Verifica conectividad** de todos los dispositivos
2. **Obtén últimas lecturas** de cada sensor
3. **Compara con valores normales** esperados
4. **Identifica dispositivos problemáticos**
5. **Evalúa calidad de datos** (frecuencia, consistencia)

Reporte de salud:
🟢 **Dispositivos Saludables**:
   • Estado: Online y funcionando correctamente
   • Últimos datos: [Timestamp reciente]
   • Sensores: [Lista de sensores activos]

🟡 **Dispositivos con Advertencias**:
   • Problemas menores detectados
   • Posibles interrupciones de conectividad
   • Lecturas fuera de rango normal

🔴 **Dispositivos Críticos**:
   • Offline por tiempo prolongado
   • Fallas de sensor detectadas
   • Errores de comunicación persistentes
"""
