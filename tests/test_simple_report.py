#!/usr/bin/env python3
"""
Versión simplificada de test para verificar que el sistema de reportes funciona
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_report_generation_simple():
    """Test simple de generación de reporte"""
    
    try:
        print("🔍 Iniciando test simple de generación de reporte...")
        
        # Importar dependencias
        from modules.agents.reporting import ReportGenerator
        
        # Crear generador
        generator = ReportGenerator()
        print("✅ ReportGenerator creado correctamente")
        
        # Datos de ejemplo como los que recibiría desde la aplicación
        user_request = "genera un informe ejecutivo con los datos del esp32y del arduino ethernet de los registros de las ultimas 48 horas, usa graficos de torta para las temperaturas y de barra para la ldr"
        
        # Metadata de ejemplo (como response del agente)
        context_metadata = {
            'data_summary': {
                'total_records': 80,
                'sensors': ['temperature', 'humidity', 'ldr'],
                'devices': ['esp32_wifi_001', 'arduino_eth_001']
            },
            'model_used': 'llama-3.1-8b-instant',
            'execution_status': 'completed'
        }
        
        # Summary text
        summary_text = """
        Análisis de Temperatura:
        • Rango detectado: 18.5°C - 28.3°C
        • Promedio: 23.4°C
        • Estado: Normal, dentro de parámetros operativos
        • Recomendación: Monitoreo continuo recomendado
        """
        
        # Parse del request
        print("📋 Parseando solicitud del usuario...")
        spec = generator.parse_user_request_to_spec(user_request, context_metadata)
        print(f"✅ Spec generado: {spec['title']}")
        
        # Generar reporte
        print("📊 Generando reporte...")
        file_bytes, filename = generator.generate_report(spec, context_metadata, summary_text)
        
        print(f"✅ Reporte generado exitosamente!")
        print(f"📄 Archivo: {filename}")
        print(f"📊 Tamaño: {len(file_bytes):,} bytes")
        
        # Guardar archivo para verificar
        with open(f"test_{filename}", "wb") as f:
            f.write(file_bytes)
        print(f"💾 Archivo guardado como: test_{filename}")
        
        return True, filename, len(file_bytes)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print("🔍 Traceback:")
        print(traceback.format_exc())
        return False, None, 0

if __name__ == "__main__":
    success, filename, size = test_report_generation_simple()
    
    if success:
        print(f"\n🎉 ¡Test exitoso!")
        print(f"✅ El sistema de reportes funciona correctamente")
        print(f"📁 Archivo generado: {filename}")
        print(f"📊 Tamaño: {size:,} bytes")
    else:
        print(f"\n❌ El test falló")
        print(f"🔧 Revisa los errores arriba para diagnosticar el problema")
