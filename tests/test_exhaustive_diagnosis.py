#!/usr/bin/env python3
"""
DIAGNÓSTICO EXHAUSTIVO - Simulación entorno Streamlit Cloud
==========================================================

Este script simula exactamente las condiciones de Streamlit Cloud
para identificar la raíz del problema.
"""

import os
import sys
import traceback
import asyncio
import json
from datetime import datetime

# Simular entorno de Streamlit Cloud
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def log_with_timestamp(message):
    """Log con timestamp para debugging"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

async def diagnostic_exhaustive():
    """Diagnóstico exhaustivo paso a paso"""
    log_with_timestamp("🔍 DIAGNÓSTICO EXHAUSTIVO - SIMULACIÓN STREAMLIT CLOUD")
    log_with_timestamp("=" * 70)
    
    # ===== FASE 1: VERIFICAR IMPORTS =====
    log_with_timestamp("📋 FASE 1: Verificando imports...")
    try:
        from modules.tools.jetson_api_connector import JetsonAPIConnector
        from modules.agents.cloud_iot_agent import CloudIoTAgent
        log_with_timestamp("   ✅ Imports exitosos")
    except Exception as e:
        log_with_timestamp(f"   ❌ Error en imports: {e}")
        return False
    
    # ===== FASE 2: VERIFICAR VERSIÓN DEL CÓDIGO =====
    log_with_timestamp("\n📋 FASE 2: Verificando versión del código...")
    try:
        # Verificar que tenemos la versión corregida
        import inspect
        source = inspect.getsource(JetsonAPIConnector.get_devices)
        if "isinstance(response, list)" in source:
            log_with_timestamp("   ✅ Código corregido presente")
        else:
            log_with_timestamp("   ❌ Código corregido NO presente")
            log_with_timestamp("   🔍 Versión actual del método get_devices:")
            log_with_timestamp(f"   {source[:200]}...")
    except Exception as e:
        log_with_timestamp(f"   ❌ Error verificando código: {e}")
    
    # ===== FASE 3: PROBAR JETSON CONNECTOR PASO A PASO =====
    log_with_timestamp("\n📋 FASE 3: Probando JetsonAPIConnector paso a paso...")
    
    try:
        # 3.1 Crear connector
        log_with_timestamp("   3.1 Creando JetsonAPIConnector...")
        connector = JetsonAPIConnector()
        log_with_timestamp(f"       Base URL: {connector.base_url}")
        
        # 3.2 Probar health check
        log_with_timestamp("   3.2 Probando health check...")
        health = connector.get_health_status()
        log_with_timestamp(f"       Health: {health}")
        
        if health.get('status') != 'healthy':
            log_with_timestamp("   ❌ API Jetson no está healthy")
            return False
        
        # 3.3 Probar get_devices - paso crítico
        log_with_timestamp("   3.3 Probando get_devices() - PASO CRÍTICO...")
        devices = connector.get_devices()
        log_with_timestamp(f"       Tipo de respuesta: {type(devices)}")
        log_with_timestamp(f"       Contenido: {devices}")
        log_with_timestamp(f"       Longitud: {len(devices) if isinstance(devices, list) else 'No es lista'}")
        
        if not devices:
            log_with_timestamp("   ❌ get_devices() devuelve lista vacía")
            
            # Debugging profundo del método
            log_with_timestamp("   🔍 Debugging profundo de get_devices()...")
            try:
                # Llamar _make_request directamente
                raw_response = connector._make_request('/devices')
                log_with_timestamp(f"       Raw response type: {type(raw_response)}")
                log_with_timestamp(f"       Raw response: {raw_response}")
                
                # Verificar lógica de parseo
                if isinstance(raw_response, list):
                    log_with_timestamp("       ✅ Respuesta es lista directa")
                elif raw_response.get('success') and 'data' in raw_response:
                    log_with_timestamp("       ✅ Respuesta encapsulada")
                else:
                    log_with_timestamp("       ❌ Formato de respuesta inesperado")
                    
            except Exception as e:
                log_with_timestamp(f"       ❌ Error en _make_request: {e}")
                traceback.print_exc()
        else:
            log_with_timestamp("   ✅ get_devices() funciona correctamente")
            for device in devices[:2]:  # Mostrar primeros 2
                log_with_timestamp(f"       - {device.get('device_id')}: {device.get('status')}")
        
        # 3.4 Probar get_sensor_data
        log_with_timestamp("   3.4 Probando get_sensor_data()...")
        if devices:
            device_id = devices[0]['device_id']
            sensor_data = connector.get_sensor_data(device_id=device_id, limit=3)
            log_with_timestamp(f"       Datos de {device_id}: {len(sensor_data)} registros")
            if sensor_data:
                log_with_timestamp(f"       Primer registro: {sensor_data[0]}")
        
    except Exception as e:
        log_with_timestamp(f"   ❌ Error en JetsonAPIConnector: {e}")
        traceback.print_exc()
        return False
    
    # ===== FASE 4: PROBAR AGENTE COMPLETO =====
    log_with_timestamp("\n📋 FASE 4: Probando CloudIoTAgent completo...")
    
    try:
        # 4.1 Crear agente
        log_with_timestamp("   4.1 Creando CloudIoTAgent...")
        agent = CloudIoTAgent()
        
        # 4.2 Inicializar agente
        log_with_timestamp("   4.2 Inicializando agente...")
        await agent.initialize()
        
        # 4.3 Verificar conector interno
        log_with_timestamp("   4.3 Verificando conector interno del agente...")
        if hasattr(agent, 'jetson_connector') and agent.jetson_connector:
            log_with_timestamp("       ✅ Agente tiene jetson_connector")
            
            # Probar desde el agente
            agent_devices = agent.jetson_connector.get_devices()
            log_with_timestamp(f"       Dispositivos desde agente: {len(agent_devices)}")
        else:
            log_with_timestamp("       ❌ Agente NO tiene jetson_connector")
            return False
        
        # 4.4 Simular flujo completo de consulta
        log_with_timestamp("   4.4 Simulando flujo de consulta...")
        query = "lista los dispositivos conectados que estan enviando datos"
        
        log_with_timestamp("       Ejecutando query...")
        result = await agent.process_query(query)
        
        log_with_timestamp(f"       Resultado type: {type(result)}")
        log_with_timestamp(f"       Resultado length: {len(str(result))}")
        
        # Analizar respuesta
        result_str = str(result).lower()
        if "esp32" in result_str or "arduino" in result_str:
            log_with_timestamp("       ✅ Respuesta contiene dispositivos específicos")
        elif "no hay datos" in result_str:
            log_with_timestamp("       ❌ Respuesta indica 'no hay datos'")
        else:
            log_with_timestamp("       ⚠️ Respuesta ambigua")
        
        log_with_timestamp(f"       Respuesta: {str(result)[:300]}...")
        
    except Exception as e:
        log_with_timestamp(f"   ❌ Error en CloudIoTAgent: {e}")
        traceback.print_exc()
        return False
    
    # ===== FASE 5: VERIFICAR VARIABLES DE ENTORNO =====
    log_with_timestamp("\n📋 FASE 5: Verificando variables de entorno...")
    
    env_vars = [
        'JETSON_API_URL',
        'GROQ_API_KEY',
        'DB_HOST',
        'DB_PORT'
    ]
    
    for var in env_vars:
        value = os.getenv(var, 'NO_CONFIGURADO')
        if var == 'GROQ_API_KEY' and value != 'NO_CONFIGURADO':
            value = value[:10] + "..." if len(value) > 10 else value
        log_with_timestamp(f"       {var}: {value}")
    
    # ===== RESUMEN FINAL =====
    log_with_timestamp("\n" + "=" * 70)
    log_with_timestamp("📊 RESUMEN DEL DIAGNÓSTICO")
    log_with_timestamp("=" * 30)
    
    if devices and len(devices) > 0:
        log_with_timestamp(f"✅ CONECTIVIDAD: API Jetson funcional ({len(devices)} dispositivos)")
    else:
        log_with_timestamp("❌ CONECTIVIDAD: Problema con get_devices()")
    
    if 'agent_devices' in locals() and len(agent_devices) > 0:
        log_with_timestamp(f"✅ AGENTE: Conector funcional ({len(agent_devices)} dispositivos)")
    else:
        log_with_timestamp("❌ AGENTE: Problema con inicialización o conector")
    
    log_with_timestamp("🎯 PRÓXIMOS PASOS: Basado en resultados del diagnóstico")
    
    return True

if __name__ == "__main__":
    asyncio.run(diagnostic_exhaustive())