#!/usr/bin/env python3
"""
Test del sistema de reportes mejorado con múltiples dispositivos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_multi_device_report():
    """Test del sistema mejorado de múltiples dispositivos"""
    
    try:
        print("🔍 Testando sistema de reportes multi-dispositivo...")
        
        # Importar dependencias
        from modules.agents.reporting import ReportGenerator
        
        # Crear generador
        generator = ReportGenerator()
        print("✅ ReportGenerator creado correctamente")
        
        # Solicitud exacta del usuario
        user_request = "genera un informe ejecutivo con los datos del esp32y del arduino ethernet de los registros de las ultimas 48 horas, usa graficos de torta para las temperaturas y de barra para la ldr"
        
        # Metadata mejorada como la que recibiría desde la aplicación
        context_metadata = {
            'data_summary': {
                'total_records': 150,
                'sensors': ['temperature', 'ldr'],
                'devices': ['esp32_wifi_001', 'arduino_eth_001']
            },
            'model_used': 'llama-3.1-8b-instant',
            'execution_status': 'completed'
        }
        
        # Summary text mejorado
        summary_text = """
        ANÁLISIS EJECUTIVO DE SENSORES IOT
        
        Durante las últimas 48 horas se monitorearon 2 dispositivos principales:
        
        ESP32 WiFi 001:
        • Sensor de temperatura: Rango 18.5°C - 28.3°C, promedio 23.4°C
        • Estado: Operativo, dentro de parámetros normales
        
        Arduino Ethernet 001:
        • Sensor LDR: Rango 420-780 lux, promedio 595 lux
        • Estado: Funcionamiento estable
        
        RECOMENDACIONES:
        • Continuar monitoreo automático
        • Revisar picos de temperatura en ESP32
        • Validar calibración del sensor LDR
        """
        
        # Parse del request
        print("📋 Parseando solicitud del usuario...")
        spec = generator.parse_user_request_to_spec(user_request, context_metadata)
        print(f"✅ Spec generado: {spec['title']}")
        print(f"📱 Dispositivos: {spec.get('devices', [])}")
        print(f"🔬 Sensores: {spec.get('sensors', [])}")
        print(f"📊 Tipos de gráficos: {spec.get('chart_types', {})}")
        
        # Generar reporte
        print("📊 Generando reporte multi-dispositivo...")
        file_bytes, filename = generator.generate_report(spec, context_metadata, summary_text)
        
        print(f"✅ Reporte generado exitosamente!")
        print(f"📄 Archivo: {filename}")
        print(f"📊 Tamaño: {len(file_bytes):} bytes")
        
        # Guardar archivo para verificar
        with open(f"test_multi_{filename}", "wb") as f:
            f.write(file_bytes)
        print(f"💾 Archivo guardado como: test_multi_{filename}")
        
        # Validar que el contenido sea completo
        if len(file_bytes) > 10000:  # Archivo robusto
            print("✅ El archivo tiene tamaño adecuado (probablemente contiene gráficos)")
        else:
            print("⚠️ El archivo parece pequeño, puede estar incompleto")
        
        return True, filename, len(file_bytes)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print("🔍 Traceback:")
        print(traceback.format_exc())
        return False, None, 0

if __name__ == "__main__":
    success, filename, size = test_multi_device_report()
    
    if success:
        print(f"\n🎉 ¡Test exitoso!")
        print(f"✅ El sistema de reportes multi-dispositivo funciona")
        print(f"📁 Archivo generado: {filename}")
        print(f"📊 Tamaño: {size:} bytes")
        print(f"\n🔍 Revisa el archivo generado para verificar que contenga:")
        print(f"   - Múltiples dispositivos (ESP32 y Arduino)")
        print(f"   - Múltiples sensores (temperatura, LDR)")
        print(f"   - Gráficos específicos (torta para temp, barras para LDR)")
        print(f"   - Análisis detallado por dispositivo")
    else:
        print(f"\n❌ El test falló")
        print(f"🔧 Revisa los errores arriba para diagnosticar el problema")