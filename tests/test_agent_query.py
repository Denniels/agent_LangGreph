#!/usr/bin/env python3
"""
Test específico del agente con consulta real
============================================

Simula exactamente lo que hace el agente cuando le preguntamos por sensores
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.agents.iot_agent_ollama import IoTAgent


async def test_agent_query():
    """Prueba específica de la consulta del agente"""
    
    print("🤖 TEST: Consulta real del agente IoT")
    print("=" * 50)
    
    # Inicializar el agente
    print("\n1️⃣ Inicializando agente...")
    agent = IoTAgent()
    
    # Hacer la consulta específica sobre sensores
    print("\n2️⃣ Consultando estado de sensores...")
    query = "¿Cuál es el estado actual de los sensores?"
    
    print(f"💬 Pregunta: {query}")
    print("\n🔄 Procesando...")
    
    response = await agent.process_message(query)
    
    print(f"\n🤖 Respuesta del agente:")
    print("-" * 40)
    print(response)
    print("-" * 40)
    
    # También probar consulta específica
    print("\n3️⃣ Consultando sensores de temperatura específicamente...")
    temp_query = "Muéstrame los sensores de temperatura activos"
    
    print(f"💬 Pregunta: {temp_query}")
    print("\n🔄 Procesando...")
    
    temp_response = await agent.process_message(temp_query)
    
    print(f"\n🤖 Respuesta del agente:")
    print("-" * 40)
    print(temp_response)
    print("-" * 40)
    
    print("\n✅ TEST COMPLETADO")


if __name__ == "__main__":
    asyncio.run(test_agent_query())
