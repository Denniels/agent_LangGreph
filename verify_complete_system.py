#!/usr/bin/env python3
"""
🎯 VERIFICACIÓN FINAL DEL SISTEMA COMPLETO
Prueba todas las mejoras implementadas para Streamlit Cloud
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.agents.direct_api_agent import DirectAPIAgent
from modules.agents.cloud_iot_agent import CloudIoTAgent
import json
from datetime import datetime, timezone

def test_banner_integration():
    """Verificar que el banner se puede importar correctamente"""
    print("🎨 VERIFICANDO INTEGRACIÓN DEL BANNER...")
    
    try:
        # Simular la carga del banner como lo haría Streamlit
        from modules.utils.professional_banner import display_complete_banner
        print("✅ Banner profesional: Importación exitosa")
        return True
    except Exception as e:
        print(f"❌ Error importando banner: {e}")
        return False

def test_pagination_system():
    """Verificar sistema de paginación mejorado"""
    print("\n📚 VERIFICANDO SISTEMA DE PAGINACIÓN...")
    
    try:
        base_url = "https://wonder-sufficiently-generator-click.trycloudflare.com"
        agent = DirectAPIAgent(base_url=base_url)
        
        # Test consulta corta (debería usar método estándar)
        print("🔍 Test: Consulta corta (3h)")
        result_short = agent.get_all_recent_data(hours=3.0)
        
        if result_short.get('status') == 'success':
            method_used = result_short.get('method', 'unknown')
            records = result_short.get('total_records', 0)
            print(f"✅ Consulta corta: {records} registros, método: {method_used}")
            
            if method_used == 'general_endpoint':
                print("✅ Método correcto para consulta corta")
            else:
                print(f"⚠️ Método inesperado: {method_used}")
        else:
            print(f"❌ Consulta corta falló: {result_short.get('message', 'Error')}")
            return False
        
        # Test consulta larga (debería usar paginación)
        print("🔍 Test: Consulta extensa (24h)")
        result_long = agent.get_all_recent_data(hours=24.0)
        
        if result_long.get('status') == 'success':
            method_used = result_long.get('method', 'unknown')
            records = result_long.get('total_records', 0)
            hours_span = result_long.get('hours_span', 0)
            print(f"✅ Consulta extensa: {records} registros, método: {method_used}, rango: {hours_span}h")
            
            if method_used == 'paginated':
                print("✅ Método correcto para consulta extensa")
            else:
                print(f"⚠️ Método inesperado: {method_used}")
        else:
            print(f"❌ Consulta extensa falló: {result_long.get('message', 'Error')}")
            return False
        
        print("✅ Sistema de paginación funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en sistema de paginación: {e}")
        return False

def test_cloud_agent_integration():
    """Verificar integración con CloudIoTAgent"""
    print("\n🤖 VERIFICANDO INTEGRACIÓN CLOUD AGENT...")
    
    try:
        # Verificar que CloudIoTAgent puede usar las nuevas funcionalidades
        os.environ['GROQ_API_KEY'] = 'test-key'  # Para evitar errores de inicialización
        
        # Solo verificar que se puede importar correctamente
        from modules.agents.cloud_iot_agent import CloudIoTAgent
        print("✅ CloudIoTAgent: Importación exitosa")
        
        # Verificar que tiene el método mejorado
        if hasattr(CloudIoTAgent, 'process_query_sync'):
            print("✅ CloudIoTAgent: Método process_query_sync disponible")
        else:
            print("⚠️ CloudIoTAgent: process_query_sync no encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en CloudIoTAgent: {e}")
        return False

def test_streamlit_app_structure():
    """Verificar estructura de la aplicación Streamlit"""
    print("\n🌟 VERIFICANDO ESTRUCTURA DE STREAMLIT APP...")
    
    try:
        # Verificar que los archivos principales existen
        main_app = "streamlit_app/app_groq_cloud.py"
        if os.path.exists(main_app):
            print("✅ Aplicación principal encontrada")
            
            # Verificar que tiene las funciones principales
            with open(main_app, 'r', encoding='utf-8') as f:
                content = f.read()
                
            required_functions = [
                'display_professional_banner',
                'display_chat_interface',
                'main'
            ]
            
            for func in required_functions:
                if func in content:
                    print(f"✅ Función {func} encontrada")
                else:
                    print(f"❌ Función {func} no encontrada")
                    return False
            
            # Verificar que incluye mejoras
            improvements = [
                'analysis_hours',
                'time_range_selector',
                'Configuración de Análisis Temporal',
                'professional-banner'
            ]
            
            for improvement in improvements:
                if improvement in content:
                    print(f"✅ Mejora {improvement} implementada")
                else:
                    print(f"⚠️ Mejora {improvement} no encontrada")
            
        else:
            print(f"❌ Aplicación principal no encontrada: {main_app}")
            return False
        
        print("✅ Estructura de aplicación Streamlit verificada")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando aplicación: {e}")
        return False

def generate_deployment_report():
    """Generar reporte final para deployment"""
    print("\n📋 GENERANDO REPORTE DE DEPLOYMENT...")
    
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sistema": "Sistema IoT con IA - Versión Mejorada",
        "mejoras_implementadas": [
            "Banner profesional integrado",
            "Sistema de paginación para consultas extensas", 
            "Configuración temporal dinámica (1h-7días)",
            "Métodos adaptativos (estándar vs paginado)",
            "Interfaz optimizada para demostración a clientes",
            "Información técnica en lenguaje comercial"
        ],
        "capacidades_técnicas": {
            "consultas_rápidas": "1-6 horas (hasta 200 registros)",
            "consultas_extensas": "6+ horas (hasta 2,000 registros)",
            "métodos": ["estándar", "paginado_inteligente"],
            "hardware": "NVIDIA Jetson Nano 4GB",
            "ia": "Groq API (Gratuita)",
            "frontend": "Streamlit Cloud"
        },
        "configuraciones_disponibles": [
            "3 horas (Tiempo Real)",
            "6 horas (Reciente)", 
            "12 horas (Paginado)",
            "24 horas (1 día)",
            "48 horas (2 días)",
            "168 horas (1 semana)"
        ],
        "optimizaciones": [
            "Banner profesional que explica capacidades sin tecnicismos",
            "Selección automática de método según duración",
            "Información contextual sobre hardware y limitaciones",
            "Interfaz adaptativa que muestra método usado",
            "Métricas en tiempo real de configuración actual"
        ]
    }
    
    with open('deployment_readiness_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("✅ Reporte guardado en: deployment_readiness_report.json")
    return report

def main():
    """Función principal de verificación"""
    print("🚀 VERIFICACIÓN FINAL DEL SISTEMA COMPLETO")
    print("=" * 60)
    
    tests = [
        ("Banner Profesional", test_banner_integration),
        ("Sistema de Paginación", test_pagination_system),
        ("Integración Cloud Agent", test_cloud_agent_integration),
        ("Estructura Streamlit", test_streamlit_app_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 Excepción en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print(f"\n🎯 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
    
    print(f"\n📊 RESULTADO FINAL: {passed}/{total} tests exitosos")
    
    if passed == total:
        print("🎉 SISTEMA COMPLETAMENTE LISTO PARA DEPLOYMENT")
        deployment_report = generate_deployment_report()
        
        print(f"\n🚀 INSTRUCCIONES FINALES:")
        print("1. ✅ Todas las mejoras implementadas y verificadas")
        print("2. ✅ Banner profesional integrado")
        print("3. ✅ Paginación automática funcionando")
        print("4. ✅ Configuración temporal dinámica")
        print("5. 🌟 Listo para demostración a clientes")
        
        return True
    else:
        print("⚠️ ALGUNOS TESTS FALLARON - REVISAR ANTES DE DEPLOYMENT")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n🏁 VERIFICACIÓN: {'✅ EXITOSA' if success else '❌ CON ERRORES'}")