# Tests del Agente Conversacional IoT

Este directorio contiene la suite completa de tests para el proyecto del Agente Conversacional IoT.

## 📁 Estructura de Tests

```
tests/
├── __init__.py              # Información del módulo de tests
├── conftest.py              # Configuración global y fixtures
├── pytest.ini              # Configuración de pytest
├── README.md               # Esta documentación
├── test_database.py        # Tests de base de datos
├── test_agent.py          # Tests del agente conversacional
├── test_tools.py          # Tests de herramientas
└── test_system.py         # Tests de integración completos
```

## 🚀 Cómo Ejecutar los Tests

### Requisitos Previos

1. **Entorno virtual activado**:
   ```bash
   # Windows
   agente\Scripts\activate
   
   # Linux/Mac
   source agente/bin/activate
   ```

2. **Dependencias instaladas**:
   ```bash
   pip install pytest pytest-asyncio
   ```

### Comandos de Ejecución

#### Ejecutar Todos los Tests
```bash
pytest
```

#### Ejecutar Tests Específicos
```bash
# Por archivo
pytest tests/test_database.py
pytest tests/test_agent.py
pytest tests/test_tools.py

# Por función específica
pytest tests/test_database.py::test_database_connection
pytest tests/test_agent.py::test_agent_initialization
```

#### Ejecutar por Categorías
```bash
# Solo tests unitarios
pytest -m unit

# Solo tests de integración
pytest -m integration

# Tests que requieren base de datos
pytest -m database

# Tests del agente
pytest -m agent
```

#### Opciones Útiles
```bash
# Modo verbose (más detalle)
pytest -v

# Mostrar output de print statements
pytest -s

# Ejecutar tests en paralelo (requiere pytest-xdist)
pytest -n auto

# Detener en el primer fallo
pytest -x

# Generar reporte de cobertura
pytest --cov=modules --cov-report=html
```

## 📋 Tipos de Tests

### 🔧 Tests Unitarios (`test_*.py`)

- **test_database.py**: 
  - Conexión a base de datos
  - Operaciones CRUD
  - Manejo de errores
  - Health checks

- **test_agent.py**:
  - Inicialización del agente
  - Procesamiento de mensajes
  - Determinación de herramientas
  - Manejo de contexto

- **test_tools.py**:
  - Herramientas de base de datos
  - Herramientas de análisis
  - Detección de anomalías
  - Generación de reportes

### 🔗 Tests de Integración (`test_system.py`)

- Funcionamiento completo del sistema
- Integración entre componentes
- Flujos de trabajo end-to-end
- Demostraciones interactivas

## 🏷️ Marcadores de Tests

Los tests están categorizados con marcadores para facilitar la ejecución selectiva:

- `@pytest.mark.unit`: Tests unitarios básicos
- `@pytest.mark.integration`: Tests de integración
- `@pytest.mark.slow`: Tests que toman más tiempo
- `@pytest.mark.database`: Tests que requieren DB
- `@pytest.mark.agent`: Tests específicos del agente
- `@pytest.mark.tools`: Tests de herramientas

### Ejemplos de Uso
```bash
# Solo tests rápidos (excluir lentos)
pytest -m "not slow"

# Tests de base de datos únicamente
pytest -m database

# Combinaciones
pytest -m "unit and not slow"
pytest -m "agent or tools"
```

## 📊 Fixtures Disponibles

Las fixtures están definidas en `conftest.py` y están disponibles para todos los tests:

- `sample_device_data`: Datos de dispositivos de ejemplo
- `sample_sensor_data`: Datos de sensores de ejemplo  
- `sample_alert_data`: Datos de alertas de ejemplo
- `setup_test_environment`: Configuración automática del entorno

### Usar Fixtures en Tests
```python
def test_example(sample_sensor_data):
    # sample_sensor_data está disponible automáticamente
    assert len(sample_sensor_data) > 0
```

## 🐛 Depuración de Tests

### Ver Output Detallado
```bash
# Mostrar prints y logs
pytest -s -v

# Mostrar traceback completo
pytest --tb=long

# Debugger interactivo en fallos
pytest --pdb
```

### Tests Específicos con Filtros
```bash
# Por nombre de función
pytest -k "test_database"

# Por nombre de clase
pytest -k "TestDatabaseTools"

# Expresiones complejas
pytest -k "database and not slow"
```

## 📈 Cobertura de Código

Para generar reportes de cobertura:

```bash
# Instalar pytest-cov
pip install pytest-cov

# Generar reporte en terminal
pytest --cov=modules

# Generar reporte HTML
pytest --cov=modules --cov-report=html

# Ver reporte en navegador
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html # Windows
```

## 🔧 Configuración Personalizada

### Variables de Entorno para Tests

Los tests usan variables de entorno mockeadas definidas en `conftest.py`. Para tests que requieren configuración real:

```bash
# Crear archivo .env.test
DB_HOST=test_host
DB_PORT=5432
DB_NAME=test_iot_db
OPENAI_API_KEY=test_key
```

### Configuración de pytest.ini

El archivo `pytest.ini` contiene la configuración predeterminada. Puedes modificarla según tus necesidades:

```ini
[tool:pytest]
addopts = -v --tb=short --strict-markers
testpaths = tests
markers = 
    unit: Unit tests
    integration: Integration tests
```

## 🚨 Resolución de Problemas

### Errores Comunes

1. **ImportError de módulos**:
   ```bash
   # Asegúrate de estar en el directorio raíz
   cd /path/to/agent_LangGreph
   pytest
   ```

2. **Tests de base de datos fallan**:
   ```bash
   # Verificar configuración de DB en .env
   # O ejecutar solo tests unitarios
   pytest -m "not database"
   ```

3. **Tests asyncio fallan**:
   ```bash
   # Instalar pytest-asyncio
   pip install pytest-asyncio
   ```

### Logs y Debugging

```python
# Agregar logging en tests
import logging
logging.basicConfig(level=logging.DEBUG)

def test_with_logs():
    logger = logging.getLogger(__name__)
    logger.debug("Debug message in test")
```

## 📝 Contribuir con Tests

### Agregar Nuevos Tests

1. **Crear archivo de test**: `test_nuevo_modulo.py`
2. **Usar convenciones**: Nombres empiezan con `test_`
3. **Agregar marcadores**: `@pytest.mark.unit`
4. **Documentar**: Docstrings explicando qué prueba cada test
5. **Usar fixtures**: Reutilizar datos de ejemplo

### Ejemplo de Test Nuevo
```python
import pytest

@pytest.mark.unit
def test_nueva_funcionalidad(sample_data):
    """Test para verificar nueva funcionalidad."""
    # Arrange
    input_data = sample_data
    
    # Act
    result = nueva_funcion(input_data)
    
    # Assert
    assert result is not None
    assert isinstance(result, dict)
```

---

Para más información sobre testing en Python, consulta la [documentación de pytest](https://docs.pytest.org/).
