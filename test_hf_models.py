#!/usr/bin/env python3
"""
Test HuggingFace Models - Probar qué modelos funcionan sin configuración web
============================================================================
"""

import os
import requests
import asyncio
from typing import List, Dict, Any

# Configurar token
HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

if not HF_TOKEN:
    print("❌ ERROR: HUGGINGFACE_API_TOKEN no configurado")
    exit(1)

# Modelos a probar (que NO requieren aceptación web)
MODELS_TO_TEST = [
    "microsoft/DialoGPT-medium",
    "microsoft/DialoGPT-small", 
    "facebook/blenderbot-400M-distill",
    "google/flan-t5-small",
    "google/flan-t5-base",
    "t5-small",
    "distilbert-base-uncased",
    "microsoft/GODEL-v1_1-base-seq2seq"
]

async def test_model(model_name: str) -> Dict[str, Any]:
    """Probar un modelo específico."""
    print(f"🧪 Probando: {model_name}")
    
    url = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Payload simple para test
    payload = {
        "inputs": "Hello, this is a test.",
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0.7
        }
    }
    
    try:
        response = await asyncio.to_thread(
            requests.post,
            url,
            headers=headers,
            json=payload,
            timeout=15
        )
        
        result = {
            "model": model_name,
            "status_code": response.status_code,
            "success": response.status_code == 200
        }
        
        if response.status_code == 200:
            result["response"] = response.json()
            print(f"   ✅ SUCCESS - {model_name}")
        else:
            result["error"] = response.text
            print(f"   ❌ FAIL - {model_name}: {response.status_code}")
            
        return result
        
    except Exception as e:
        print(f"   💥 ERROR - {model_name}: {e}")
        return {
            "model": model_name,
            "success": False,
            "error": str(e)
        }

async def main():
    """Función principal de testing."""
    print("🔍 TESTING HUGGINGFACE MODELS")
    print("=" * 60)
    print(f"🔑 Token configurado: {HF_TOKEN[:10]}..." if HF_TOKEN else "❌ Sin token")
    print()
    
    results = []
    
    for model in MODELS_TO_TEST:
        result = await test_model(model)
        results.append(result)
        await asyncio.sleep(1)  # Evitar rate limiting
        print()
    
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    working_models = []
    failing_models = []
    
    for result in results:
        if result.get("success"):
            working_models.append(result["model"])
            print(f"✅ {result['model']}")
        else:
            failing_models.append(result["model"])
            error = result.get("error", "Unknown error")
            print(f"❌ {result['model']}: {error[:50]}...")
    
    print(f"\n🎯 MODELOS QUE FUNCIONAN ({len(working_models)}):")
    for model in working_models:
        print(f"   • {model}")
    
    print(f"\n⚠️  MODELOS QUE FALLAN ({len(failing_models)}):")
    for model in failing_models:
        print(f"   • {model}")
    
    if working_models:
        print(f"\n🚀 RECOMENDACIÓN: Usar {working_models[0]}")
        return working_models[0]
    else:
        print(f"\n❌ Ningún modelo funcionó - revisa configuración del token")
        return None

if __name__ == "__main__":
    asyncio.run(main())
