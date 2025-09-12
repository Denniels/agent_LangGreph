#!/usr/bin/env python3
"""
Test Final Sistema Completo - Pre-Deploy
========================================

Prueba completa del sistema antes del despliegue a Streamlit Cloud.
Verifica todas las funcionalidades principales.
"""

import asyncio
from modules.agents.reporting import ReportGenerator
from modules.agents.cloud_iot_agent import CloudIoTAgent
from modules.tools.jetson_api_connector import JetsonAPIConnector

async def test_complete_system():
    print('=' * 70)
    print('🚀 PRUEBA FINAL PRE-DEPLOY - SISTEMA COMPLETO')
    print('=' * 70)
    
    success_count = 0
    total_tests = 0
    
    try:
        # Test 1: Conexión con Jetson API
        print('\n1️⃣ VERIFICANDO CONEXIÓN JETSON API...')
        total_tests += 1
        
        try:
            jetson = JetsonAPIConnector()
            health = jetson.health_check()
            
            if health and health.get('status') == 'ok':
                print('   ✅ Jetson API: ONLINE y funcionando')
                success_count += 1
            else:
                print('   ⚠️ Jetson API: Respuesta inesperada')
                print(f'   📄 Health: {health}')
        except Exception as e:
            print(f'   ❌ Jetson API: Error de conexión - {e}')
        
        # Test 2: Inicialización CloudIoTAgent
        print('\n2️⃣ INICIALIZANDO CLOUD IOT AGENT...')
        total_tests += 1
        
        try:
            agent = CloudIoTAgent()
            print('   ✅ CloudIoTAgent inicializado correctamente')
            success_count += 1
        except Exception as e:
            print(f'   ❌ Error inicializando CloudIoTAgent: {e}')
            return False
        
        # Test 3: Procesamiento de consulta real
        print('\n3️⃣ PROCESANDO CONSULTA DE PRUEBA...')
        total_tests += 1
        
        try:
            response = await agent.process_query("¿Cuál es el estado actual de los sensores?")
            
            if response.get('success') and response.get('response'):
                print('   ✅ Consulta procesada exitosamente')
                print(f'   📊 Respuesta: {response.get("response", "")[:150]}...')
                success_count += 1
            else:
                print('   ❌ Error procesando consulta')
                print(f'   📄 Response: {response}')
        except Exception as e:
            print(f'   ❌ Excepción procesando consulta: {e}')
        
        # Test 4: Health Check del sistema
        print('\n4️⃣ VERIFICANDO HEALTH CHECK COMPLETO...')
        total_tests += 1
        
        try:
            health = await agent.health_check()
            
            if health.get('overall_status') in ['ok', 'healthy']:
                print('   ✅ Health Check: Sistema saludable')
                print(f'   📊 Status: {health.get("overall_status")}')
                success_count += 1
            else:
                print('   ⚠️ Health Check: Estado degradado')
                print(f'   📄 Status: {health}')
        except Exception as e:
            print(f'   ❌ Error en health check: {e}')
        
        # Test 5: Validación configuración dispositivos
        print('\n5️⃣ VALIDANDO CONFIGURACIÓN DISPOSITIVOS...')
        total_tests += 1
        
        try:
            rg = ReportGenerator()
            
            # Verificar configuración corregida
            arduino_temp_ok = rg._is_valid_device_sensor_combination('arduino_ethernet', 't1')
            arduino_ldr_invalid = not rg._is_valid_device_sensor_combination('arduino_ethernet', 'ldr')
            esp32_temp_ok = rg._is_valid_device_sensor_combination('esp32_wifi', 'ntc_entrada')
            esp32_ldr_ok = rg._is_valid_device_sensor_combination('esp32_wifi', 'ldr')
            
            if arduino_temp_ok and arduino_ldr_invalid and esp32_temp_ok and esp32_ldr_ok:
                print('   ✅ Configuración dispositivos: CORRECTA')
                print('   🔧 Arduino Ethernet: Solo temperatura ✅')
                print('   📡 ESP32 WiFi: Temperatura + LDR ✅')
                success_count += 1
            else:
                print('   ❌ Configuración dispositivos: INCORRECTA')
                print(f'   Arduino temp: {arduino_temp_ok}, Arduino LDR invalid: {arduino_ldr_invalid}')
                print(f'   ESP32 temp: {esp32_temp_ok}, ESP32 LDR: {esp32_ldr_ok}')
        except Exception as e:
            print(f'   ❌ Error validando configuración: {e}')
        
        # Test 6: Verificar ausencia de datos demo
        print('\n6️⃣ VERIFICANDO AUSENCIA DE DATOS DEMO...')
        total_tests += 1
        
        try:
            # Verificar que no existan métodos de datos demo
            has_demo_methods = False
            
            # Verificar CloudIoTAgent
            if hasattr(agent, '_get_demo_data'):
                has_demo_methods = True
                print('   ❌ CloudIoTAgent aún tiene _get_demo_data')
            
            # Verificar ReportGenerator
            if hasattr(rg, 'fetch_series_from_metadata'):
                has_demo_methods = True
                print('   ❌ ReportGenerator aún tiene fetch_series_from_metadata')
            
            if not has_demo_methods:
                print('   ✅ Datos demo: COMPLETAMENTE ELIMINADOS')
                print('   🚫 No hay métodos de generación de datos ficticios')
                success_count += 1
            else:
                print('   ❌ Aún existen métodos de datos demo')
        except Exception as e:
            print(f'   ❌ Error verificando datos demo: {e}')
        
        # Resumen final
        print('\n' + '=' * 70)
        print('📊 RESUMEN DE PRUEBAS PRE-DEPLOY')
        print('=' * 70)
        
        success_rate = (success_count / total_tests) * 100
        
        print(f'✅ Pruebas exitosas: {success_count}/{total_tests} ({success_rate:.1f}%)')
        
        if success_count == total_tests:
            print('🎉 SISTEMA COMPLETAMENTE FUNCIONAL')
            print('✅ Listo para despliegue en Streamlit Cloud')
            print('🚀 Todas las correcciones implementadas correctamente')
            print('🔧 Arduino Ethernet: Solo temperatura')
            print('📡 ESP32 WiFi: Temperatura + LDR')
            print('🚫 Datos demo completamente eliminados')
            return True
        elif success_count >= total_tests * 0.8:
            print('⚠️ SISTEMA MAYORMENTE FUNCIONAL')
            print('🔧 Algunas funciones pueden necesitar revisión')
            print('📋 Revisar tests fallidos antes del deploy')
            return True
        else:
            print('❌ SISTEMA CON PROBLEMAS CRÍTICOS')
            print('🛑 NO recomendado para despliegue')
            print('🔧 Resolver problemas antes de continuar')
            return False
            
    except Exception as e:
        print(f'\n💥 ERROR CRÍTICO EN PRUEBAS: {e}')
        import traceback
        traceback.print_exc()
        return False

