#!/usr/bin/env python3
"""
Quick Setup Script - Sistema de URLs Automático
===============================================

Script de configuración rápida para implementar el nuevo sistema de gestión
automática de URLs de Cloudflare en el proyecto.

Este script:
1. Configura el sistema de URLs automático
2. Actualiza la URL actual a la nueva
3. Valida que todo funcione correctamente
4. Proporciona instrucciones para migrar el código

Uso:
    python quick_setup.py --new-url https://replica-subscriber-permission-restricted.trycloudflare.com
    python quick_setup.py --validate
    python quick_setup.py --migrate-example

Autor: IoT Agent System
Fecha: 22 de octubre de 2025
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

def setup_new_url_system(new_url: str = None):
    """
    Configurar el nuevo sistema de URLs automático.
    
    Args:
        new_url: Nueva URL de Cloudflare
    """
    print("🚀 CONFIGURANDO SISTEMA DE URLs AUTOMÁTICO")
    print("=" * 50)
    
    # URL por defecto si no se proporciona
    if not new_url:
        new_url = "https://replica-subscriber-permission-restricted.trycloudflare.com"
    
    print(f"🎯 Configurando con URL: {new_url}")
    
    # 1. Importar y configurar el manager
    try:
        from modules.utils.cloudflare_url_manager import get_cloudflare_url_manager
        from modules.utils.jetson_url_config import refresh_jetson_url, add_new_cloudflare_url
        
        print("✅ Módulos importados correctamente")
        
        # 2. Agregar la nueva URL al sistema
        print("📝 Registrando nueva URL...")
        add_new_cloudflare_url(new_url)
        
        # 3. Refrescar URLs
        print("🔄 Actualizando sistema...")
        current_url = refresh_jetson_url()
        
        print(f"✅ Sistema configurado con URL: {current_url}")
        
        # 4. Validar funcionamiento
        manager = get_cloudflare_url_manager()
        health = manager.health_check()
        
        print(f"\n🏥 Estado del sistema:")
        print(f"   Salud general: {health['overall_health']}")
        print(f"   URL actual: {health['current_url']}")
        print(f"   URL funciona: {health['current_url_working']}")
        
        if health['overall_health'] == 'healthy':
            print("🎉 ¡Sistema configurado correctamente!")
            return True
        else:
            print("⚠️ Sistema configurado pero con problemas de conectividad")
            return False
            
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("💡 Asegúrate de que los archivos del sistema estén en modules/utils/")
        return False
    except Exception as e:
        print(f"❌ Error configurando sistema: {e}")
        return False

def validate_system():
    """Validar que el sistema funcione correctamente."""
    print("🔍 VALIDANDO SISTEMA DE URLs")
    print("=" * 35)
    
    try:
        # Importar componentes
        from modules.utils.jetson_url_config import (
            JETSON_API_URL, 
            get_current_jetson_url,
            validate_jetson_url,
            get_jetson_config
        )
        from modules.utils.cloudflare_url_manager import get_cloudflare_url_manager
        
        print("✅ Módulos importados")
        
        # Mostrar configuración actual
        config = get_jetson_config()
        print(f"\n📊 Configuración actual:")
        for key, value in config.items():
            print(f"   {key}: {value}")
        
        # Validar URL
        print(f"\n🧪 Validando conectividad...")
        is_valid = validate_jetson_url()
        print(f"   URL válida: {'✅' if is_valid else '❌'}")
        
        # Estado del manager
        manager = get_cloudflare_url_manager()
        status = manager.get_status()
        
        print(f"\n🔧 Estado del manager:")
        print(f"   Cache válido: {'✅' if status['cache_valid'] else '❌'}")
        print(f"   URLs fallback: {len(status['fallback_urls'])}")
        
        # Reporte de salud completo
        health = manager.health_check()
        print(f"\n🏥 Salud del sistema: {health['overall_health']}")
        
        if health['recommendations']:
            print(f"📋 Recomendaciones:")
            for rec in health['recommendations']:
                print(f"   - {rec}")
        
        return health['overall_health'] == 'healthy'
        
    except Exception as e:
        print(f"❌ Error en validación: {e}")
        return False

def show_migration_guide():
    """Mostrar guía de migración para el código existente."""
    print("📖 GUÍA DE MIGRACIÓN RÁPIDA")
    print("=" * 30)
    
    print("""
🔄 PASOS PARA MIGRAR CÓDIGO EXISTENTE:

1️⃣ MÉTODO SIMPLE - Reemplazar URLs hardcodeadas:
   
   ❌ ANTES:
   base_url = "https://replica-subscriber-permission-restricted.trycloudflare.com"
   
   ✅ DESPUÉS:
   from modules.utils.jetson_url_config import JETSON_API_URL
   base_url = JETSON_API_URL

2️⃣ MÉTODO DINÁMICO - Para URLs que necesitan actualizarse:
   
   ❌ ANTES:
   url = "https://replica-subscriber-permission-restricted.trycloudflare.com"
   
   ✅ DESPUÉS:
   from modules.utils.jetson_url_config import get_current_jetson_url
   url = get_current_jetson_url()

