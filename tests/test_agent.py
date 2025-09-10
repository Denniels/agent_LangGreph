"""
Tests para el agente conversacional IoT
======================================

Tests unitarios para verificar la funcionalidad del agente IoT.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from modules.agents.iot_agent import IoTAgent
from modules.utils.config import Config


@pytest.fixture
def mock_config():
    """Fixture para configuración mockeada."""
    with patch.object(Config, 'OPENAI_API_KEY', 'test_key'):
        with patch.object(Config, 'validate', return_value=True):
            yield


@pytest.fixture
async def iot_agent(mock_config):
    """Fixture para obtener una instancia del agente IoT."""
    with patch('modules.agents.iot_agent.ChatOpenAI') as mock_llm:
        # Configurar mock del LLM
        mock_llm_instance = Mock()
        mock_llm_instance.ainvoke = Mock(return_value=Mock(content="Respuesta de prueba"))
        mock_llm.return_value = mock_llm_instance
        
        agent = IoTAgent()
        yield agent


def test_agent_initialization(mock_config):
    """Test para verificar la inicialización del agente."""
    with patch('modules.agents.iot_agent.ChatOpenAI'):
        agent = IoTAgent()
        
        assert agent is not None, "El agente debe inicializarse correctamente"
        assert hasattr(agent, 'db_tools'), "El agente debe tener herramientas de DB"
        assert hasattr(agent, 'analysis_tools'), "El agente debe tener herramientas de análisis"
        assert len(agent.conversation_history) > 0, "Debe tener un prompt de sistema"


def test_determine_tools():
    """Test para verificar la determinación de herramientas."""
    with patch('modules.agents.iot_agent.ChatOpenAI'):
        agent = IoTAgent()
        
        # Test para datos de sensores
        tools = agent._determine_tools("¿Cuáles son los datos de temperatura?")
        assert 'sensor_data' in tools, "Debe detectar la necesidad de datos de sensores"
        
        # Test para dispositivos
        tools = agent._determine_tools("¿Qué dispositivos están activos?")
        assert 'devices' in tools, "Debe detectar la necesidad de datos de dispositivos"
        
        # Test para alertas
        tools = agent._determine_tools("¿Hay alertas en el sistema?")
        assert 'alerts' in tools, "Debe detectar la necesidad de datos de alertas"
        
        # Test para análisis
        tools = agent._determine_tools("Analiza las tendencias de los sensores")
        assert 'analysis' in tools, "Debe detectar la necesidad de análisis"


@pytest.mark.asyncio
async def test_process_message_basic(iot_agent):
    """Test básico para procesar mensajes."""
    # Mock de las herramientas
    with patch.object(iot_agent.db_tools, 'get_sensor_data_tool', return_value=[]):
        with patch.object(iot_agent.db_tools, 'get_devices_tool', return_value=[]):
            with patch.object(iot_agent.db_tools, 'get_alerts_tool', return_value=[]):
                
                response = await iot_agent.process_message("Hola, ¿cómo estás?")
                
                assert isinstance(response, str), "La respuesta debe ser una cadena"
                assert len(response) > 0, "La respuesta no debe estar vacía"


@pytest.mark.asyncio
async def test_gather_context_data(iot_agent):
    """Test para recopilar datos de contexto."""
    # Mock de las herramientas
    mock_sensor_data = [
        {"device_id": "TEST_001", "sensor_type": "temperature", "value": 25.0}
    ]
    mock_devices = [
        {"device_id": "TEST_001", "device_name": "Test Device", "status": "active"}
    ]
    mock_alerts = [
        {"device_id": "TEST_001", "alert_type": "test", "severity": "low"}
    ]
    
    with patch.object(iot_agent.db_tools, 'get_sensor_data_tool', return_value=mock_sensor_data):
        with patch.object(iot_agent.db_tools, 'get_devices_tool', return_value=mock_devices):
            with patch.object(iot_agent.db_tools, 'get_alerts_tool', return_value=mock_alerts):
                
                tools = ['sensor_data', 'devices', 'alerts']
                context = await iot_agent._gather_context_data(tools, "test message")
                
                assert 'sensor_data' in context, "Debe incluir datos de sensores"
                assert 'devices' in context, "Debe incluir datos de dispositivos"
                assert 'alerts' in context, "Debe incluir datos de alertas"
                assert context['sensor_data'] == mock_sensor_data
                assert context['devices'] == mock_devices
                assert context['alerts'] == mock_alerts


def test_create_enriched_message(iot_agent):
    """Test para crear mensajes enriquecidos."""
    original_message = "¿Cuál es el estado del sistema?"
    context_data = {
        'sensor_data': [{"device_id": "TEST_001"}],
        'devices': [{"device_id": "TEST_001"}],
        'alerts': []
    }
    
    enriched = iot_agent._create_enriched_message(original_message, context_data)
    
    assert original_message in enriched, "Debe incluir el mensaje original"
    assert "Datos de sensores recientes" in enriched, "Debe mencionar los datos de sensores"
    assert "Dispositivos activos" in enriched, "Debe mencionar los dispositivos"


def test_clear_history(iot_agent):
    """Test para limpiar el historial."""
    # Agregar algunos mensajes
    iot_agent.conversation_history.append(Mock())
    iot_agent.conversation_history.append(Mock())
    
    initial_length = len(iot_agent.conversation_history)
    assert initial_length > 1, "Debe tener más de un mensaje inicialmente"
    
    iot_agent.clear_history()
    
    # Debe quedar solo el prompt del sistema
    assert len(iot_agent.conversation_history) == 1, "Debe quedar solo el prompt del sistema"


def test_get_conversation_summary(iot_agent):
    """Test para obtener resumen de conversación."""
    summary = iot_agent.get_conversation_summary()
    
    assert 'total_messages' in summary, "Debe incluir total de mensajes"
    assert 'user_messages' in summary, "Debe incluir mensajes de usuario"
    assert 'assistant_messages' in summary, "Debe incluir mensajes del asistente"
    assert isinstance(summary['total_messages'], int), "Total debe ser un entero"


@pytest.mark.asyncio
async def test_error_handling(iot_agent):
    """Test para manejo de errores."""
    # Simular error en las herramientas
    with patch.object(iot_agent.db_tools, 'get_sensor_data_tool', side_effect=Exception("Test error")):
        
        response = await iot_agent.process_message("¿Cuáles son los datos de sensores?")
        
        # Debe manejar el error gracefully
        assert isinstance(response, str), "Debe retornar una respuesta válida"
        assert "error" in response.lower() or "lo siento" in response.lower(), "Debe indicar que hubo un error"


if __name__ == "__main__":
    # Ejecutar tests específicos si se ejecuta directamente
    pytest.main([__file__, "-v"])
