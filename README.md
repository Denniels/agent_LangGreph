# 🤖 Agente Conversacional IoT con LangGraph

Un agente conversacional inteligente diseñado para gestionar y analizar sistemas IoT (Internet de las Cosas) utilizando LangGraph, PostgreSQL y Streamlit.

## 🚀 Características

- **Agente Conversacional**: Interfaz natural para consultar datos IoT
- **Análisis en Tiempo Real**: Detección de tendencias y anomalías
- **Gestión de Alertas**: Sistema de alertas automático y manual
- **Dashboard Interactivo**: Visualización de datos con Streamlit
- **Base de Datos PostgreSQL**: Almacenamiento robusto de datos IoT
- **Arquitectura Modular**: Código organizado y escalable

## 📋 Requisitos

- Python 3.8+
- PostgreSQL 12+
- OpenAI API Key
- Git

## 🛠️ Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/agent_LangGreph.git
cd agent_LangGreph
```

### 2. Crear y Activar Entorno Virtual

```bash
# Crear entorno virtual
python -m venv agente

# Activar entorno virtual
# En Windows:
agente\Scripts\activate
# En Linux/Mac:
source agente/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# PostgreSQL Configuration
DB_HOST=192.168.0.102
DB_PORT=5432
DB_NAME=iot_db
DB_USER=iot_user
DB_PASSWORD=DAms15820

# OpenAI Configuration
OPENAI_API_KEY=tu_openai_api_key_aqui
OPENAI_MODEL=gpt-4

# Application Configuration
APP_NAME=Agente IoT
APP_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO

# Streamlit Configuration
STREAMLIT_PORT=8501
STREAMLIT_HOST=localhost
```

### 5. Configurar Base de Datos

Ejecutar los scripts SQL en PostgreSQL:

```bash
# Conectar a PostgreSQL como superusuario
psql -U postgres -h 192.168.0.102

# Crear base de datos y usuario
CREATE DATABASE iot_db;
CREATE USER iot_user WITH PASSWORD 'DAms15820';
GRANT ALL PRIVILEGES ON DATABASE iot_db TO iot_user;

# Conectar a la nueva base de datos
\c iot_db

# Ejecutar esquema
\i database/schema.sql

# Insertar datos de ejemplo
\i database/sample_data.sql
```

## 🚀 Uso

### Ejecutar la Aplicación

```bash
python main.py
```

Opciones disponibles:
1. **Aplicación Streamlit** (recomendado) - Interfaz web completa
2. **Probar conexión DB** - Verificar conectividad
3. **Probar agente** - Prueba de funcionalidad
4. **Modo CLI** - Interfaz de línea de comandos
5. **Salir**

### Acceder a la Interfaz Web

Una vez iniciada la aplicación Streamlit, visitar:
```
http://localhost:8501
```

## 📊 Funcionalidades del Agente

### Consultas Soportadas

- **Datos de Sensores**: "¿Cuáles son los últimos datos de temperatura?"
- **Estado de Dispositivos**: "¿Qué dispositivos están activos?"
- **Gestión de Alertas**: "¿Hay alertas activas en el sistema?"
- **Análisis de Tendencias**: "Analiza las tendencias de los sensores"
- **Detección de Anomalías**: "¿Has detectado alguna anomalía?"
- **Reportes**: "Genera un reporte del sistema"

### Capacidades de Análisis

- Análisis de tendencias temporales
- Detección automática de anomalías
- Generación de reportes resumidos
- Alertas basadas en umbrales
- Visualizaciones interactivas

## 🏗️ Arquitectura

```
agent_LangGreph/
├── modules/                    # Módulos principales
│   ├── agents/                # Agentes conversacionales
│   │   ├── iot_agent.py      # Agente principal IoT
│   │   └── graph_builder.py  # Constructor de gráficos LangGraph
│   ├── database/             # Conectores de base de datos
│   │   ├── db_connector.py   # Conector PostgreSQL
│   │   └── models.py         # Modelos de datos
│   ├── tools/                # Herramientas del agente
│   │   ├── database_tools.py # Herramientas de DB
│   │   └── analysis_tools.py # Herramientas de análisis
│   └── utils/                # Utilidades
│       ├── config.py         # Configuración
│       └── logger.py         # Sistema de logging
├── streamlit_app/            # Aplicación web
│   └── app.py               # Interfaz Streamlit
├── database/                # Scripts de DB
│   ├── schema.sql          # Esquema de tablas
│   └── sample_data.sql     # Datos de ejemplo
├── tests/                   # Tests unitarios
├── logs/                    # Archivos de log
├── agente/                  # Entorno virtual
├── .env                     # Variables de entorno
├── requirements.txt         # Dependencias
└── main.py                 # Punto de entrada
```

## � Configuración Avanzada

### Variables de Entorno Adicionales

```env
# Logging
LOG_LEVEL=DEBUG              # DEBUG, INFO, WARNING, ERROR

# Database Connection Pool
DB_MIN_POOL_SIZE=1
DB_MAX_POOL_SIZE=10

# OpenAI Settings
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=2000

# Streamlit Customization
STREAMLIT_THEME=light
```

### Personalización del Agente

El comportamiento del agente se puede personalizar modificando:

- `modules/agents/iot_agent.py` - Lógica principal del agente
- `modules/tools/` - Herramientas disponibles
- `streamlit_app/app.py` - Interfaz de usuario

## 📈 Monitoreo y Logs

Los logs se almacenan en:
- `logs/app.log` - Log principal de la aplicación
- Consola - Output en tiempo real

Niveles de log configurables:
- DEBUG: Información detallada
- INFO: Información general
- WARNING: Advertencias
- ERROR: Errores críticos

## 🧪 Testing

Ejecutar tests unitarios:

```bash
# Ejecutar todos los tests
python -m pytest tests/

# Ejecutar tests específicos
python -m pytest tests/test_database.py

# Con cobertura
python -m pytest --cov=modules tests/
```

## 🛡️ Seguridad

- Variables de entorno para credenciales sensibles
- Conexiones de DB con pool de conexiones
- Validación de inputs en el agente
- Logging de seguridad

## 📝 API Reference

### Métodos Principales del Agente

```python
# Procesar mensaje del usuario
response = await agent.process_message("tu consulta aquí")

# Obtener datos de sensores
data = await db_tools.get_sensor_data_tool(device_id="TEMP_001", limit=10)

# Crear alerta
success = await db_tools.create_alert_tool(
    device_id="TEMP_001",
    alert_type="high_temperature", 
    message="Temperatura alta",
    severity="high"
)

# Analizar tendencias
analysis = analysis_tools.analyze_sensor_trends(sensor_data)
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

Para reportar bugs o solicitar características:

1. Crear un issue en GitHub
2. Incluir información detallada del problema
3. Adjuntar logs relevantes

## 📚 Recursos Adicionales

- [Documentación de LangGraph](https://langchain-ai.github.io/langgraph/)
- [Documentación de Streamlit](https://docs.streamlit.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [OpenAI API Reference](https://platform.openai.com/docs/)

---

**Desarrollado con ❤️ usando LangGraph, Streamlit y PostgreSQL**