3️⃣ MÉTODO AVANZADO - Con auto-recuperación:
   
   ✅ NUEVO:
   from modules.utils.jetson_url_config import (
       JETSON_API_URL, 
       validate_jetson_url, 
       refresh_jetson_url
   )
   
   base_url = JETSON_API_URL
   if not validate_jetson_url(base_url):
       base_url = refresh_jetson_url()

4️⃣ ARCHIVOS PRINCIPALES A MIGRAR:
   - streamlit_app/app_cloud.py
   - modules/agents/cloud_iot_agent.py
   - modules/tools/jetson_api_connector*.py
   - tests/*.py
   - *.py (archivos con URLs hardcodeadas)

5️⃣ AUTOMATIZACIÓN:
   python url_update_automation.py --update
   python url_update_automation.py --monitor  # Para monitoreo continuo

💡 VENTAJAS DEL NUEVO SISTEMA:
   ✅ URLs siempre actualizadas automáticamente
   ✅ Auto-detección de cambios de Cloudflare
   ✅ Fallback robusto cuando una URL falla
   ✅ Cache inteligente para mejor rendimiento
   ✅ Compatible con Streamlit Cloud
   ✅ No más modificaciones manuales de 50+ archivos
""")

def run_migration_example():
    """Ejecutar ejemplo práctico de migración."""
    print("🧪 EJEMPLO PRÁCTICO DE MIGRACIÓN")
    print("=" * 35)
    
    try:
        from examples.url_migration_examples import main as run_examples
        run_examples()
        
    except ImportError:
        print("⚠️ Archivo de ejemplos no encontrado")
        print("💡 Ejecuta: python examples/url_migration_examples.py")
    except Exception as e:
        print(f"❌ Error ejecutando ejemplos: {e}")

def create_deployment_config():
    """Crear configuración para deployment en Streamlit Cloud."""
    print("☁️ CREANDO CONFIGURACIÓN PARA STREAMLIT CLOUD")
    print("=" * 45)
    
    # Crear archivo de secrets actualizado
    secrets_content = f'''# Streamlit Cloud Secrets - Actualizado {datetime.now().strftime("%Y-%m-%d")}
# ================================================================

# API Keys
GROQ_API_KEY = "TU_API_KEY_DE_GROQ_AQUI"

# Jetson API URL - Se actualiza automáticamente por el sistema
JETSON_API_URL = "https://replica-subscriber-permission-restricted.trycloudflare.com"

# Configuración opcional
JETSON_API_TIMEOUT = 30
JETSON_API_RETRIES = 3
DEBUG_MODE = false

# Sistema de URLs automático - configuración
URL_CACHE_TTL = 300
URL_AUTO_REFRESH = true
URL_MONITORING_ENABLED = true
'''
    
    secrets_file = Path(".streamlit/secrets.toml")
    secrets_file.parent.mkdir(exist_ok=True)
    
    with open(secrets_file, 'w', encoding='utf-8') as f:
        f.write(secrets_content)
    
    print(f"✅ Archivo de secrets creado: {secrets_file}")
    
    # Crear README actualizado
    readme_content = f'''# 🚀 DEPLOY AUTOMATIZADO EN STREAMLIT CLOUD

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
Generado automáticamente el {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
'''
    
    readme_file = Path("DEPLOY_AUTOMATICO.md")
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Guía de deploy creada: {readme_file}")
    
    print(f"\n🎉 Configuración para Streamlit Cloud lista!")
    print(f"📁 Archivos creados:")
    print(f"   - {secrets_file}")
    print(f"   - {readme_file}")

def main():
    """Función principal del script de configuración."""
    parser = argparse.ArgumentParser(
        description="Configuración rápida del sistema de URLs automático"
    )
    
    parser.add_argument(
        '--new-url',
        type=str,
        help='Nueva URL de Cloudflare a configurar'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validar que el sistema funcione'
    )
    
    parser.add_argument(
        '--migrate-guide',
        action='store_true',
        help='Mostrar guía de migración'
    )
    
    parser.add_argument(
        '--migrate-example',
        action='store_true',
        help='Ejecutar ejemplo de migración'
    )
    
    parser.add_argument(
        '--deploy-config',
        action='store_true',
        help='Crear configuración para Streamlit Cloud'
    )
    
    args = parser.parse_args()
    
    if args.validate:
        success = validate_system()
        sys.exit(0 if success else 1)
        
    elif args.migrate_guide:
        show_migration_guide()
        
    elif args.migrate_example:
        run_migration_example()
        
    elif args.deploy_config:
        create_deployment_config()
        
    else:
        # Configuración completa por defecto
        print("🎉 CONFIGURACIÓN COMPLETA DEL SISTEMA")
        print("=" * 40)
        
        # 1. Configurar sistema
        success = setup_new_url_system(args.new_url)
        
        if success:
            # 2. Crear configuración de deploy
            create_deployment_config()
            
            # 3. Mostrar guía de migración
            show_migration_guide()
            
            print("\n🎊 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
            print("\n📋 PRÓXIMOS PASOS:")
            print("1. Migra tu código usando la guía mostrada")
            print("2. Prueba el sistema: python quick_setup.py --validate")
            print("3. Configura Streamlit Cloud con los archivos generados")
            print("4. Opcional: python url_update_automation.py --monitor")
            
        else:
            print("\n❌ Configuración incompleta")
            print("🔧 Revisa los errores mostrados arriba")
            sys.exit(1)

if __name__ == "__main__":
    main()