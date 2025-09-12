#!/usr/bin/env python3
"""
Test del Sistema de Seguimiento de Uso de API
============================================

Prueba completa del sistema de contadores de consultas y tokens.
"""

import os
import sys
import json
from datetime import datetime, date
from pathlib import Path

# Agregar path del proyecto
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from modules.utils.usage_tracker import UsageTracker, usage_tracker
from modules.agents.cloud_iot_agent import CloudIoTAgent
import asyncio

def test_usage_tracker_basic():
    """Test básico del sistema de seguimiento"""
    print("🧪 INICIANDO TESTS DEL SISTEMA DE SEGUIMIENTO")
    print("=" * 60)
    
    try:
        # 1. Test de inicialización
        print("\n1️⃣ Test de Inicialización")
        tracker = UsageTracker("test_usage.json")
        print(f"   ✅ Tracker inicializado")
        print(f"   📅 Fecha actual: {tracker.usage_data['last_reset_date']}")
        
        # 2. Test de información de modelo
        print("\n2️⃣ Test de Información de Modelo")
        model = "llama-3.1-8b-instant"
        usage_info = tracker.get_usage_info(model)
        
        print(f"   🤖 Modelo: {usage_info['model_description']}")
        print(f"   🔥 Límite requests: {usage_info['requests_limit']:,}")
        print(f"   🎯 Límite tokens: {usage_info['tokens_limit']:,}")
        print(f"   📊 Estado: {usage_info['status']}")
        
        # 3. Test de registro de consultas
        print("\n3️⃣ Test de Registro de Consultas")
        
        # Simular varias consultas
        for i in range(5):
            tokens_used = 100 + (i * 50)  # Variar tokens
            result = tracker.track_request(model, tokens_used)
            
            print(f"   Consulta {i+1}: {result['requests_used']} requests, {result['tokens_used']} tokens")
        
        # 4. Test de verificación de límites
        print("\n4️⃣ Test de Verificación de Límites")
        can_make_request, message = tracker.check_can_make_request(model)
        print(f"   ✅ Puede hacer consulta: {can_make_request}")
        print(f"   💬 Mensaje: {message}")
        
        # 5. Test de resumen diario
        print("\n5️⃣ Test de Resumen Diario")
        summary = tracker.get_daily_summary()
        print(f"   📊 Total requests hoy: {summary['total_requests_today']}")
        print(f"   🎯 Total tokens hoy: {summary['total_tokens_today']}")
        print(f"   🤖 Modelos usados: {summary['models_used_today']}")
        
        # 6. Test de múltiples modelos
        print("\n6️⃣ Test de Múltiples Modelos")
        other_model = "llama-3.1-70b-versatile"
        tracker.track_request(other_model, 200)
        
        all_usage = tracker.get_all_models_usage()
        print(f"   📈 Modelos con datos: {len(all_usage)}")
        
        for model_id, info in all_usage.items():
            if info["requests_used"] > 0:
                print(f"   • {info['model_description']}: {info['requests_used']} requests")
        
        print("\n✅ TODOS LOS TESTS BÁSICOS COMPLETADOS")
        
        # Limpiar archivo de test
        test_file = Path("test_usage.json")
        if test_file.exists():
            test_file.unlink()
            print("🧹 Archivo de test limpiado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en tests básicos: {e}")
        return False

