#!/usr/bin/env python3
"""
Pruebas específicas de los endpoints que funcionan para el agente
"""

import requests
import json
from datetime import datetime

API_BASE_URL = "https://wonder-sufficiently-generator-click.trycloudflare.com"

def test_working_endpoints():
    """Probar los endpoints que sabemos que funcionan"""
    print("🧪 PRUEBAS DE ENDPOINTS ESPECÍFICOS")
    print("=" * 50)
    
    endpoints = [
        "/",
        "/health", 
        "/status",
        "/devices",
        "/data"
    ]
    
    for endpoint in endpoints:
        print(f"\n📍 Testing {endpoint}:")
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Structure: {type(data)}")
                
                if isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())}")
                    
                    # Mostrar datos específicos según el endpoint
                    if endpoint == "/devices" and "data" in data:
                        devices_data = data["data"]
                        if isinstance(devices_data, list):
                            print(f"  📱 Devices found: {len(devices_data)}")
                            for i, device in enumerate(devices_data[:3]):  # Solo primeros 3
                                print(f"    {i+1}. {device}")
                    
                    elif endpoint == "/data" and "data" in data:
                        sensor_data = data["data"]
                        if isinstance(sensor_data, list):
                            print(f"  📊 Data records: {len(sensor_data)}")
                            for i, record in enumerate(sensor_data[:3]):  # Solo primeros 3
                                print(f"    {i+1}. {record}")
                    
                    elif endpoint == "/health":
                        health_data = data
                        print(f"  💓 Health status: {health_data}")
                        
                    elif endpoint == "/status":
                        status_data = data  
                        print(f"  🔄 System status: {status_data}")
                        
                else:
                    print(f"  Raw data: {data}")
                    
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_data_with_parameters():
    """Probar endpoint /data con diferentes parámetros"""
    print(f"\n🧪 PRUEBAS DE /data CON PARÁMETROS")
    print("=" * 50)
    
    test_params = [
        {},  # Sin parámetros
        {"limit": 10},
        {"limit": 5},
        {"device_id": "esp32_wifi_001"},
        {"device_id": "arduino_eth_001"},
        {"limit": 20, "device_id": "esp32_wifi_001"},
    ]
    
    for params in test_params:
        param_str = "&".join([f"{k}={v}" for k, v in params.items()]) if params else "sin parámetros"
        print(f"\n  🔍 /data?{param_str}")
        
        try:
            response = requests.get(f"{API_BASE_URL}/data", params=params, timeout=10)
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "data" in data:
                    records = data["data"]
                    if isinstance(records, list):
                        print(f"    📊 Records returned: {len(records)}")
                        if records:
                            print(f"    📝 Sample record: {records[0]}")
                else:
                    print(f"    📄 Response: {data}")
            else:
                print(f"    ❌ Error response: {response.text[:100]}")
                
        except Exception as e:
            print(f"    ❌ Exception: {e}")

def test_specific_device_endpoints():
    """Probar endpoints específicos de dispositivos"""
    print(f"\n🧪 PRUEBAS DE ENDPOINTS DE DISPOSITIVOS ESPECÍFICOS")
    print("=" * 50)
    
    devices_to_test = ["esp32_wifi_001", "arduino_eth_001"]
    
    for device_id in devices_to_test:
        print(f"\n  📱 Testing device: {device_id}")
        
        # Probar /devices/{device_id}
        try:
            response = requests.get(f"{API_BASE_URL}/devices/{device_id}", timeout=10)
            print(f"    /devices/{device_id}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"      Device info: {data}")
        except Exception as e:
            print(f"    /devices/{device_id}: Error - {e}")
        
        # Probar /data/{device_id}
        try:
            response = requests.get(f"{API_BASE_URL}/data/{device_id}", timeout=10)
            print(f"    /data/{device_id}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "data" in data:
                    records = data["data"]
                    if isinstance(records, list):
                        print(f"      Data records: {len(records)}")
                        if records:
                            print(f"      Sample: {records[0]}")
        except Exception as e:
            print(f"    /data/{device_id}: Error - {e}")

def test_data_structure_analysis():
    """Analizar estructura detallada de los datos"""
    print(f"\n🧪 ANÁLISIS DETALLADO DE ESTRUCTURA DE DATOS")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/data", params={"limit": 5}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            print("  📋 Estructura completa de respuesta:")
            print(f"    Response type: {type(data)}")
            print(f"    Response keys: {list(data.keys()) if isinstance(data, dict) else 'No keys'}")
            
            if isinstance(data, dict) and "data" in data:
                records = data["data"]
                print(f"    Data type: {type(records)}")
                print(f"    Data length: {len(records) if isinstance(records, list) else 'Not a list'}")
                
                if isinstance(records, list) and records:
                    first_record = records[0]
                    print(f"    Record type: {type(first_record)}")
                    if isinstance(first_record, dict):
                        print(f"    Record keys: {list(first_record.keys())}")
                        print(f"    Sample record: {first_record}")
                        
                        # Analizar tipos de datos en el registro
                        print("    📊 Data types in record:")
                        for key, value in first_record.items():
                            print(f"      {key}: {type(value).__name__} = {value}")
                            
    except Exception as e:
        print(f"  ❌ Error analyzing data structure: {e}")

def main():
    """Ejecutar todas las pruebas específicas"""
    print("🔬 PRUEBAS ESPECÍFICAS DE ENDPOINTS JETSON API")
    print("=" * 60)
    print(f"🎯 Target: {API_BASE_URL}")
    print(f"🕐 Started: {datetime.now()}")
    
    test_working_endpoints()
    test_data_with_parameters()
    test_specific_device_endpoints()
    test_data_structure_analysis()
    
    print("\n" + "=" * 60)
    print("✅ PRUEBAS ESPECÍFICAS COMPLETADAS")
    print("📊 Usar esta información para crear el adaptador del agente")

if __name__ == "__main__":
    main()
