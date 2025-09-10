"""
Tests para el módulo de base de datos
====================================

Tests unitarios para verificar la funcionalidad del conector de base de datos.
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from modules.database.db_connector import DatabaseConnector, get_db
from modules.utils.config import Config


@pytest.fixture
async def db_connector():
    """Fixture para obtener una instancia del conector de DB."""
    connector = await get_db()
    yield connector
    if connector.pool:
        await connector.disconnect()


@pytest.mark.asyncio
async def test_database_connection():
    """Test para verificar la conexión a la base de datos."""
    connector = DatabaseConnector()
    
    try:
        await connector.connect()
        assert connector.pool is not None, "Pool de conexiones no inicializado"
        
        # Verificar health check
        health = await connector.health_check()
        assert health is True, "Health check falló"
        
    finally:
        await connector.disconnect()


@pytest.mark.asyncio
async def test_get_sensor_data(db_connector):
    """Test para obtener datos de sensores."""
    data = await db_connector.get_sensor_data(limit=5)
    
    assert isinstance(data, list), "Los datos deben ser una lista"
    
    if data:
        # Verificar estructura de los datos
        sample = data[0]
        required_fields = ['device_id', 'sensor_type', 'value', 'unit', 'timestamp']
        
        for field in required_fields:
            assert field in sample, f"Campo {field} faltante en los datos"


@pytest.mark.asyncio
async def test_get_active_devices(db_connector):
    """Test para obtener dispositivos activos."""
    devices = await db_connector.get_active_devices()
    
    assert isinstance(devices, list), "Los dispositivos deben ser una lista"
    
    if devices:
        # Verificar estructura
        sample = devices[0]
        required_fields = ['device_id', 'device_name', 'device_type', 'status']
        
        for field in required_fields:
            assert field in sample, f"Campo {field} faltante en los dispositivos"
        
        # Verificar que solo hay dispositivos activos
        assert sample['status'] == 'active', "Solo deben retornarse dispositivos activos"


@pytest.mark.asyncio
async def test_get_alerts(db_connector):
    """Test para obtener alertas."""
    # Obtener solo alertas activas
    active_alerts = await db_connector.get_alerts(active_only=True)
    assert isinstance(active_alerts, list), "Las alertas deben ser una lista"
    
    # Obtener todas las alertas
    all_alerts = await db_connector.get_alerts(active_only=False)
    assert isinstance(all_alerts, list), "Las alertas deben ser una lista"
    assert len(all_alerts) >= len(active_alerts), "Debe haber más o igual alertas totales que activas"


@pytest.mark.asyncio
async def test_create_alert(db_connector):
    """Test para crear una nueva alerta."""
    # Crear una alerta de prueba
    success = await db_connector.create_alert(
        device_id="TEST_DEVICE",
        alert_type="test_alert",
        message="Esta es una alerta de prueba",
        severity="low"
    )
    
    assert success is True, "La creación de alerta debe ser exitosa"
    
    # Verificar que la alerta fue creada
    alerts = await db_connector.get_alerts(active_only=True)
    test_alerts = [a for a in alerts if a.get('device_id') == 'TEST_DEVICE']
    
    assert len(test_alerts) > 0, "La alerta de prueba debe existir"


@pytest.mark.asyncio
async def test_execute_query(db_connector):
    """Test para ejecutar consultas personalizadas."""
    # Consulta simple
    result = await db_connector.execute_query("SELECT 1 as test_value")
    
    assert len(result) == 1, "Debe retornar un resultado"
    assert result[0]['test_value'] == 1, "El valor debe ser 1"


@pytest.mark.asyncio
async def test_database_error_handling():
    """Test para manejo de errores de base de datos."""
    connector = DatabaseConnector()
    
    # Intentar ejecutar consulta sin conectar
    with pytest.raises(Exception):
        await connector.execute_query("SELECT * FROM nonexistent_table")


if __name__ == "__main__":
    # Ejecutar tests específicos si se ejecuta directamente
    pytest.main([__file__, "-v"])
