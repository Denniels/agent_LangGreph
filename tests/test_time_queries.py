"""
🕒 TEST DE CONSULTAS POR TIEMPO
===============================

Test específico para verificar que el agente maneja correctamente
consultas por tiempo como "últimos 3 minutos", "última hora", etc.
"""

import sys
import os
import asyncio
from datetime import datetime

# Agregar path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from modules.agents.cloud_iot_agent import CloudIoTAgent, create_cloud_iot_agent

def print_separator(title: str):
    """Imprimir separador visual"""
    print(f"\n{'='*60}")
    print(f"🕒 {title}")
    print(f"{'='*60}")

async def test_time_queries():
    """Probar diferentes tipos de consultas por tiempo"""
    print_separator("TESTS DE CONSULTAS POR TIEMPO")
    
    try:
        # 1. Crear agente
        print("🤖 Creando CloudIoTAgent...")
        agent = create_cloud_iot_agent()
        print("✅ Agente creado")
        
        # 2. Lista de consultas por tiempo para probar
        time_queries = [
            "listame los registros de los últimos 3 minutos",
            "muestra los datos de los últimos 5 minutos", 
            "dame los registros de la última hora",
            "últimos 10 minutos de datos",
            "registros de los últimos 2 hrs"
        ]
        
        results = []
        
        for i, query in enumerate(time_queries, 1):
            print(f"\n🔍 TEST {i}: '{query}'")
            print("-" * 50)
            
            try:
                response = await agent.process_query(query)
                
                success = response.get('success', False)
                data_summary = response.get('data_summary', {})
                devices = data_summary.get('devices', [])
                total_records = data_summary.get('total_records', 0)
                
                print(f"✅ Éxito: {success}")
                print(f"📱 Dispositivos detectados: {devices}")
                print(f"📊 Registros totales: {total_records}")
                
                if len(devices) >= 2:
                    print("✅ CORRECTO: Ve ambos dispositivos")
                else:
                    print("❌ PROBLEMA: Solo ve 1 dispositivo o ninguno")
                
                # Mostrar parte de la respuesta
                response_text = response.get('response', '')
                preview = response_text[:300] + "..." if len(response_text) > 300 else response_text
                print(f"\n📝 Respuesta (preview):")
                print(preview)
                
                results.append({
                    'query': query,
                    'success': success,
                    'devices_count': len(devices),
                    'devices': devices,
                    'records_count': total_records,
                    'response_preview': preview
                })
                
            except Exception as e:
                print(f"❌ Error: {e}")
                results.append({
                    'query': query,
                    'success': False,
                    'error': str(e)
                })
        
        # 3. Resumen de resultados
        print_separator("RESUMEN DE TESTS POR TIEMPO")
        
        successful_tests = sum(1 for r in results if r.get('success', False))
        total_tests = len(results)
        
        print(f"📊 Tests exitosos: {successful_tests}/{total_tests}")
        
        for i, result in enumerate(results, 1):
            status = "✅" if result.get('success', False) else "❌"
            devices_count = result.get('devices_count', 0)
            devices_status = "✅" if devices_count >= 2 else "❌"
            
            print(f"{status} Test {i}: {result['query'][:30]}...")
            print(f"   {devices_status} Dispositivos: {devices_count} detectados")
            
            if 'error' in result:
                print(f"   🔥 Error: {result['error']}")
        
        # 4. Verificar mejora específica
        print_separator("VERIFICACIÓN DE MEJORA ESPECÍFICA")
        
        # Test específico del problema reportado
        problem_query = "listame los registros de los últimos 3 minutos"
        print(f"🎯 Probando consulta específica del problema: '{problem_query}'")
        
        response = await agent.process_query(problem_query)
        devices = response.get('data_summary', {}).get('devices', [])
        
        if len(devices) >= 2:
            print("🎉 ¡PROBLEMA RESUELTO! Ahora ve ambos dispositivos en consultas por tiempo")
            print(f"   📱 Dispositivos detectados: {devices}")
        else:
            print("⚠️ Problema AÚN PRESENTE - Solo detecta:", devices)
        
        return results
        
    except Exception as e:
        print(f"❌ Error general en test: {e}")
        import traceback
        traceback.print_exc()
        return []

async def test_comparison_count_vs_time():
    """Comparar consultas por cantidad vs por tiempo"""
    print_separator("COMPARACIÓN: CANTIDAD vs TIEMPO")
    
    try:
        agent = create_cloud_iot_agent()
        
        # Consulta por cantidad (sabemos que funciona)
        print("🔢 Probando consulta por CANTIDAD...")
        count_response = await agent.process_query("listame los últimos 15 registros de cada dispositivo")
        count_devices = count_response.get('data_summary', {}).get('devices', [])
        count_records = count_response.get('data_summary', {}).get('total_records', 0)
        
        print(f"   📱 Dispositivos: {count_devices}")
        print(f"   📊 Registros: {count_records}")
        
        # Consulta por tiempo (lo que estamos arreglando)
        print("\n🕒 Probando consulta por TIEMPO...")
        time_response = await agent.process_query("listame los registros de los últimos 3 minutos")
        time_devices = time_response.get('data_summary', {}).get('devices', [])
        time_records = time_response.get('data_summary', {}).get('total_records', 0)
        
        print(f"   📱 Dispositivos: {time_devices}")
        print(f"   📊 Registros: {time_records}")
        
        # Comparación
        print("\n📋 COMPARACIÓN:")
        print(f"   Cantidad - Dispositivos: {len(count_devices)}, Registros: {count_records}")
        print(f"   Tiempo   - Dispositivos: {len(time_devices)}, Registros: {time_records}")
        
        if len(count_devices) == len(time_devices) and len(time_devices) >= 2:
            print("✅ ¡EXCELENTE! Ambos tipos de consulta ven la misma cantidad de dispositivos")
        else:
            print("⚠️ Inconsistencia detectada entre consultas por cantidad y tiempo")
        
        return {
            'count_query': {
                'devices': count_devices,
                'records': count_records
            },
            'time_query': {
                'devices': time_devices,
                'records': time_records
            }
        }
        
    except Exception as e:
        print(f"❌ Error en comparación: {e}")
        return {}

async def main():
    """Función principal"""
    print("🕒 TEST COMPLETO DE CONSULTAS POR TIEMPO")
    print("=" * 60)
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Objetivo: Verificar que consultas por tiempo vean TODOS los dispositivos")
    
    # 1. Tests principales
    time_results = await test_time_queries()
    
    # 2. Comparación
    comparison = await test_comparison_count_vs_time()
    
    # 3. Guardar resultados
    import json
    results = {
        'timestamp': datetime.now().isoformat(),
        'time_query_tests': time_results,
        'comparison': comparison
    }
    
    with open('time_query_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Resultados guardados en: time_query_test_results.json")
    
    print_separator("TEST COMPLETADO")

if __name__ == "__main__":
    asyncio.run(main())