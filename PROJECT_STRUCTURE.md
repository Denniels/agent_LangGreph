# 📁 ESTRUCTURA DEL PROYECTO - Agent LangGraph IoT# Estructura del Proyecto IoT Conversacional



## 🏗️ **ARQUITECTURA REORGANIZADA**## 📁 Repositorio Reorganizado (Buenas Prácticas)



``````

agent_LangGreph/agent_LangGreph/

│├── 📄 .env                           # Variables de entorno

├── 📄 README.md                     # Presentación principal del proyecto├── 📄 main.py                        # Punto de entrada principal

├── 📄 requirements.txt              # Dependencias Python├── 📄 README.md                      # Documentación del proyecto

├── 📄 main.py                      # Punto de entrada principal├── 📄 requirements.txt               # Dependencias de Python

├── 📄 app.py                       # Aplicación principal│

├── 🔧 .env                         # Variables de entorno├── 📁 agente/                        # Entorno virtual Python

├── ⚙️ .gitignore                   # Configuración Git│   ├── 📁 Lib/site-packages/        # Paquetes instalados

││   ├── 📁 Scripts/                   # Ejecutables del entorno

├── 📂 streamlit_app/               # 🚀 APLICACIÓN WEB PRINCIPAL│   └── 📄 pyvenv.cfg                 # Configuración del entorno

│   ├── app_groq_cloud.py          # App principal con Groq + Cloud│

│   ├── app_langgraph.py           # Interfaz LangGraph├── 📁 database/                      # Scripts y esquemas de BD

│   └── ...                        # Otras variantes de apps│   ├── 📄 schema.sql                 # Esquema de PostgreSQL

││   └── 📄 sample_data.sql            # Datos de ejemplo

├── 📂 modules/                     # 🧩 MÓDULOS CORE DEL SISTEMA│

│   ├── agents/                    # Agentes inteligentes├── 📁 logs/                          # Archivos de log

│   │   ├── cloud_iot_agent.py     # Agente IoT principal (Groq)│   └── 📄 app.log                    # Log principal de la aplicación

│   │   ├── reporting.py           # Generador de reportes│

│   │   └── ...├── 📁 modules/                       # Código fuente modularizado

│   ├── tools/                     # Herramientas y conectores│   ├── 📄 __init__.py

│   │   ├── jetson_api_connector.py # Conector API Jetson│   │

│   │   └── ...│   ├── 📁 agents/                    # Agentes conversacionales

│   ├── utils/                     # Utilidades compartidas│   │   ├── 📄 __init__.py

│   ├── database/                  # Conectores de base de datos│   │   ├── 📄 graph_builder.py       # Constructor de grafos LangGraph

│   ├── app_simple_reports.py      # Generador de reportes simple│   │   └── 📄 iot_agent.py           # Agente principal IoT

│   ├── report_handler.py          # Manejador de reportes│   │

│   └── config_cloud.py            # Configuración de nube│   ├── 📁 database/                  # Conectores y modelos de BD

││   │   ├── 📄 __init__.py

├── 📂 tests/                      # 🧪 TESTING Y DEBUGGING│   │   ├── 📄 db_connector.py        # Conector PostgreSQL asyncio

│   ├── test_*.py                  # Tests automatizados│   │   └── 📄 models.py              # Modelos de datos

│   ├── debug_*.py                 # Scripts de debugging│   │

│   ├── analyze_*.py               # Scripts de análisis│   ├── 📁 tools/                     # Herramientas del agente

│   ├── check_*.py                 # Scripts de verificación│   │   ├── 📄 __init__.py

│   ├── explore_*.py               # Scripts de exploración│   │   ├── 📄 analysis_tools.py      # Análisis de datos IoT

│   ├── diagnose_*.py              # Scripts de diagnóstico│   │   └── 📄 database_tools.py      # Herramientas de BD

│   └── *.pdf                      # Reportes de prueba│   │

││   └── 📁 utils/                     # Utilidades comunes

├── 📂 docs/                       # 📚 DOCUMENTACIÓN│       ├── 📄 __init__.py

│   ├── DEPLOYMENT_GUIDE.md        # Guía de despliegue│       ├── 📄 config.py              # Configuración

│   ├── CORRECCIONES_REPORTES.md   # Historial de correcciones│       └── 📄 logger.py              # Sistema de logging

│   ├── SISTEMA_COMPLETO.md        # Documentación del sistema│

│   └── ...                        # Otros documentos técnicos├── 📁 streamlit_app/                 # Interfaz web Streamlit

││   └── 📄 app.py                     # Aplicación web principal

├── 📂 prompts/                    # 🤖 PROMPTS DEL SISTEMA│

│   ├── system_prompt.py           # Prompts del sistema└── 📁 tests/                         # Suite de pruebas completa

│   └── query_prompts.py           # Prompts de consultas    ├── 📄 __init__.py

