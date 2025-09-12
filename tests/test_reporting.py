"""
Tests para el módulo de generación de reportes
============================================

Pruebas unitarias para la funcionalidad de reportes ejecutivos.
"""

import pytest
import json
from datetime import datetime
from modules.agents.reporting import ReportGenerator, create_report_generator


class TestReportGenerator:
    """Tests para la clase ReportGenerator"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.generator = create_report_generator()
        self.sample_metadata = {
            "data_summary": {
                "total_records": 80,
                "sensors": ["ntc_entrada", "ntc_salida", "ldr"],
                "devices": ["esp32_wifi_001", "arduino_eth_001"]
            },
            "verification": {
                "confidence": 85,
                "timestamp": "2025-09-12T10:30:00Z"
            }
        }
    
    def test_parse_user_request_to_spec_pdf(self):
        """Test parsing de solicitud PDF"""
        user_text = "Dame un reporte ejecutivo en PDF del ESP32, sensor ntc_entrada, con gráfico de líneas"
        
        spec = self.generator.parse_user_request_to_spec(user_text, self.sample_metadata)
        
        assert spec is not None
        assert spec["format"] == "pdf"
        assert spec["device_id"] == "esp32_wifi_001"
        assert spec["sensor"] == "ntc_entrada"
        assert spec["chart"]["type"] == "line"
        assert "summary" in spec["sections"]
    
    def test_parse_user_request_to_spec_csv(self):
        """Test parsing de solicitud CSV"""
        user_text = "Exporta CSV con todos los registros de arduino_eth_001 para el sensor ldr"
        
        spec = self.generator.parse_user_request_to_spec(user_text, self.sample_metadata)
        
        assert spec is not None
        assert spec["format"] == "csv"
        assert spec["device_id"] == "arduino_eth_001"
        assert spec["sensor"] == "ldr"
        assert spec["sections"] == ["table"]
    
    def test_parse_user_request_non_report(self):
        """Test que no es solicitud de reporte"""
        user_text = "¿Cuál es la temperatura actual de los sensores?"
        
        spec = self.generator.parse_user_request_to_spec(user_text, self.sample_metadata)
        
        assert spec is None
    
    def test_fetch_series_from_metadata(self):
        """Test extracción de series temporales"""
        data_points = self.generator.fetch_series_from_metadata(
            "esp32_wifi_001", "ntc_entrada", self.sample_metadata, 50
        )
        
        assert len(data_points) <= 50
        assert len(data_points) > 0
        
        # Verificar estructura de datos
        point = data_points[0]
        assert "t" in point
        assert "v" in point
        assert isinstance(point["v"], (int, float))
    
    def test_build_plotly_figure(self):
        """Test construcción de figura Plotly"""
        timestamps = ["2025-09-12T10:00:00", "2025-09-12T11:00:00", "2025-09-12T12:00:00"]
        values = [25.5, 26.2, 25.8]
        
        fig = self.generator.build_plotly_figure(
            timestamps, values, "line", "Test Chart", "Temperature"
        )
        
        assert fig is not None
        assert len(fig.data) == 1
        assert fig.data[0].name == "Temperature"
    
    def test_export_csv_from_table(self):
        """Test exportación CSV"""
        data_points = [
            {"t": "2025-09-12T10:00:00", "v": 25.5},
            {"t": "2025-09-12T11:00:00", "v": 26.2}
        ]
        
        csv_bytes = self.generator.export_csv_from_table(
            data_points, "esp32_wifi_001", "ntc_entrada"
        )
        
        assert len(csv_bytes) > 0
        csv_text = csv_bytes.decode('utf-8')
        assert "esp32_wifi_001" in csv_text
        assert "ntc_entrada" in csv_text
    
    def test_export_xlsx_from_table(self):
        """Test exportación XLSX"""
        data_points = [
            {"t": "2025-09-12T10:00:00", "v": 25.5},
            {"t": "2025-09-12T11:00:00", "v": 26.2}
        ]
        
        xlsx_bytes = self.generator.export_xlsx_from_table(
            data_points, "esp32_wifi_001", "ntc_entrada"
        )
        
        assert len(xlsx_bytes) > 0
        # Los archivos XLSX son binarios, verificar que no esté vacío
    
    def test_generate_pdf_from_spec(self):
        """Test generación PDF"""
        spec = {
            "title": "Test Report",
            "device_id": "esp32_wifi_001",
            "sensor": "ntc_entrada",
            "time_range": {"description": "últimas 24 horas"},
            "sections": ["summary", "metrics"],
            "format": "pdf"
        }
        
        summary_text = "Este es un reporte de prueba para validar la funcionalidad."
        metrics = {
            "total_registros": 50,
            "dispositivo": "esp32_wifi_001",
            "sensor": "ntc_entrada"
        }
        
        pdf_bytes = self.generator.generate_pdf_from_spec(spec, summary_text, metrics)
        
        assert len(pdf_bytes) > 0
        # Verificar que empiece con header PDF
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_generate_report_full_flow(self):
        """Test flujo completo de generación de reporte"""
        spec = {
            "title": "Reporte Completo",
            "device_id": "esp32_wifi_001",
            "sensor": "ntc_entrada",
            "time_range": {"description": "últimas 24 horas"},
            "chart": {"type": "line", "sample_points": 10, "y_label": "°C"},
            "sections": ["summary", "metrics", "chart"],
            "format": "pdf"
        }
        
        summary_text = "Reporte de prueba completo"
        
        file_bytes, filename = self.generator.generate_report(
            spec, self.sample_metadata, summary_text
        )
        
        assert len(file_bytes) > 0
        assert filename.endswith('.pdf')
        assert "esp32_wifi_001" in filename
        assert "ntc_entrada" in filename
    
    def test_supported_formats(self):
        """Test formatos soportados"""
        expected_formats = ["pdf", "csv", "xlsx", "png", "html"]
        
        for fmt in expected_formats:
            assert fmt in self.generator.supported_formats
    
    def test_chart_types(self):
        """Test tipos de gráfico soportados"""
        expected_chart_types = ["line", "bar", "area", "scatter", "heatmap"]
        
        for chart_type in expected_chart_types:
            assert chart_type in self.generator.chart_types


def test_create_report_generator():
    """Test factory function"""
    generator = create_report_generator()
    
    assert isinstance(generator, ReportGenerator)
    assert hasattr(generator, 'parse_user_request_to_spec')
    assert hasattr(generator, 'generate_report')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
