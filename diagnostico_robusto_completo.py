#!/usr/bin/env python3
"""
DIAGNÓSTICO EXHAUSTIVO Y ROBUSTO DEL SISTEMA IOT
==============================================

Análisis completo para identificar la causa raíz de la desconexión 
entre el chat (que no ve datos) y el dashboard (que sí ve datos).
"""

import sys
import os
import asyncio
import logging
import traceback
from datetime import datetime

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_1_environment_and_imports():
    """TEST 1: Verificar entorno y imports"""
    print("🔍 TEST 1: VERIFICACIÓN DE ENTORNO")
    print("=" * 50)
    
    try:
        # Variables de entorno críticas
        groq_key = os.getenv('GROQ_API_KEY')
        jetson_url = os.getenv('JETSON_API_URL')
        
        print(f"✅ GROQ_API_KEY presente: {bool(groq_key)}")
        if groq_key:
            print(f"   Longitud: {len(groq_key)} chars")
            print(f"   Primeros 10: {groq_key[:10]}...")
        
        print(f"✅ JETSON_API_URL: {jetson_url}")
        
        # Imports críticos
        from modules.tools.direct_jetson_connector import DirectJetsonConnector
        from modules.agents.cloud_iot_agent import CloudIoTAgent
        from modules.utils.intelligent_prompt_generator import create_intelligent_prompt
        
        print("✅ Imports críticos: OK")
        return True
        
    except Exception as e:
        print(f"❌ Error en TEST 1: {e}")
        traceback.print_exc()
        return False

def test_2_direct_connector_raw():
    """TEST 2: Probar DirectJetsonConnector directamente"""
    print("\n🔍 TEST 2: DIRECTJETSONCONNECTOR PURO")
    print("=" * 50)
    
    try:
        from modules.tools.direct_jetson_connector import DirectJetsonConnector
        
        # URL que sabemos que funciona (del dashboard)
        base_url = "https://roof-imposed-noticed-fire.trycloudflare.com"
        connector = DirectJetsonConnector(base_url)
        
        # Test de conexión
        print("🌐 Probando conexión...")
        health = connector.test_connection()
        print(f"   Status: {health.get('status')}")
        
        # Test de dispositivos
        print("📱 Probando get_devices...")
        devices = connector.get_devices_direct()
        print(f"   Dispositivos encontrados: {len(devices)}")
        for device in devices:
            print(f"   - {device}")
        
        # Test de datos
        print("📊 Probando get_sensor_data_direct...")
        data = connector.get_sensor_data_direct(limit=50)
        print(f"   Registros encontrados: {len(data)}")
        if data:
            print(f"   Primer registro: {data[0]}")
            print(f"   Último registro: {data[-1]}")
        
        # Test de método de compatibilidad
        print("🔄 Probando get_sensor_data (método de compatibilidad)...")
        compat_data = connector.get_sensor_data(limit=50)
        print(f"   Registros con método compatible: {len(compat_data)}")
        
        return len(data) > 0
        
    except Exception as e:
        print(f"❌ Error en TEST 2: {e}")
        traceback.print_exc()
        return False

