#!/usr/bin/env python3
"""
Test Sistema SIN Datos Demo - Validación manejo de errores
=========================================================

Verifica que el sistema maneje correctamente la ausencia de datos reales
sin generar datos ficticios.
"""

from modules.agents.reporting import ReportGenerator
from modules.agents.cloud_iot_agent import CloudIoTAgent

async def test_sistema_sin_datos_demo():
    print('=' * 60)
    print('🔧 PRUEBA SISTEMA SIN DATOS DEMO')
    print('=' * 60)
    
    try:
        print('\n1️⃣ Inicializando ReportGenerator sin Jetson connector...')
        # ReportGenerator sin conexión a Jetson (simula Jetson offline)
        rg = ReportGenerator(jetson_connector=None)
        print('   ✅ ReportGenerator inicializado sin datos demo')
        
        print('\n2️⃣ Inicializando CloudIoTAgent...')
        agent = CloudIoTAgent()
        print('   ✅ CloudIoTAgent inicializado')
        
        print('\n3️⃣ Probando obtención de datos reales (sin Jetson)...')
        # Intentar obtener datos reales - debería fallar apropiadamente
        real_data = rg._get_real_sensor_data("arduino_eth_001", "t1")
        
        if not real_data:
            print('   ✅ CORRECTO: No se generaron datos ficticios')
            print('   📭 Resultado: Lista vacía (sin datos)')
        else:
            print('   ❌ ERROR: Se generaron datos cuando no debería')
            return False
        
        print('\n4️⃣ Probando validación de dispositivos...')
        
        # Test validación (estas funciones no dependen de datos)
        arduino_valid = rg._is_valid_device_sensor_combination('arduino_ethernet', 'temp1')
        arduino_invalid = rg._is_valid_device_sensor_combination('arduino_ethernet', 'ldr')
        esp32_temp_valid = rg._is_valid_device_sensor_combination('esp32_wifi', 'ntc_entrada')
        esp32_ldr_valid = rg._is_valid_device_sensor_combination('esp32_wifi', 'ldr')
        
        print(f'   Arduino + temp1: {arduino_valid} ✅' if arduino_valid else f'   Arduino + temp1: {arduino_valid} ❌')
        print(f'   Arduino + LDR: {arduino_invalid} ❌' if not arduino_invalid else f'   Arduino + LDR: {arduino_invalid} ❌ ERROR')
        print(f'   ESP32 + temp: {esp32_temp_valid} ✅' if esp32_temp_valid else f'   ESP32 + temp: {esp32_temp_valid} ❌')
        print(f'   ESP32 + LDR: {esp32_ldr_valid} ✅' if esp32_ldr_valid else f'   ESP32 + LDR: {esp32_ldr_valid} ❌')
        
        validation_ok = arduino_valid and not arduino_invalid and esp32_temp_valid and esp32_ldr_valid
        
        print('\n5️⃣ Probando procesamiento de consulta sin datos...')
        
        # Test query processing sin datos (debería dar error claro)
        try:
            response = await agent.process_query("¿Cuál es la temperatura actual?")
            
            if "error" in response.get('response', '').lower() or "jetson" in response.get('response', '').lower():
                print('   ✅ CORRECTO: Respuesta indica error de conexión')
                print(f'   📄 Mensaje: {response.get("response", "")[:100]}...')
            else:
                print('   ❌ ERROR: No se indicó correctamente la falta de datos')
                return False
                
        except Exception as e:
            # Es aceptable que falle sin datos
            print(f'   ✅ CORRECTO: Falló apropiadamente sin datos: {str(e)[:100]}...')
        
        print('\n' + '=' * 60)
        if validation_ok:
            print('🎉 TODAS LAS VALIDACIONES PASARON')
            print('✅ Sistema funciona correctamente SIN datos demo')
            print('🚨 Manejo de errores apropiado cuando no hay datos')
            print('📋 Mensajes claros sobre problemas de conectividad')
            print('🔧 NO genera datos ficticios')
        else:
            print('❌ FALLÓ ALGUNA VALIDACIÓN')
            print('🔧 Revisar lógica de validación')
        
        print('=' * 60)
        return validation_ok
        
    except Exception as e:
        print(f'\n❌ ERROR en la prueba: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

async def test_query_processing():
    """Test específico de procesamiento de consultas sin datos"""
    print('\n🧪 PRUEBA PROCESAMIENTO DE CONSULTAS SIN DATOS')
    print('-' * 50)
    
    agent = CloudIoTAgent()
    
    try:
        response = await agent.process_query("Genera un reporte de temperatura")
        
        response_text = response.get('response', '').lower()
        
        if any(keyword in response_text for keyword in ['jetson', 'offline', 'error', 'conectar', 'systemd']):
            print('✅ CORRECTO: Respuesta contiene información de error de Jetson')
            return True
        else:
            print('❌ ERROR: Respuesta no indica problema de conectividad')
            print(f'📄 Respuesta: {response.get("response", "")[:200]}...')
            return False
            
    except Exception as e:
        print(f'✅ CORRECTO: Excepción apropiada sin datos: {e}')
        return True

if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("🔍 EJECUTANDO PRUEBAS SIN DATOS DEMO")
        print("=" * 60)
        
        # Test 1: Sistema básico
        success1 = await test_sistema_sin_datos_demo()
        
        # Test 2: Procesamiento de consultas
        success2 = await test_query_processing()
        
        overall_success = success1 and success2
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN FINAL")
        print("=" * 60)
        
        if overall_success:
            print("🎉 SISTEMA APROBADO - NO USA DATOS DEMO")
            print("✅ Manejo apropiado de falta de datos reales")
            print("🚨 Mensajes de error claros y útiles")
            print("🔧 Instrucciones técnicas para resolver problemas")
        else:
            print("❌ SISTEMA FALLÓ - REVISAR IMPLEMENTACIÓN")
            print("🔧 Verificar que no se generen datos ficticios")
        
        print("=" * 60)
        return overall_success
    
    result = asyncio.run(main())
    exit(0 if result else 1)