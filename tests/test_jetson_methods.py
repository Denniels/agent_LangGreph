#!/usr/bin/env python3
"""
Test específico de JetsonAPIConnector
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.tools.jetson_api_connector import JetsonAPIConnector

def test_jetson_connector_methods():
    """Probar métodos específicos del conector"""
    print("=== TEST DE METODOS JETSON API CONNECTOR ===")
    print()
    
    # Crear conector
    connector = JetsonAPIConnector()
    print(f"Base URL: {connector.base_url}")
    print()
    
    # Test 1: Health Status
    try:
        print("1. Probando get_health_status()...")
        health = connector.get_health_status()
        print(f"   Health: {health}")
        print()
    except Exception as e:
        print(f"   ERROR: {e}")
        print()
    
    # Test 2: Get Devices
    try:
        print("2. Probando get_devices()...")
        devices = connector.get_devices()
        print(f"   Devices returned: {devices}")
        print(f"   Type: {type(devices)}")
        print(f"   Length: {len(devices) if isinstance(devices, list) else 'Not a list'}")
        print()
    except Exception as e:
        print(f"   ERROR: {e}")
        print()
    
    # Test 3: Get Sensor Data (sin device_id)
    try:
        print("3. Probando get_sensor_data() sin device_id...")
        data = connector.get_sensor_data(limit=5)
        print(f"   Data returned: {len(data) if isinstance(data, list) else 'Not a list'} records")
        if isinstance(data, list) and data:
            print(f"   First record: {data[0]}")
        print()
    except Exception as e:
        print(f"   ERROR: {e}")
        print()
    
    # Test 4: Get Sensor Data con device_id específico
    try:
        print("4. Probando get_sensor_data() con device_id='esp32_wifi_001'...")
        data = connector.get_sensor_data(device_id='esp32_wifi_001', limit=5)
        print(f"   Data returned: {len(data) if isinstance(data, list) else 'Not a list'} records")
        if isinstance(data, list) and data:
            print(f"   First record: {data[0]}")
        print()
    except Exception as e:
        print(f"   ERROR: {e}")
        print()
    
    # Test 5: Get Connected Devices (method used by agent)
    try:
        print("5. Probando get_connected_devices()...")
        devices = connector.get_connected_devices()
        print(f"   Connected devices: {devices}")
        print(f"   Type: {type(devices)}")
        print(f"   Length: {len(devices) if isinstance(devices, list) else 'Not a list'}")
        print()
    except Exception as e:
        print(f"   ERROR: {e}")
        print()

if __name__ == "__main__":
    test_jetson_connector_methods()