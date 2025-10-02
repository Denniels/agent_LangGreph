#!/usr/bin/env python3
"""
Test final simple del agente
"""
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.agents.cloud_iot_agent import CloudIoTAgent

async def test_final():
    """Test final simple"""
    print("=== TEST FINAL - AGENTE CORREGIDO ===")
    
    agent = CloudIoTAgent()
    await agent.initialize()
    
    query = "¿Qué dispositivos están conectados y qué datos tienen?"
    result = await agent.process_query(query)
    
    print(f"Consulta: {query}")
    print(f"Respuesta: {result}")
    
    if "esp32" in str(result).lower() or "arduino" in str(result).lower():
        print("\n✅ ÉXITO: El agente puede acceder a los datos de la API Jetson")
    else:
        print("\n⚠️ Agente no menciona dispositivos específicos")

if __name__ == "__main__":
    asyncio.run(test_final())