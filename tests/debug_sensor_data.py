#!/usr/bin/env python3
"""
Debug específico para el problema de sensor_data vacía
=====================================================

Script para probar exactamente qué está consultando el agente
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.database.db_connector import get_db
from modules.tools.database_tools import DatabaseTools
from datetime import datetime, timedelta


async def debug_sensor_data():
    """Debug paso a paso de las consultas del agente"""
    
    print("🔍 DEBUG: Verificando consultas del agente IoT")
    print("=" * 60)
    
    # 1. Probar conexión directa a la base de datos
    print("\n1️⃣ Probando conexión directa...")
    db = await get_db()
    
    # 2. Probar consulta SQL directa
    print("\n2️⃣ Consultando datos más recientes (últimas 24 horas)...")
    recent_query = """
        SELECT 
            id, device_id, sensor_type, value, unit, timestamp, created_at
        FROM sensor_data 
        WHERE timestamp >= NOW() - INTERVAL '24 hours'
        ORDER BY timestamp DESC 
        LIMIT 10
    """
    
    recent_data = await db.execute_query(recent_query)
    print(f"📊 Datos recientes (24h): {len(recent_data)} registros")
    
    if recent_data:
        print("🔍 Primer registro reciente:")
        for key, value in recent_data[0].items():
            print(f"   {key}: {value}")
    else:
        print("❌ No hay datos recientes en las últimas 24 horas")
    
    # 3. Probar consulta general (últimos 10 registros sin filtro de tiempo)
    print("\n3️⃣ Consultando últimos 10 registros sin filtro...")
    general_data = await db.get_sensor_data(limit=10)
    print(f"📊 Últimos registros: {len(general_data)} registros")
    
    if general_data:
        print("🔍 Primer registro general:")
        for key, value in general_data[0].items():
            print(f"   {key}: {value}")
            
        print(f"\n📅 Timestamp más reciente: {general_data[0]['timestamp']}")
        print(f"📅 Creado: {general_data[0]['created_at']}")
    else:
        print("❌ No hay datos en la tabla sensor_data")
    
    # 4. Probar DatabaseTools (como lo usa el agente)
    print("\n4️⃣ Probando DatabaseTools (como el agente)...")
    db_tools = DatabaseTools()
    agent_data = await db_tools.get_sensor_data_tool(limit=10)
    print(f"📊 Datos via DatabaseTools: {len(agent_data)} registros")
    
    if agent_data:
        print("🔍 Primer registro via DatabaseTools:")
        for key, value in agent_data[0].items():
            print(f"   {key}: {value}")
    else:
        print("❌ DatabaseTools no encuentra datos")
    
    # 5. Verificar dispositivos específicos de las imágenes
    print("\n5️⃣ Verificando dispositivos específicos...")
    
    devices_to_check = ['arduino_eth_001', 'esp32_wifi_001']
    
    for device_id in devices_to_check:
        print(f"\n🔍 Dispositivo: {device_id}")
        device_data = await db.get_sensor_data(device_id=device_id, limit=5)
        print(f"   📊 Registros: {len(device_data)}")
        
        if device_data:
            latest = device_data[0]
            print(f"   📅 Último registro: {latest['timestamp']}")
            print(f"   🔢 Sensor: {latest['sensor_type']}")
            print(f"   📈 Valor: {latest['value']} {latest.get('unit', '')}")
    
    # 6. Verificar conteo total
    print("\n6️⃣ Verificando conteo total...")
    count_query = "SELECT COUNT(*) as total FROM sensor_data"
    count_result = await db.execute_query(count_query)
    total_records = count_result[0]['total']
    print(f"📊 Total de registros en sensor_data: {total_records:,}")
    
    # 7. Verificar registros por fecha
    print("\n7️⃣ Verificando registros por fecha...")
    today = datetime.now().strftime('%Y-%m-%d')
    date_query = """
        SELECT 
            DATE(timestamp) as fecha,
            COUNT(*) as registros
        FROM sensor_data 
        WHERE timestamp >= NOW() - INTERVAL '7 days'
        GROUP BY DATE(timestamp)
        ORDER BY fecha DESC
    """
    
    date_data = await db.execute_query(date_query)
    print("📅 Registros por día (últimos 7 días):")
    for row in date_data:
        print(f"   {row['fecha']}: {row['registros']:,} registros")
    
    await db.disconnect()
    
    print("\n" + "=" * 60)
    print("🔍 DEBUG COMPLETADO")


if __name__ == "__main__":
    asyncio.run(debug_sensor_data())
