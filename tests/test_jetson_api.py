#!/usr/bin/env python3
"""
Script de pruebas para verificar la API de Jetson vía Cloudflare Tunnel
Antes de modificar el agente, verificamos conectividad y endpoints
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# URL base de la API
API_BASE_URL = "https://respect-craps-lit-aged.trycloudflare.com"

def test_api_connectivity():
    """Test básico de conectividad"""
    print("🔍 TEST 1: CONECTIVIDAD BÁSICA")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        print(f"  ✅ Status Code: {response.status_code}")
        print(f"  ✅ Response Headers: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            print(f"  ✅ JSON Response: {response.json()}")
        else:
            print(f"  📄 Text Response: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error de conectividad: {e}")
    except Exception as e:
        print(f"  ❌ Error general: {e}")

def test_common_endpoints():
    """Probar endpoints comunes de APIs"""
    print("\n🔍 TEST 2: ENDPOINTS COMUNES")
    print("=" * 50)
    
    common_endpoints = [
        "/",
        "/health", 
        "/api",
        "/api/health",
        "/api/status",
        "/api/devices",
        "/api/sensors", 
        "/api/sensor_data",
        "/api/data",
        "/docs",
        "/redoc",
        "/openapi.json"
    ]
    
    for endpoint in common_endpoints:
        try:
            url = f"{API_BASE_URL}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"  ✅ {endpoint}: {response.status_code}")
                
                # Si es JSON, mostrar estructura
                if response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            print(f"      🔑 Keys: {list(data.keys())}")
                        elif isinstance(data, list) and len(data) > 0:
                            print(f"      📊 List with {len(data)} items")
                            if isinstance(data[0], dict):
                                print(f"      🔑 First item keys: {list(data[0].keys())}")
                    except:
                        pass
                        
            elif response.status_code == 404:
                print(f"  ❌ {endpoint}: 404 Not Found")
            else:
                print(f"  ⚠️ {endpoint}: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"  ⏰ {endpoint}: Timeout")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {endpoint}: {e}")

def test_with_different_methods():
    """Probar diferentes métodos HTTP"""
    print("\n🔍 TEST 3: MÉTODOS HTTP")
    print("=" * 50)
    
    endpoints_to_test = [
        "/api/devices",
        "/api/sensors",
        "/api/data"
    ]
    
    methods = ["GET", "POST", "OPTIONS"]
    
    for endpoint in endpoints_to_test:
        print(f"\n  📍 Testing {endpoint}:")
        for method in methods:
            try:
                url = f"{API_BASE_URL}{endpoint}"
                
                if method == "GET":
                    response = requests.get(url, timeout=5)
                elif method == "POST":
                    response = requests.post(url, json={}, timeout=5)
                elif method == "OPTIONS":
                    response = requests.options(url, timeout=5)
                
                print(f"    {method}: {response.status_code}")
                
                # Mostrar headers CORS si existen
                if method == "OPTIONS":
                    cors_headers = {k: v for k, v in response.headers.items() 
                                  if k.lower().startswith('access-control')}
                    if cors_headers:
                        print(f"      CORS: {cors_headers}")
                
            except Exception as e:
                print(f"    {method}: Error - {e}")

def test_with_query_parameters():
    """Probar con parámetros de consulta"""
    print("\n🔍 TEST 4: PARÁMETROS DE CONSULTA")
    print("=" * 50)
    
    endpoints_with_params = [
        ("/api/devices", {}),
        ("/api/sensors", {}),
        ("/api/data", {}),
        ("/api/sensors", {"limit": 10}),
        ("/api/sensors", {"device_id": "esp32_wifi_001"}),
        ("/api/data", {"limit": 5, "device": "arduino_eth_001"}),
        ("/api/sensors", {"from": "2025-09-10", "to": "2025-09-11"}),
    ]
    
    for endpoint, params in endpoints_with_params:
        try:
            url = f"{API_BASE_URL}{endpoint}"
            response = requests.get(url, params=params, timeout=5)
            
            param_str = "&".join([f"{k}={v}" for k, v in params.items()]) if params else "sin parámetros"
            
            if response.status_code == 200:
                print(f"  ✅ {endpoint}?{param_str}: {response.status_code}")
                
                # Intentar parsear JSON y mostrar info
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"      📊 Retornó {len(data)} elementos")
                    elif isinstance(data, dict):
                        print(f"      🔑 Keys: {list(data.keys())}")
                except:
                    print(f"      📄 Respuesta no-JSON: {len(response.text)} chars")
            else:
                print(f"  ❌ {endpoint}?{param_str}: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {endpoint}?{param_str}: {e}")

def test_authentication_methods():
    """Probar diferentes métodos de autenticación"""
    print("\n🔍 TEST 5: MÉTODOS DE AUTENTICACIÓN")
    print("=" * 50)
    
    test_endpoint = "/api/devices"
    
    auth_methods = [
        ("Sin auth", {}),
        ("Bearer token", {"Authorization": "Bearer test_token"}),
        ("API Key header", {"X-API-Key": "test_key"}),
        ("API Key query", {}, {"api_key": "test_key"}),
        ("Basic auth", {"Authorization": "Basic dGVzdDp0ZXN0"}),  # test:test
    ]
    
    for auth_name, headers, *params in auth_methods:
        try:
            url = f"{API_BASE_URL}{test_endpoint}"
            query_params = params[0] if params else {}
            
            response = requests.get(url, headers=headers, params=query_params, timeout=5)
            
            print(f"  {auth_name}: {response.status_code}")
            
            # Si hay un status especial, mostrar detalles
            if response.status_code in [401, 403]:
                print(f"    🔒 Auth requerida: {response.text[:100]}")
            elif response.status_code == 200:
                print(f"    ✅ Acceso permitido")
                
        except Exception as e:
            print(f"  {auth_name}: Error - {e}")

def comprehensive_api_discovery():
    """Descubrimiento comprensivo de la API"""
    print("\n🔍 TEST 6: DESCUBRIMIENTO COMPRENSIVO")
    print("=" * 50)
    
    # Intentar obtener documentación de la API
    doc_endpoints = ["/docs", "/redoc", "/openapi.json", "/swagger.json", "/api-docs"]
    
    for doc_endpoint in doc_endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{doc_endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"  ✅ Documentación encontrada en: {doc_endpoint}")
                
                if doc_endpoint.endswith('.json'):
                    try:
                        openapi_spec = response.json()
                        if 'paths' in openapi_spec:
                            print(f"      📋 Endpoints disponibles:")
                            for path in openapi_spec['paths'].keys():
                                print(f"        • {path}")
                    except:
                        pass
                        
        except Exception as e:
            continue
    
    print(f"\n  🌐 URL base probada: {API_BASE_URL}")
    print(f"  🕐 Timestamp: {datetime.now()}")

def main():
    """Ejecutar todas las pruebas"""
    print("🧪 PRUEBAS DE CONECTIVIDAD API JETSON VIA CLOUDFLARE")
    print("=" * 60)
    print(f"🎯 Target: {API_BASE_URL}")
    print(f"🕐 Iniciado: {datetime.now()}")
    print()
    
    # Ejecutar todas las pruebas
    test_api_connectivity()
    test_common_endpoints()
    test_with_different_methods()
    test_with_query_parameters()
    test_authentication_methods()
    comprehensive_api_discovery()
    
    print("\n" + "=" * 60)
    print("✅ PRUEBAS COMPLETADAS")
    print("🔄 Revisar resultados para identificar endpoints válidos")

if __name__ == "__main__":
    main()
