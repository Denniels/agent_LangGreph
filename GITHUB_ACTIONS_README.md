# 🤖 GitHub Actions - Automatización Completa de URLs de Cloudflare

## 🎯 Objetivo

Este sistema automatiza completamente la detección y actualización de URLs de Cloudflare cuando cambian, sin intervención manual necesaria.

## 🔄 Flujo de Automatización

### 1. **Detección Automática** (Cada 5 minutos)
- GitHub Actions ejecuta el workflow automáticamente
- Consulta el endpoint `/cf_url` para obtener la URL actual
- Compara con la URL guardada anteriormente

### 2. **Actualización Automática** (Si hay cambios)
- Actualiza todos los archivos con la nueva URL
- Genera commit con mensaje descriptivo
- Push automático al repositorio

### 3. **Deploy Automático** (Streamlit Cloud)
- Streamlit Cloud detecta el push automáticamente
- Redeploy automático con la nueva URL
- Sistema operativo sin downtime

## 📋 Configuración Necesaria

### Secrets de Streamlit Cloud (SOLO estos)
```toml
# SOLO mantener esto en Streamlit Cloud secrets:
GROQ_API_KEY = "tu_api_key_aqui"

# NO agregar JETSON_API_URL - se detecta automáticamente
```

### Repository Settings (GitHub)
- ✅ Actions habilitadas (default)
- ✅ Push automático habilitado (default) 
- ✅ Streamlit Cloud conectado al repo

## 🚀 Activación del Sistema

### Automática
- Se ejecuta cada 5 minutos automáticamente
- No requiere intervención manual

### Manual (si es necesario)
```bash
# Desde GitHub web interface:
Actions → "Auto-Update Cloudflare URLs" → "Run workflow"

# O desde CLI:
gh workflow run cloudflare-url-update.yml
```

## 📊 Monitoreo

### Logs en GitHub Actions
- Ver ejecuciones: `Actions` tab en GitHub
- Logs detallados de cada ejecución
- Notificaciones automáticas si falla

### Verificación Local
```bash
# Verificar estado del sistema
python test_complete_integration.py --test-current-system

# Simular cambio de URL
python test_complete_integration.py --simulate-new-url https://nueva-url.trycloudflare.com
```

## 🔧 Troubleshooting

### Si GitHub Actions falla:
1. Revisar logs en GitHub Actions tab
2. Verificar que el endpoint `/cf_url` esté respondiendo
3. Ejecutar manualmente: `python url_update_automation.py --update`

### Si Streamlit Cloud no se actualiza:
1. Verificar que NO haya `JETSON_API_URL` en secrets
2. Forzar redeploy en Streamlit Cloud
3. Verificar logs de Streamlit Cloud

### Si el sistema no detecta cambios:
1. Forzar actualización: `python url_update_automation.py --update --force`
2. Verificar conectividad con Jetson API
3. Revisar cache del sistema: `python quick_setup.py --validate`

## 📈 Estadísticas del Sistema

### Frecuencia de Ejecución
- **Automática**: Cada 5 minutos
- **Tiempo promedio**: ~30 segundos por ejecución
- **Costo**: Mínimo (GitHub Actions free tier)

### Eficiencia
- **Sin cambios**: ~5 segundos (solo verificación)
- **Con cambios**: ~30 segundos (actualización completa)
- **Archivos monitoreados**: 60+ archivos automáticamente

## 🎉 Beneficios

### ✅ Para Desarrollo
- No más URLs hardcodeadas
- Desarrollo sin interrupciones
- Sistema auto-sanador

### ✅ Para Producción  
- Zero-downtime en cambios
- Actualizaciones automáticas 24/7
- Monitoreo continuo integrado

### ✅ Para el Equipo
- No más coordinación manual
- Historial automático de cambios
- Concentración en features importantes

## 🔮 Funcionalidades Avanzadas Disponibles

### Notificaciones (Opcional)
Agregar a `.github/workflows/cloudflare-url-update.yml`:
```yaml
- name: Notify Slack
  if: steps.check_changes.outputs.changes_detected == 'true'
  run: |
    curl -X POST -H 'Content-type: application/json' \
      --data '{"text":"🔄 Cloudflare URL updated automatically!"}' \
      ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Validación Adicional
```yaml
- name: Test new URL
  run: |
    python -c "
    import requests
    url = '$(python -c "from modules.utils.jetson_url_config import get_current_jetson_url; print(get_current_jetson_url())")'
    response = requests.get(f'{url}/health', timeout=10)
    assert response.status_code == 200, 'New URL not responding'
    print('✅ New URL validated successfully')
    "
```

## 📞 Soporte

### Logs Útiles
```bash
# Ver estado del sistema
python quick_setup.py --validate

# Health check completo
python -c "
from modules.utils.cloudflare_url_manager import get_cloudflare_url_manager
manager = get_cloudflare_url_manager()
health = manager.health_check()
print(f'Estado: {health}')
"
```

### Contacto
- 🐛 Issues: GitHub Issues tab
- 📧 Crítico: Verificar GitHub Actions logs
- 🔄 Reset: `python quick_setup.py --new-url URL_MANUAL`

---

**¡Sistema completamente automatizado y listo para producción!** 🚀