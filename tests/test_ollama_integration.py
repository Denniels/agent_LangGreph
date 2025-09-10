#!/usr/bin/env python3
"""
Test de conexión con Ollama y el agente IoT
==========================================

Script para probar que Ollama funciona correctamente con nuestro agente.
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.agents.ollama_integration import OllamaLLMIntegration
from modules.agents.iot_agent_ollama import IoTAgent
from modules.utils.logger import logger


async def test_ollama_connection():
    """Prueba la conexión básica con Ollama."""
    print("🔍 Probando conexión con Ollama...")
    
    try:
        # Inicializar integración
        ollama_llm = OllamaLLMIntegration()
        
        # Probar conexión
        is_connected = await ollama_llm.test_connection()
        
        if is_connected:
            print("✅ Conexión con Ollama exitosa")
            
            # Probar generación de respuesta simple
            print("\n🤖 Probando generación de respuesta...")
            response = await ollama_llm.generate_response(
                "¡Hola! ¿Puedes confirmar que estás funcionando correctamente?"
            )
            
            print(f"📝 Respuesta de Ollama: {response[:200]}...")
            return True
        else:
            print("❌ Error al conectar con Ollama")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de Ollama: {e}")
        return False


async def test_iot_agent():
    """Prueba el agente IoT completo."""
    print("\n🤖 Probando agente IoT completo...")
    
    try:
        # Inicializar agente
        agent = IoTAgent()
        
        # Probar salud del sistema
        print("🔧 Verificando salud del sistema...")
        health_report = await agent.test_system_health()
        
        print(f"📊 Estado general: {health_report['overall_status']}")
        
        if "components" in health_report:
            for component, status in health_report["components"].items():
                status_icon = "✅" if status["status"] == "healthy" else "❌"
                print(f"   {status_icon} {component}: {status['status']}")
                
                if "error" in status:
                    print(f"      ⚠️ Error: {status['error']}")
        
        # Probar consulta real
        print("\n💬 Probando consulta real...")
        test_query = "¿Cuál es el estado actual de los sensores de temperatura?"
        
        response = await agent.process_message(test_query)
        print(f"📝 Consulta: {test_query}")
        print(f"🤖 Respuesta: {response[:300]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba del agente: {e}")
        return False


async def test_database_integration():
    """Prueba la integración con la base de datos."""
    print("\n🗄️ Probando integración con base de datos...")
    
    try:
        from modules.tools.database_tools import DatabaseTools
        
        db_tools = DatabaseTools()
        
        # Probar obtención de datos
        print("📊 Obteniendo datos de sensores...")
        sensor_data = await db_tools.get_sensor_data_tool(limit=5)
        print(f"✅ Obtenidos {len(sensor_data)} registros de sensores")
        
        # Probar dispositivos
        print("📱 Obteniendo dispositivos...")
        devices = await db_tools.get_devices_tool()
        print(f"✅ Encontrados {len(devices)} dispositivos")
        
        # Probar alertas
        print("🚨 Obteniendo alertas...")
        alerts = await db_tools.get_alerts_tool()
        print(f"✅ Encontradas {len(alerts)} alertas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de base de datos: {e}")
        return False


async def run_comprehensive_test():
    """Ejecuta una prueba completa del sistema."""
    print("🚀 Iniciando prueba completa del sistema IoT con Ollama")
    print("=" * 60)
    
    # Prueba 1: Conexión Ollama
    ollama_ok = await test_ollama_connection()
    
    # Prueba 2: Base de datos
    db_ok = await test_database_integration()
    
    # Prueba 3: Agente completo
    agent_ok = await test_iot_agent()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"🤖 Ollama: {'✅ OK' if ollama_ok else '❌ FALLO'}")
    print(f"🗄️ Base de datos: {'✅ OK' if db_ok else '❌ FALLO'}")
    print(f"🤖 Agente IoT: {'✅ OK' if agent_ok else '❌ FALLO'}")
    
    if all([ollama_ok, db_ok, agent_ok]):
        print("\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("✅ Listo para usar la interfaz Streamlit")
        return True
    else:
        print("\n⚠️ Algunos componentes tienen problemas")
        print("🔧 Revisa los errores anteriores para diagnosticar")
        return False


if __name__ == "__main__":
    # Ejecutar prueba completa
    success = asyncio.run(run_comprehensive_test())
    
    if success:
        print("\n🚀 Para usar la interfaz web, ejecuta:")
        print("   streamlit run streamlit_app/app_ollama.py")
    else:
        print("\n🛠️ Soluciona los problemas antes de continuar")
    
    sys.exit(0 if success else 1)
