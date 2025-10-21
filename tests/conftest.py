"""
Configuración global para tests
==============================

Configuración común y fixtures compartidas para todos los tests.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

@pytest.fixture(scope="session")
def event_loop():
    """
    Fixture para el loop de eventos asyncio.
    Necesario para tests asíncronos.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """
    Configuración automática del entorno de pruebas.
    Se ejecuta antes de cada test.
    """
    # Variables de entorno de prueba
    monkeypatch.setenv("DB_HOST", "test_host")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_password")
    monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")
    monkeypatch.setenv("LOG_LEVEL", "ERROR")  # Silenciar logs en tests

@pytest.fixture
def db_connector():
    """Fixture mock para DatabaseConnector."""
    mock_instance = AsyncMock()
    
    # Configurar métodos mock
    mock_instance.connect.return_value = None
    mock_instance.close.return_value = None
    mock_instance.health_check.return_value = True
    mock_instance.get_sensor_data.return_value = []
    mock_instance.get_active_devices.return_value = []
    mock_instance.get_alerts.return_value = []
    mock_instance.create_alert.return_value = True
    mock_instance.execute_query.return_value = []
    
    return mock_instance

@pytest.fixture
def iot_agent():
    """Fixture mock para IoTAgent."""
    mock_instance = Mock()
    
    # Configurar propiedades y métodos mock
    mock_instance.conversation_history = []
    mock_instance.db_tools = Mock()
    mock_instance.analysis_tools = Mock()
    mock_instance.client = AsyncMock()
    
    # Métodos del agente
    mock_instance.process_message = AsyncMock(return_value="Respuesta mock")
    mock_instance._create_enriched_message = Mock(return_value="Mensaje enriquecido")
    mock_instance.get_conversation_summary = Mock(return_value="Resumen mock")
    mock_instance.clear_history = Mock()
    mock_instance._gather_context_data = AsyncMock(return_value={})
    mock_instance._determine_tools_needed = Mock(return_value=[])
    
    return mock_instance

@pytest.fixture
def db_tools():
    """Fixture mock para DatabaseTools."""
    mock_instance = Mock()
    
    # Configurar base de datos mock
    mock_instance.db = AsyncMock()
    
    # Configurar métodos mock
    mock_instance.get_sensor_data_tool = AsyncMock(return_value=[])
    mock_instance.get_devices_tool = AsyncMock(return_value=[])
    mock_instance.get_alerts_tool = AsyncMock(return_value=[])
    mock_instance.create_alert_tool = AsyncMock(return_value=True)
    
    return mock_instance

@pytest.fixture
def sample_device_data():
    """
    Fixture con datos de dispositivos basado en el esquema real.
    """
    from datetime import datetime, timedelta
    base_time = datetime.now()
    
    return [
        {
            "device_id": "esp32_wifi_001",
            "device_type": "arduino_ethernet", 
            "name": "ESP32 WiFi Sensor",
            "ip_address": "192.168.0.105",
            "port": None,
            "status": "online",
            "last_seen": base_time - timedelta(minutes=5),
            "metadata": {"protocol": "wifi", "sensors": ["ldr", "ntc_entrada", "ntc_salida"]},
            "created_at": base_time - timedelta(days=30),
            "updated_at": base_time - timedelta(minutes=5)
        },
        {
            "device_id": "arduino_eth_001",
            "device_type": "arduino_ethernet",
            "name": "Arduino Ethernet Sensor",
            "ip_address": "192.168.0.106", 
            "port": None,
            "status": "online",
            "last_seen": base_time - timedelta(minutes=2),
            "metadata": {"protocol": "ethernet", "sensors": ["avg", "t2"]},
            "created_at": base_time - timedelta(days=15),
            "updated_at": base_time - timedelta(minutes=2)
        },
        {
            "device_id": "net_device_192_168_0_107",
            "device_type": "web_device",
            "name": "Web Device 192.168.0.107",
            "ip_address": "192.168.0.107",
            "port": None,
            "status": "online",
            "last_seen": base_time - timedelta(minutes=1),
            "metadata": {"protocol": "http", "device_type": "web_device"},
            "created_at": base_time - timedelta(days=10),
            "updated_at": base_time - timedelta(minutes=1)
        }
    ]

