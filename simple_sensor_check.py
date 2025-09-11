#!/usr/bin/env python3
"""
Script simple para verificar sensores reales
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.database.db_connector import DatabaseConnector

async def simple_check():
    """Verificación simple de sensores"""
    
    try:
        print("🔍 VERIFICANDO SENSORES REALES...")
        
        db = DatabaseConnector()
        await db.connect()
        
        # Consulta simple
        query = "SELECT DISTINCT sensor_type FROM sensor_data ORDER BY sensor_type;"
        result = await db.execute_query(query)
        
        print("\n📊 TIPOS DE SENSORES ENCONTRADOS:")
        if result:
            for row in result:
                sensor_type = row[0] if isinstance(row, (list, tuple)) else row
                print(f"  ✓ {sensor_type}")
        else:
            print("  ❌ No se encontraron sensores")
        
        # Verificar también dispositivos
        query2 = "SELECT device_id, device_type FROM devices WHERE status = 'active';"
        result2 = await db.execute_query(query2)
        
        print("\n🔌 DISPOSITIVOS ACTIVOS:")
        if result2:
            for row in result2:
                device_id = row[0] if isinstance(row, (list, tuple)) else row
                device_type = row[1] if isinstance(row, (list, tuple)) and len(row) > 1 else "N/D"
                print(f"  ✓ {device_id} ({device_type})")
        else:
            print("  ❌ No se encontraron dispositivos activos")
        
        await db.close()
        print("\n✅ VERIFICACIÓN COMPLETADA")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_check())
