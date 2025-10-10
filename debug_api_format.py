"""
Diagnóstico directo de la API para entender el formato real
"""

import requests
import json

def debug_api_format():
    """Revisar el formato real de la API"""
    base_url = "https://dependent-discussions-venice-filling.trycloudflare.com"
    
    print("🔍 DIAGNÓSTICO DIRECTO DE LA API")
    print("=" * 50)
    
    try:
        # Test 1: Devices endpoint
        print("\n📱 TEST: /devices")
        devices_url = f"{base_url}/devices"
        response = requests.get(devices_url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Raw response: {response.text[:500]}")
        
        try:
            devices_json = response.json()
            print(f"JSON parsed: {json.dumps(devices_json, indent=2)[:500]}")
            print(f"Type: {type(devices_json)}")
            if isinstance(devices_json, list) and devices_json:
                print(f"First item type: {type(devices_json[0])}")
                print(f"First item: {devices_json[0]}")
        except Exception as e:
            print(f"Error parsing JSON: {e}")
        
        # Test 2: Data endpoint (si hay dispositivos)
        if response.status_code == 200:
            try:
                devices_json = response.json()
                if devices_json and len(devices_json) > 0:
                    first_device = devices_json[0]
                    
                    # Si es string, usar directamente
                    if isinstance(first_device, str):
                        device_id = first_device
                    elif isinstance(first_device, dict):
                        device_id = first_device.get('device_id', list(first_device.keys())[0] if first_device else None)
                    else:
                        device_id = str(first_device)
                    
                    if device_id:
                        print(f"\n📊 TEST: /data/{device_id}")
                        data_url = f"{base_url}/data/{device_id}"
                        data_response = requests.get(data_url, params={'hours': 0.17}, timeout=10)
                        print(f"Status: {data_response.status_code}")
                        print(f"Raw response: {data_response.text[:300]}")
                        
                        try:
                            data_json = data_response.json()
                            print(f"Data type: {type(data_json)}")
                            if isinstance(data_json, list) and data_json:
                                print(f"First data item: {json.dumps(data_json[0], indent=2)}")
                        except Exception as e:
                            print(f"Error parsing data JSON: {e}")
            except Exception as e:
                print(f"Error getting data: {e}")
                
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    debug_api_format()