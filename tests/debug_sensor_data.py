#!/usr/bin/env python3
"""
Debug simple de la estructura de datos de la base de datos
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.database.db_connector import DatabaseConnector

async def debug_db_structure():
    """Debug de la estructura de datos"""
    
    print("🔍 DEBUG ESTRUCTURA DE DATOS")
    print("=" * 40)
    
    try:
        db = DatabaseConnector()
        await db.connect()
        
        # Consulta simple
        query = "SELECT COUNT(*) FROM sensor_data;"
        result = await db.execute_query(query)
        
        print(f"Query: {query}")
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
        
        if result:
            print(f"First item type: {type(result[0])}")
            print(f"First item: {result[0]}")
            
            if isinstance(result[0], dict):
                print(f"Keys: {result[0].keys()}")
            elif isinstance(result[0], (list, tuple)):
                print(f"Length: {len(result[0])}")
                print(f"Values: {result[0]}")
        
        # Otra consulta para verificar estructura
        query2 = "SELECT device_id, sensor_type FROM sensor_data LIMIT 1;"
        result2 = await db.execute_query(query2)
        
        print(f"\nQuery2: {query2}")
        print(f"Result2: {result2}")
        
        if result2:
            print(f"First item2: {result2[0]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_db_structure())
