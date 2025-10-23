#!/usr/bin/env python3
"""
URL Discovery Tool - Herramienta de Descubrimiento de URLs
========================================================

Herramienta simple para probar conectividad con URLs de Cloudflare
y determinar cuál es la URL actual que funciona.
"""

import requests
import time
from datetime import datetime

def test_url_connectivity(url: str) -> dict:
    """
    Probar conectividad con una URL.
    
    Args:
        url: URL a probar
        
    Returns:
        Diccionario con resultados de la prueba
    """
    print(f"🔍 Probando: {url}")
    
    try:
        # Probar endpoint de salud
        start_time = time.time()
        response = requests.get(
            f"{url}/health",
            timeout=15,
            allow_redirects=True,
            headers={'User-Agent': 'URLDiscoveryTool/1.0'}
        )
        response_time = (time.time() - start_time) * 1000
        
        result = {
            'url': url,
            'status': 'SUCCESS',
            'status_code': response.status_code,
            'response_time_ms': round(response_time, 2),
            'accessible': response.status_code == 200,
            'timestamp': datetime.now().isoformat()
        }
        
        if response.status_code == 200:
            print(f"  ✅ FUNCIONA - HTTP {response.status_code} ({response_time:.1f}ms)")
        else:
            print(f"  🟡 RESPONDE - HTTP {response.status_code} ({response_time:.1f}ms)")
            
        return result
        
    except requests.exceptions.ConnectTimeout:
        print(f"  ⏰ TIMEOUT - No responde en 15s")
        return {
            'url': url,
            'status': 'TIMEOUT',
            'error': 'Connection timeout',
            'accessible': False,
            'timestamp': datetime.now().isoformat()
        }
        
    except requests.exceptions.ConnectionError as e:
        if 'Failed to resolve' in str(e) or 'getaddrinfo failed' in str(e):
            print(f"  🚫 DNS FAIL - No existe")
            return {
                'url': url,
                'status': 'DNS_FAIL',
                'error': 'DNS resolution failed',
                'accessible': False,
                'timestamp': datetime.now().isoformat()
            }
        else:
            print(f"  🔴 CONEXIÓN - {str(e)[:50]}...")
            return {
                'url': url,
                'status': 'CONNECTION_ERROR',
                'error': str(e),
                'accessible': False,
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        print(f"  ❌ ERROR - {str(e)[:50]}...")
        return {
            'url': url,
            'status': 'ERROR',
            'error': str(e),
            'accessible': False,
            'timestamp': datetime.now().isoformat()
        }

def discover_working_urls():
    """Descubrir qué URLs funcionan actualmente."""
    print("🔍 DESCUBRIMIENTO DE URLs DE CLOUDFLARE")
    print("=" * 50)
    print(f"⏰ Hora de prueba: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # URLs candidatas para probar
    candidate_urls = [
        "https://returned-convenience-tower-switched.trycloudflare.com",
        "https://reflect-wed-governmental-fisher.trycloudflare.com", 
        "https://replica-subscriber-permission-restricted.trycloudflare.com",
        # Agregar más URLs si las conoces
    ]
    
    results = []
    working_urls = []
    
    print("🧪 PROBANDO URLS CANDIDATAS:")
    print("-" * 30)
    
    for url in candidate_urls:
        result = test_url_connectivity(url)
        results.append(result)
        
        if result['accessible']:
            working_urls.append(url)
    
    print(f"\n📊 RESUMEN:")
    print(f"  URLs probadas: {len(candidate_urls)}")
    print(f"  URLs funcionando: {len(working_urls)}")
    
    if working_urls:
        print(f"\n✅ URLs QUE FUNCIONAN:")
        for url in working_urls:
            print(f"  ✅ {url}")
        print(f"\n💡 RECOMENDACIÓN: Usar la primera URL que funcione")
        return working_urls[0]
    else:
        print(f"\n🚫 NINGUNA URL FUNCIONA ACTUALMENTE")
        print(f"📝 Esto significa que:")
        print(f"  - El servidor puede estar reiniciando")
        print(f"  - La URL cambió a una que no conocemos")
        print(f"  - Hay problemas de conectividad")
        print(f"\n💡 SUGERENCIAS:")
        print(f"  1. Verificar el dashboard: https://iotapp-jvwtoekeo73ruxn9mdhfnc.streamlit.app/")
        print(f"  2. Esperar unos minutos y volver a probar")
        print(f"  3. Verificar que el servidor esté ejecutándose")
        return None

if __name__ == "__main__":
    working_url = discover_working_urls()
    
    if working_url:
        print(f"\n🎯 URL RECOMENDADA PARA USO: {working_url}")
        
        # Probar algunas consultas básicas
        print(f"\n🔬 PROBANDO FUNCIONALIDAD BÁSICA:")
        try:
            # Probar endpoint de dispositivos
            response = requests.get(f"{working_url}/devices", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ /devices: {len(data)} dispositivos")
            else:
                print(f"  🟡 /devices: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ /devices: Error - {str(e)[:50]}...")
        
        try:
            # Probar endpoint de datos
            response = requests.get(f"{working_url}/data", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ /data: {len(data)} registros")
            else:
                print(f"  🟡 /data: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ /data: Error - {str(e)[:50]}...")
    
    print(f"\n✅ Descubrimiento completado!")