#!/usr/bin/env python3
"""
Script para explorar la estructura de la base de datos IoT en Jetson Nano
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def explore_database():
    """Explora la estructura de la base de datos IoT"""
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Configuración de la base de datos en Jetson Nano
    db_config = {
        'host': os.getenv('DB_HOST', '192.168.0.102'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'iot_system'),
        'user': os.getenv('DB_USER', 'iot_user'),
        'password': os.getenv('DB_PASSWORD', 'iot_password123')
    }
    
    print(f"🔗 Intentando conectar a:")
    print(f"   Host: {db_config['host']}")
    print(f"   Puerto: {db_config['port']}")
    print(f"   Base de datos: {db_config['database']}")
    print(f"   Usuario: {db_config['user']}")
    print("-" * 50)
    
    try:
        print("⏳ Conectando a la base de datos...")
        conn = await asyncpg.connect(**db_config)
        print("✅ ¡Conexión exitosa!")
        
        # Verificar versión de PostgreSQL
        version = await conn.fetchval("SELECT version()")
        print(f"📋 Versión PostgreSQL: {version}")
        
        # Listar todas las tablas
        print("\n📊 Tablas en la base de datos:")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        if not tables:
            print("   ❌ No se encontraron tablas")
            await conn.close()
            return
        
        for table in tables:
            print(f"   📄 {table[0]}")
        
        print("\n" + "="*60)
        
        # Explorar estructura de cada tabla
        for table in tables:
            table_name = table[0]
            print(f"\n🔍 Estructura de la tabla '{table_name}':")
            
            # Obtener columnas
            columns = await conn.fetch("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable, 
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = $1
                ORDER BY ordinal_position;
            """, table_name)
            
            for col in columns:
                nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                default = f", DEFAULT: {col[3]}" if col[3] else ""
                length = f"({col[4]})" if col[4] else ""
                print(f"   📌 {col[0]}: {col[1]}{length} {nullable}{default}")
            
            # Contar registros
            try:
                count = await conn.fetchval(f'SELECT COUNT(*) FROM "{table_name}"')
                print(f"   📊 Registros: {count}")
            except Exception as e:
                print(f"   ❌ Error contando registros: {e}")
            
            # Mostrar algunos datos de ejemplo (primeros 3 registros)
            if table_name in ['devices', 'sensor_data', 'alerts']:
                try:
                    sample_data = await conn.fetch(f'SELECT * FROM "{table_name}" LIMIT 3')
                    if sample_data:
                        print(f"   🔍 Datos de ejemplo:")
                        for i, row in enumerate(sample_data, 1):
                            print(f"      Registro {i}: {dict(row)}")
                    else:
                        print(f"   📝 No hay datos en la tabla")
                except Exception as e:
                    print(f"   ❌ Error obteniendo datos de ejemplo: {e}")
            
            print("-" * 40)
        
        await conn.close()
        print("\n✅ Exploración completada exitosamente")
        
    except ConnectionError as e:
        print(f"❌ Error de conexión: {e}")
        print("🔧 Posibles soluciones:")
        print("   1. Verificar que PostgreSQL esté ejecutándose en la Jetson Nano")
        print("   2. Verificar la conectividad de red (ping 192.168.0.102)")
        print("   3. Verificar que el puerto 5432 esté abierto")
        print("   4. Verificar credenciales de base de datos")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        print(f"   Tipo: {type(e).__name__}")

async def test_network_connectivity():
    """Prueba la conectividad de red básica"""
    import subprocess
    import platform
    
    host = "192.168.0.102"
    
    print(f"🌐 Probando conectividad a {host}...")
    
    # Comando ping según el sistema operativo
    if platform.system().lower() == "windows":
        cmd = ["ping", "-n", "3", host]
    else:
        cmd = ["ping", "-c", "3", host]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Conectividad de red OK")
            return True
        else:
            print("❌ No hay conectividad de red")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error probando conectividad: {e}")
        return False

async def main():
    """Función principal"""
    print("🚀 Explorador de Base de Datos IoT")
    print("=" * 50)
    
    # Probar conectividad primero
    if await test_network_connectivity():
        await explore_database()
    else:
        print("\n⚠️  Sin conectividad de red. No se puede acceder a la base de datos.")

if __name__ == "__main__":
    asyncio.run(main())
