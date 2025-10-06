#!/usr/bin/env python3
"""Test de get_temperature_data corregido"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.tools.jetson_api_connector import JetsonAPIConnector

print("🌡️ PROBANDO get_temperature_data CORREGIDO...")

try:
    # Crear conector
    connector = JetsonAPIConnector()
    print(f"✅ Conector creado")
    
    # Test de temperatura con límite corregido
    print("\n📊 OBTENIENDO DATOS DE TEMPERATURA...")
    temp_data = connector.get_temperature_data(limit=200)  # Límite aumentado
    print(f"🌡️ Registros de temperatura encontrados: {len(temp_data)}")
    
    # Agrupar por dispositivo y tipo de sensor
    by_device = {}
    for record in temp_data:
        device_id = record.get('device_id')
        sensor_type = record.get('sensor_type')
        
        if device_id not in by_device:
            by_device[device_id] = {}
        if sensor_type not in by_device[device_id]:
            by_device[device_id][sensor_type] = 0
        by_device[device_id][sensor_type] += 1
    
    # Mostrar estadísticas
    for device_id, sensors in by_device.items():
        print(f"\n📱 {device_id}:")
        for sensor_type, count in sensors.items():
            print(f"   🌡️ {sensor_type}: {count} registros")
    
    # Mostrar algunos registros recientes
    print(f"\n📋 ÚLTIMOS 5 REGISTROS:")
    for i, record in enumerate(temp_data[:5]):
        device_id = record.get('device_id')
        sensor_type = record.get('sensor_type')
        value = record.get('value')
        timestamp = record.get('timestamp', '')
        print(f"   {i+1}. {device_id} - {sensor_type}: {value}°C ({timestamp})")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()