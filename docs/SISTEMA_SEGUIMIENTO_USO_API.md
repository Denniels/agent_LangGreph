# Sistema de Seguimiento de Uso de API - Groq

## 🎯 Descripción General

El sistema de seguimiento de uso de API permite monitorear y controlar el uso diario de las APIs de Groq, evitando sobrepasar los límites gratuitos y proporcionando transparencia total al usuario sobre su consumo.

## ✨ Características Principales

### 📊 **Seguimiento en Tiempo Real**
- ✅ Contador de consultas (requests) por modelo
- ✅ Contador de tokens utilizados
- ✅ Cálculo automático de porcentajes de uso
- ✅ Estado visual del consumo (normal/advertencia/crítico)

### 🔄 **Reset Automático Diario**
- ✅ Los contadores se resetean automáticamente cada día
- ✅ Sincronizado con los límites de Groq (medianoche UTC)
- ✅ Persistencia de datos entre sesiones

### 🚨 **Protección Contra Límites**
- ✅ Verificación previa antes de hacer consultas
- ✅ Bloqueo automático al alcanzar límites
- ✅ Mensajes informativos y alertas visuales
- ✅ Degradación gradual con advertencias

### 📈 **Interfaz Visual Completa**
- ✅ Pestaña dedicada en Streamlit
- ✅ Métricas en tiempo real en sidebar
- ✅ Gráficos de progreso con barras de color
- ✅ Tablas de todos los modelos disponibles

## 🤖 Modelos Soportados y Límites (ACTUALIZADOS Sep 2025)

| Modelo | Descripción | Requests/día | Tokens/día |
|--------|-------------|--------------|------------|
| `llama-3.1-8b-instant` | Llama 3.1 8B Instant | 14,400 | 1,000,000 |
| `llama-3.3-70b-versatile` | Llama 3.3 70B Versatile | 1,000 | 1,000,000 |
| `meta-llama/llama-guard-4-12b` | Meta Llama Guard 4 12B | 14,400 | 1,000,000 |
| `groq/compound` | Groq Compound | 250 | 1,000,000 |
| `groq/compound-mini` | Groq Compound Mini | 250 | 1,000,000 |
| `gemma2-9b-it` | Gemma 2 9B IT | 14,400 | 1,000,000 |

### 📋 Modelos Legacy (Compatibilidad)
| Modelo | Descripción | Requests/día | Tokens/día |
|--------|-------------|--------------|------------|
| `llama-3.1-70b-versatile` | Llama 3.1 70B Versatile | 1,000 | 1,000,000 |
| `llama3-8b-8192` | Llama 3 8B | 14,400 | 1,000,000 |
| `llama3-70b-8192` | Llama 3 70B | 1,000 | 1,000,000 |
| `mixtral-8x7b-32768` | Mixtral 8x7B | 14,400 | 1,000,000 |
| `gemma-7b-it` | Gemma 7B IT | 14,400 | 1,000,000 |

## 🏗️ Arquitectura del Sistema

### 📁 **Estructura de Archivos**

```
modules/utils/
├── usage_tracker.py          # 🧠 Lógica principal del seguimiento
├── streamlit_usage_display.py # 🎨 Componentes visuales para Streamlit
└── __init__.py

usage_data.json               # 💾 Persistencia de datos (creado automáticamente)
```

### 🔧 **Componentes Clave**

#### 1. **UsageTracker** (`usage_tracker.py`)
```python
from modules.utils.usage_tracker import usage_tracker

# Registrar una consulta
usage_info = usage_tracker.track_request("llama-3.1-8b-instant", tokens_used=150)

# Verificar si se puede hacer una consulta
can_make, message = usage_tracker.check_can_make_request("llama-3.1-8b-instant")

# Obtener información completa
info = usage_tracker.get_usage_info("llama-3.1-8b-instant")
```

#### 2. **Display Components** (`streamlit_usage_display.py`)
```python
from modules.utils.streamlit_usage_display import display_usage_metrics

# Mostrar métricas en Streamlit
display_usage_metrics(usage_info, "main_usage")
```

#### 3. **Integración con CloudIoTAgent**
```python
# El agente automáticamente registra uso y verifica límites
response = await agent.process_query("¿Cuál es la temperatura?")
```

## 🚀 Integración Completa

### 📊 **En CloudIoTAgent**

El sistema está completamente integrado en el agente principal:

