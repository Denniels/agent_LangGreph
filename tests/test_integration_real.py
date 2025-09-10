#!/usr/bin/env python3
"""
Test de integración simple
==========================

Test simple que demuestra la funcionalidad del agente IoT con la base de datos real.
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.database.db_connector import get_db
from modules.tools.database_tools import DatabaseTools
from modules.tools.analysis_tools import AnalysisTools


@pytest.mark.asyncio
async def test_integration_with_real_database():
    """
    Test de integración que demuestra el funcionamiento completo del sistema.
    """
    print("\n🚀 Iniciando test de integración...")
    
    # Test 1: Conexión a base de datos
    print("📊 Test 1: Conexión a base de datos")
    db = await get_db()
    health = await db.health_check()
    assert health, "La base de datos debe estar accesible"
    print("   ✅ Conexión exitosa")
    
    # Test 2: Database Tools
    print("🔧 Test 2: Database Tools")
    db_tools = DatabaseTools()
    
    # Obtener dispositivos
    devices = await db_tools.get_devices_tool()
    assert isinstance(devices, list), "Debe retornar una lista de dispositivos"
    print(f"   ✅ {len(devices)} dispositivos encontrados")
    
    # Obtener datos de sensores
    sensor_data = await db_tools.get_sensor_data_tool(limit=10)
    assert isinstance(sensor_data, list), "Debe retornar una lista de datos"
    print(f"   ✅ {len(sensor_data)} registros de sensores obtenidos")
    
    # Obtener alertas/eventos
    alerts = await db_tools.get_alerts_tool()
    assert isinstance(alerts, list), "Debe retornar una lista de alertas"
    print(f"   ✅ {len(alerts)} eventos/alertas encontrados")
    
    # Test 3: Analysis Tools
    print("📈 Test 3: Analysis Tools")
    analysis_tools = AnalysisTools()
    
    if sensor_data:
        # Analizar tendencias
        trends = analysis_tools.analyze_sensor_trends(sensor_data)
        assert isinstance(trends, dict), "Debe retornar análisis de tendencias"
        print(f"   ✅ Análisis de tendencias completado")
        
        # Detectar anomalías
        anomalies = analysis_tools.detect_anomalies(sensor_data)
        assert isinstance(anomalies, dict), "Debe retornar detección de anomalías"
        print(f"   ✅ Detección de anomalías completada")
        
        # Generar reporte
        report = analysis_tools.generate_summary_report(sensor_data, alerts)
        assert isinstance(report, dict), "Debe retornar un reporte"
        assert "summary" in report, "El reporte debe tener un resumen"
        print(f"   ✅ Reporte generado exitosamente")
    
    # Test 4: Crear evento de prueba
    print("✏️ Test 4: Crear evento de prueba")
    if devices:
        test_device = devices[0].get('device_id', 'test_device')
        success = await db_tools.create_alert_tool(
            device_id=test_device,
            alert_type='integration_test',
            message='Test de integración exitoso',
            severity='medium'
        )
        assert success, "Debe poder crear eventos"
        print(f"   ✅ Evento creado para dispositivo {test_device}")
    
    print("🎉 ¡Test de integración completado exitosamente!")
    print("=" * 60)
    print("✅ Base de datos funcionando")
    print("✅ Database Tools funcionando") 
    print("✅ Analysis Tools funcionando")
    print("✅ Creación de eventos funcionando")
    print("✅ Sistema completo operativo")


if __name__ == "__main__":
    # Ejecutar el test directamente
    asyncio.run(test_integration_with_real_database())
