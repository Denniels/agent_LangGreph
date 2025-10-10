#!/usr/bin/env python3
"""Test detallado de health check"""

import requests

url = "https://respect-craps-lit-aged.trycloudflare.com"

print(f"🔍 DIAGNOSTICO DETALLADO: {url}")

try:
    # Test 1: Health
    print("\n1️⃣ PROBANDO /health")
    response = requests.get(f"{url}/health", timeout=(10, 30))
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Data: {data}")
        print(f"   Status value: {data.get('status')}")
        print(f"   Is healthy: {data.get('status') == 'healthy'}")
    
    # Test 2: Devices
    print("\n2️⃣ PROBANDO /devices")
    response = requests.get(f"{url}/devices", timeout=(10, 30))
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        devices = response.json()
        print(f"   Type: {type(devices)}")
        if isinstance(devices, list):
            print(f"   Count: {len(devices)}")
            for i, device in enumerate(devices[:3]):  # Mostrar primeros 3
                print(f"   Device {i}: {device}")
        else:
            print(f"   Data: {devices}")
    
    # Test 3: Data 
    print("\n3️⃣ PROBANDO /data")
    response = requests.get(f"{url}/data", params={'limit': 1}, timeout=(10, 30))
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        sensor_data = response.json()
        print(f"   Type: {type(sensor_data)}")
        if isinstance(sensor_data, list):
            print(f"   Count: {len(sensor_data)}")
            if sensor_data:
                print(f"   Sample: {sensor_data[0]}")
        else:
            print(f"   Data: {sensor_data}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()