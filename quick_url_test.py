#!/usr/bin/env python3
"""
Quick URL Detection Test - Prueba Rápida Antes/Después del Reinicio
================================================================

Script simple para ejecutar antes y después del reinicio del servidor
para verificar que el sistema de detección de URLs funcione correctamente.
"""

import sys
import os
sys.path.append('.')

import time
from datetime import datetime

def test_url_detection():
    """Probar detección de URL y mostrar resultados."""
    print("🧪 PRUEBA RÁPIDA DE DETECCIÓN DE URL DE CLOUDFLARE")
    print("=" * 60)
    print(f"⏰ Hora de prueba: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Probar sistema híbrido
    print("1️⃣ Probando sistema híbrido...")
    try:
        from modules.utils.hybrid_url_manager import get_jetson_url_hybrid
        start_time = time.time()
        url = get_jetson_url_hybrid()
        response_time = (time.time() - start_time) * 1000
        
        print(f"   ✅ ÉXITO: {url}")
        print(f"   ⏱️ Tiempo: {response_time:.1f}ms")
        
        # Probar conectividad
        import requests
        try:
            response = requests.get(f"{url}/health", timeout=10)
            if response.status_code == 200:
                print(f"   🟢 Conectividad: OK (HTTP {response.status_code})")
            else:
                print(f"   🟡 Conectividad: Respuesta {response.status_code}")
        except Exception as conn_error:
            print(f"   🔴 Conectividad: ERROR - {conn_error}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print()
    
    # 2. Probar scraping del dashboard
    print("2️⃣ Probando dashboard scraping...")
    try:
        from modules.utils.dashboard_url_extractor import get_jetson_url_from_dashboard
        start_time = time.time()
        url = get_jetson_url_from_dashboard()
        response_time = (time.time() - start_time) * 1000
        
        print(f"   ✅ ÉXITO: {url}")
        print(f"   ⏱️ Tiempo: {response_time:.1f}ms")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print()
    
    # 3. Probar aplicación principal
    print("3️⃣ Probando configuración de la aplicación...")
    try:
        # Simular importación de la app
        os.environ['GROQ_API_KEY'] = 'test-key'  # Temporal para evitar errores
        
        from streamlit_app.app_final_simplified import JETSON_API_URL
        print(f"   ✅ URL configurada en app: {JETSON_API_URL}")
        
        # Probar conectividad
        import requests
        try:
            response = requests.get(f"{JETSON_API_URL}/health", timeout=10)
            if response.status_code == 200:
                print(f"   🟢 App conectividad: OK")
            else:
                print(f"   🟡 App conectividad: HTTP {response.status_code}")
        except:
            print(f"   🔴 App conectividad: ERROR")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print()
    
    # 4. Resumen
    print("📋 RESUMEN DE LA PRUEBA")
    print("-" * 30)
    print("✅ = Método funcionando correctamente")
    print("❌ = Método con problemas")
    print("🟢 = URL responde correctamente")
    print("🔴 = URL no responde")
    print()
    print("💡 RECOMENDACIÓN:")
    print("   Ejecuta este script ANTES y DESPUÉS del reinicio")
    print("   para verificar que el sistema detecte el cambio de URL.")
    print()
    print("🔄 Después del reinicio, la URL debería cambiar automáticamente")
    print("   y todos los métodos deberían detectar la nueva URL.")


def save_test_snapshot():
    """Guardar snapshot del estado actual."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"url_snapshot_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"URL Detection Snapshot - {datetime.now()}\n")
            f.write("=" * 50 + "\n\n")
            
            # Intentar obtener URLs de todos los métodos
            methods = [
                ("Hybrid Manager", "modules.utils.hybrid_url_manager", "get_jetson_url_hybrid"),
                ("Dashboard Scraping", "modules.utils.dashboard_url_extractor", "get_jetson_url_from_dashboard"),
            ]
            
            for method_name, module_name, function_name in methods:
                try:
                    module = __import__(module_name, fromlist=[function_name])
                    func = getattr(module, function_name)
                    url = func()
                    f.write(f"{method_name}: {url}\n")
                except Exception as e:
                    f.write(f"{method_name}: ERROR - {e}\n")
            
            # Configuración de la app
            try:
                os.environ['GROQ_API_KEY'] = 'test-key'
                from streamlit_app.app_final_simplified import JETSON_API_URL
                f.write(f"App Configuration: {JETSON_API_URL}\n")
            except Exception as e:
                f.write(f"App Configuration: ERROR - {e}\n")
        
        print(f"📸 Snapshot guardado en: {filename}")
        
    except Exception as e:
        print(f"❌ Error guardando snapshot: {e}")


if __name__ == "__main__":
    print("🚀 EJECUTANDO PRUEBA RÁPIDA DE DETECCIÓN DE URL")
    print()
    
    # Ejecutar prueba
    test_url_detection()
    
    # Preguntar si guardar snapshot
    save_snapshot = input("\n💾 ¿Guardar snapshot del estado actual? (y/N): ").lower().strip()
    if save_snapshot == 'y':
        save_test_snapshot()
    
    print("\n✅ Prueba completada!")
    print("\n🔄 INSTRUCCIONES PARA EL REINICIO:")
    print("1. 📸 Ejecuta este script ANTES del reinicio (ya lo hiciste)")
    print("2. 🔄 Reinicia el servidor")
    print("3. ⏱️ Espera 2-3 minutos después del reinicio")
    print("4. 🧪 Ejecuta este script DESPUÉS del reinicio")
    print("5. 🔍 Compara los resultados - la URL debería haber cambiado")
    print()
    print("📱 Si todo funciona correctamente, verás una URL diferente")
    print("   en todos los métodos después del reinicio.")