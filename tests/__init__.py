"""
Tests para el Agente Conversacional IoT
======================================

Suite completa de tests para verificar el funcionamiento del agente IoT.

Estructura de tests:
- test_database.py: Tests para conectores y operaciones de base de datos
- test_agent.py: Tests para el agente conversacional principal
- test_tools.py: Tests para herramientas de análisis y base de datos
- test_system.py: Tests de integración y sistema completo
- conftest.py: Configuración global y fixtures compartidas
- pytest.ini: Configuración de pytest

Cómo ejecutar los tests:
------------------------

# Ejecutar todos los tests
pytest

# Ejecutar tests específicos
pytest tests/test_database.py
pytest tests/test_agent.py

# Ejecutar tests por categoría
pytest -m unit
pytest -m integration
pytest -m slow

# Ejecutar con cobertura
pytest --cov=modules

# Ejecutar en modo verbose
pytest -v

# Ejecutar tests específicos por nombre
pytest -k "test_database_connection"

Marcadores disponibles:
----------------------
- unit: Tests unitarios
- integration: Tests de integración
- slow: Tests que toman más tiempo
- database: Tests que requieren base de datos
- agent: Tests del agente conversacional
- tools: Tests de herramientas
"""

__version__ = "1.0.0"
__author__ = "Agente IoT Team"