```python
# 1. Verificación previa
can_make_request, usage_message = usage_tracker.check_can_make_request(self.groq_model)

if not can_make_request:
    # Retornar mensaje de límite alcanzado
    return limite_alcanzado_response

# 2. Procesamiento normal
response = self.groq_integration.generate_response(prompt, model=self.groq_model)

# 3. Registro automático
usage_info = usage_tracker.track_request(self.groq_model, estimated_tokens)

# 4. Información en health check
health["api_usage"] = usage_info
```

### 🎨 **En Streamlit**

#### **Pestaña Dedicada "Uso de API"**
- 📊 Métricas principales del modelo actual
- 📈 Barras de progreso visuales
- 🤖 Tabla de todos los modelos
- 📋 Información detallada de límites
- 🔧 Controles administrativos

#### **Sidebar Informativo**
- 🔥 Contador compacto de consultas
- 🎯 Estado visual del uso
- ⚠️ Alertas en tiempo real

## 📋 Estados del Sistema

### ✅ **Normal** (0-74% de uso)
- Color: Verde
- Mensaje: "Uso normal: X requests disponibles"
- Acción: Continúa normalmente

### ⚠️ **Advertencia** (75-89% de uso)
- Color: Naranja
- Mensaje: "Uso alto: X% de requests utilizados"
- Acción: Continúa con advertencia

### 🚨 **Crítico** (90-99% de uso)
- Color: Rojo
- Mensaje: "Uso crítico: X% de requests utilizados"
- Acción: Continúa con alerta crítica

### 🚫 **Límite Alcanzado** (100% de uso)
- Color: Rojo sólido
- Mensaje: "Límite diario alcanzado"
- Acción: Bloqueo automático hasta reset

## 💾 Persistencia de Datos

### **Estructura JSON**
```json
{
  "last_reset_date": "2025-09-12",
  "daily_usage": {
    "llama-3.1-8b-instant": {
      "requests": 150,
      "tokens": 45000,
      "last_request": "2025-09-12T10:30:00"
    }
  },
  "total_lifetime": {
    "requests": 1500,
    "tokens": 450000,
    "days_active": 10
  }
}
```

### **Reset Automático**
- ✅ Detección automática de nuevo día
- ✅ Preservación de estadísticas lifetime
- ✅ Reinicio limpio de contadores diarios

## 🧪 Testing Completo

### **Suite de Tests**
```bash
# Ejecutar tests completos
agente\Scripts\activate; python tests\test_usage_tracking.py
```

### **Tests Incluidos**
1. ✅ **Test Básico**: Inicialización, registro, verificación
2. ✅ **Test Integración**: CloudIoTAgent, health checks
3. ✅ **Test Límites**: Comportamiento cerca de límites

## 🔧 Configuración y Uso

### **Configuración Automática**
```python
# No requiere configuración manual - funciona automáticamente
from modules.utils.usage_tracker import usage_tracker

# Ya está configurado con límites de Groq
```

### **Uso Manual (Opcional)**
```python
# Para otros modelos o APIs
tracker = UsageTracker("custom_usage.json")
tracker.daily_limits["custom-model"] = {
    "requests": 1000,
    "tokens": 50000,
    "description": "Modelo Personalizado"
}
```

## 📈 Beneficios del Sistema

### **Para Usuarios**
- 🎯 **Transparencia Total**: Saben exactamente cuánto han usado
- ⚠️ **Alertas Preventivas**: Avisos antes de agotar límites
- 📊 **Control Visual**: Interfaz clara y comprensible
- 🔄 **Reset Automático**: Sin intervención manual necesaria

### **Para Desarrolladores**
- 🛡️ **Protección Automática**: Previene errores de límite
- 📋 **Logging Completo**: Información detallada de uso
- 🔧 **Fácil Integración**: Drop-in en cualquier componente
- 🧪 **Testing Completo**: Suite de tests exhaustiva

### **Para el Sistema**
- 💰 **Gestión de Costos**: Aunque Groq es gratis, previene abusos
- 📊 **Métricas Operacionales**: Datos de uso para optimización
- 🚀 **Escalabilidad**: Preparado para múltiples modelos
- 🔄 **Mantenimiento Cero**: Funciona automáticamente

## 🎉 Conclusión

El sistema de seguimiento de uso de API proporciona:

1. **🛡️ Protección Completa** contra límites de API
2. **📊 Visibilidad Total** del consumo en tiempo real
3. **🎨 Interfaz Intuitiva** para usuarios finales
4. **🔧 Integración Seamless** con el agente existente
5. **🧪 Testing Robusto** para confiabilidad

**✅ Estado: Completamente implementado y funcionando**
**🚀 Listo para producción en Streamlit Cloud**