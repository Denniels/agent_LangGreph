#!/usr/bin/env python3
"""
Script para verificar qué tipos de sensores existen REALMENTE en la base de datos
y identificar el problema de "alucinaciones" del LLM
"""

import asyncio
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from modules.database.db_connector import DatabaseConnector
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("Asegúrate de estar en el entorno virtual correcto")
    sys.exit(1)

async def analyze_real_sensors():
    """Analiza qué sensores existen realmente en la base de datos"""
    
    try:
        print("🔍 DIAGNÓSTICO DE SENSORES REALES")
        print("=" * 50)
        
        db = DatabaseConnector()
        
        # 1. Verificar tipos de sensores únicos
        print("\n📊 TIPOS DE SENSORES EN LA BASE DE DATOS:")
        query_sensors = """
        SELECT DISTINCT sensor_type, COUNT(*) as total_readings,
               MIN(timestamp) as first_reading,
               MAX(timestamp) as last_reading
        FROM sensor_data 
        GROUP BY sensor_type 
        ORDER BY total_readings DESC;
        """
        
        sensor_results = await db.execute_query(query_sensors)
        
        if sensor_results:
            for row in sensor_results:
                print(f"  ✓ {row[0]}: {row[1]} lecturas ({row[2]} → {row[3]})")
        else:
            print("  ❌ No se encontraron datos de sensores")
        
        # 2. Verificar dispositivos activos
        print("\n🔌 DISPOSITIVOS ACTIVOS:")
        query_devices = """
        SELECT device_id, device_type, device_name, location, status, last_seen
        FROM devices 
        ORDER BY status DESC, device_id;
        """
        
        device_results = await db.execute_query(query_devices)
        
        if device_results:
            for row in device_results:
                status_icon = "🟢" if row[4] == 'active' else "🔴"
                print(f"  {status_icon} {row[0]} ({row[1]}): {row[2]} - {row[3]} | Último visto: {row[5]}")
        else:
            print("  ❌ No se encontraron dispositivos")
        
        # 3. Verificar últimas lecturas por tipo de sensor
        print("\n📈 ÚLTIMAS LECTURAS POR TIPO DE SENSOR:")
        query_recent = """
        SELECT sensor_type, device_id, value, unit, timestamp, location
        FROM sensor_data 
        WHERE timestamp >= NOW() - INTERVAL '1 hour'
        ORDER BY sensor_type, timestamp DESC;
        """
        
        recent_results = await db.execute_query(query_recent)
        
        if recent_results:
            current_type = None
            for row in recent_results:
                if row[0] != current_type:
                    current_type = row[0]
                    print(f"\n  📊 {current_type.upper()}:")
                print(f"    • {row[1]}: {row[2]} {row[3]} ({row[4]}) - {row[5]}")
        else:
            print("  ❌ No hay lecturas recientes (última hora)")
        
        # 4. Resumen de configuración de alertas
        print("\n⚠️ CONFIGURACIÓN DE ALERTAS:")
        query_config = """
        SELECT sc.device_id, sc.sensor_type, sc.min_threshold, sc.max_threshold, sc.alert_enabled
        FROM sensor_config sc
        JOIN devices d ON sc.device_id = d.device_id
        WHERE d.status = 'active'
        ORDER BY sc.sensor_type, sc.device_id;
        """
        
        config_results = await db.execute_query(query_config)
        
        if config_results:
            for row in config_results:
                enabled_icon = "✅" if row[4] else "❌"
                print(f"  {enabled_icon} {row[1]} ({row[0]}): {row[2]} - {row[3]}")
        else:
            print("  ❌ No hay configuración de alertas")
        
        print("\n" + "=" * 50)
        print("✅ DIAGNÓSTICO COMPLETADO")
        
        await db.close()
        
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(analyze_real_sensors())
