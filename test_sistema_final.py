#!/usr/bin/env python3
"""
Test final del sistema corregido - Validación configuración real dispositivos
"""

from modules.agents.reporting import ReportGenerator
from modules.agents.cloud_iot_agent import CloudIoTAgent
import json

def test_configuracion_corregida():
    print('=' * 60)
    print('🔧 PRUEBA SISTEMA CORREGIDO - CONFIGURACIÓN REAL')
    print('=' * 60)
    
    try:
        print('\n1️⃣ Inicializando ReportGenerator...')
        rg = ReportGenerator()
        print('   ✅ ReportGenerator inicializado correctamente')
        
        print('\n2️⃣ Inicializando CloudIoTAgent...')
        agent = CloudIoTAgent()
        print('   ✅ CloudIoTAgent inicializado correctamente')
        
        print('\n3️⃣ Obteniendo datos demo corregidos...')
        demo_data = agent._get_demo_data()
        print('   ✅ Datos demo generados')
        
        print('\n📊 VALIDACIÓN CONFIGURACIÓN POR DISPOSITIVO:')
        print('-' * 50)
        
        for device, data in demo_data.items():
            print(f'\n🔸 DISPOSITIVO: {device}')
            sensors = list(data.keys())
            print(f'   📋 Sensores detectados: {sensors}')
            
            # Validación Arduino Ethernet
            if 'arduino_ethernet' in device.lower():
                has_ldr = any('ldr' in sensor.lower() for sensor in sensors)
                temp_sensors = [s for s in sensors if 'temp' in s.lower()]
                
                print(f'   🌡️  Sensores temperatura: {len(temp_sensors)}')
                print(f'   💡 Sensor LDR presente: {has_ldr}')
                
                if has_ldr:
                    print('   ❌ ERROR: Arduino Ethernet NO debe tener LDR')
                    return False
                else:
                    print('   ✅ CORRECTO: Arduino Ethernet sin LDR')
                
                if len(temp_sensors) >= 2:
                    print('   ✅ CORRECTO: Sensores temperatura presentes')
                else:
                    print('   ❌ ERROR: Faltan sensores de temperatura')
                    return False
            
            # Validación ESP32 WiFi
            elif 'esp32' in device.lower():
                has_ldr = any('ldr' in sensor.lower() for sensor in sensors)
                temp_sensors = [s for s in sensors if 'temp' in s.lower() or 'ntc' in s.lower()]
                
                print(f'   🌡️  Sensores temperatura: {len(temp_sensors)}')
                print(f'   💡 Sensor LDR presente: {has_ldr}')
                
                if not has_ldr:
                    print('   ❌ ERROR: ESP32 WiFi DEBE tener LDR')
                    return False
                else:
                    print('   ✅ CORRECTO: ESP32 WiFi con LDR')
                
                if len(temp_sensors) >= 2:
                    print('   ✅ CORRECTO: Sensores temperatura presentes')
                else:
                    print('   ❌ ERROR: Faltan sensores de temperatura')
                    return False
        
        print('\n4️⃣ Probando validación de dispositivos...')
        
        # Test validación
        arduino_valid = rg._is_valid_device_sensor_combination('arduino_ethernet', 'temp1')
        arduino_invalid = rg._is_valid_device_sensor_combination('arduino_ethernet', 'ldr')
        esp32_temp_valid = rg._is_valid_device_sensor_combination('esp32_wifi', 'ntc_entrada')
        esp32_ldr_valid = rg._is_valid_device_sensor_combination('esp32_wifi', 'ldr')
        
        print(f'   Arduino + temp1: {arduino_valid} ✅' if arduino_valid else f'   Arduino + temp1: {arduino_valid} ❌')
        print(f'   Arduino + LDR: {arduino_invalid} ❌' if not arduino_invalid else f'   Arduino + LDR: {arduino_invalid} ❌ ERROR')
        print(f'   ESP32 + temp: {esp32_temp_valid} ✅' if esp32_temp_valid else f'   ESP32 + temp: {esp32_temp_valid} ❌')
        print(f'   ESP32 + LDR: {esp32_ldr_valid} ✅' if esp32_ldr_valid else f'   ESP32 + LDR: {esp32_ldr_valid} ❌')
        
        validation_ok = arduino_valid and not arduino_invalid and esp32_temp_valid and esp32_ldr_valid
        
        print('\n' + '=' * 60)
        if validation_ok:
            print('🎉 TODAS LAS VALIDACIONES PASARON')
            print('✅ Sistema corregido funcionando correctamente')
            print('📊 Configuración real de dispositivos implementada')
            print('🔧 Arduino Ethernet: Solo temperatura')
            print('📡 ESP32 WiFi: Temperatura + LDR')
        else:
            print('❌ FALLÓ ALGUNA VALIDACIÓN')
            print('🔧 Revisar configuración del sistema')
        
        print('=' * 60)
        return validation_ok
        
    except Exception as e:
        print(f'\n❌ ERROR en la prueba: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_configuracion_corregida()
    exit(0 if success else 1)