# 🚀 DEPLOY EN STREAMLIT CLOUD - GUÍA COMPLETA

## 📋 PRERREQUISITOS

### 1. Cuenta Groq (GRATIS)
- Ve a: https://console.groq.com/
- Crea una cuenta gratuita
- Genera una API Key en: https://console.groq.com/keys
- **GUARDA LA API KEY** (la necesitarás después)

### 2. Repository en GitHub
- Fork este repositorio o súbelo a tu GitHub
- Asegúrate que esté público o dale acceso a Streamlit

## 🎯 PASOS PARA DEPLOY

### Paso 1: Ir a Streamlit Cloud
- Ve a: https://share.streamlit.io/
- Inicia sesión con GitHub

### Paso 2: Crear Nueva App
1. Clic en **"New app"**
2. Selecciona tu repositorio: `agent_LangGreph`
3. **IMPORTANTE**: En "Main file path" pon: `app.py`
4. En "App URL" elige un nombre único

### Paso 3: Configurar Secrets (CRÍTICO)
1. Después de crear la app, ve a **Settings** ⚙️
2. Clic en **"Secrets"**
3. Clic en **"Edit Secrets"**
4. Pega esta configuración:

```toml
GROQ_API_KEY = "TU_API_KEY_DE_GROQ_AQUI"
JETSON_API_URL = "https://couples-mario-repository-alive.trycloudflare.com"
```

5. **¡IMPORTANTE!** Reemplaza `TU_API_KEY_DE_GROQ_AQUI` con tu API key real
6. Guarda los cambios

### Paso 4: Deploy
- La app se deployará automáticamente
- Toma 2-3 minutos la primera vez
- Verás logs de instalación de dependencias

## ✅ VERIFICACIÓN DE FUNCIONAMIENTO

### Funcionalidades que DEBEN funcionar:
- ✅ **Chat IoT**: Consultas al agente sobre sensores
- ✅ **Gráficos**: Visualizaciones matplotlib
- ✅ **Reportes**: Generación de PDFs/Excel
- ✅ **Datos en tiempo real**: Conexión a Jetson

### Troubleshooting Común:

#### ❌ "ModuleNotFoundError"
- **Causa**: requirements.txt desactualizado
- **Solución**: Reboot la app en Streamlit Cloud

#### ❌ "GROQ_API_KEY not found"
- **Causa**: Secrets mal configurados
- **Solución**: Verifica los Secrets en Settings

#### ❌ "No data available"
- **Causa**: Jetson offline (normal)
- **Comportamiento**: App funciona con datos simulados

#### ❌ App muy lenta
- **Causa**: Cache frío
- **Solución**: Espera 30 segundos, recarga

## 🎛️ CONFIGURACIÓN AVANZADA

### Variables de Entorno Opcionales:
```toml
# En Streamlit Cloud Secrets
DEBUG_MODE = true
CACHE_TTL = 600
MODEL_NAME = "llama-3.1-70b-versatile"
```

### URLs de Jetson Alternativas:
Si tu Jetson está en otra URL, cambia en Secrets:
```toml
JETSON_API_URL = "https://tu-nueva-url.trycloudflare.com"
```

## 📊 MONITOREO

### Métricas a Verificar:
- **Tiempo de carga**: < 5 segundos
- **Respuesta del chat**: < 10 segundos
- **Generación de gráficos**: < 3 segundos
- **Reportes**: < 15 segundos

### Logs Importantes:
- `✅ Todas las importaciones exitosas`
- `✅ Conector creado`
- `🎯 ¡Sistema listo para Streamlit Cloud!`

## 🚨 PROBLEMAS CONOCIDOS Y SOLUCIONES

### 1. Error de Matplotlib
```python
# Si aparece error de backend
import matplotlib
matplotlib.use('Agg')
```
**Solución**: Ya incluido en el código

### 2. Error de Memory/Resources
**Causa**: App muy pesada
**Solución**: Cache optimizado ya implementado

### 3. Timeout en Requests
**Causa**: Jetson offline
**Comportamiento**: Normal, usa datos simulados

## 🎉 DEPLOY EXITOSO

Si ves esta pantalla en tu app:
```
🤖 Agente IoT Completo
✅ Todas las funcionalidades cargadas
📊 Conectado a sensores remotos
```

**¡FELICIDADES!** Tu app está funcionando correctamente.

## 📞 SOPORTE

Si tienes problemas:
1. Verifica los logs en Streamlit Cloud
2. Confirma que GROQ_API_KEY esté configurado
3. Reboot la app si es necesario
4. Verifica que requirements.txt esté actualizado

---
**Última actualización**: Octubre 2025
**Versión**: 2.0 - Optimizado para Streamlit Cloud