│    ├── 📄 conftest.py                # Configuración de pytest

├── 📂 database/                   # 🗄️ ESQUEMAS DE BD    ├── 📄 pytest.ini                 # Configuración de pruebas

│   └── schema.sql                 # Esquema de base de datos    ├── 📄 README.md                  # Documentación de tests

│    │

├── 📂 logs/                       # 📋 LOGS DEL SISTEMA    ├── 📄 test_agent.py              # Tests de agentes

│   └── app.log                    # Logs de aplicación    ├── 📄 test_database.py           # Tests de base de datos

│    ├── 📄 test_tools.py              # Tests de herramientas

└── 📂 agente/                     # 🏗️ ENTORNO VIRTUAL (legacy)    ├── 📄 test_system.py             # Tests de sistema

    └── ...                        # Archivos del entorno virtual    ├── 📄 test_integration_simple.py # Tests de integración

```    │

    ├── 📄 test_integration_real.py   # ✅ Test con BD real (FUNCIONAL)

## 🎯 **ARCHIVOS PRINCIPALES DE PRODUCCIÓN**    ├── 📄 test_real_db.py            # Tests específicos BD real

    ├── 📄 diagnose_db.py             # Diagnóstico de conectividad

### **Aplicación Web (Streamlit Cloud)**    └── 📄 explore_db.py              # Exploración de estructura BD

- `streamlit_app/app_groq_cloud.py` - Aplicación principal en producción```

- `modules/agents/cloud_iot_agent.py` - Agente IoT inteligente

- `modules/agents/reporting.py` - Generador de reportes profesionales## 🎯 Estado Actual del Proyecto

- `modules/tools/jetson_api_connector.py` - Conector API de datos

### ✅ Componentes Funcionando

### **Configuración**- **Base de Datos Real**: PostgreSQL 10.23 en Jetson Nano (192.168.0.102)

- `.env` - Variables de entorno (API keys, configuración)- **Conectividad**: SSH + PostgreSQL configurado para acceso externo  

- `requirements.txt` - Dependencias del proyecto- **Datos Reales**: 4.2M registros de sensores, 6 dispositivos IoT activos

- `.streamlit/config.toml` - Configuración de Streamlit- **Análisis**: Herramientas de análisis procesando datos en vivo

- **Tests de Integración**: `test_integration_real.py` PASANDO ✅

### **Entrada del Sistema**

- `main.py` - Punto de entrada principal### 🔧 Hardware IoT Conectado

- `app.py` - Aplicación base- **ESP32 WiFi**: Sensores LDR y NTC (dispositivo: esp32_wifi_001)

- **Arduino Ethernet**: Sensores de temperatura (dispositivo: arduino_eth_002)  

## 🧪 **TESTING Y DESARROLLO**- **Dispositivos de Red**: Monitoreo de conectividad (net_device_*)



Todos los archivos de testing, debugging y desarrollo están organizados en:### 📊 Base de Datos Real

- `tests/` - Scripts de prueba, debugging y análisis```sql

- `docs/` - Documentación técnica y guías-- Tablas principales

devices       (6 dispositivos activos)

## 🚀 **COMANDOS DE EJECUCIÓN**sensor_data   (4.2M registros históricos)

system_events (alertas y eventos del sistema)

```bash```

# Desarrollo local

streamlit run streamlit_app/app_groq_cloud.py### 🧪 Testing

- **Tests Principales**: `test_integration_real.py` - Prueba completa con BD real

# Punto de entrada principal- **Tests Unitarios**: Necesitan ajustes en fixtures (algunos fallan)

python main.py- **Cobertura**: Componentes principales cubiertos



# Tests## 🚀 Próximos Pasos

python -m pytest tests/

```1. **Integración IA**: Configurar Ollama para conversación natural

2. **Interfaz Web**: Completar aplicación Streamlit

## 📋 **NOTAS DE REORGANIZACIÓN**3. **Optimización**: Mejorar rendimiento de queries y análisis

4. **Documentación**: Completar documentación de API

- ✅ Archivos .md movidos a `docs/` (excepto README.md)

- ✅ Scripts de test/debug movidos a `tests/`## 📝 Arquitectura

- ✅ Módulos auxiliares movidos a `modules/`

- ✅ Estructura limpia y organizada```

- ✅ Separación clara entre producción y desarrolloUsuario → Streamlit → Agente IoT → LangGraph → Herramientas → PostgreSQL

                         ↓

**Fecha de reorganización:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")                   Análisis IA ← Ollama
```

---
**Estado**: Repositorio reorganizado siguiendo mejores prácticas ✅  
**Base de Datos**: Conectada y funcionando con datos reales ✅  
**Tests**: Test principal de integración funcionando ✅  
**Listo para**: Integración de modelo conversacional con Ollama 🚀
