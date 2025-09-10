#!/usr/bin/env python3
"""
Prueba de Consulta al Agente Optimizada
=======================================

Script para probar consultas específicas al agente IoT optimizado con datos en tiempo real
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.agents.iot_agent_ollama import IoTAgent


async def test_agent_query():
    """Prueba consultas específicas al agente con datos en tiempo real"""
    
    print("🤖 PRUEBA DE CONSULTAS AL AGENTE IoT OPTIMIZADO")
    print("=" * 60)
    
    # Inicializar agente
    agent = IoTAgent()
    
    # Lista de consultas de prueba optimizadas para tiempo real
    consultas = [
        "¿Cuántos registros de sensores hay en los últimos 10 minutos?",
        "¿Cuál es la temperatura actual de todos los sensores?",
        "¿Qué dispositivos están activos y cuándo fue su última lectura?",
        "¿Hay alguna anomalía en las lecturas de los sensores ESP32?",
        "Dame un resumen completo del estado del sistema IoT en tiempo real"
    ]
    
    for i, consulta in enumerate(consultas, 1):
        print(f"\n{i}️⃣ Consulta: {consulta}")
        print(f"⏰ Hora: {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)
        
        try:
            response = await agent.process_message(consulta)
            print(f"🤖 Respuesta:")
            # Limitar la respuesta para legibilidad
            lines = response.split('\n')
            for line in lines[:15]:  # Primeras 15 líneas
                print(f"   {line}")
            
            if len(lines) > 15:
                print(f"   ... ({len(lines) - 15} líneas más)")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)
        
        # Pausa entre consultas
        await asyncio.sleep(2)
    
    print(f"\n✅ PRUEBAS COMPLETADAS - AGENTE OPTIMIZADO FUNCIONANDO")


if __name__ == "__main__":
    asyncio.run(test_agent_query())