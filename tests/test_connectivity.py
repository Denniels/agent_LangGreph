#!/usr/bin/env python3
"""
Test de conectividad con Jetson API
"""
import requests
import json

def test_jetson_connectivity():
    """Probar conectividad completa con Jetson API"""
    base_url = "https://plain-state-refers-nutritional.trycloudflare.com"
    
    print("=== VERIFICACION DE CONECTIVIDAD JETSON API ===")
    print(f"URL Base: {base_url}")
    print()
    
    # Test 1: Health check
    try:
        print("1. Probando health check...")
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Health: {data.get('status')}")
            print(f"   Devices: {data.get('devices_count')}")
        print()
    except Exception as e:
        print(f"   ERROR: {e}")
        print()
    
    # Test 2: Dispositivos
    try:
        print("2. Probando lista de dispositivos...")
        response = requests.get(f"{base_url}/devices", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            devices = data.get('devices', [])
            print(f"   Dispositivos encontrados: {len(devices)}")
            for device in devices:
                print(f"     - {device}")
        print()
    except Exception as e:
        print(f"   ERROR: {e}")
        print()
    
    # Test 3: Datos específicos del ESP32
    try:
        print("3. Probando datos del ESP32...")
        response = requests.get(f"{base_url}/data/esp32_wifi_001", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Registros: {len(data)}")
            if data:
                first_record = data[0]
                print(f"   Campos disponibles: {list(first_record.keys())}")
                print(f"   Device ID: {first_record.get('device_id')}")
                print(f"   Sensor Type: {first_record.get('sensor_type')}")
                print(f"   Value: {first_record.get('value')}")
                print(f"   Timestamp: {first_record.get('timestamp')}")
        print()
    except Exception as e:
        print(f"   ERROR: {e}")
        print()
    
    # Test 4: Endpoint genérico de datos
    try:
        print("4. Probando endpoint generico de datos...")
        response = requests.get(f"{base_url}/data", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total registros: {len(data)}")
            if data:
                # Contar por dispositivo
                devices = {}
                for record in data:
                    device = record.get('device_id', 'unknown')
                    devices[device] = devices.get(device, 0) + 1
                
                print("   Registros por dispositivo:")
                for device, count in devices.items():
                    print(f"     - {device}: {count} registros")
        print()
    except Exception as e:
        print(f"   ERROR: {e}")
        print()

if __name__ == "__main__":
    test_jetson_connectivity()