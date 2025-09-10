#!/usr/bin/env python3
"""
Test de conexión con la base de datos real
==========================================

Script para probar que nuestro connector funciona con la base de datos real.
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.database.db_connector import get_db
from modules.utils.logger import logger


async def test_real_database():
    """Prueba la conexión y operaciones con la base de datos real."""
    
    print("🔍 Probando conexión con base de datos real...")
    print("=" * 60)
    
    try:
        # Obtener conexión
        db = await get_db()
        
        # Test 1: Health check
        print("🩺 Test 1: Health Check")
        health = await db.health_check()
        print(f"   Estado: {'✅ OK' if health else '❌ ERROR'}")
        
        if not health:
            print("❌ No se puede conectar a la base de datos")
            return
        
        # Test 2: Obtener dispositivos activos
        print("\n📱 Test 2: Dispositivos Activos")
        devices = await db.get_active_devices()
        print(f"   Dispositivos encontrados: {len(devices)}")
        for i, device in enumerate(devices[:3]):  # Mostrar solo los primeros 3
            print(f"   {i+1}. {device['device_id']} ({device['device_type']}) - {device['status']}")
        
        # Test 3: Obtener datos de sensores
        print("\n🌡️ Test 3: Datos de Sensores")
        sensor_data = await db.get_sensor_data(limit=5)
        print(f"   Registros encontrados: {len(sensor_data)}")
        for i, data in enumerate(sensor_data):
            print(f"   {i+1}. {data['device_id']} - {data['sensor_type']}: {data['value']} {data['unit']}")
        
        # Test 4: Obtener eventos/alertas
        print("\n🚨 Test 4: Eventos del Sistema")
        events = await db.get_alerts(active_only=True)
        print(f"   Eventos encontrados: {len(events)}")
        for i, event in enumerate(events[:3]):  # Mostrar solo los primeros 3
            print(f"   {i+1}. {event['event_type']} - {event.get('device_id', 'N/A')} - {event.get('message', '')[:50]}...")
        
        # Test 5: Crear un evento de prueba
        print("\n✏️ Test 5: Crear Evento de Prueba")
        test_device = devices[0]['device_id'] if devices else 'test_device'
        success = await db.create_alert(
            device_id=test_device,
            event_type='test_event',
            message='Evento de prueba desde Python',
            metadata={'source': 'test_script', 'version': '1.0'}
        )
        print(f"   Evento creado: {'✅ OK' if success else '❌ ERROR'}")
        
        print("\n🎉 ¡Todos los tests completados exitosamente!")
        print("✅ La conexión con la base de datos real funciona correctamente")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        logger.error(f"Error en test de base de datos: {e}")
    
    finally:
        # Cerrar conexión
        try:
            if 'db' in locals():
                await db.close()
        except:
            pass


if __name__ == "__main__":
    print("🚀 Iniciando tests de base de datos real...")
    asyncio.run(test_real_database())
