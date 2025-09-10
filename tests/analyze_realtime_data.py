#!/usr/bin/env python3
"""
Análisis de datos en tiempo real
===============================

Script para verificar exactamente cuántos registros hay en tiempo real
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.database.db_connector import get_db


async def analyze_realtime_data():
    """Analiza los datos en tiempo real para entender el problema"""
    
    print("🔍 ANÁLISIS DE DATOS EN TIEMPO REAL")
    print("=" * 60)
    
    db = await get_db()
    
    # 1. Verificar registros de los últimos 10 minutos
    print("\n1️⃣ Registros de los últimos 10 minutos...")
    query_10min = """
        SELECT 
            device_id,
            sensor_type,
            COUNT(*) as registros,
            MIN(timestamp) as primer_registro,
            MAX(timestamp) as ultimo_registro
        FROM sensor_data 
        WHERE timestamp >= NOW() - INTERVAL '10 minutes'
        GROUP BY device_id, sensor_type
        ORDER BY ultimo_registro DESC
    """
    
    data_10min = await db.execute_query(query_10min)
    total_10min = sum(row['registros'] for row in data_10min)
    
    print(f"📊 Total de registros (10 min): {total_10min}")
    print(f"📱 Dispositivos activos: {len(set(row['device_id'] for row in data_10min))}")
    
    for row in data_10min:
        print(f"   {row['device_id']} - {row['sensor_type']}: {row['registros']} registros")
        print(f"      Último: {row['ultimo_registro']}")
    
    # 2. Verificar registros de los últimos 2 minutos
    print("\n2️⃣ Registros de los últimos 2 minutos...")
    query_2min = """
        SELECT 
            device_id,
            sensor_type,
            value,
            timestamp
        FROM sensor_data 
        WHERE timestamp >= NOW() - INTERVAL '2 minutes'
        ORDER BY timestamp DESC
        LIMIT 50
    """
    
    data_2min = await db.execute_query(query_2min)
    print(f"📊 Registros últimos 2 min: {len(data_2min)}")
    
    if data_2min:
        print(f"🕐 Más reciente: {data_2min[0]['timestamp']}")
        print(f"🕐 Más antiguo: {data_2min[-1]['timestamp']}")
        
        print("\n📋 Últimos 10 registros:")
        for i, row in enumerate(data_2min[:10]):
            print(f"   {i+1}. {row['device_id']} - {row['sensor_type']}: {row['value']} @ {row['timestamp']}")
    
    # 3. Verificar lo que obtiene el agente actualmente
    print("\n3️⃣ Comparando con las consultas del agente...")
    
    # Consulta actual del agente (limit=10)
    agent_query = """
        SELECT 
            id,
            device_id,
            sensor_type,
            value,
            unit,
            timestamp,
            created_at
        FROM sensor_data
        ORDER BY timestamp DESC 
        LIMIT 10
    """
    
    agent_data = await db.execute_query(agent_query)
    print(f"📊 Datos del agente (limit=10): {len(agent_data)}")
    
    if agent_data:
        print(f"🕐 Más reciente: {agent_data[0]['timestamp']}")
        print(f"🕐 Más antiguo: {agent_data[-1]['timestamp']}")
    
    # 4. Proponer consulta optimizada
    print("\n4️⃣ Consulta optimizada propuesta...")
    optimized_query = """
        SELECT 
            id,
            device_id,
            sensor_type,
            value,
            unit,
            timestamp,
            created_at
        FROM sensor_data
        WHERE timestamp >= NOW() - INTERVAL '10 minutes'
        ORDER BY timestamp DESC 
        LIMIT 200
    """
    
    optimized_data = await db.execute_query(optimized_query)
    print(f"📊 Datos optimizados (10min, limit=200): {len(optimized_data)}")
    
    if optimized_data:
        print(f"🕐 Más reciente: {optimized_data[0]['timestamp']}")
        print(f"🕐 Más antiguo: {optimized_data[-1]['timestamp']}")
        
        # Agrupar por dispositivo
        devices_count = {}
        for row in optimized_data:
            device = row['device_id']
            if device not in devices_count:
                devices_count[device] = 0
            devices_count[device] += 1
        
        print("\n📱 Registros por dispositivo (optimizado):")
        for device, count in devices_count.items():
            print(f"   {device}: {count} registros")
    
    # 5. Verificar frecuencia de datos
    print("\n5️⃣ Análisis de frecuencia...")
    frequency_query = """
        SELECT 
            device_id,
            DATE_TRUNC('minute', timestamp) as minuto,
            COUNT(*) as registros_por_minuto
        FROM sensor_data 
        WHERE timestamp >= NOW() - INTERVAL '10 minutes'
        GROUP BY device_id, DATE_TRUNC('minute', timestamp)
        ORDER BY minuto DESC, device_id
        LIMIT 20
    """
    
    frequency_data = await db.execute_query(frequency_query)
    print(f"📈 Frecuencia por minuto:")
    
    for row in frequency_data:
        print(f"   {row['device_id']} @ {row['minuto']}: {row['registros_por_minuto']} reg/min")
    
    await db.disconnect()
    
    print("\n" + "=" * 60)
    print("✅ ANÁLISIS COMPLETADO")


if __name__ == "__main__":
    asyncio.run(analyze_realtime_data())