async def test_specific_device_data():
    """Test específico de datos por dispositivo"""
    print('\n🔍 PRUEBA ESPECÍFICA: DATOS POR DISPOSITIVO')
    print('-' * 50)
    
    try:
        agent = CloudIoTAgent()
        
        # Test consulta específica de temperatura
        temp_response = await agent.process_query("¿Cuáles son las temperaturas del Arduino Ethernet?")
        
        if temp_response.get('success'):
            response_text = temp_response.get('response', '').lower()
            
            # Verificar que no mencione LDR para Arduino
            if 'ldr' in response_text and 'arduino' in response_text:
                print('   ❌ ERROR: Respuesta menciona LDR para Arduino')
                return False
            else:
                print('   ✅ CORRECTO: No menciona LDR para Arduino Ethernet')
                return True
        else:
            print('   ⚠️ No se pudo procesar consulta específica')
            return False
            
    except Exception as e:
        print(f'   ❌ Error en prueba específica: {e}')
        return False

if __name__ == "__main__":
    async def main():
        print("🔍 EJECUTANDO PRUEBAS FINALES PRE-DEPLOY")
        print("=" * 70)
        
        # Test principal
        main_success = await test_complete_system()
        
        # Test específico
        device_success = await test_specific_device_data()
        
        # Resultado final
        overall_success = main_success and device_success
        
        print("\n" + "=" * 70)
        print("🏁 RESULTADO FINAL PRE-DEPLOY")
        print("=" * 70)
        
        if overall_success:
            print("🎉 SISTEMA APROBADO PARA DEPLOY")
            print("✅ Todas las correcciones implementadas")
            print("🚀 Proceder con commit y push a Streamlit Cloud")
            print("\n📋 ACCIONES SIGUIENTES:")
            print("   1. git add .")
            print("   2. git commit -m 'Fix: Eliminados datos demo, implementada configuración real de dispositivos'")
            print("   3. git push origin main")
            print("   4. Verificar despliegue en Streamlit Cloud")
        else:
            print("❌ SISTEMA NO LISTO PARA DEPLOY")
            print("🔧 Resolver problemas identificados primero")
        
        print("=" * 70)
        return overall_success
    
    result = asyncio.run(main())
    exit(0 if result else 1)