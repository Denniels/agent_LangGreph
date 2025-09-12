# Estructura del Proyecto IoT Conversacional

## 📁 Repositorio Reorganizado (Buenas Prácticas)

```
agent_LangGreph/
├── 📄 .env                           # Variables de entorno
├── 📄 main.py                        # Punto de entrada principal
├── 📄 README.md                      # Documentación del proyecto
├── 📄 requirements.txt               # Dependencias de Python
│
├── 📁 agente/                        # Entorno virtual Python
│   ├── 📁 Lib/site-packages/        # Paquetes instalados
│   ├── 📁 Scripts/                   # Ejecutables del entorno
│   └── 📄 pyvenv.cfg                 # Configuración del entorno
│
├── 📁 database/                      # Scripts y esquemas de BD
│   ├── 📄 schema.sql                 # Esquema de PostgreSQL
│   └── 📄 sample_data.sql            # Datos de ejemplo
│
├── 📁 logs/                          # Archivos de log
│   └── 📄 app.log                    # Log principal de la aplicación
│
├── 📁 modules/                       # Código fuente modularizado
│   ├── 📄 __init__.py
│   │
│   ├── 📁 agents/                    # Agentes conversacionales
│   │   ├── 📄 __init__.py
│   │   ├── 📄 graph_builder.py       # Constructor de grafos LangGraph
│   │   └── 📄 iot_agent.py           # Agente principal IoT
│   │
│   ├── 📁 database/                  # Conectores y modelos de BD
│   │   ├── 📄 __init__.py
│   │   ├── 📄 db_connector.py        # Conector PostgreSQL asyncio
│   │   └── 📄 models.py              # Modelos de datos
│   │
│   ├── 📁 tools/                     # Herramientas del agente
│   │   ├── 📄 __init__.py
│   │   ├── 📄 analysis_tools.py      # Análisis de datos IoT
│   │   └── 📄 database_tools.py      # Herramientas de BD
│   │
│   └── 📁 utils/                     # Utilidades comunes
│       ├── 📄 __init__.py
│       ├── 📄 config.py              # Configuración
│       └── 📄 logger.py              # Sistema de logging
│
├── 📁 streamlit_app/                 # Interfaz web Streamlit
│   └── 📄 app.py                     # Aplicación web principal
│
└── 📁 tests/                         # Suite de pruebas completa
    ├── 📄 __init__.py
    ├── 📄 conftest.py                # Configuración de pytest
    ├── 📄 pytest.ini                 # Configuración de pruebas
    ├── 📄 README.md                  # Documentación de tests
    │
    ├── 📄 test_agent.py              # Tests de agentes
    ├── 📄 test_database.py           # Tests de base de datos
    ├── 📄 test_tools.py              # Tests de herramientas
    ├── 📄 test_system.py             # Tests de sistema
    ├── 📄 test_integration_simple.py # Tests de integración
    │
    ├── 📄 test_integration_real.py   # ✅ Test con BD real (FUNCIONAL)
    ├── 📄 test_real_db.py            # Tests específicos BD real
    ├── 📄 diagnose_db.py             # Diagnóstico de conectividad
    └── 📄 explore_db.py              # Exploración de estructura BD
```

## 🎯 Estado Actual del Proyecto

### ✅ Componentes Funcionando
- **Base de Datos Real**: PostgreSQL 10.23 en Jetson Nano (192.168.0.102)
- **Conectividad**: SSH + PostgreSQL configurado para acceso externo  
- **Datos Reales**: 4.2M registros de sensores, 6 dispositivos IoT activos
- **Análisis**: Herramientas de análisis procesando datos en vivo
- **Tests de Integración**: `test_integration_real.py` PASANDO ✅

### 🔧 Hardware IoT Conectado
- **ESP32 WiFi**: Sensores LDR y NTC (dispositivo: esp32_wifi_001)
- **Arduino Ethernet**: Sensores de temperatura (dispositivo: arduino_eth_002)  
- **Dispositivos de Red**: Monitoreo de conectividad (net_device_*)

### 📊 Base de Datos Real
```sql
-- Tablas principales
devices       (6 dispositivos activos)
sensor_data   (4.2M registros históricos)
system_events (alertas y eventos del sistema)
```

### 🧪 Testing
- **Tests Principales**: `test_integration_real.py` - Prueba completa con BD real
- **Tests Unitarios**: Necesitan ajustes en fixtures (algunos fallan)
- **Cobertura**: Componentes principales cubiertos

## 🚀 Próximos Pasos

1. **Integración IA**: Configurar Ollama para conversación natural
2. **Interfaz Web**: Completar aplicación Streamlit
3. **Optimización**: Mejorar rendimiento de queries y análisis
4. **Documentación**: Completar documentación de API

## 📝 Arquitectura

```
Usuario → Streamlit → Agente IoT → LangGraph → Herramientas → PostgreSQL
                         ↓
                   Análisis IA ← Ollama
```

---
**Estado**: Repositorio reorganizado siguiendo mejores prácticas ✅  
**Base de Datos**: Conectada y funcionando con datos reales ✅  
**Tests**: Test principal de integración funcionando ✅  
**Listo para**: Integración de modelo conversacional con Ollama 🚀
