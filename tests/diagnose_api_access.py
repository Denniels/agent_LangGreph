"""
🔍 DIAGNÓSTICO EXHAUSTIVO DE ACCESO A API JETSON
==================================================

Script para diagnosticar por qué el agente solo ve 1 dispositivo mientras 
el frontend ve 2 dispositivos con todos sus datos.

Este script:
1. Prueba directamente la API de Jetson
2. Analiza las respuestas completas
3. Compara con lo que recibe el agente
4. Identifica puntos de falla en el flujo de datos
"""

import sys
import os
import requests
import json
from datetime import datetime, timezone
from typing import Dict, List, Any

# Agregar path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from modules.tools.jetson_api_connector import JetsonAPIConnector, create_jetson_connector
from modules.agents.cloud_iot_agent import CloudIoTAgent

def print_separator(title: str):
    """Imprimir separador visual"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def test_direct_api_calls():
    """Probar llamadas directas a la API sin el conector del agente"""
    print_separator("PRUEBAS DIRECTAS A LA API JETSON")
    
    base_url = "https://replica-subscriber-permission-restricted.trycloudflare.com"
    session = requests.Session()
    session.timeout = 10
    
    results = {
        'base_url': base_url,
        'tests': {},
        'timestamp': datetime.now().isoformat()
    }
    
    # Test 1: Health check
    try:
        print("📡 Probando /health...")
        response = session.get(f"{base_url}/health")
        health_data = response.json()
        results['tests']['health'] = {
            'status_code': response.status_code,
            'data': health_data,
            'success': response.status_code == 200
        }
        print(f"✅ Health: {health_data}")
    except Exception as e:
        results['tests']['health'] = {'error': str(e), 'success': False}
        print(f"❌ Health error: {e}")
    
    # Test 2: Devices endpoint
    try:
        print("📡 Probando /devices...")
        response = session.get(f"{base_url}/devices")
        devices_data = response.json()
        results['tests']['devices'] = {
            'status_code': response.status_code,
            'data': devices_data,
            'device_count': len(devices_data) if isinstance(devices_data, list) else 0,
            'success': response.status_code == 200
        }
        print(f"✅ Devices ({len(devices_data)} encontrados):")
        for i, device in enumerate(devices_data):
            print(f"   {i+1}. {device.get('device_id', 'unknown')} - {device.get('status', 'unknown')}")
    except Exception as e:
        results['tests']['devices'] = {'error': str(e), 'success': False}
        print(f"❌ Devices error: {e}")
    
    # Test 3: Data endpoint general
    try:
        print("📡 Probando /data (general)...")
        response = session.get(f"{base_url}/data", params={'limit': 50})
        data_general = response.json()
        results['tests']['data_general'] = {
            'status_code': response.status_code,
            'data_count': len(data_general) if isinstance(data_general, list) else 0,
            'success': response.status_code == 200,
            'sample': data_general[0] if data_general else None
        }
        print(f"✅ Data general ({len(data_general)} registros)")
        
        # Contar por dispositivo
        device_counts = {}
        for record in data_general:
            device_id = record.get('device_id', 'unknown')
            device_counts[device_id] = device_counts.get(device_id, 0) + 1
        
        print("📊 Registros por dispositivo:")
        for device_id, count in device_counts.items():
            print(f"   📱 {device_id}: {count} registros")
        
    except Exception as e:
        results['tests']['data_general'] = {'error': str(e), 'success': False}
        print(f"❌ Data general error: {e}")
    
    # Test 4: Data específica para cada dispositivo conocido
    known_devices = ['arduino_eth_001', 'esp32_wifi_001']
    for device_id in known_devices:
        try:
            print(f"📡 Probando /data/{device_id}...")
            response = session.get(f"{base_url}/data/{device_id}", params={'limit': 50})
            device_data = response.json()
            results['tests'][f'data_{device_id}'] = {
                'status_code': response.status_code,
                'data_count': len(device_data) if isinstance(device_data, list) else 0,
                'success': response.status_code == 200,
                'sample': device_data[0] if device_data else None
            }
            print(f"✅ Data {device_id} ({len(device_data)} registros)")
            
            # Mostrar tipos de sensor
            sensor_types = set()
            for record in device_data[:10]:  # Primeros 10
                sensor_types.add(record.get('sensor_type', 'unknown'))
            print(f"   🔧 Tipos de sensor: {', '.join(sensor_types)}")
            
        except Exception as e:
            results['tests'][f'data_{device_id}'] = {'error': str(e), 'success': False}
            print(f"❌ Data {device_id} error: {e}")
    
    return results

def test_agent_connector():
    """Probar el conector del agente paso a paso"""
    print_separator("PRUEBAS DEL CONECTOR DEL AGENTE")
    
    try:
        # Crear conector
        print("🔧 Creando JetsonAPIConnector...")
        connector = create_jetson_connector()
        print(f"✅ Conector creado: {connector.base_url}")
        
        results = {
            'connector_info': {
                'base_url': connector.base_url,
                'robust_mode': hasattr(connector, 'manager') and connector.manager is not None
            },
            'tests': {}
        }
        
        # Test 1: Conectividad robusta
        print("🚀 Probando conectividad robusta...")
        robust_test = connector.test_robust_connectivity()
        results['tests']['robust_connectivity'] = robust_test
        print(f"✅ Conectividad robusta: {robust_test['connectivity']}")
        
        # Test 2: Get devices
        print("📱 Probando get_devices()...")
        devices = connector.get_devices()
        results['tests']['get_devices'] = {
            'device_count': len(devices),
            'devices': devices,
            'success': len(devices) > 0
        }
        print(f"✅ Dispositivos encontrados: {len(devices)}")
        for device in devices:
            print(f"   📱 {device.get('device_id', 'unknown')} - {device.get('status', 'unknown')}")
        
        # Test 3: Get sensor data (general)
        print("📊 Probando get_sensor_data()...")
        sensor_data = connector.get_sensor_data(limit=50)
        results['tests']['get_sensor_data'] = {
            'data_count': len(sensor_data),
            'success': len(sensor_data) > 0,
            'sample': sensor_data[0] if sensor_data else None
        }
        print(f"✅ Datos de sensores: {len(sensor_data)} registros")
        
        # Contar por dispositivo
        device_counts = {}
        for record in sensor_data:
            device_id = record.get('device_id', 'unknown')
            device_counts[device_id] = device_counts.get(device_id, 0) + 1
        
        print("📊 Registros por dispositivo (desde connector):")
        for device_id, count in device_counts.items():
            print(f"   📱 {device_id}: {count} registros")
        
        # Test 4: Get sensor data específico para cada dispositivo
        for device_id in ['arduino_eth_001', 'esp32_wifi_001']:
            print(f"📊 Probando get_sensor_data(device_id='{device_id}')...")
            device_data = connector.get_sensor_data(device_id=device_id, limit=50)
            results['tests'][f'get_sensor_data_{device_id}'] = {
                'data_count': len(device_data),
                'success': len(device_data) > 0,
                'sample': device_data[0] if device_data else None
            }
            print(f"✅ Datos {device_id}: {len(device_data)} registros")
        
        # Test 5: Get temperature data
        print("🌡️ Probando get_temperature_data()...")
        temp_data = connector.get_temperature_data(limit=50)
        results['tests']['get_temperature_data'] = {
            'data_count': len(temp_data),
            'success': len(temp_data) > 0,
            'sample': temp_data[0] if temp_data else None
        }
        print(f"✅ Datos de temperatura: {len(temp_data)} registros")
        
        # Contar temperatura por dispositivo
        temp_device_counts = {}
        for record in temp_data:
            device_id = record.get('device_id', 'unknown')
            temp_device_counts[device_id] = temp_device_counts.get(device_id, 0) + 1
        
        print("🌡️ Registros de temperatura por dispositivo:")
        for device_id, count in temp_device_counts.items():
            print(f"   📱 {device_id}: {count} registros")
        
        # Test 6: Formatted data for LLM
        print("📝 Probando format_data_for_llm()...")
        formatted = connector.format_data_for_llm(sensor_data[:20])
        results['tests']['format_data_for_llm'] = {
            'formatted_length': len(formatted),
            'success': bool(formatted and len(formatted) > 0)
        }
        print(f"✅ Datos formateados: {len(formatted)} caracteres")
        print("🔍 Vista previa del formato:")
        print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
        
        return results
        
    except Exception as e:
        print(f"❌ Error en connector: {e}")
        return {'error': str(e)}

def test_agent_flow():
    """Probar el flujo completo del agente"""
    print_separator("PRUEBAS DEL FLUJO COMPLETO DEL AGENTE")
    
    try:
        # Crear agente
        print("🤖 Creando CloudIoTAgent...")
        agent = CloudIoTAgent()
        print("✅ Agente creado exitosamente")
        
        # Test query simple
        print("💬 Probando query: 'listame los dispositivos disponibles'...")
        
        # Simular input del usuario
        test_query = "listame los dispositivos disponibles"
        
        # Crear input para el agente
        agent_input = {
            "input": test_query,
            "chat_history": []
        }
        
        # Ejecutar el agente
        print("⚙️ Ejecutando agente...")
        result = agent.invoke(agent_input)
        
        print("✅ Respuesta del agente:")
        print("-" * 40)
        print(result.get('output', 'No output found'))
        print("-" * 40)
        
        return {
            'query': test_query,
            'response': result.get('output', ''),
            'success': bool(result.get('output'))
        }
        
    except Exception as e:
        print(f"❌ Error en agente: {e}")
        return {'error': str(e)}

def compare_results(api_results: Dict, connector_results: Dict):
    """Comparar resultados entre API directa y conector del agente"""
    print_separator("COMPARACIÓN DE RESULTADOS")
    
    # Comparar dispositivos
    api_devices = api_results['tests'].get('devices', {}).get('device_count', 0)
    connector_devices = connector_results['tests'].get('get_devices', {}).get('device_count', 0)
    
    print(f"📱 DISPOSITIVOS:")
    print(f"   API directa: {api_devices} dispositivos")
    print(f"   Conector agente: {connector_devices} dispositivos")
    
    if api_devices != connector_devices:
        print(f"   ⚠️ DIFERENCIA DETECTADA: {api_devices - connector_devices}")
    else:
        print(f"   ✅ Coinciden")
    
    # Comparar datos generales
    api_data = api_results['tests'].get('data_general', {}).get('data_count', 0)
    connector_data = connector_results['tests'].get('get_sensor_data', {}).get('data_count', 0)
    
    print(f"📊 DATOS GENERALES:")
    print(f"   API directa: {api_data} registros")
    print(f"   Conector agente: {connector_data} registros")
    
    if api_data != connector_data:
        print(f"   ⚠️ DIFERENCIA DETECTADA: {api_data - connector_data}")
    else:
        print(f"   ✅ Coinciden")
    
    # Comparar dispositivos específicos
    print(f"📋 DISPOSITIVOS ESPECÍFICOS:")
    for device_id in ['arduino_eth_001', 'esp32_wifi_001']:
        api_device_data = api_results['tests'].get(f'data_{device_id}', {}).get('data_count', 0)
        connector_device_data = connector_results['tests'].get(f'get_sensor_data_{device_id}', {}).get('data_count', 0)
        
        print(f"   {device_id}:")
        print(f"     API directa: {api_device_data} registros")
        print(f"     Conector agente: {connector_device_data} registros")
        
        if api_device_data != connector_device_data:
            print(f"     ⚠️ DIFERENCIA: {api_device_data - connector_device_data}")
        else:
            print(f"     ✅ Coinciden")

def main():
    """Función principal de diagnóstico"""
    print("🔍 DIAGNÓSTICO EXHAUSTIVO DE ACCESO A API JETSON")
    print("=" * 60)
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Objetivo: Identificar por qué agente ve 1 dispositivo vs frontend 2 dispositivos")
    
    # 1. Probar API directamente
    api_results = test_direct_api_calls()
    
    # 2. Probar conector del agente
    connector_results = test_agent_connector()
    
    # 3. Probar flujo completo del agente
    agent_results = test_agent_flow()
    
    # 4. Comparar resultados
    if 'error' not in api_results and 'error' not in connector_results:
        compare_results(api_results, connector_results)
    
    # 5. Resumen de diagnóstico
    print_separator("RESUMEN DE DIAGNÓSTICO")
    
    print("📋 RESULTADOS CLAVE:")
    
    # Dispositivos en API directa
    api_devices = api_results['tests'].get('devices', {}).get('device_count', 'ERROR')
    print(f"   🔗 API directa: {api_devices} dispositivos detectados")
    
    # Dispositivos en conector
    if 'error' not in connector_results:
        connector_devices = connector_results['tests'].get('get_devices', {}).get('device_count', 'ERROR')
        print(f"   🤖 Conector agente: {connector_devices} dispositivos detectados")
    else:
        print(f"   🤖 Conector agente: ERROR - {connector_results['error']}")
    
    # Flujo del agente
    if 'error' not in agent_results:
        print(f"   ✅ Flujo del agente: FUNCIONAL")
    else:
        print(f"   ❌ Flujo del agente: ERROR - {agent_results['error']}")
    
    # Guardar resultados completos
    full_results = {
        'timestamp': datetime.now().isoformat(),
        'api_results': api_results,
        'connector_results': connector_results,
        'agent_results': agent_results
    }
    
    with open('diagnostic_results.json', 'w', encoding='utf-8') as f:
        json.dump(full_results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Resultados completos guardados en: diagnostic_results.json")
    
    print_separator("DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    main()