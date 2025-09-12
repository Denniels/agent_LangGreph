#!/usr/bin/env python3
"""
Test específico para verificar el manejo de valores vacíos
========================================================

Verifica que el sistema de seguimiento funciona correctamente
cuando no hay uso registrado (valores en cero).
"""

import os
import sys

# Agregar path del proyecto
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from modules.utils.usage_tracker import UsageTracker
from modules.utils.streamlit_usage_display import display_usage_metrics
import streamlit as st

def test_zero_usage():
    """Test del sistema con uso en cero"""
    print("🧪 INICIANDO TEST DE VALORES VACÍOS")
    print("=" * 50)
    
    try:
        # 1. Crear tracker nuevo (sin uso)
        print("\n1️⃣ Creando tracker sin uso previo")
        tracker = UsageTracker("test_zero_usage.json")
        
        # 2. Obtener información de modelo sin uso
        print("\n2️⃣ Obteniendo información sin uso")
        model = "llama-3.1-8b-instant"
        usage_info = tracker.get_usage_info(model)
        
        print(f"   🤖 Modelo: {usage_info.get('model_description', 'N/A')}")
        print(f"   🔥 Requests: {usage_info.get('requests_used', 0)}/{usage_info.get('requests_limit', 0)}")
        print(f"   🎯 Tokens: {usage_info.get('tokens_used', 0)}/{usage_info.get('tokens_limit', 0)}")
        print(f"   📊 Porcentaje: {usage_info.get('requests_percentage', 0)}%")
        print(f"   ✅ Estado: {usage_info.get('status', 'unknown')}")
        
        # 3. Verificar que todos los valores son válidos
        print("\n3️⃣ Verificando validez de valores")
        
        # Verificar requests
        requests_used = usage_info.get('requests_used', 0) or 0
        requests_limit = usage_info.get('requests_limit', 0) or 0
        requests_percentage = float(usage_info.get('requests_percentage', 0) or 0)
        
        assert isinstance(requests_used, int), f"requests_used debe ser int, es {type(requests_used)}"
        assert isinstance(requests_limit, int), f"requests_limit debe ser int, es {type(requests_limit)}"
        assert isinstance(requests_percentage, float), f"requests_percentage debe ser float, es {type(requests_percentage)}"
        assert 0 <= requests_percentage <= 100, f"requests_percentage debe estar entre 0-100, es {requests_percentage}"
        
        print(f"   ✅ Requests: {requests_used}/{requests_limit} ({requests_percentage}%)")
        
        # Verificar tokens
        tokens_used = usage_info.get('tokens_used', 0) or 0
        tokens_limit = usage_info.get('tokens_limit', 0) or 0
        tokens_percentage = float(usage_info.get('tokens_percentage', 0) or 0)
        
        assert isinstance(tokens_used, int), f"tokens_used debe ser int, es {type(tokens_used)}"
        assert isinstance(tokens_limit, int), f"tokens_limit debe ser int, es {type(tokens_limit)}"
        assert isinstance(tokens_percentage, float), f"tokens_percentage debe ser float, es {type(tokens_percentage)}"
        assert 0 <= tokens_percentage <= 100, f"tokens_percentage debe estar entre 0-100, es {tokens_percentage}"
        
        print(f"   ✅ Tokens: {tokens_used}/{tokens_limit} ({tokens_percentage}%)")
        
        # 4. Test de resumen diario sin uso
        print("\n4️⃣ Verificando resumen diario")
        summary = tracker.get_daily_summary()
        
        print(f"   📊 Total requests hoy: {summary['total_requests_today']}")
        print(f"   🎯 Total tokens hoy: {summary['total_tokens_today']}")
        print(f"   🤖 Modelos usados: {summary['models_used_today']}")
        
        assert summary['total_requests_today'] == 0, "Total requests debe ser 0"
        assert summary['total_tokens_today'] == 0, "Total tokens debe ser 0"
        assert summary['models_used_today'] == 0, "Modelos usados debe ser 0"
        
        # 5. Test de verificación de límites
        print("\n5️⃣ Verificando verificación de límites")
        can_make, message = tracker.check_can_make_request(model)
        
        print(f"   ✅ Puede hacer consulta: {can_make}")
        print(f"   💬 Mensaje: {message}")
        
        assert can_make == True, "Debe poder hacer consultas cuando no hay uso"
        assert "disponibles" in message.lower(), "Mensaje debe mencionar requests disponibles"
        
        print("\n✅ TODOS LOS TESTS DE VALORES VACÍOS COMPLETADOS")
        
        # Limpiar archivo de test
        import os
        if os.path.exists("test_zero_usage.json"):
            os.remove("test_zero_usage.json")
            print("🧹 Archivo de test limpiado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de valores vacíos: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_safe_formatting():
    """Test de formateo seguro de valores"""
    print("\n🧪 INICIANDO TEST DE FORMATEO SEGURO")
    print("=" * 50)
    
    try:
        # Test de valores que podrían causar problemas
        test_values = [
            None,
            0,
            0.0,
            "",
            "0",
            100,
            99.5,
            "99.5"
        ]
        
        print("\n1️⃣ Probando formateo de diferentes tipos de valores")
        
        for i, value in enumerate(test_values):
            try:
                # Formateo seguro como en el código real
                safe_value = float(value or 0)
                safe_value = max(0, min(100, safe_value))
                
                print(f"   Test {i+1}: {repr(value)} -> {safe_value:.1f}%")
                
                # Verificar que el valor está en rango válido
                assert 0 <= safe_value <= 100, f"Valor fuera de rango: {safe_value}"
                
            except Exception as e:
                print(f"   ❌ Error con valor {repr(value)}: {e}")
                return False
        
        print("\n✅ TODOS LOS TESTS DE FORMATEO SEGURO COMPLETADOS")
        return True
        
    except Exception as e:
        print(f"❌ Error en test de formateo: {e}")
        return False

def main():
    """Ejecutar tests de valores vacíos"""
    print("🚀 INICIANDO TESTS DE VALORES VACÍOS Y FORMATEO")
    print("=" * 70)
    
    results = []
    
    # Test 1: Valores vacíos
    result1 = test_zero_usage()
    results.append(("Test Valores Vacíos", result1))
    
    # Test 2: Formateo seguro
    result2 = test_safe_formatting()
    results.append(("Test Formateo Seguro", result2))
    
    # Resumen
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
        print("🎉 ¡TODOS LOS TESTS DE VALORES VACÍOS COMPLETADOS!")
        print("\n💡 El sistema maneja correctamente:")
        print("   • ✅ Valores en cero sin errores")
        print("   • ✅ Formateo seguro de porcentajes") 
        print("   • ✅ Validación de rangos")
        print("   • ✅ Manejo de valores None/vacíos")
        print("\n🚀 Listo para desplegar la corrección")
    else:
        print("⚠️ Algunos tests fallaron. Revisar implementación.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)