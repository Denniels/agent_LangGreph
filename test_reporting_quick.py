#!/usr/bin/env python3
"""
Test rápido del sistema de reportes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.agents.reporting import ReportGenerator
import json

def test_reporting_system():
    """Test rápido del sistema de reportes"""
    
    print("🔍 Iniciando test del sistema de reportes...")
    
    # Crear instancia del generador
    try:
        generator = ReportGenerator()
        print("✅ ReportGenerator creado correctamente")
    except Exception as e:
        print(f"❌ Error creando ReportGenerator: {e}")
        return False
    
    # Test de parsing de request
    user_request = "genera un informe ejecutivo con los datos del esp32y del arduino ethernet de los registros de las ultimas 48 horas, usa graficos de torta para las temperaturas y de barra para la ldr"
    
    # Metadata de ejemplo
    context_metadata = {
        'esp32': {'temperature': 'Temperatura ESP32', 'humidity': 'Humedad ESP32'},
        'arduino_ethernet': {'temperature': 'Temperatura Arduino', 'ldr': 'Sensor LDR'}
    }
    
    try:
        spec = generator.parse_user_request_to_spec(user_request, context_metadata)
        print("✅ Request parseado correctamente")
        print(f"📋 Spec generado: {json.dumps(spec, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ Error parseando request: {e}")
        return False
    
    # Test de generación de datos mock
    try:
        # Generar datos de ejemplo para múltiples series
        series_data = {}
        
        # Agregar datos para ESP32
        series_data['esp32_temperature'] = generator.fetch_series_from_metadata(
            'esp32', 'temperature', context_metadata, 100
        )
        
        # Agregar datos para Arduino Ethernet
        series_data['arduino_ethernet_ldr'] = generator.fetch_series_from_metadata(
            'arduino_ethernet', 'ldr', context_metadata, 100
        )
        
        print("✅ Datos mock generados correctamente")
        print(f"📊 Series generadas: {list(series_data.keys())}")
        
        # Mostrar ejemplo de datos
        for series_name, data in series_data.items():
            print(f"   - {series_name}: {len(data)} puntos")
            
    except Exception as e:
        print(f"❌ Error generando datos mock: {e}")
        return False
    
    # Test de creación de gráficos
    try:
        import plotly.graph_objects as go
        
        # Crear un gráfico simple
        fig = go.Figure()
        fig.add_trace(go.Bar(x=['A', 'B', 'C'], y=[1, 2, 3]))
        fig.update_layout(title="Test Chart")
        
        # Test de exportación PNG
        png_bytes = generator.export_figure_png(fig)
        print(f"✅ Gráfico exportado a PNG correctamente ({len(png_bytes)} bytes)")
        
    except Exception as e:
        print(f"❌ Error creando/exportando gráfico: {e}")
        return False
    
    # Test de generación de reporte completo
    try:
        summary_text = "Este es un reporte ejecutivo de prueba que muestra los datos recopilados de los dispositivos ESP32 y Arduino Ethernet durante las últimas 48 horas."
        
        report_data, filename = generator.generate_report(spec, context_metadata, summary_text)
        print("✅ Reporte generado correctamente")
        print(f"📁 Archivo generado: {filename}")
        print(f"📊 Tamaño del archivo: {len(report_data)} bytes")
            
    except Exception as e:
        print(f"❌ Error generando reporte completo: {e}")
        return False
    
    print("\n🎉 ¡Todos los tests pasaron correctamente!")
    return True

if __name__ == "__main__":
    test_reporting_system()