@pytest.fixture
def sample_sensor_data():
    """
    Fixture con datos de sensores basado en el esquema real.
    """
    from datetime import datetime, timedelta
    
    base_time = datetime.now()
    data = []
    
    # Datos de temperatura del Arduino USB
    for i in range(24):
        data.append({
            "id": i + 1,
            "device_id": "ARDUINO_USB_001",
            "sensor_type": "temperature",
            "value": 20.0 + (i % 5) + (i * 0.1),  # Valores entre 20-25
            "unit": "°C",
            "raw_data": {"adc_value": 512 + i * 10},
            "timestamp": base_time - timedelta(hours=i),
            "created_at": base_time - timedelta(hours=i)
        })
    
    # Datos de humedad del Arduino USB
    for i in range(24):
        data.append({
            "id": i + 25,
            "device_id": "ARDUINO_USB_001",
            "sensor_type": "humidity",
            "value": 45.0 + (i % 10),  # Valores entre 45-54
            "unit": "%",
            "raw_data": {"adc_value": 300 + i * 5},
            "timestamp": base_time - timedelta(hours=i),
            "created_at": base_time - timedelta(hours=i)
        })
    
    # Datos del Modbus
    for i in range(12):
        data.append({
            "id": i + 49,
            "device_id": "MODBUS_001",
            "sensor_type": "pressure",
            "value": 1.2 + (i % 3) * 0.1,  # Valores entre 1.2-1.5
            "unit": "bar",
            "raw_data": {"register_address": 40001, "raw_value": 1200 + i * 10},
            "timestamp": base_time - timedelta(hours=i * 2),
            "created_at": base_time - timedelta(hours=i * 2)
        })
    
    return data

@pytest.fixture
def sample_system_events():
    """
    Fixture con eventos del sistema basado en el esquema real.
    """
    from datetime import datetime, timedelta
    
    base_time = datetime.now()
    
    return [
        {
            "id": 1,
            "event_type": "device_connected",
            "device_id": "ARDUINO_USB_001",
            "message": "Arduino USB device connected successfully",
            "metadata": {"port": "COM3", "baud_rate": 9600},
            "timestamp": base_time - timedelta(hours=4)
        },
        {
            "id": 2,
            "event_type": "device_disconnected",
            "device_id": "PLC_001",
            "message": "PLC connection lost",
            "metadata": {"error_code": "TIMEOUT", "retry_count": 3},
            "timestamp": base_time - timedelta(hours=2)
        },
        {
            "id": 3,
            "event_type": "error",
            "device_id": "MODBUS_001",
            "message": "Modbus read exception",
            "metadata": {"exception_code": 2, "function_code": 3},
            "timestamp": base_time - timedelta(hours=1)
        },
        {
            "id": 4,
            "event_type": "device_connected",
            "device_id": "MODBUS_001",
            "message": "Modbus device reconnected",
            "metadata": {"ip_address": "192.168.1.100", "unit_id": 1},
            "timestamp": base_time - timedelta(minutes=30)
        }
    ]

@pytest.fixture
def sample_alert_data():
    """
    Fixture con datos de alertas de ejemplo.
    """
    from datetime import datetime, timedelta
    
    base_time = datetime.now()
    
    return [
        {
            "alert_id": 1,
            "device_id": "TEMP_001",
            "alert_type": "high_temperature",
            "message": "Temperature exceeds threshold: 28.5°C",
            "severity": "high",
            "status": "active",
            "created_at": base_time - timedelta(hours=2),
            "resolved_at": None
        },
        {
            "alert_id": 2,
            "device_id": "HUM_001",
            "alert_type": "high_humidity",
            
            "severity": "medium",
            "status": "active",
            "created_at": base_time - timedelta(hours=1),
            "resolved_at": None
        },
        {
            "alert_id": 3,
            "device_id": "TEMP_002",
            "alert_type": "device_offline",
            "message": "Device not responding for 2 hours",
            "severity": "high",
            "status": "resolved",
            "created_at": base_time - timedelta(hours=4),
            "resolved_at": base_time - timedelta(hours=3)
        }
    ]

# Configuración de pytest
def pytest_configure(config):
    """
    Configuración adicional de pytest.
    """
    # Agregar marcadores personalizados
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "agent: marks tests related to agent functionality"
    )

def pytest_collection_modifyitems(config, items):
    """
    Modificar items de la colección de tests.
    """
    # Agregar marcador 'unit' por defecto a todos los tests
    for item in items:
        if not any(mark.name in ['integration', 'slow'] for mark in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
