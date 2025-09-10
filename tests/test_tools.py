"""
Tests para las herramientas del agente
======================================

Tests unitarios para verificar la funcionalidad de las herramientas de análisis y base de datos.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from modules.tools.database_tools import DatabaseTools
from modules.tools.analysis_tools import AnalysisTools


class TestDatabaseTools:
    """Tests para DatabaseTools."""
    
    @pytest.fixture
    async def db_tools(self):
        """Fixture para DatabaseTools."""
        tools = DatabaseTools()
        # Mock del conector de DB
        mock_db = Mock()
        tools.db = mock_db
        yield tools
    
    @pytest.mark.asyncio
    async def test_get_sensor_data_tool(self, db_tools):
        """Test para obtener datos de sensores."""
        # Mock de datos de sensores
        mock_data = [
            {
                "device_id": "TEMP_001",
                "sensor_type": "temperature",
                "value": 25.5,
                "unit": "°C",
                "timestamp": datetime.now(),
                "location": "Office"
            }
        ]
        
        db_tools.db.get_sensor_data.return_value = mock_data
        
        result = await db_tools.get_sensor_data_tool(device_id="TEMP_001", limit=10)
        
        assert result == mock_data
        db_tools.db.get_sensor_data.assert_called_once_with("TEMP_001", 10)
    
    @pytest.mark.asyncio
    async def test_get_devices_tool(self, db_tools):
        """Test para obtener dispositivos."""
        mock_devices = [
            {
                "device_id": "TEMP_001",
                "device_name": "Temperature Sensor",
                "device_type": "temperature_sensor",
                "location": "Office",
                "status": "active"
            }
        ]
        
        db_tools.db.get_active_devices.return_value = mock_devices
        
        result = await db_tools.get_devices_tool()
        
        assert result == mock_devices
        db_tools.db.get_active_devices.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_alerts_tool(self, db_tools):
        """Test para obtener alertas."""
        mock_alerts = [
            {
                "alert_id": 1,
                "device_id": "TEMP_001",
                "alert_type": "high_temperature",
                "message": "Temperature too high",
                "severity": "high",
                "status": "active"
            }
        ]
        
        db_tools.db.get_alerts.return_value = mock_alerts
        
        result = await db_tools.get_alerts_tool(active_only=True)
        
        assert result == mock_alerts
        db_tools.db.get_alerts.assert_called_once_with(True)
    
    @pytest.mark.asyncio
    async def test_create_alert_tool(self, db_tools):
        """Test para crear alertas."""
        db_tools.db.create_alert.return_value = True
        
        result = await db_tools.create_alert_tool(
            device_id="TEMP_001",
            alert_type="test_alert",
            message="Test message",
            severity="medium"
        )
        
        assert result is True
        db_tools.db.create_alert.assert_called_once_with(
            "TEMP_001", "test_alert", "Test message", "medium"
        )
    
    @pytest.mark.asyncio
    async def test_error_handling(self, db_tools):
        """Test para manejo de errores."""
        db_tools.db.get_sensor_data.side_effect = Exception("Database error")
        
        result = await db_tools.get_sensor_data_tool()
        
        assert result == []  # Debe retornar lista vacía en caso de error


class TestAnalysisTools:
    """Tests para AnalysisTools."""
    
    @pytest.fixture
    def analysis_tools(self):
        """Fixture para AnalysisTools."""
        return AnalysisTools()
    
    @pytest.fixture
    def sample_sensor_data(self):
        """Datos de sensores de ejemplo."""
        base_time = datetime.now()
        return [
            {
                "device_id": "TEMP_001",
                "sensor_type": "temperature",
                "value": 20.0 + i,
                "unit": "°C",
                "timestamp": base_time - timedelta(hours=i),
                "location": "Office"
            }
            for i in range(10)
        ]
    
    def test_analyze_sensor_trends(self, analysis_tools, sample_sensor_data):
        """Test para análisis de tendencias."""
        result = analysis_tools.analyze_sensor_trends(sample_sensor_data)
        
        assert 'total_readings' in result
        assert 'devices_analyzed' in result
        assert 'sensor_types' in result
        assert 'by_sensor_type' in result
        
        assert result['total_readings'] == len(sample_sensor_data)
        assert result['devices_analyzed'] == 1
        assert 'temperature' in result['sensor_types']
        
        # Verificar análisis específico por tipo de sensor
        temp_analysis = result['by_sensor_type']['temperature']
        assert 'avg_value' in temp_analysis
        assert 'min_value' in temp_analysis
        assert 'max_value' in temp_analysis
        assert 'trend' in temp_analysis
    
    def test_analyze_empty_data(self, analysis_tools):
        """Test para datos vacíos."""
        result = analysis_tools.analyze_sensor_trends([])
        
        assert 'error' in result
        assert result['error'] == "No hay datos para analizar"
    
    def test_calculate_trend(self, analysis_tools):
        """Test para cálculo de tendencias."""
        # Tendencia creciente
        increasing_values = [1.0, 2.0, 3.0, 4.0, 5.0]
        trend = analysis_tools._calculate_trend(increasing_values)
        assert trend == "increasing"
        
        # Tendencia decreciente
        decreasing_values = [5.0, 4.0, 3.0, 2.0, 1.0]
        trend = analysis_tools._calculate_trend(decreasing_values)
        assert trend == "decreasing"
        
        # Tendencia estable
        stable_values = [3.0, 3.1, 2.9, 3.0, 3.1]
        trend = analysis_tools._calculate_trend(stable_values)
        assert trend == "stable"
        
        # Datos insuficientes
        insufficient_data = [1.0]
        trend = analysis_tools._calculate_trend(insufficient_data)
        assert trend == "insufficient_data"
    
    def test_detect_anomalies(self, analysis_tools, sample_sensor_data):
        """Test para detección de anomalías."""
        # Agregar un valor anómalo
        anomalous_data = sample_sensor_data.copy()
        anomalous_data.append({
            "device_id": "TEMP_001",
            "sensor_type": "temperature",
            "value": 100.0,  # Valor muy alto
            "unit": "°C",
            "timestamp": datetime.now(),
            "location": "Office"
        })
        
        anomalies = analysis_tools.detect_anomalies(anomalous_data, threshold_factor=2.0)
        
        assert len(anomalies) > 0, "Debe detectar al menos una anomalía"
        
        # Verificar estructura de la anomalía
        anomaly = anomalies[0]
        required_fields = ['device_id', 'sensor_type', 'value', 'timestamp', 'expected_range', 'severity']
        for field in required_fields:
            assert field in anomaly, f"Campo {field} faltante en anomalía"
    
    def test_detect_anomalies_empty_data(self, analysis_tools):
        """Test para detección de anomalías con datos vacíos."""
        anomalies = analysis_tools.detect_anomalies([])
        assert anomalies == []
    
    def test_generate_summary_report(self, analysis_tools, sample_sensor_data):
        """Test para generar reporte resumen."""
        sample_alerts = [
            {
                "alert_id": 1,
                "device_id": "TEMP_001",
                "alert_type": "high_temperature",
                "severity": "high",
                "status": "active"
            }
        ]
        
        report = analysis_tools.generate_summary_report(sample_sensor_data, sample_alerts)
        
        assert 'generated_at' in report
        assert 'sensor_summary' in report
        assert 'alerts_summary' in report
        assert 'anomalies_summary' in report
        assert 'recommendations' in report
        
        # Verificar estructura del resumen de alertas
        alerts_summary = report['alerts_summary']
        assert 'total_active_alerts' in alerts_summary
        assert 'by_severity' in alerts_summary
        assert alerts_summary['total_active_alerts'] == len(sample_alerts)
    
    def test_generate_recommendations(self, analysis_tools):
        """Test para generar recomendaciones."""
        # Simular análisis con muchas alertas
        many_alerts = [{"severity": "high"} for _ in range(10)]
        
        # Simular anomalías de alta severidad
        high_severity_anomalies = [{"severity": "high"} for _ in range(3)]
        
        sensor_analysis = {
            "by_sensor_type": {
                "temperature": {"trend": "increasing"}
            }
        }
        
        recommendations = analysis_tools._generate_recommendations(
            sensor_analysis, many_alerts, high_severity_anomalies
        )
        
        assert len(recommendations) > 0, "Debe generar recomendaciones"
        assert any("alertas activas" in rec.lower() for rec in recommendations)
        assert any("anomalías" in rec.lower() for rec in recommendations)
        assert any("tendencia creciente" in rec.lower() for rec in recommendations)


if __name__ == "__main__":
    # Ejecutar tests específicos si se ejecuta directamente
    pytest.main([__file__, "-v"])
