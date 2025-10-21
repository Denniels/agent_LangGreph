#!/usr/bin/env python3
"""
Script para eliminar referencias a sensores artificiales que no existen en el hardware real.

HARDWARE REAL CONFIRMADO:
- ESP32: ldr, ntc_entrada, ntc_salida  
- Arduino Ethernet: temperature_1, temperature_2, temperature_avg

SENSORES ARTIFICIALES A ELIMINAR: humidity, pressure, co2, voltage, motion
"""
import os
import re

def fix_test_files():
    """Corrige archivos de test eliminando sensores artificiales"""
    
    # Patrones a corregir
    replacements = [
        # Reemplazar listas de sensores con sensores falsos
        (r"'sensors': \['temperature', 'humidity', 'ldr'\]", "'sensors': ['temperature', 'ldr']"),
        (r'"sensors": \["temperature", "humidity", "ldr"\]', '"sensors": ["temperature", "ldr"]'),
        
        # Reemplazar mappings con sensores falsos
        (r"'humidity': 'Humedad ESP32'[,}]", ""),
        (r'"humidity": "Humedad ESP32"[,}]', ""),
        
        # Eliminar definiciones de datos de sensores falsos
        (r'{\s*"device_id": "[^"]*",\s*"sensor_type": "humidity"[^}]*},?\s*', ''),
        (r'{\s*"device_id": "[^"]*",\s*"sensor_type": "pressure"[^}]*},?\s*', ''),
        (r'{\s*"device_id": "[^"]*",\s*"sensor_type": "voltage"[^}]*},?\s*', ''),
        
        # Eliminar alerts de sensores falsos
        (r'{\s*"alert_type": "high_humidity"[^}]*},?\s*', ''),
        (r'"message": "Humidity levels too high[^"]*"[,}]', ''),
    ]
    
    test_files = [
        'tests/conftest.py',
        'tests/test_simple_report.py', 
        'tests/test_reporting_quick.py',
        'tests/test_multi_device_report.py',
        'modules/app_simple_reports.py'
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"🔧 Corrigiendo {file_path}...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Aplicar todas las correcciones
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
            
            # Limpiar líneas vacías múltiples 
            content = re.sub(r'\n\n\n+', '\n\n', content)
            
            # Limpiar comas colgantes en listas/diccionarios
            content = re.sub(r',(\s*[}\]])', r'\1', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ {file_path} corregido")
            else:
                print(f"  ℹ️  {file_path} sin cambios necesarios")
        else:
            print(f"  ⚠️  {file_path} no encontrado")

def verify_real_sensors_only():
    """Verifica que solo se referencien sensores reales"""
    
    real_sensors = ['temperature', 'ldr', 'ntc_entrada', 'ntc_salida', 'temperature_1', 'temperature_2', 'temperature_avg']
    fake_sensors = ['humidity', 'pressure', 'co2', 'voltage', 'motion']
    
    files_to_check = [
        'modules/agents/cloud_iot_agent.py',
        'modules/agents/data_verification_node.py', 
        'modules/agents/remote_langgraph_nodes.py',
        'modules/agents/groq_integration.py',
        'modules/tools/analysis_tools.py'
    ]
    
    print("\n🔍 Verificando que solo se referencien sensores reales...")
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            found_fakes = []
            for fake in fake_sensors:
                if fake in content:
                    found_fakes.append(fake)
            
            if found_fakes:
                print(f"  ⚠️  {file_path}: Referencias a sensores falsos encontradas: {found_fakes}")
            else:
                print(f"  ✅ {file_path}: Solo sensores reales")

if __name__ == "__main__":
    print("🚀 Iniciando corrección de sensores artificiales...")
    print("HARDWARE REAL: Solo temperatura (NTC/thermistores) + LDR (luminosidad)")
    print("ELIMINANDO: humidity, pressure, co2, voltage, motion\n")
    
    fix_test_files()
    verify_real_sensors_only()
    
    print("\n✨ Corrección completada!")
    print("💡 El sistema ahora refleja únicamente el hardware real existente.")