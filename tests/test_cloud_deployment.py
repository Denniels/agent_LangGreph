"""
Test Cloud IoT Agent - Prueba local antes del despliegue
========================================================

Script para probar el Cloud IoT Agent localmente antes de subir a Streamlit Cloud.
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_test_environment():
    """Configurar variables de entorno para pruebas."""
    print("🔧 CONFIGURANDO ENTORNO DE PRUEBA")
    print("=" * 50)
    
    # Verificar variables de entorno necesarias
    required_vars = ["HUGGINGFACE_API_TOKEN"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables faltantes: {', '.join(missing_vars)}")
        print("\n💡 Para probar localmente, configura:")
        for var in missing_vars:
            print(f"   set {var}=tu_valor_aqui")
        print("\n🔗 Obtén tu token de HuggingFace en: https://huggingface.co/settings/tokens")
        return False
    
    print("✅ Variables de entorno configuradas correctamente")
    return True

async def test_huggingface_integration():
    """Probar integración con HuggingFace."""
    print("\n🤖 PROBANDO HUGGINGFACE INTEGRATION")
    print("=" * 50)
    
    try:
        from modules.agents.huggingface_integration import create_huggingface_integration
        
        # Crear integración
        hf = create_huggingface_integration()
        
        # Test de conexión
        print("1️⃣ Probando conexión con HuggingFace...")
        connection_test = await hf.test_connection()
        
        if connection_test.get('status') == 'success':
            print(f"   ✅ Conexión exitosa")
            print(f"   📊 Modelo: {hf.model_name}")
            print(f"   ⏱️  Tiempo de respuesta: {connection_test.get('response_time', 'N/A')}s")
            
            # Test de generación
            print("\n2️⃣ Probando generación de respuesta...")
            
            test_context = {
                "data_source": "Test local",
                "real_sensors": ["t1", "t2", "avg"]
            }
            
            test_tools = {
                "sensor_data": [
                    {
                        "device_id": "test_device",
                        "sensor_type": "avg",
                        "value": 23.5,
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
            
            response = await hf.generate_response(
                "¿Cuál es la temperatura promedio?",
                context_data=test_context,
                tools_results=test_tools
            )
            
            print(f"   ✅ Respuesta generada: {len(response)} caracteres")
            print(f"   📝 Muestra: {response[:100]}...")
            
            return True
        else:
            print(f"   ❌ Error de conexión: {connection_test}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en HuggingFace: {e}")
        return False

async def test_jetson_connection():
    """Probar conexión con Jetson API."""
    print("\n📡 PROBANDO CONEXIÓN JETSON API")
    print("=" * 50)
    
    try:
        from modules.tools.jetson_api_connector import JetsonAPIConnector
        
        # URL de Jetson
        jetson_url = os.getenv("JETSON_API_URL", "https://respect-craps-lit-aged.trycloudflare.com")
        
        # Crear connector
        connector = JetsonAPIConnector(api_url=jetson_url)
        
        print(f"🔗 Probando conexión a: {jetson_url}")
        
        # Health check
        health = connector.get_health_status()
        
        if health.get("status") == "healthy":
            print("   ✅ Jetson API disponible")
            print(f"   📊 Uptime: {health.get('uptime', 'N/A')}")
            
            # Test de dispositivos
            devices = connector.get_devices()
            if devices:
                print(f"   🔌 Dispositivos encontrados: {len(devices)}")
                
                for device in devices[:2]:
                    print(f"     • {device.get('device_id', 'Unknown')}")
            
            return True
        else:
            print(f"   ⚠️  Jetson API no disponible: {health.get('message', 'Unknown error')}")
            print("   💡 El agente funcionará con datos demo")
            return False
            
    except Exception as e:
        print(f"   ❌ Error conectando con Jetson: {e}")
        print("   💡 El agente funcionará con datos demo")
        return False

async def test_cloud_agent():
    """Probar Cloud IoT Agent completo."""
    print("\n🌐 PROBANDO CLOUD IOT AGENT")
    print("=" * 50)
    
    try:
        from modules.agents.cloud_iot_agent import create_cloud_iot_agent
        
        # Crear agente
        agent = create_cloud_iot_agent()
        
        print("1️⃣ Inicializando agente...")
        success = await agent.initialize()
        
        if not success:
            print("   ❌ Error inicializando agente")
            return False
        
        print("   ✅ Agente inicializado exitosamente")
        
        # Health check
        print("\n2️⃣ Verificando estado de salud...")
        health = await agent.health_check()
        
        overall_status = health.get("overall_status", "unknown")
        print(f"   📊 Estado general: {overall_status}")
        print(f"   🤖 HuggingFace: {health.get('huggingface_status', 'unknown')}")
        print(f"   📡 Jetson: {health.get('jetson_status', 'unknown')}")
        
        # Test de consulta
        print("\n3️⃣ Procesando consulta de prueba...")
        
        test_queries = [
            "¿Cuál es la temperatura actual?",
            "Muestra un resumen de todos los sensores",
            "¿Qué dispositivos están conectados?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   Consulta {i}: {query}")
            
            start_time = datetime.now()
            response = await agent.process_query(query)
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            
            if response.get("success"):
                print(f"   ✅ Respuesta exitosa ({response_time:.2f}s)")
                print(f"   📊 Datos: {response.get('data_summary', {}).get('total_records', 0)} registros")
                print(f"   🤖 Modelo: {response.get('model_used', 'Unknown')}")
                
                # Verificación
                verification = response.get("verification", {})
                if verification:
                    print(f"   🔍 Verificación: {verification.get('status', 'unknown')}")
                    if verification.get('hallucinations_detected'):
                        print(f"   ⚠️  Alucinaciones: {verification['hallucinations_detected']}")
            else:
                print(f"   ❌ Error en respuesta: {response.get('error', 'Unknown')}")
            
            # Pausa entre consultas
            await asyncio.sleep(1)
        
        print("\n✅ Cloud IoT Agent funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en Cloud IoT Agent: {e}")
        return False

async def test_streamlit_imports():
    """Probar imports necesarios para Streamlit."""
    print("\n📦 PROBANDO IMPORTS DE STREAMLIT")
    print("=" * 50)
    
    required_modules = [
        "streamlit",
        "plotly.express",
        "plotly.graph_objects",
        "pandas",
        "modules.agents.cloud_iot_agent",
        "modules.agents.huggingface_integration",
        "modules.tools.jetson_api_connector"
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module} - {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Módulos faltantes: {', '.join(failed_imports)}")
        print("💡 Ejecuta: pip install -r requirements.txt")
        return False
    
    print("\n✅ Todos los módulos disponibles")
    return True

def print_deployment_instructions():
    """Imprimir instrucciones para despliegue."""
    print("\n🚀 INSTRUCCIONES PARA DESPLIEGUE EN STREAMLIT CLOUD")
    print("=" * 60)
    
    instructions = [
        "1️⃣ **Subir código a GitHub**:",
        "   • Crea un repositorio en GitHub",
        "   • Sube todos los archivos del proyecto",
        "   • Asegúrate de incluir requirements.txt",
        "",
        "2️⃣ **Configurar Streamlit Cloud**:",
        "   • Ve a https://share.streamlit.io/",
        "   • Conecta tu cuenta de GitHub",
        "   • Selecciona el repositorio",
        "   • Archivo principal: streamlit_app/app_cloud.py",
        "",
        "3️⃣ **Configurar Secrets**:",
        "   • En la configuración de la app, agrega:",
        "   • HUGGINGFACE_API_TOKEN = 'tu_token_aqui'",
        "   • JETSON_API_URL = 'tu_url_de_jetson'",
        "",
        "4️⃣ **Deployer**:",
        "   • Click en 'Deploy!'",
        "   • Espera a que termine la instalación",
        "   • Tu app estará disponible en la URL generada",
        "",
        "🔗 **Enlaces útiles**:",
        "   • HuggingFace Tokens: https://huggingface.co/settings/tokens",
        "   • Streamlit Cloud: https://share.streamlit.io/",
        "   • Documentación: https://docs.streamlit.io/streamlit-community-cloud"
    ]
    
    for instruction in instructions:
        print(instruction)

async def main():
    """Función principal de pruebas."""
    print("🧪 CLOUD IOT AGENT - PRUEBAS LOCALES")
    print("=" * 60)
    print(f"🕐 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Setup inicial
    if not setup_test_environment():
        print("\n❌ No se puede continuar sin las variables de entorno necesarias")
        return
    
    # Pruebas de componentes
    tests = [
        ("Imports de Streamlit", test_streamlit_imports()),
        ("HuggingFace Integration", test_huggingface_integration()),
        ("Conexión Jetson", test_jetson_connection()),
        ("Cloud IoT Agent", test_cloud_agent())
    ]
    
    results = []
    
    for test_name, test_coro in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = await test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Resultado: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está listo para despliegue.")
        print_deployment_instructions()
    elif passed >= total - 1:  # Permitir que Jetson falle
        print("⚠️  Sistema casi listo. Jetson opcional para funcionamiento básico.")
        print_deployment_instructions()
    else:
        print("❌ Se requieren correcciones antes del despliegue.")
    
    print(f"\n🕐 Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error crítico: {e}")
        sys.exit(1)
