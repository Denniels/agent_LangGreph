#!/usr/bin/env python3
"""
Test del Agente IoT con Streamlit MEJORADO
=========================================

Prueba específica para verificar que el agente funciona correctamente
en el entorno de Streamlit con las mejoras de event loop.
"""

import asyncio
import sys
from pathlib import Path
import concurrent.futures
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.agents.iot_agent_ollama import IoTAgent


def test_streamlit_safe_execution():
    """Simula exactamente cómo Streamlit ejecuta el agente"""
    
    print("🔬 TEST DE EJECUCIÓN SEGURA PARA STREAMLIT")
    print("=" * 60)
    
    def create_and_test_agent():
        """Crea y prueba el agente en un thread separado"""
        async def run_test():
            # Crear agente
            agent = IoTAgent()
            print("✅ Agente creado exitosamente")
            
            # Probar consulta
            query = "¿Cuál es el estado actual de los sensores?"
            print(f"🔍 Probando consulta: {query}")
            
            response = await agent.process_message(query)
            return response
        
        # Ejecutar en nuevo event loop
        return asyncio.run(run_test())
    
    print("\n1️⃣ Prueba con ThreadPoolExecutor (como Streamlit mejorado)...")
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(create_and_test_agent)
            response = future.result(timeout=30)
            
        print("✅ ThreadPoolExecutor funcionó correctamente")
        print(f"📝 Respuesta recibida: {len(response)} caracteres")
        
        # Verificar que la respuesta contiene datos
        if "sensores" in response.lower() and len(response) > 100:
            print("✅ Respuesta contiene datos de sensores")
        else:
            print("⚠️ Respuesta parece estar vacía o genérica")
            
    except Exception as e:
        print(f"❌ Error en ThreadPoolExecutor: {e}")
    
    print("\n2️⃣ Prueba directa (para comparación)...")
    try:
        async def direct_test():
            agent = IoTAgent()
            return await agent.process_message("¿Cuántos dispositivos están activos?")
        
        response = asyncio.run(direct_test())
        print("✅ Ejecución directa funcionó")
        print(f"📝 Respuesta recibida: {len(response)} caracteres")
        
    except Exception as e:
        print(f"❌ Error en ejecución directa: {e}")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETADO")


if __name__ == "__main__":
    test_streamlit_safe_execution()
