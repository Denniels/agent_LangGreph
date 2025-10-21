#!/usr/bin/env python3
"""
Verificación de sensores reales en la API Jetson
Detectar dónde se están generando datos falsos de humedad y presión
"""

import requests
import json
from collections import defaultdict, Counter

def verify_real_sensors():
    """Verificar qué sensores existen realmente en la API"""
    
    print("🔍 VERIFICANDO SENSORES REALES EN API JETSON")
    print("=" * 60)
    
    try:
        # Obtener datos directos de la API
        url = "https://wonder-sufficiently-generator-click.trycloudflare.com/data?hours=1"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error HTTP: {response.status_code}")
            return
            
        data = response.json()
        print(f"✅ Datos obtenidos: {len(data)} registros")
        
        # Analizar datos reales
        devices = set()
        sensor_types = set()
        device_sensors = defaultdict(set)
        sensor_values = defaultdict(list)
        
        print("\n📊 ANÁLISIS DE REGISTROS DISPONIBLES:")
        print("-" * 60)
        
        # Verificar si data es lista o dict
        if isinstance(data, dict):
            print(f"⚠️  Datos en formato dict: {list(data.keys())}")
            if 'data' in data:
                data = data['data']
            else:
                print(f"❌ Estructura inesperada de datos")
                return
        
        print(f"📊 Analizando {len(data)} registros...")
        
        for i, record in enumerate(data):
            if i >= 20:  # Limitar a 20 registros
                break
                
            device_id = record.get('device_id', 'unknown')
            sensor_type = record.get('sensor_type', 'unknown')
            value = record.get('value', 0)
            timestamp = record.get('timestamp', 'unknown')
            
            devices.add(device_id)
            sensor_types.add(sensor_type)
            device_sensors[device_id].add(sensor_type)
            sensor_values[sensor_type].append(value)
            
            print(f"{i+1:2d}. {device_id:15} | {sensor_type:12} | {value:8} | {timestamp}")
        
        print("\n" + "=" * 60)
        print("📋 RESUMEN DE SENSORES REALES:")
        print("=" * 60)
        
        print(f"🔧 Dispositivos encontrados: {len(devices)}")
        for device in sorted(devices):
            print(f"   • {device}")
            
        print(f"\n🌡️ Tipos de sensores encontrados: {len(sensor_types)}")
        for sensor in sorted(sensor_types):
            values = sensor_values[sensor]
            if values:
                print(f"   • {sensor:12} | Min: {min(values):8.2f} | Max: {max(values):8.2f} | Count: {len(values)}")
        
        print(f"\n🔗 Sensores por dispositivo:")
        for device, sensors in sorted(device_sensors.items()):
            print(f"   • {device:15} -> {', '.join(sorted(sensors))}")
        
        # Detectar sensores sospechosos
        print(f"\n🚨 ANÁLISIS DE SENSORES SOSPECHOSOS:")
        print("-" * 60)
        
        suspicious_sensors = []
        if 'humidity' in sensor_types:
            suspicious_sensors.append('humidity')
            print("❌ DETECTADO: Sensor de HUMEDAD (no existe físicamente)")
        
        if 'pressure' in sensor_types:
            suspicious_sensors.append('pressure')
            print("❌ DETECTADO: Sensor de PRESIÓN (no existe físicamente)")
            
        if 'co2' in sensor_types:
            suspicious_sensors.append('co2')
            print("❌ DETECTADO: Sensor de CO2 (no existe físicamente)")
            
        if 'voltage' in sensor_types:
            print("⚠️  DETECTADO: Sensor de VOLTAJE (revisar si es real)")
        
        expected_sensors = {'temperature', 'light', 'ldr'}
        real_sensors = sensor_types.intersection(expected_sensors)
        fake_sensors = sensor_types - expected_sensors
        
        print(f"\n✅ Sensores REALES esperados: {sorted(real_sensors)}")
        print(f"❌ Sensores FALSOS detectados: {sorted(fake_sensors)}")
        
        if suspicious_sensors:
            print(f"\n🎯 CONCLUSIÓN:")
            print(f"   Los sensores {suspicious_sensors} están siendo generados artificialmente")
            print(f"   NO existen en el hardware real (solo temperatura + LDR)")
            
        return {
            'real_sensors': real_sensors,
            'fake_sensors': fake_sensors,
            'devices': devices,
            'total_records': len(data)
        }
        
    except Exception as e:
        print(f"❌ Error verificando sensores: {e}")
        return None

if __name__ == "__main__":
    result = verify_real_sensors()
    
    if result and result['fake_sensors']:
        print(f"\n🔧 ACCIÓN REQUERIDA:")
        print(f"   Eliminar generación artificial de: {sorted(result['fake_sensors'])}")
        print(f"   Mantener solo sensores reales: {sorted(result['real_sensors'])}")