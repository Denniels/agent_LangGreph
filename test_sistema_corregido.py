#!/usr/bin/env python3
"""
Test completo del sistema corregido
- Verifica que Arduino Ethernet solo reporte temperatura (T1, T2, AVG)
- Verifica que ESP32 WiFi reporte temperatura (NTC entrada/salida) + LDR
- Valida la generación de reportes e insights
"""

import asyncio
import json
from datetime import datetime
from modules.agents.reporting import ReportGenerator
from modules.agents.cloud_iot_agent import CloudIoTAgent

def test_device_sensor_validation():
    """Prueba las funciones de validación de dispositivos y sensores"""
    print("🧪 Probando validación de dispositivos y sensores...")
    
    reporter = ReportGenerator()
    
    # Pruebas de configuración válida
    valid_combinations = [
        ("Arduino_Ethernet_192.168.0.106", "t1"),
        ("Arduino_Ethernet_192.168.0.106", "t2"),
        ("Arduino_Ethernet_192.168.0.106", "avg"),
        ("ESP32_WiFi_192.168.0.105", "ntc_entrada"),
        ("ESP32_WiFi_192.168.0.105", "ntc_salida"),
        ("ESP32_WiFi_192.168.0.105", "ldr")
    ]
    
    # Pruebas de configuración inválida (no deben existir)
    invalid_combinations = [
        ("Arduino_Ethernet_192.168.0.106", "ldr"),  # Arduino NO tiene LDR
        ("Arduino_Ethernet_192.168.0.106", "ntc_entrada"),  # Arduino usa t1/t2
        ("ESP32_WiFi_192.168.0.105", "t1"),  # ESP32 usa ntc_entrada/salida
        ("ESP32_WiFi_192.168.0.105", "avg")  # ESP32 no calcula promedio
    ]
    
    print("✅ Validando combinaciones VÁLIDAS:")
    for device, sensor in valid_combinations:
        is_valid = reporter._is_valid_device_sensor_combination(device, sensor)
        status = "✅" if is_valid else "❌"
        print(f"   {status} {device} -> {sensor}")
        if not is_valid:
            print(f"      ⚠️ ERROR: Esta combinación debería ser válida!")
    
    print("\n❌ Validando combinaciones INVÁLIDAS:")
    for device, sensor in invalid_combinations:
        is_valid = reporter._is_valid_device_sensor_combination(device, sensor)
        status = "❌" if not is_valid else "✅"
        print(f"   {status} {device} -> {sensor}")
        if is_valid:
            print(f"      ⚠️ ERROR: Esta combinación debería ser inválida!")

async def test_demo_data_generation():
    """Prueba la generación de datos demo corregida"""
    print("\n🧪 Probando generación de datos demo...")
    
    cloud_agent = CloudIoTAgent()
    demo_data = await cloud_agent._get_demo_data()
    
    print(f"📊 Datos generados: {len(demo_data)} entradas")
    
    # Verificar que Arduino solo tenga sensores de temperatura
    arduino_data = [d for d in demo_data if "Arduino_Ethernet" in d.get("device", "")]
    arduino_sensors = set(d.get("sensor", "") for d in arduino_data)
    print(f"🔌 Arduino Ethernet sensores: {arduino_sensors}")
    
    if "ldr" in arduino_sensors:
        print("   ❌ ERROR: Arduino NO debería tener sensor LDR!")
    else:
        print("   ✅ Correcto: Arduino solo tiene sensores de temperatura")
    
    # Verificar que ESP32 tenga temperatura y LDR
    esp32_data = [d for d in demo_data if "ESP32_WiFi" in d.get("device", "")]
    esp32_sensors = set(d.get("sensor", "") for d in esp32_data)
    print(f"📡 ESP32 WiFi sensores: {esp32_sensors}")
    
    if "ldr" in esp32_sensors and any("ntc" in s for s in esp32_sensors):
        print("   ✅ Correcto: ESP32 tiene temperatura + LDR")
    else:
        print("   ❌ ERROR: ESP32 debería tener sensores NTC + LDR!")

async def test_report_generation():
    """Prueba la generación completa de reportes"""
    print("\n🧪 Probando generación de reportes...")
    
    reporter = ReportGenerator()
    
    # Generar reporte usando datos demo
    try:
        report = await reporter.generate_comprehensive_report()
        
        if not report:
            print("❌ ERROR: No se pudo generar el reporte")
            return
        
        print(f"📄 Reporte generado exitosamente ({len(report)} caracteres)")
        
        # Verificar que el reporte NO mencione LDR para Arduino
        if "Arduino" in report and "LDR" in report:
            lines_with_arduino_ldr = []
            for line_num, line in enumerate(report.split('\n'), 1):
                if "Arduino" in line and ("LDR" in line or "luminosidad" in line):
                    lines_with_arduino_ldr.append(f"Línea {line_num}: {line.strip()}")
            
            if lines_with_arduino_ldr:
                print("❌ ERROR: Reporte menciona LDR para Arduino:")
                for line_info in lines_with_arduino_ldr:
                    print(f"   {line_info}")
            else:
                print("✅ Correcto: No se menciona LDR para Arduino")
        else:
            print("✅ Correcto: No hay referencias incorrectas a LDR en Arduino")
        
        # Verificar que ESP32 sí tenga menciones de LDR
        if "ESP32" in report and "LDR" in report:
            print("✅ Correcto: ESP32 incluye información de LDR")
        else:
            print("⚠️ Advertencia: ESP32 podría no estar reportando LDR")
        
        # Mostrar un fragmento del reporte
        print("\n📄 Fragmento del reporte generado:")
        lines = report.split('\n')
        for i, line in enumerate(lines[:15]):
            print(f"   {line}")
        if len(lines) > 15:
            print(f"   ... (y {len(lines)-15} líneas más)")
    
    except Exception as e:
        print(f"❌ ERROR al generar reporte: {e}")

def main():
    """Ejecuta todas las pruebas del sistema corregido"""
    print("🚀 Iniciando pruebas del sistema corregido")
    print("="*60)
    
    # Pruebas síncronas
    test_device_sensor_validation()
    
    # Pruebas asíncronas
    asyncio.run(test_demo_data_generation())
    asyncio.run(test_report_generation())
    
    print("\n" + "="*60)
    print("✅ Pruebas completadas")
    print("\n📋 Configuración correcta del sistema:")
    print("   🔌 Arduino Ethernet (192.168.0.106): t1, t2, avg")
    print("   📡 ESP32 WiFi (192.168.0.105): ntc_entrada, ntc_salida, ldr")

if __name__ == "__main__":
    main()