async def test_3_cloud_iot_agent_step_by_step():
    """TEST 3: Probar CloudIoTAgent paso a paso"""
    print("\n🔍 TEST 3: CLOUDIOTAGENT PASO A PASO")
    print("=" * 50)
    
    try:
        from modules.agents.cloud_iot_agent import CloudIoTAgent
        
        # Inicializar agente
        print("🤖 Inicializando CloudIoTAgent...")
        agent = CloudIoTAgent()
        
        # Inicializar sistemas
        print("⚙️ Inicializando sistemas...")
        init_result = await agent.initialize()
        print(f"   Inicialización: {init_result}")
        
        # Verificar conectores
        print("🔗 Verificando conectores...")
        print(f"   jetson_connector tipo: {type(agent.jetson_connector)}")
        print(f"   direct_connector tipo: {type(agent.direct_connector)}")
        print(f"   Son el mismo objeto: {agent.jetson_connector is agent.direct_connector}")
        
        # Test de datos con el conector del agente
        print("📊 Probando obtención de datos del agente...")
        
        if hasattr(agent.jetson_connector, 'get_sensor_data'):
            data = agent.jetson_connector.get_sensor_data(limit=50)
            print(f"   Datos del jetson_connector: {len(data)} registros")
        else:
            print("   ❌ jetson_connector no tiene get_sensor_data")
        
        if hasattr(agent.direct_connector, 'get_sensor_data_direct'):
            direct_data = agent.direct_connector.get_sensor_data_direct(limit=50)
            print(f"   Datos del direct_connector: {len(direct_data)} registros")
        else:
            print("   ❌ direct_connector no tiene get_sensor_data_direct")
        
        # Test de consulta real
        print("💬 Probando consulta simple...")
        response = await agent.process_query("¿Cuántos dispositivos están conectados?")
        
        print(f"   Success: {response.get('success')}")
        print(f"   Response length: {len(response.get('response', ''))}")
        print(f"   Response preview: {response.get('response', '')[:200]}...")
        
        return response.get('success', False)
        
    except Exception as e:
        print(f"❌ Error en TEST 3: {e}")
        traceback.print_exc()
        return False

def test_4_data_flow_analysis():
    """TEST 4: Análisis del flujo de datos"""
    print("\n🔍 TEST 4: ANÁLISIS DEL FLUJO DE DATOS")
    print("=" * 50)
    
    try:
        from modules.tools.direct_jetson_connector import DirectJetsonConnector
        
        base_url = "https://roof-imposed-noticed-fire.trycloudflare.com"
        connector = DirectJetsonConnector(base_url)
        
        # Obtener datos paso a paso
        print("📊 Obteniendo datos completos...")
        all_data = connector.get_all_data_simple()
        
        print(f"   Estructura de respuesta: {type(all_data)}")
        print(f"   Keys disponibles: {list(all_data.keys()) if isinstance(all_data, dict) else 'No es dict'}")
        
        devices = all_data.get('devices', [])
        sensor_data = all_data.get('sensor_data', [])
        
        print(f"   Dispositivos: {len(devices)}")
        print(f"   Datos de sensores: {len(sensor_data)}")
        
        if devices:
            print("   Dispositivos encontrados:")
            for device in devices:
                print(f"     - {device}")
        
        if sensor_data:
            print("   Muestra de datos de sensores:")
            for i, record in enumerate(sensor_data[:3]):
                print(f"     [{i}] {record}")
        
        # Verificar formato de datos
        print("\n🔍 Análisis de formato de datos:")
        if sensor_data:
            first_record = sensor_data[0]
            print(f"   Tipo de registro: {type(first_record)}")
            print(f"   Keys del registro: {list(first_record.keys()) if isinstance(first_record, dict) else 'No es dict'}")
            
            # Verificar campos críticos
            has_device_id = 'device_id' in first_record
            has_timestamp = 'timestamp' in first_record
            sensor_fields = [k for k in first_record.keys() if k not in ['device_id', 'timestamp', 'id']]
            
            print(f"   Tiene device_id: {has_device_id}")
            print(f"   Tiene timestamp: {has_timestamp}")
            print(f"   Campos de sensores: {sensor_fields}")
        
        return len(sensor_data) > 0
        
    except Exception as e:
        print(f"❌ Error en TEST 4: {e}")
        traceback.print_exc()
        return False

