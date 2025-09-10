"""
Archivo Principal del Agente Conversacional IoT
===============================================

Punto de entrada principal para ejecutar la aplicación.
"""

import os
import sys
import asyncio
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from modules.utils.config import Config
from modules.utils.logger import setup_logger
from modules.database import get_db

logger = setup_logger(__name__)


async def test_database_connection():
    """
    Prueba la conexión a la base de datos.
    """
    try:
        logger.info("Probando conexión a la base de datos...")
        db = await get_db()
        health_check = await db.health_check()
        
        if health_check:
            logger.info("✅ Conexión a la base de datos exitosa")
            return True
        else:
            logger.error("❌ Fallo en el health check de la base de datos")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error conectando a la base de datos: {e}")
        return False


async def test_agent_functionality():
    """
    Prueba la funcionalidad básica del agente.
    """
    try:
        logger.info("Probando funcionalidad del agente...")
        
        from modules.agents.iot_agent import IoTAgent
        
        agent = IoTAgent()
        response = await agent.process_message("¿Cuál es el estado actual del sistema?")
        
        logger.info("✅ Agente funcionando correctamente")
        logger.info(f"Respuesta de prueba: {response[:100]}...")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error probando el agente: {e}")
        return False


def check_environment():
    """
    Verifica que las variables de entorno estén configuradas correctamente.
    """
    logger.info("Verificando configuración del entorno...")
    
    if Config.validate():
        logger.info("✅ Configuración del entorno válida")
        return True
    else:
        logger.error("❌ Configuración del entorno incompleta")
        logger.info("Asegúrate de que el archivo .env contenga:")
        logger.info("- DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD")
        logger.info("- OPENAI_API_KEY")
        return False


def run_streamlit_app():
    """
    Ejecuta la aplicación Streamlit.
    """
    logger.info("Iniciando aplicación Streamlit...")
    
    # Cambiar al directorio de la aplicación
    streamlit_dir = root_dir / "streamlit_app"
    os.chdir(streamlit_dir)
    
    # Ejecutar Streamlit
    import subprocess
    
    cmd = [
        sys.executable, 
        "-m", "streamlit", "run", "app.py",
        "--server.port", str(Config.STREAMLIT_PORT),
        "--server.address", Config.STREAMLIT_HOST
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error ejecutando Streamlit: {e}")
    except KeyboardInterrupt:
        logger.info("Aplicación detenida por el usuario")


async def run_cli_test():
    """
    Ejecuta una prueba básica desde línea de comandos.
    """
    logger.info("=== Prueba CLI del Agente IoT ===")
    
    from modules.agents.iot_agent import IoTAgent
    
    agent = IoTAgent()
    
    test_queries = [
        "¿Cuántos dispositivos hay en el sistema?",
        "¿Hay alguna alerta activa?",
        "Muéstrame los datos de temperatura más recientes",
        "¿Qué anomalías has detectado?"
    ]
    
    for query in test_queries:
        logger.info(f"\n🤖 Pregunta: {query}")
        try:
            response = await agent.process_message(query)
            logger.info(f"📝 Respuesta: {response}")
        except Exception as e:
            logger.error(f"❌ Error: {e}")
        
        print("-" * 80)


def main():
    """
    Función principal.
    """
    logger.info("🚀 Iniciando Agente Conversacional IoT")
    logger.info(f"Directorio de trabajo: {root_dir}")
    
    # Verificar configuración
    if not check_environment():
        sys.exit(1)
    
    # Menú de opciones
    print("\n" + "="*60)
    print("🤖 AGENTE CONVERSACIONAL IOT")
    print("="*60)
    print("1. 🌐 Ejecutar aplicación Streamlit (recomendado)")
    print("2. 🔧 Probar conexión a base de datos")
    print("3. 🧪 Probar funcionalidad del agente")
    print("4. 💬 Modo CLI de prueba")
    print("5. ❌ Salir")
    print("="*60)
    
    try:
        choice = input("\nSelecciona una opción (1-5): ").strip()
        
        if choice == "1":
            run_streamlit_app()
        
        elif choice == "2":
            result = asyncio.run(test_database_connection())
            if result:
                print("\n✅ Conexión a la base de datos exitosa")
            else:
                print("\n❌ Error de conexión a la base de datos")
        
        elif choice == "3":
            result = asyncio.run(test_agent_functionality())
            if result:
                print("\n✅ Agente funcionando correctamente")
            else:
                print("\n❌ Error en la funcionalidad del agente")
        
        elif choice == "4":
            asyncio.run(run_cli_test())
        
        elif choice == "5":
            logger.info("👋 ¡Hasta luego!")
            sys.exit(0)
        
        else:
            print("❌ Opción inválida")
            
    except KeyboardInterrupt:
        logger.info("\n👋 Aplicación detenida por el usuario")
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()
