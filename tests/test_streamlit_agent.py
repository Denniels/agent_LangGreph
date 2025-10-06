"""
🔍 TEST ESPECÍFICO DEL AGENTE EN STREAMLIT
=========================================

Test específico para probar el agente de Streamlit y ver exactamente
qué dispositivos y datos está viendo.
"""

import sys
import os
import asyncio
from datetime import datetime

# Agregar path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from modules.agents.cloud_iot_agent import CloudIoTAgent, create_cloud_iot_agent

def print_separator(title: str):
    """Imprimir separador visual"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

async def test_streamlit_agent():
    """Probar el agente específico de Streamlit"""
    print_separator("TEST DEL AGENTE DE STREAMLIT")
    
    try:
        # 1. Crear agente
        print("🤖 Creando CloudIoTAgent...")
        agent = create_cloud_iot_agent()
        print("✅ Agente creado")
        
        # 2. Health check
        print("\n🏥 Verificando salud del agente...")
        health = await agent.health_check()
        print(f"✅ Status general: {health.get('overall_status', 'unknown')}")
        print(f"   📊 Agente: {health.get('agent_status', 'unknown')}")
        print(f"   🤖 Groq: {health.get('groq_status', 'unknown')}")
        print(f"   📡 Jetson: {health.get('jetson_status', 'unknown')}")
        
        # Mostrar info de uso de API si está disponible
        if 'api_usage' in health:
            usage = health['api_usage']
            print(f"   💳 Uso API: {usage.get('requests_used', 0)}/{usage.get('requests_limit', 0)} consultas")
        
        # 3. Probar consulta simple de dispositivos
        print("\n📱 Consultando dispositivos disponibles...")
        response1 = await agent.process_query("listame los dispositivos disponibles")
        
        print(f"✅ Consulta 1 exitosa: {response1.get('success', False)}")
        print(f"📊 Datos procesados: {response1.get('data_summary', {})}")
        
        print(f"\n🔍 Respuesta del agente:")
        print("-" * 40)
        print(response1.get('response', 'Sin respuesta'))
        print("-" * 40)
        
        # 4. Probar consulta específica de últimos registros
        print("\n📋 Consultando últimos 10 registros...")
        response2 = await agent.process_query("listame los últimos 10 registros de cada dispositivo")
        
        print(f"✅ Consulta 2 exitosa: {response2.get('success', False)}")
        print(f"📊 Datos procesados: {response2.get('data_summary', {})}")
        
        print(f"\n🔍 Respuesta del agente:")
        print("-" * 40)
        print(response2.get('response', 'Sin respuesta'))
        print("-" * 40)
        
        # 5. Probar acceso directo al conector del agente
        print("\n🔧 Probando conector interno del agente...")
        if hasattr(agent, 'jetson_connector') and agent.jetson_connector:
            connector = agent.jetson_connector
            
            # Test dispositivos
            devices = connector.get_devices()
            print(f"✅ Dispositivos desde conector interno: {len(devices)}")
            for device in devices:
                print(f"   📱 {device.get('device_id', 'unknown')} - {device.get('status', 'unknown')}")
            
            # Test datos generales
            sensor_data = connector.get_sensor_data(limit=20)
            print(f"✅ Datos desde conector interno: {len(sensor_data)} registros")
            
            # Contar por dispositivo
            device_counts = {}
            for record in sensor_data:
                device_id = record.get('device_id', 'unknown')
                device_counts[device_id] = device_counts.get(device_id, 0) + 1
            
            print("📊 Registros por dispositivo (conector interno):")
            for device_id, count in device_counts.items():
                print(f"   📱 {device_id}: {count} registros")
        else:
            print("❌ Conector interno no disponible")
        
        # 6. Resumen de hallazgos
        print_separator("RESUMEN DE HALLAZGOS DEL AGENTE")
        
        print("📋 DISPOSITIVOS DETECTADOS:")
        for response in [response1, response2]:
            if response.get('success'):
                devices_found = response.get('data_summary', {}).get('devices', [])
                sensors_found = response.get('data_summary', {}).get('sensors', [])
                total_records = response.get('data_summary', {}).get('total_records', 0)
                
                print(f"   🔍 Consulta: {devices_found} dispositivos")
                print(f"   🔧 Sensores: {sensors_found}")
                print(f"   📊 Registros: {total_records}")
                break
        
        return {
            'health': health,
            'responses': [response1, response2],
            'connector_test': {
                'devices': len(devices) if 'devices' in locals() else 0,
                'data_records': len(sensor_data) if 'sensor_data' in locals() else 0
            }
        }
        
    except Exception as e:
        print(f"❌ Error en test del agente: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

async def main():
    """Función principal"""
    print("🔍 TEST ESPECÍFICO DEL AGENTE DE STREAMLIT")
    print("=" * 60)
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Objetivo: Verificar qué ve exactamente el agente de Streamlit")
    
    # Ejecutar test
    results = await test_streamlit_agent()
    
    # Guardar resultados
    import json
    with open('streamlit_agent_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Resultados guardados en: streamlit_agent_test_results.json")
    
    print_separator("TEST COMPLETADO")

if __name__ == "__main__":
    asyncio.run(main())