#!/usr/bin/env python3
"""
Script de diagnóstico para la conexión a PostgreSQL en Jetson Nano
"""

import asyncio
import asyncpg
import os
import socket
import subprocess
import platform
import sys
from pathlib import Path
from dotenv import load_dotenv

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

# Cargar variables de entorno
load_dotenv(Path(__file__).parent.parent / '.env')

async def test_port_connectivity():
    """Prueba la conectividad específica del puerto PostgreSQL"""
    host = os.getenv('DB_HOST', '192.168.0.102')
    port = int(os.getenv('DB_PORT', 5432))
    
    print(f"🔍 Probando puerto {port} en {host}...")
    
    try:
        # Crear socket TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Puerto {port} está abierto y accesible")
            return True
        else:
            print(f"❌ Puerto {port} no está accesible (código: {result})")
            return False
            
    except Exception as e:
        print(f"❌ Error probando puerto: {e}")
        return False

async def test_database_variations():
    """Prueba diferentes variaciones de configuración de base de datos"""
    
    base_config = {
        'host': os.getenv('DB_HOST', '192.168.0.102'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'user': os.getenv('DB_USER', 'iot_user'),
        'password': os.getenv('DB_PASSWORD', 'DAms15820')
    }
    
    # Diferentes combinaciones de base de datos y usuarios comunes
    test_configs = [
        # Configuración del .env
        {**base_config, 'database': 'iot_db'},
        # Configuraciones comunes
        {**base_config, 'database': 'iot_monitoring', 'user': 'postgres', 'password': 'postgres'},
        {**base_config, 'database': 'iot_monitoring', 'user': 'postgres', 'password': 'postgres123'},
        {**base_config, 'database': 'postgres', 'user': 'postgres', 'password': 'postgres'},
        {**base_config, 'database': 'postgres', 'user': 'postgres', 'password': 'postgres123'},
        {**base_config, 'database': 'iot_system'},
        {**base_config, 'database': 'iot_monitoring'},
        # Con usuario postgres
        {**base_config, 'database': 'iot_db', 'user': 'postgres', 'password': 'postgres'},
        {**base_config, 'database': 'iot_db', 'user': 'postgres', 'password': 'postgres123'},
    ]
    
    print("\n🧪 Probando diferentes configuraciones de base de datos...")
    print("-" * 60)
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n🔄 Prueba {i}: DB={config['database']}, User={config['user']}")
        
        try:
            conn = await asyncio.wait_for(
                asyncpg.connect(**config), 
                timeout=10
            )
            
            print("✅ ¡CONEXIÓN EXITOSA!")
            
            # Probar una consulta simple
            try:
                version = await conn.fetchval("SELECT version()")
                print(f"   📋 PostgreSQL: {version[:50]}...")
                
                # Listar bases de datos
                databases = await conn.fetch("SELECT datname FROM pg_database WHERE datistemplate = false")
                print(f"   🗄️  Bases de datos disponibles:")
                for db in databases:
                    print(f"      - {db['datname']}")
                
                await conn.close()
                print(f"\n🎯 CONFIGURACIÓN FUNCIONAL ENCONTRADA:")
                print(f"   Host: {config['host']}")
                print(f"   Puerto: {config['port']}")
                print(f"   Base de datos: {config['database']}")
                print(f"   Usuario: {config['user']}")
                print(f"   Contraseña: {'*' * len(config['password'])}")
                return config
                
            except Exception as e:
                print(f"   ⚠️  Conectó pero falló consulta: {e}")
                await conn.close()
                
        except asyncio.TimeoutError:
            print("   ❌ Timeout (>10s)")
        except asyncpg.exceptions.InvalidCatalogNameError:
            print(f"   ❌ Base de datos '{config['database']}' no existe")
        except asyncpg.exceptions.InvalidPasswordError:
            print("   ❌ Usuario/contraseña incorrectos")
        except ConnectionRefusedError:
            print("   ❌ Conexión rechazada")
        except Exception as e:
            print(f"   ❌ Error: {type(e).__name__}: {e}")
    
    print("\n❌ Ninguna configuración funcionó")
    return None

async def scan_common_ports():
    """Escanea puertos comunes en la Jetson Nano"""
    host = os.getenv('DB_HOST', '192.168.0.102')
    common_ports = [22, 80, 443, 5432, 3306, 5000, 8080, 8000]
    
    print(f"\n🔍 Escaneando puertos comunes en {host}...")
    
    open_ports = []
    
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                open_ports.append(port)
                print(f"   ✅ Puerto {port} abierto")
            else:
                print(f"   ❌ Puerto {port} cerrado")
                
        except Exception:
            print(f"   ❌ Puerto {port} error")
    
    if open_ports:
        print(f"\n📡 Puertos abiertos encontrados: {open_ports}")
    else:
        print("\n❌ No se encontraron puertos abiertos")
    
    return open_ports

async def main():
    """Función principal de diagnóstico"""
    print("🔧 DIAGNÓSTICO DE CONEXIÓN A BASE DE DATOS")
    print("=" * 60)
    
    # Mostrar configuración actual
    print("\n📋 Configuración actual desde .env:")
    print(f"   Host: {os.getenv('DB_HOST')}")
    print(f"   Puerto: {os.getenv('DB_PORT')}")
    print(f"   Base de datos: {os.getenv('DB_NAME')}")
    print(f"   Usuario: {os.getenv('DB_USER')}")
    print(f"   Contraseña: {'*' * len(os.getenv('DB_PASSWORD', ''))}")
    
    # Ping básico
    print(f"\n🌐 Verificando conectividad básica...")
    host = os.getenv('DB_HOST', '192.168.0.102')
    
    if platform.system().lower() == "windows":
        cmd = ["ping", "-n", "2", host]
    else:
        cmd = ["ping", "-c", "2", host]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ping exitoso - red accesible")
        else:
            print("❌ Ping falló - problema de red")
            return
    except Exception as e:
        print(f"❌ Error en ping: {e}")
        return
    
    # Escanear puertos
    await scan_common_ports()
    
    # Probar puerto PostgreSQL específicamente
    if await test_port_connectivity():
        # Si el puerto está abierto, probar diferentes configuraciones
        working_config = await test_database_variations()
        
        if working_config:
            print(f"\n✅ ¡DIAGNÓSTICO EXITOSO!")
            print(f"📝 Actualiza tu .env con esta configuración:")
            print(f"DB_HOST={working_config['host']}")
            print(f"DB_PORT={working_config['port']}")
            print(f"DB_NAME={working_config['database']}")
            print(f"DB_USER={working_config['user']}")
            print(f"DB_PASSWORD={working_config['password']}")
        else:
            print(f"\n❌ Puerto abierto pero ninguna configuración de DB funciona")
            print(f"🔧 Verifica en la Jetson Nano:")
            print(f"   1. sudo systemctl status postgresql")
            print(f"   2. sudo -u postgres psql -l")
            print(f"   3. Configuración en /etc/postgresql/*/main/pg_hba.conf")
    else:
        print(f"\n❌ Puerto PostgreSQL no accesible")
        print(f"🔧 En la Jetson Nano, verifica:")
        print(f"   1. sudo systemctl start postgresql")
        print(f"   2. sudo ufw allow 5432")
        print(f"   3. Editar postgresql.conf: listen_addresses = '*'")

if __name__ == "__main__":
    asyncio.run(main())
