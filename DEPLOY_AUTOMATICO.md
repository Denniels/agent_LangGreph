# 🚀 DEPLOY AUTOMATIZADO EN STREAMLIT CLOUD

## ✨ NUEVA FUNCIONALIDAD: URLs AUTOMÁTICAS

Este sistema ahora gestiona automáticamente las URLs de Cloudflare que cambian.
**No necesitas modificar archivos manualmente cuando cambie la URL.**

## 🔧 CONFIGURACIÓN EN STREAMLIT CLOUD

1. Ve a tu app en Streamlit Cloud
2. Settings → Secrets
3. Pega esta configuración:

```toml
GROQ_API_KEY = "tu_api_key_real_aqui"
JETSON_API_URL = "https://replica-subscriber-permission-restricted.trycloudflare.com"
URL_AUTO_REFRESH = true
```

## 🎯 CARACTERÍSTICAS AUTOMÁTICAS

✅ **Auto-detección**: Detecta automáticamente cuando cambia la URL de Cloudflare
✅ **Cache inteligente**: Optimiza rendimiento con cache de 5 minutos
✅ **Fallback robusto**: Usa URLs alternativas si una falla
✅ **Zero-downtime**: Transiciones suaves entre URLs
✅ **Cloud-compatible**: Funciona perfectamente en Streamlit Cloud

## 🔄 MONITOREO AUTOMÁTICO

El sistema consulta el endpoint `/cf_url` para obtener la URL actual.
Si detecta cambios, actualiza automáticamente todas las conexiones.

## 📞 SOPORTE

Si tienes problemas, revisa los logs de Streamlit Cloud.
El sistema registra todos los cambios de URL automáticamente.

---
Generado automáticamente el 2025-10-22 15:46:26