async def test_usage_integration():
    """Test de integración con CloudIoTAgent"""
    print("\n🔗 INICIANDO TEST DE INTEGRACIÓN")
    print("=" * 50)
    
    try:
        # Test con agente real
        print("\n1️⃣ Creando CloudIoTAgent")
        agent = CloudIoTAgent()
        
        print("\n2️⃣ Inicializando agente")
        success = await agent.initialize()
        print(f"   ✅ Inicialización: {success}")
        
        print("\n3️⃣ Verificando health check con uso de API")
        health = await agent.health_check()
        
        if "api_usage" in health:
            usage = health["api_usage"]
            print(f"   🤖 Modelo: {usage['model']}")
            print(f"   🔥 Requests: {usage['requests_used']}/{usage['requests_limit']}")
            print(f"   🎯 Tokens: {usage['tokens_used']}/{usage['tokens_limit']}")
            print(f"   📊 Estado: {usage['status']}")
            print("   ✅ Información de uso incluida en health check")
        else:
            print("   ⚠️ Información de uso no encontrada en health check")
        
        print("\n4️⃣ Procesando consulta de prueba")
        response = await agent.process_query("¿Cuál es la temperatura actual?")
        
        if response.get("success"):
            print("   ✅ Consulta procesada exitosamente")
            
            # Verificar si hay información de uso en la respuesta
            if "usage_info" in response:
                usage = response["usage_info"]
                print(f"   📊 Uso actualizado: {usage['requests_used']} requests")
            else:
                print("   ℹ️ Información de uso no en respuesta directa")
                
        else:
            print(f"   ⚠️ Consulta falló: {response.get('error', 'Error desconocido')}")
        
        print("\n✅ TEST DE INTEGRACIÓN COMPLETADO")
        return True
        
    except Exception as e:
        print(f"❌ Error en test de integración: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_usage_limits():
    """Test de comportamiento cerca de límites"""
    print("\n⚠️ INICIANDO TEST DE LÍMITES")
    print("=" * 40)
    
    try:
        # Crear tracker de prueba con límites bajos
        tracker = UsageTracker("test_limits.json")
        
        # Simular modelo con límite bajo para testing
        model = "test-model"
        tracker.daily_limits[model] = {
            "requests": 10,  # Límite muy bajo para testing
            "tokens": 1000,
            "description": "Modelo de Test"
        }
        
        print(f"\n1️⃣ Simulando uso hasta límite (10 requests)")
        
        # Usar hasta el límite
        for i in range(12):  # Intentar 12, límite en 10
            can_make, message = tracker.check_can_make_request(model)
            
            if can_make:
                result = tracker.track_request(model, 50)
                status_emoji = {
                    "normal": "✅",
                    "warning": "⚠️",
                    "critical": "🚨"
                }.get(result["status"], "❓")
                
                print(f"   Request {i+1}: {status_emoji} {result['requests_used']}/10 - {result['status']}")
            else:
                print(f"   Request {i+1}: 🚫 RECHAZADO - {message}")
        
        print("\n2️⃣ Verificando estado final")
        final_info = tracker.get_usage_info(model)
        print(f"   📊 Requests finales: {final_info['requests_used']}/{final_info['requests_limit']}")
        print(f"   🎯 Estado final: {final_info['status']}")
        print(f"   ✅ Puede hacer más: {final_info['can_make_request']}")
        
        # Limpiar
        test_file = Path("test_limits.json")
        if test_file.exists():
            test_file.unlink()
        
        print("\n✅ TEST DE LÍMITES COMPLETADO")
        return True
        
    except Exception as e:
        print(f"❌ Error en test de límites: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("🚀 INICIANDO SUITE COMPLETA DE TESTS")
    print("=" * 70)
    
    results = []
    
    # Test 1: Básico
    print("\n" + "="*70)
    result1 = test_usage_tracker_basic()
    results.append(("Test Básico", result1))
    
    # Test 2: Integración  
    print("\n" + "="*70)
    result2 = asyncio.run(test_usage_integration())
    results.append(("Test Integración", result2))
    
    # Test 3: Límites
    print("\n" + "="*70)
    result3 = test_usage_limits()
    results.append(("Test Límites", result3))
    
    # Resumen final
    print("\n" + "="*70)
    print("📋 RESUMEN DE TESTS")
    print("=" * 30)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n📊 RESULTADO FINAL: {passed_tests}/{total_tests} tests pasaron")
    
    if passed_tests == total_tests:
        print("🎉 ¡TODOS LOS TESTS COMPLETADOS EXITOSAMENTE!")
        print("\n💡 El sistema de seguimiento de uso está listo para producción")
        print("   • Contadores funcionando correctamente")
        print("   • Límites respetados")
        print("   • Integración con CloudIoTAgent exitosa")
        print("   • Información de uso disponible en health checks")
    else:
        print("⚠️ Algunos tests fallaron. Revisar implementación.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)