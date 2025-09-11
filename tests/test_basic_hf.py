#!/usr/bin/env python3
"""
Test Basic HuggingFace Models - Modelos básicos que deberían funcionar
=====================================================================
"""

import os
import requests
import asyncio

# Token de HuggingFace
HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

# Modelos más básicos que suelen estar disponibles
BASIC_MODELS = [
    "gpt2",
    "distilgpt2", 
    "microsoft/DialoGPT-small",
    "facebook/blenderbot_small-90M"
]

async def test_basic_model(model_name: str):
    """Probar modelo básico."""
    print(f"🧪 Probando modelo básico: {model_name}")
    
    url = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Payload ultra-simple
    payload = {
        "inputs": "Temperature sensors show:"
    }
    
    try:
        response = await asyncio.to_thread(
            requests.post,
            url,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ SUCCESS: {result}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   💥 Exception: {e}")
        return False

async def main():
    print("🔧 TESTING BASIC HUGGINGFACE MODELS")
    print("=" * 50)
    
    if not HF_TOKEN:
        print("❌ Token no configurado")
        return
    
    print(f"🔑 Token: {HF_TOKEN[:10]}...")
    print()
    
    working_models = []
    
    for model in BASIC_MODELS:
        success = await test_basic_model(model)
        if success:
            working_models.append(model)
        print()
        await asyncio.sleep(1)
    
    print("📊 RESULTADOS:")
    print(f"   Modelos funcionando: {working_models}")
    
    if working_models:
        print(f"🚀 Usar: {working_models[0]}")
    else:
        print("❌ Necesitas configurar billing en HuggingFace")
        print("   Ve a: https://huggingface.co/settings/billing")

if __name__ == "__main__":
    asyncio.run(main())
