"""
Tests de Sistema del Agente IoT
==============================

Tests de integración para probar las funcionalidades completas del agente IoT.
"""

import asyncio
import sys
from pathlib import Path
import pytest

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from modules.utils.config import Config
from modules.utils.logger import setup_logger
from modules.database import get_db

logger = setup_logger(__name__)


@pytest.mark.integration
@pytest.mark.slow
async def test_basic_functionality():
    """
    Prueba las funcionalidades básicas del sistema.
    """
    print("🚀 Iniciando pruebas del sistema...")
    
    # Verificar configuración
    print("\n1. ✅ Verificando configuración...")
    if not Config.validate():
        print("❌ Error: Configuración incompleta")
        return False
    print("✅ Configuración válida")
    
    # Probar conexión a DB
    print("\n2. 🔗 Probando conexión a la base de datos...")
    try:
        db = await get_db()
        health = await db.health_check()
        if health:
            print("✅ Conexión a DB exitosa")
        else:
            print("❌ Error en health check de DB")
            return False
    except Exception as e:
        print(f"❌ Error conectando a DB: {e}")
        return False
    
    # Probar herramientas de DB
    print("\n3. 🛠️ Probando herramientas de base de datos...")
    try:
        from modules.tools.database_tools import DatabaseTools
        
        db_tools = DatabaseTools()
        
        # Obtener dispositivos
        devices = await db_tools.get_devices_tool()
        print(f"✅ Dispositivos encontrados: {len(devices)}")
        
        # Obtener datos de sensores
        sensor_data = await db_tools.get_sensor_data_tool(limit=5)
        print(f"✅ Datos de sensores: {len(sensor_data)}")
        
        # Obtener alertas
        alerts = await db_tools.get_alerts_tool()
        print(f"✅ Alertas encontradas: {len(alerts)}")
        
    except Exception as e:
        print(f"❌ Error probando herramientas DB: {e}")
        return False
    
    # Probar herramientas de análisis
    print("\n4. 📊 Probando herramientas de análisis...")
    try:
        from modules.tools.analysis_tools import AnalysisTools
        
        analysis_tools = AnalysisTools()
        
        if sensor_data:
            # Analizar tendencias
            trends = analysis_tools.analyze_sensor_trends(sensor_data)
            print(f"✅ Análisis de tendencias completado")
            
            # Detectar anomalías
            anomalies = analysis_tools.detect_anomalies(sensor_data)
            print(f"✅ Anomalías detectadas: {len(anomalies)}")
            
            # Generar reporte
            report = analysis_tools.generate_summary_report(sensor_data, alerts)
            print(f"✅ Reporte generado")
        else:
            print("⚠️ No hay datos de sensores para analizar")
    
    except Exception as e:
        print(f"❌ Error probando análisis: {e}")
        return False
    
    # Probar agente principal
    print("\n5. 🤖 Probando agente conversacional...")
    try:
        from modules.agents.iot_agent import IoTAgent
        
        agent = IoTAgent()
        
        # Probar algunas consultas
        test_queries = [
            "¿Cuántos dispositivos hay activos?",
            "¿Hay alertas en el sistema?",
            "¿Cuál es el estado de los sensores?"
        ]
        
        for query in test_queries:
            print(f"\n   🔹 Pregunta: {query}")
            try:
                response = await agent.process_message(query)
                print(f"   ✅ Respuesta generada: {len(response)} caracteres")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Error probando agente: {e}")
        return False
    
    print("\n🎉 ¡Todas las pruebas completadas exitosamente!")
    return True


@pytest.mark.integration
@pytest.mark.agent
async def test_demo_conversation():
    """
    Demostración de una conversación con el agente.
    """
    print("\n" + "="*60)
    print("🎬 DEMOSTRACIÓN DEL AGENTE CONVERSACIONAL IoT")
    print("="*60)
    
    try:
        from modules.agents.iot_agent import IoTAgent
        
        agent = IoTAgent()
        
        demo_queries = [
            "Hola, ¿puedes ayudarme con el sistema IoT?",
            "¿Cuántos dispositivos tenemos en total?",
            "¿Hay alguna alerta activa que deba revisar?",
            "Muéstrame los datos más recientes de temperatura",
            "¿Has detectado alguna anomalía en los sensores?",
            "Genera un reporte del estado actual del sistema"
        ]
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n{i}. 👤 Usuario: {query}")
            print("   🤖 Agente: ", end="", flush=True)
            
            try:
                response = await agent.process_message(query)
                # Mostrar respuesta línea por línea para efecto dramático
                for line in response.split('\n'):
                    if line.strip():
                        print(f"\n              {line.strip()}")
                        await asyncio.sleep(0.1)  # Pausa para efecto
            except Exception as e:
                print(f"Error: {e}")
            
            print("\n" + "-"*60)
            await asyncio.sleep(1)  # Pausa entre preguntas
        
        print("\n🎉 ¡Demostración completada!")
        
    except Exception as e:
        print(f"❌ Error en la demostración: {e}")


def print_system_info():
    """
    Muestra información del sistema.
    """
    print("📋 INFORMACIÓN DEL SISTEMA")
    print("-" * 40)
    print(f"Aplicación: {Config.APP_NAME}")
    print(f"Versión: {Config.APP_VERSION}")
    print(f"Base de Datos: {Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
    print(f"Usuario DB: {Config.DB_USER}")
    print(f"Modelo OpenAI: {Config.OPENAI_MODEL}")
    print(f"Nivel de Log: {Config.LOG_LEVEL}")
    print(f"Puerto Streamlit: {Config.STREAMLIT_PORT}")


async def main():
    """
    Función principal del script de prueba.
    """
    print("🧪 SCRIPT DE PRUEBA DEL AGENTE IOT")
    print("=" * 50)
    
    print_system_info()
    
    print("\n¿Qué te gustaría hacer?")
    print("1. 🔧 Ejecutar pruebas básicas")
    print("2. 🎬 Ver demostración conversacional")
    print("3. 🔄 Ejecutar ambas")
    print("4. ❌ Salir")
    
    try:
        choice = input("\nSelecciona una opción (1-4): ").strip()
        
        if choice == "1":
            await test_basic_functionality()
        elif choice == "2":
            await test_demo_conversation()
        elif choice == "3":
            success = await test_basic_functionality()
            if success:
                await test_demo_conversation()
        elif choice == "4":
            print("👋 ¡Hasta luego!")
        else:
            print("❌ Opción inválida")
    
    except KeyboardInterrupt:
        print("\n\n👋 Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")


if __name__ == "__main__":
    asyncio.run(main())
