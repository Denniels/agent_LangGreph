"""
Verificación Completa del Sistema Ultra-Robusto
==============================================

Script integral para verificar que todos los componentes del sistema
ultra-robusto funcionen correctamente antes del deployment.
"""

import os
import sys
import json
import traceback
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Verificar que todos los imports necesarios funcionen."""
    print("🔄 Verificando imports del sistema ultra-robusto...")
    
    try:
        # Imports básicos
        import streamlit as st
        print("✅ Streamlit importado correctamente")
        
        # Imports del sistema ultra-robusto
        from modules.tools.ultra_robust_connector import UltraRobustJetsonConnector
        print("✅ UltraRobustJetsonConnector importado correctamente")
        
        from modules.agents.ultra_robust_agent import UltraRobustIoTAgent
        print("✅ UltraRobustIoTAgent importado correctamente")
        
        from modules.utils.executive_report_generator import ExecutiveReportGenerator
        print("✅ ExecutiveReportGenerator importado correctamente")
        
        from modules.utils.visualization_engine import VisualizationEngine
        print("✅ VisualizationEngine importado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        traceback.print_exc()
        return False

def test_connector():
    """Verificar funcionamiento del conector ultra-robusto."""
    print("\n🔄 Verificando UltraRobustJetsonConnector...")
    
    try:
        from modules.tools.ultra_robust_connector import UltraRobustJetsonConnector
        
        # Inicializar conector con URL actual
        base_url = "https://wonder-sufficiently-generator-click.trycloudflare.com"
        connector = UltraRobustJetsonConnector(base_url)
        print("✅ Conector inicializado correctamente")
        
        # Test de dispositivos
        print("📡 Testeando obtención de dispositivos...")
        devices = connector.get_devices_robust()
        print(f"✅ Dispositivos obtenidos: {len(devices) if devices else 0}")
        
        if devices:
            print(f"   Primer dispositivo: {devices[0]}")
        
        # Test de datos de sensores (usando primer dispositivo si está disponible)
        print("📊 Testeando obtención de datos de sensores...")
        if devices and len(devices) > 0:
            device_id = devices[0].get('device_id', 'esp32_wifi_001')
            sensor_data = connector.get_sensor_data_robust(device_id, hours=1)
            print(f"✅ Datos de sensores obtenidos: {len(sensor_data) if sensor_data else 0}")
        else:
            sensor_data = []
            print("⚠️ No hay dispositivos disponibles para test de sensores")
        
        # Test comprehensivo
        print("🔧 Testeando análisis comprehensivo...")
        comprehensive_data = connector.get_all_data_comprehensive(hours=2, max_records_per_device=100)
        print(f"✅ Análisis comprehensivo: {len(comprehensive_data) if comprehensive_data else 0} registros")
        
        return True, {
            'devices': len(devices) if devices else 0,
            'sensor_data': len(sensor_data) if sensor_data else 0,
            'comprehensive_data': len(comprehensive_data) if comprehensive_data else 0
        }
        
    except Exception as e:
        print(f"❌ Error en conector: {e}")
        traceback.print_exc()
        return False, {}

def test_agent():
    """Verificar funcionamiento del agente ultra-robusto."""
    print("\n🔄 Verificando UltraRobustIoTAgent...")
    
    try:
        from modules.tools.ultra_robust_connector import UltraRobustJetsonConnector
        from modules.agents.ultra_robust_agent import UltraRobustIoTAgent
        from modules.utils.visualization_engine import VisualizationEngine
        
        # Inicializar componentes
        base_url = "https://wonder-sufficiently-generator-click.trycloudflare.com"
        connector = UltraRobustJetsonConnector(base_url)
        visualization_engine = VisualizationEngine()
        agent = UltraRobustIoTAgent(connector, visualization_engine)
        print("✅ Agente inicializado correctamente")
        
        # Test de query
        print("🤖 Testeando procesamiento de query...")
        test_query = """
        Proporciona un análisis técnico del estado actual del sistema IoT.
        Incluye métricas de dispositivos, sensores y calidad de datos.
        """
        
        response = agent.process_query(test_query, hours=2)
        print("✅ Query procesada correctamente")
        
        # Verificar estructura de respuesta
        required_keys = ['response', 'data_summary', 'analysis_metadata']
        for key in required_keys:
            if key in response:
                print(f"✅ Respuesta contiene '{key}'")
            else:
                print(f"⚠️ Respuesta no contiene '{key}'")
        
        print(f"📝 Longitud de respuesta: {len(response.get('response', ''))}")
        
        return True, response
        
    except Exception as e:
        print(f"❌ Error en agente: {e}")
        traceback.print_exc()
        return False, {}

def test_report_generator():
    """Verificar funcionamiento del generador de reportes."""
    print("\n🔄 Verificando ExecutiveReportGenerator...")
    
    try:
        from modules.tools.ultra_robust_connector import UltraRobustJetsonConnector
        from modules.utils.executive_report_generator import ExecutiveReportGenerator
        from modules.utils.visualization_engine import VisualizationEngine
        
        # Inicializar componentes
        base_url = "https://wonder-sufficiently-generator-click.trycloudflare.com"
        connector = UltraRobustJetsonConnector(base_url)
        visualization_engine = VisualizationEngine()
        report_generator = ExecutiveReportGenerator(connector, visualization_engine)
        print("✅ Generador de reportes inicializado correctamente")
        
        # Test de generación de reporte
        print("📋 Testeando generación de reporte ejecutivo...")
        report = report_generator.generate_comprehensive_report(hours=2, report_type="executive")
        print("✅ Reporte ejecutivo generado correctamente")
        
        # Verificar estructura del reporte
        required_sections = [
            'metadata', 'executive_summary', 'technical_analysis', 
            'performance_metrics', 'recommendations', 'visualizations'
        ]
        
        for section in required_sections:
            if section in report:
                print(f"✅ Reporte contiene sección '{section}'")
            else:
                print(f"⚠️ Reporte no contiene sección '{section}'")
        
        # Test de exportación HTML
        print("📄 Testeando exportación a HTML...")
        html_content = report_generator.export_to_html(report)
        print(f"✅ HTML generado: {len(html_content)} caracteres")
        
        return True, report
        
    except Exception as e:
        print(f"❌ Error en generador de reportes: {e}")
        traceback.print_exc()
        return False, {}

def test_streamlit_app():
    """Verificar que la aplicación Streamlit se puede importar."""
    print("\n🔄 Verificando aplicación Streamlit...")
    
    try:
        # Verificar que existe el archivo
        app_path = "streamlit_app/app_ultra_robust.py"
        if os.path.exists(app_path):
            print(f"✅ Archivo de aplicación encontrado: {app_path}")
        else:
            print(f"❌ Archivo de aplicación no encontrado: {app_path}")
            return False
        
        # Verificar importación (sin ejecutar)
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar imports clave
        required_imports = [
            'streamlit',
            'UltraRobustJetsonConnector',
            'UltraRobustIoTAgent',
            'ExecutiveReportGenerator',
            'VisualizationEngine'
        ]
        
        for import_name in required_imports:
            if import_name in content:
                print(f"✅ Aplicación incluye import de '{import_name}'")
            else:
                print(f"⚠️ Aplicación no incluye import de '{import_name}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando aplicación Streamlit: {e}")
        return False

def create_system_report(test_results):
    """Crear reporte del estado del sistema."""
    print("\n📊 Generando reporte del sistema...")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'system_status': 'UNKNOWN',
        'test_results': test_results,
        'summary': {},
        'recommendations': []
    }
    
    # Determinar estado del sistema
    passed_tests = sum(1 for result in test_results.values() if result.get('status') == 'PASS')
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    if success_rate == 100:
        report['system_status'] = 'OPTIMAL'
        report['summary']['message'] = f"Sistema completamente operativo ({passed_tests}/{total_tests} tests pasados)"
    elif success_rate >= 80:
        report['system_status'] = 'OPERATIONAL'
        report['summary']['message'] = f"Sistema operativo con advertencias ({passed_tests}/{total_tests} tests pasados)"
    elif success_rate >= 60:
        report['system_status'] = 'DEGRADED'
        report['summary']['message'] = f"Sistema con degradación ({passed_tests}/{total_tests} tests pasados)"
    else:
        report['system_status'] = 'CRITICAL'
        report['summary']['message'] = f"Sistema con problemas críticos ({passed_tests}/{total_tests} tests pasados)"
    
    report['summary']['success_rate'] = success_rate
    report['summary']['passed_tests'] = passed_tests
    report['summary']['total_tests'] = total_tests
    
    # Recomendaciones
    if report['system_status'] == 'OPTIMAL':
        report['recommendations'].append("✅ Sistema listo para deployment")
        report['recommendations'].append("🚀 Proceder con actualización en Streamlit Cloud")
    elif report['system_status'] == 'OPERATIONAL':
        report['recommendations'].append("⚠️ Revisar advertencias antes del deployment")
        report['recommendations'].append("🔧 Realizar pruebas adicionales si es necesario")
    else:
        report['recommendations'].append("❌ NO proceder con deployment")
        report['recommendations'].append("🔧 Resolver problemas críticos identificados")
    
    return report

def main():
    """Función principal de verificación."""
    print("🚀 VERIFICACIÓN COMPLETA DEL SISTEMA ULTRA-ROBUSTO")
    print("=" * 60)
    
    test_results = {}
    
    # Test 1: Imports
    print("\n1️⃣ TEST DE IMPORTS")
    imports_ok = test_imports()
    test_results['imports'] = {
        'status': 'PASS' if imports_ok else 'FAIL',
        'description': 'Verificación de imports del sistema'
    }
    
    if not imports_ok:
        print("❌ FALLÓ TEST DE IMPORTS - No se pueden ejecutar tests adicionales")
        return
    
    # Test 2: Conector
    print("\n2️⃣ TEST DE CONECTOR ULTRA-ROBUSTO")
    connector_ok, connector_data = test_connector()
    test_results['connector'] = {
        'status': 'PASS' if connector_ok else 'FAIL',
        'description': 'Verificación del conector ultra-robusto',
        'data': connector_data
    }
    
    # Test 3: Agente
    print("\n3️⃣ TEST DE AGENTE ULTRA-ROBUSTO")
    agent_ok, agent_response = test_agent()
    test_results['agent'] = {
        'status': 'PASS' if agent_ok else 'FAIL',
        'description': 'Verificación del agente ultra-robusto',
        'response_length': len(agent_response.get('response', '')) if agent_ok else 0
    }
    
    # Test 4: Generador de reportes
    print("\n4️⃣ TEST DE GENERADOR DE REPORTES")
    report_ok, report_data = test_report_generator()
    test_results['report_generator'] = {
        'status': 'PASS' if report_ok else 'FAIL',
        'description': 'Verificación del generador de reportes ejecutivos',
        'sections': list(report_data.keys()) if report_ok else []
    }
    
    # Test 5: Aplicación Streamlit
    print("\n5️⃣ TEST DE APLICACIÓN STREAMLIT")
    app_ok = test_streamlit_app()
    test_results['streamlit_app'] = {
        'status': 'PASS' if app_ok else 'FAIL',
        'description': 'Verificación de la aplicación Streamlit'
    }
    
    # Generar reporte final
    print("\n" + "=" * 60)
    system_report = create_system_report(test_results)
    
    print(f"🎯 ESTADO DEL SISTEMA: {system_report['system_status']}")
    print(f"📊 {system_report['summary']['message']}")
    print(f"📈 Tasa de éxito: {system_report['summary']['success_rate']:.1f}%")
    
    print("\n🚀 RECOMENDACIONES:")
    for recommendation in system_report['recommendations']:
        print(f"   {recommendation}")
    
    # Guardar reporte
    report_file = f"system_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(system_report, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Reporte guardado en: {report_file}")
    except Exception as e:
        print(f"⚠️ No se pudo guardar el reporte: {e}")
    
    print("\n" + "=" * 60)
    print("✅ VERIFICACIÓN COMPLETA FINALIZADA")
    
    return system_report['system_status'] in ['OPTIMAL', 'OPERATIONAL']

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)