#!/usr/bin/env python3
"""
Test GPT-2 Simple - Probar el modelo más básico
===============================================
"""

import os
import requests
import json

# Token de HuggingFace
HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

def test_gpt2_simple():
    """Probar GPT-2 con configuración mínima."""
    print("🧪 PROBANDO GPT-2 BÁSICO")
    print("=" * 30)
    
    if not HF_TOKEN:
        print("❌ Token no configurado")
        return False
    
    print(f"🔑 Token: {HF_TOKEN[:10]}...")
    
    # URL de GPT-2
    url = "https://api-inference.huggingface.co/models/gpt2"
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }
    
    # Payload ultra-simple
    payload = {
        "inputs": "Temperature is"
    }
    
    try:
        print("📡 Enviando request...")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"📄 Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error Response: {response.text}")
            
            # Verificar si es problema de billing
            if "billing" in response.text.lower() or "payment" in response.text.lower():
                print("\n💳 BILLING REQUERIDO:")
                print("   Ve a: https://huggingface.co/settings/billing")
                print("   Añade una tarjeta de crédito (no se cobrará para uso básico)")
            
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

def test_alternative_endpoint():
    """Probar endpoint alternativo."""
    print("\n🔄 PROBANDO ENDPOINT ALTERNATIVO")
    print("=" * 35)
    
    # URL alternativa
    url = "https://api-inference.huggingface.co/models/openai-gpt"
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }
    
    payload = {
        "inputs": "Hello world"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Endpoint alternativo funciona!")
            return True
        else:
            print(f"❌ También falló: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

if __name__ == "__main__":
    success1 = test_gpt2_simple()
    success2 = test_alternative_endpoint()
    
    print("\n📋 RESUMEN:")
    if success1 or success2:
        print("🎉 ¡Al menos un endpoint funciona!")
    else:
        print("❌ Necesitas configurar billing en HuggingFace")
        print("🔗 https://huggingface.co/settings/billing")
