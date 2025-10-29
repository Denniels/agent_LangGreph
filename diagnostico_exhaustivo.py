#!/usr/bin/env python3
"""
DIAGNÓSTICO EXHAUSTIVO DEL CHAT IoT
===================================
Rastrear exactamente dónde se pierden los datos en la cadena de procesamiento
"""

import asyncio
import logging
import json
from datetime import datetime

# Configurar logging detallado
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def diagnostico_exhaustivo():
    print("=" * 80)
    print("🔍 DIAGNÓSTICO EXHAUSTIVO DEL CHAT IoT")
    print("=" * 80)
    
    try:
        # PASO 1: Verificar imports y inicialización
        print("\n📦 PASO 1: Verificando imports...")
        
        from modules.agents.cloud_iot_agent import CloudIoTAgent
        from modules.tools.direct_jetson_connector import DirectJetsonConnector
        print("✅ Imports exitosos")
        
        # PASO 2: Verificar obtención de datos directa
        print("\n📡 PASO 2: Verificando obtención directa de datos...")
        
        connector = DirectJetsonConnector('https://along-critical-decorative-physics.trycloudflare.com')
        data_result = connector.get_all_data_simple()
        
        if data_result.get('status') == 'success':
            raw_data = data_result.get('sensor_data', [])
            print(f"✅ Datos obtenidos directamente: {len(raw_data)} registros")
            
            # Analizar tipos de datos
            if raw_data:
                sample_record = raw_data[0]
                print(f"📋 Estructura de datos: {list(sample_record.keys())}")
                print(f"📊 Dispositivos únicos: {len(set(r.get('device_id', 'unknown') for r in raw_data))}")
                print(f"🔧 Sensores únicos: {len(set(r.get('sensor_type', 'unknown') for r in raw_data))}")
            else:
                print("❌ PROBLEMA: raw_data está vacío")
                return
        else:
            print(f"❌ PROBLEMA: Error obteniendo datos: {data_result}")
            return
        
        # PASO 3: Verificar procesamiento en el agente
        print("\n🤖 PASO 3: Verificando procesamiento en CloudIoTAgent...")
        
        agent = CloudIoTAgent()
        await agent.initialize()
        
        # Crear estado inicial simulado para diagnóstico
        from modules.agents.langgraph_state import create_initial_state
        test_query = "dame una estadística de los datos de los sensores de ambos dispositivos de las últimas 24 horas"
        initial_state = create_initial_state(test_query)
        
        # PASO 4: Ejecutar nodo de recolección de datos
        print("\n📊 PASO 4: Ejecutando _remote_data_collector_node...")
        
        collector_result = await agent._remote_data_collector_node(initial_state)
        collected_data = collector_result.get("raw_data", [])
        
        print(f"📈 Datos recolectados por el agente: {len(collected_data)} registros")
        
        if not collected_data:
            print("❌ PROBLEMA CRÍTICO: El agente no obtuvo datos")
            print(f"📋 Estado del collector: {collector_result.get('execution_status', 'unknown')}")
            print(f"🔧 Método usado: {collector_result.get('data_collection_method', 'unknown')}")
            return
        
        # PASO 5: Ejecutar nodo de análisis de datos
        print("\n🧠 PASO 5: Ejecutando _data_analyzer_node...")
        
        analyzer_result = await agent._data_analyzer_node(collector_result)
        formatted_data = analyzer_result.get("formatted_data", "")
        sensor_summary = analyzer_result.get("sensor_summary", {})
        comprehensive_analysis = analyzer_result.get("comprehensive_analysis", {})
        
        print(f"📄 Formatted data generado: {len(formatted_data)} caracteres")
        print(f"📊 Sensor summary: {len(sensor_summary)} sensores")
        print(f"🔍 Comprehensive analysis: {len(comprehensive_analysis)} elementos")
        
        if not formatted_data:
            print("❌ PROBLEMA CRÍTICO: formatted_data está vacío")
            print(f"📋 Estado del analyzer: {analyzer_result.get('execution_status', 'unknown')}")
            return
        
        # PASO 6: Verificar contenido del formatted_data
        print("\n📝 PASO 6: Analizando contenido de formatted_data...")
        
        print(f"📄 Primeros 300 chars de formatted_data:")
        print("-" * 50)
        print(formatted_data[:300])
        print("-" * 50)
        
        # Verificar si contiene información real de dispositivos
        dispositivos_reales = ['esp32_wifi_001', 'arduino_eth_001']
        dispositivos_encontrados = [d for d in dispositivos_reales if d in formatted_data.lower()]
        
        print(f"🖥️ Dispositivos reales encontrados en formatted_data: {dispositivos_encontrados}")
        
        if not dispositivos_encontrados:
            print("❌ PROBLEMA CRÍTICO: formatted_data no contiene información de dispositivos reales")
        
        # Verificar si contiene números/estadísticas
        numeros_encontrados = any(char.isdigit() for char in formatted_data)
        print(f"📊 Contiene números/estadísticas: {numeros_encontrados}")
        
        # PASO 7: Ejecutar nodo de generación de respuesta
        print("\n💬 PASO 7: Ejecutando _response_generator_node...")
        
        response_result = await agent._response_generator_node(analyzer_result)
        final_response = response_result.get("final_response", "")
        
        print(f"💭 Respuesta final generada: {len(final_response)} caracteres")
        
        if final_response:
            print(f"📄 Primeros 300 chars de respuesta final:")
            print("-" * 50)
            print(final_response[:300])
            print("-" * 50)
            
            # Verificar si la respuesta final contiene datos reales
            dispositivos_en_respuesta = [d for d in dispositivos_reales if d in final_response.lower()]
            print(f"🖥️ Dispositivos reales en respuesta final: {dispositivos_en_respuesta}")
            
            numeros_en_respuesta = any(char.isdigit() for char in final_response)
            print(f"📊 Contiene números en respuesta: {numeros_en_respuesta}")
        
        # PASO 8: Verificar función de formateo básico
        print("\n🔧 PASO 8: Verificando _generate_basic_intelligent_response...")
        
        # Simular llamada directa
        basic_response = agent._generate_basic_intelligent_response(
            user_query=test_query,
            formatted_data=formatted_data,
            analysis=comprehensive_analysis,
            raw_data=collected_data,
            sensor_summary=sensor_summary
        )
        
        print(f"📝 Respuesta básica generada: {len(basic_response)} caracteres")
        
        if basic_response:
            print(f"📄 Primeros 300 chars de respuesta básica:")
            print("-" * 50)
            print(basic_response[:300])
            print("-" * 50)
            
            # Verificar contenido
            dispositivos_en_basica = [d for d in dispositivos_reales if d in basic_response.lower()]
            print(f"🖥️ Dispositivos reales en respuesta básica: {dispositivos_en_basica}")
        
        # DIAGNÓSTICO FINAL
        print("\n" + "=" * 80)
        print("🎯 DIAGNÓSTICO FINAL")
        print("=" * 80)
        
        if len(collected_data) > 0:
            print("✅ Datos recolectados correctamente")
        else:
            print("❌ FALLO: Recolección de datos")
            
        if len(formatted_data) > 0:
            print("✅ Datos formateados correctamente")
        else:
            print("❌ FALLO: Formateo de datos")
            
        if dispositivos_encontrados:
            print("✅ Dispositivos reales presentes en datos formateados")
        else:
            print("❌ FALLO: Dispositivos reales NO presentes en datos formateados")
            
        if len(final_response) > 0:
            print("✅ Respuesta final generada")
        else:
            print("❌ FALLO: Generación de respuesta final")
            
        if dispositivos_en_respuesta:
            print("✅ Dispositivos reales presentes en respuesta final")
        else:
            print("❌ FALLO: Dispositivos reales NO presentes en respuesta final")
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO en diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diagnostico_exhaustivo())