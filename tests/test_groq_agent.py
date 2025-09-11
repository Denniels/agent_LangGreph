"""
Test del Cloud IoT Agent con Groq API
=====================================

Prueba completa del agente IoT usando Groq en lugar de HuggingFace.
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar path del proyecto
sys.path.append(os.path.abspath('.'))

from modules.agents.cloud_iot_agent import create_cloud_iot_agent

async def test_groq_agent():
    """
    Probar el agente IoT completo con Groq
    """
    print("🚀 PRUEBA DEL CLOUD IOT AGENT CON GROQ")
    print("=" * 60)
    
    try:
        # 1. Crear agente cloud con Groq
        print("\n1️⃣ Creando Cloud IoT Agent...")
        agent = create_cloud_iot_agent(groq_model="llama-3.1-8b-instant")
        
        # 2. Health check
        print("\n2️⃣ Verificando estado del agente...")
        health = await agent.health_check()
        print(f"   Status general: {health.get('overall_status')}")
        print(f"   Groq status: {health.get('groq_status')}")
        print(f"   Jetson status: {health.get('jetson_status')}")
        
        # 3. Procesar consultas de prueba
        test_queries = [
            "¿Cuál es la temperatura actual de los sensores?",
            "Dame un resumen de todos los datos de sensores",
            "¿Hay algún sensor con valores anormales?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i+2}️⃣ Procesando consulta: '{query}'")
            
            try:
                response = await agent.process_query(query)
                
                if response.get('success'):
                    print(f"   ✅ Success: {response['success']}")
                    print(f"   📊 Datos procesados: {response['data_summary']['total_records']} registros")
                    print(f"   🤖 Modelo usado: {response.get('model_used')}")
                    print(f"   🔍 Status: {response.get('execution_status')}")
                    print(f"   ⚠️ Verificación: {response.get('verification', {}).get('status')}")
                    print(f"   📝 Respuesta: {response['response'][:300]}...")
                else:
                    print(f"   ❌ Error: {response.get('error')}")
                    
            except Exception as e:
                print(f"   ❌ Excepción procesando consulta: {e}")
        
        print(f"\n" + "=" * 60)
        print("✅ PRUEBAS COMPLETADAS")
        print("\n📊 RESUMEN:")
        print(f"   • Groq API: {'✅ Funcionando' if health.get('groq_status') == 'success' else '⚠️ Fallback'}")
        print(f"   • Jetson API: {'✅ Conectado' if health.get('jetson_status') == 'healthy' else '⚠️ Demo'}")
        print(f"   • Agente: {'✅ Operativo' if health.get('overall_status') == 'healthy' else '⚠️ Degradado'}")
        
    except Exception as e:
        print(f"❌ Error en prueba principal: {e}")
        import traceback
        traceback.print_exc()

def check_environment():
    """
    Verificar configuración del entorno
    """
    print("🔧 VERIFICANDO ENTORNO")
    print("=" * 30)
    
    groq_key = os.getenv('GROQ_API_KEY')
    if groq_key:
        print(f"✅ GROQ_API_KEY: {groq_key[:10]}...{groq_key[-5:]}")
    else:
        print("⚠️ GROQ_API_KEY no configurada (funcionará en modo fallback)")
    
    jetson_url = os.getenv('JETSON_API_URL', 'default')
    print(f"📡 JETSON_API_URL: {jetson_url}")
    
    return True

if __name__ == "__main__":
    print(f"🕐 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if check_environment():
        asyncio.run(test_groq_agent())
    else:
        print("❌ Configuración de entorno incompleta")
