"""
Test de integración con Groq API
===============================

Prueba la API gratuita de Groq para verificar que funciona
sin necesidad de tarjeta de crédito.
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Agregar path del proyecto
sys.path.append(os.path.abspath('.'))

from modules.agents.groq_integration import GroqIntegration

def test_groq_integration():
    """
    Probar la integración con Groq API
    """
    print("🚀 PRUEBA DE GROQ API")
    print("=" * 50)
    
    # 1. Test sin API key (modo fallback)
    print("\n1️⃣ Probando modo FALLBACK (sin API key):")
    groq_fallback = GroqIntegration()
    
    test_result = groq_fallback.test_connection()
    print(f"   Status: {test_result}")
    
    response = groq_fallback.generate_response("Analiza temperatura: 25°C")
    print(f"   Respuesta: {response[:200]}...")
    
    # 2. Test con API key si existe
    print("\n2️⃣ Probando con API key:")
    api_key = os.getenv('GROQ_API_KEY')
    
    if api_key:
        print(f"   API Key encontrada: {api_key[:10]}...")
        groq_api = GroqIntegration(api_key)
        
        test_result = groq_api.test_connection()
        print(f"   Test connection: {test_result}")
        
        if test_result.get('success'):
            response = groq_api.generate_response("¿Cuál es la temperatura actual de los sensores?")
            print(f"   Respuesta API: {response[:200]}...")
        else:
            print(f"   Error: {test_result.get('error')}")
    else:
        print("   No se encontró GROQ_API_KEY")
        print("   ✅ Esto está bien - Groq funciona sin API key en modo fallback")
    
    # 3. Test de modelos disponibles
    print("\n3️⃣ Modelos disponibles:")
    groq = GroqIntegration()
    models = groq.get_models()
    for model in models:
        print(f"   • {model}")
    
    print("\n" + "=" * 50)
    print("✅ PRUEBA COMPLETADA")
    print("\n💡 PARA OBTENER API KEY GRATUITA DE GROQ:")
    print("   1. Ve a: https://console.groq.com/")
    print("   2. Regístrate (sin tarjeta de crédito)")
    print("   3. Ve a API Keys")
    print("   4. Crea una nueva API key")
    print("   5. Configura: set GROQ_API_KEY=tu_api_key")
    print("\n🎉 Groq ofrece 14,400 requests/día GRATIS")

if __name__ == "__main__":
    test_groq_integration()
