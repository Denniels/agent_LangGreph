#!/usr/bin/env python3
"""
Diagnóstico completo de acceso a base de datos
Verifica que el agente pueda acceder a TODOS los datos reales
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.database.db_connector import DatabaseConnector
from datetime import datetime, timedelta

async def comprehensive_db_test():
    """Diagnóstico exhaustivo de la base de datos"""
    
    print("🔍 DIAGNÓSTICO COMPLETO DE BASE DE DATOS")
    print("=" * 60)
    
    try:
        db = DatabaseConnector()
        await db.connect()
        print("✅ Conexión establecida exitosamente")
        
        # 1. VERIFICAR CONTEO TOTAL DE REGISTROS
        print("\n📊 CONTEO TOTAL DE REGISTROS:")
        total_query = "SELECT COUNT(*) as total_records FROM sensor_data;"
        total_result = await db.execute_query(total_query)
        
        if total_result:
            total_count = total_result[0]['total_records']
            print(f"  🔢 Total de registros: {total_count:,}")
        
        # 2. CONTEO POR DISPOSITIVO
        print("\n🔌 REGISTROS POR DISPOSITIVO:")
        device_query = """
        SELECT device_id, COUNT(*) as count, 
               MIN(timestamp) as first_record,
               MAX(timestamp) as last_record
        FROM sensor_data 
        GROUP BY device_id 
        ORDER BY count DESC;
        """
        device_results = await db.execute_query(device_query)
        
        if device_results:
            for row in device_results:
                device_id = row['device_id']
                count = row['count']
                first = row['first_record']
                last = row['last_record']
                print(f"  📱 {device_id}: {count:,} registros ({first} → {last})")
        
        # 3. CONTEO POR TIPO DE SENSOR
        print("\n🌡️ REGISTROS POR TIPO DE SENSOR:")
        sensor_query = """
        SELECT sensor_type, COUNT(*) as count,
               MIN(timestamp) as first_record,
               MAX(timestamp) as last_record
        FROM sensor_data 
        GROUP BY sensor_type 
        ORDER BY count DESC;
        """
        sensor_results = await db.execute_query(sensor_query)
        
        if sensor_results:
            for row in sensor_results:
                sensor_type = row['sensor_type']
                count = row['count']
                first = row['first_record']
                last = row['last_record']
                print(f"  📊 {sensor_type}: {count:,} registros ({first} → {last})")
        
        # 4. VERIFICAR DATOS RECIENTES (últimos 10 minutos)
        print("\n⏰ DATOS RECIENTES (últimos 10 minutos):")
        recent_query = """
        SELECT device_id, sensor_type, COUNT(*) as count,
               MIN(value) as min_val, MAX(value) as max_val, AVG(value) as avg_val
        FROM sensor_data 
        WHERE timestamp >= NOW() - INTERVAL '10 minutes'
        GROUP BY device_id, sensor_type
        ORDER BY device_id, sensor_type;
        """
        recent_results = await db.execute_query(recent_query)
        
        if recent_results:
            for row in recent_results:
                device = row['device_id']
                sensor = row['sensor_type']
                count = row['count']
                min_val = row['min_val']
                max_val = row['max_val']
                avg_val = row['avg_val']
                print(f"  🔥 {device}/{sensor}: {count} registros | Min: {min_val:.2f} | Max: {max_val:.2f} | Avg: {avg_val:.2f}")
        else:
            print("  ❌ NO SE ENCONTRARON DATOS RECIENTES")
        
        # 5. VERIFICAR DATOS DEL ÚLTIMO DÍA
        print("\n📅 DATOS DEL ÚLTIMO DÍA:")
        day_query = """
        SELECT COUNT(*) as total_day,
               COUNT(DISTINCT device_id) as unique_devices,
               COUNT(DISTINCT sensor_type) as unique_sensors
        FROM sensor_data 
        WHERE timestamp >= NOW() - INTERVAL '24 hours';
        """
        day_results = await db.execute_query(day_query)
        
        if day_results:
            row = day_results[0]
            total_day = row['total_day']
            devices = row['unique_devices']
            sensors = row['unique_sensors']
            print(f"  📈 Últimas 24h: {total_day:,} registros de {devices} dispositivos y {sensors} tipos de sensores")
        
        # 6. MUESTRA DE DATOS MÁS RECIENTES
        print("\n🔍 MUESTRA DE DATOS MÁS RECIENTES (últimos 20):")
        sample_query = """
        SELECT device_id, sensor_type, value, unit, timestamp
        FROM sensor_data 
        ORDER BY timestamp DESC 
        LIMIT 20;
        """
        sample_results = await db.execute_query(sample_query)
        
        if sample_results:
            for i, row in enumerate(sample_results):
                device = row['device_id']
                sensor = row['sensor_type']
                value = row['value']
                unit = row['unit']
                timestamp = row['timestamp']
                print(f"  {i+1:2d}. {device}/{sensor}: {value} {unit} ({timestamp})")
        else:
            print("  ❌ NO SE ENCONTRARON DATOS")
        
        # 7. VERIFICAR CONFIGURACIÓN DE CONEXIÓN
        print("\n🔧 CONFIGURACIÓN DE CONEXIÓN:")
        print(f"  🏠 Host: {db.host}")
        print(f"  🔌 Puerto: {db.port}")
        print(f"  🗄️ Base de datos: {db.database}")
        print(f"  👤 Usuario: {db.user}")
        print(f"  🔑 Password: {'***' if db.password else 'NO CONFIGURADO'}")
        
        # 8. VERIFICAR ESTADO DE TABLAS
        print("\n📋 ESTADO DE TABLAS:")
        tables_query = """
        SELECT table_name, 
               (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
        FROM information_schema.tables t
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """
        tables_results = await db.execute_query(tables_query)
        
        if tables_results:
            for row in tables_results:
                table_name = row['table_name']
                columns = row['column_count']
                print(f"  📊 {table_name}: {columns} columnas")
        
        print("\n" + "=" * 60)
        print("✅ DIAGNÓSTICO COMPLETADO")
        
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(comprehensive_db_test())