def test_5_streamlit_vs_direct():
    """TEST 5: Comparar lo que ve Streamlit vs ejecución directa"""
    print("\n🔍 TEST 5: STREAMLIT VS EJECUCIÓN DIRECTA")
    print("=" * 50)
    
    try:
        # Simular entorno Streamlit
        print("🎭 Simulando entorno Streamlit...")
        
        # Mock de streamlit
        class MockStreamlit:
            class secrets:
                @staticmethod
                def get(key, default=None):
                    # Simular secrets de Streamlit
                    if key == 'GROQ_API_KEY':
                        return os.getenv('GROQ_API_KEY', default)
                    return default
        
        import sys
        sys.modules['streamlit'] = MockStreamlit()
        
        # Intentar import como si fuera Streamlit
        from modules.agents.cloud_iot_agent import CloudIoTAgent
        
        print("✅ Import simulando Streamlit: OK")
        
        # Verificar variables de entorno en contexto Streamlit
        try:
            import streamlit as st
            groq_from_secrets = st.secrets.get('GROQ_API_KEY', None)
            groq_from_env = os.getenv('GROQ_API_KEY')
            
            print(f"   GROQ desde secrets: {bool(groq_from_secrets)}")
            print(f"   GROQ desde env: {bool(groq_from_env)}")
            print(f"   Son iguales: {groq_from_secrets == groq_from_env}")
            
        except Exception as e:
            print(f"   Error accediendo a secrets: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en TEST 5: {e}")
        traceback.print_exc()
        return False

async def test_6_complete_workflow():
    """TEST 6: Workflow completo de una consulta"""
    print("\n🔍 TEST 6: WORKFLOW COMPLETO")
    print("=" * 50)
    
    try:
        from modules.agents.cloud_iot_agent import CloudIoTAgent
        
        # Inicializar con logging detallado
        agent = CloudIoTAgent()
        await agent.initialize()
        
        # Consulta específica que sabemos que debería funcionar
        query = "¿Cuántos dispositivos están activos?"
        print(f"💬 Procesando consulta: '{query}'")
        
        # Procesar con debug
        response = await agent.process_query(query)
        
        print(f"\n📋 RESULTADO COMPLETO:")
        print(f"   Success: {response.get('success')}")
        print(f"   Model used: {response.get('model_used')}")
        print(f"   Processing time: {response.get('processing_time', 0):.2f}s")
        print(f"   Data points: {response.get('data_points', 0)}")
        print(f"   Charts generated: {len(response.get('charts', []))}")
        
        print(f"\n📝 RESPUESTA:")
        print(response.get('response', 'Sin respuesta'))
        
        # Análisis de la respuesta
        response_text = response.get('response', '').lower()
        contains_no_data = any(phrase in response_text for phrase in [
            'no hay', 'no se encontraron', 'no disponible', 'sin datos'
        ])
        
        contains_data_info = any(phrase in response_text for phrase in [
            'dispositivos', 'registros', 'sensores', 'activos'
        ])
        
        print(f"\n🔍 ANÁLISIS DE RESPUESTA:")
        print(f"   Contiene frases de 'sin datos': {contains_no_data}")
        print(f"   Contiene información de datos: {contains_data_info}")
        
        return response.get('success', False) and not contains_no_data
        
    except Exception as e:
        print(f"❌ Error en TEST 6: {e}")
        traceback.print_exc()
        return False

async def main():
    """Ejecutar todos los tests de diagnóstico"""
    print("🚀 DIAGNÓSTICO EXHAUSTIVO DEL SISTEMA IOT")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print("=" * 60)
    
    tests = [
        ("Entorno e Imports", test_1_environment_and_imports),
        ("DirectJetsonConnector", test_2_direct_connector_raw),
        ("CloudIoTAgent", test_3_cloud_iot_agent_step_by_step),
        ("Flujo de Datos", test_4_data_flow_analysis),
        ("Streamlit vs Directo", test_5_streamlit_vs_direct),
        ("Workflow Completo", test_6_complete_workflow),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ FALLO CRÍTICO EN {test_name}: {e}")
            results[test_name] = False
    
    # Resumen final
    print(f"\n{'='*60}")
    print("📊 RESUMEN DE DIAGNÓSTICO")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 TODOS LOS TESTS PASARON - El problema puede estar en Streamlit Cloud")
    else:
        print("🔥 HAY PROBLEMAS CRÍTICOS - Requiere corrección inmediata")
        
        # Análisis de fallos
        failed_tests = [name for name, result in results.items() if not result]
        print(f"\n🔍 TESTS FALLIDOS: {', '.join(failed_tests)}")

if __name__ == "__main__":
    asyncio.run(main())