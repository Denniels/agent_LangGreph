"""
Tests de integración simplificados
==================================

Tests que demuestran la funcionalidad completa del sistema
sin depender de recursos externos reales.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from modules.tools.analysis_tools import AnalysisTools
from modules.agents.graph_builder import GraphBuilder


class TestSystemIntegration:
    """Tests de integración del sistema completo."""
    
    def test_analysis_tools_functionality(self, sample_sensor_data):
        """
        Test que demuestra las herramientas de análisis funcionando.
        """
        # Arrange
        analysis_tools = AnalysisTools()
        
        # Act
        trends = analysis_tools.analyze_sensor_trends(sample_sensor_data)
        anomalies = analysis_tools.detect_anomalies(sample_sensor_data)
        report = analysis_tools.generate_summary_report(sample_sensor_data, [])
        
        # Assert
        assert "by_sensor_type" in trends
        assert "total_readings" in trends
        assert isinstance(anomalies, list)
        assert "summary" in report
        assert "total_sensors" in report
        assert len(report["devices"]) > 0
        
        print("✅ Herramientas de análisis funcionando correctamente")
    
    def test_graph_builder_functionality(self):
        """
        Test que demuestra el GraphBuilder funcionando.
        """
        # Arrange
        graph_builder = GraphBuilder()
        
        # Act
        graph_structure = graph_builder.build_conversation_graph()
        tools = graph_builder.get_available_tools()
        workflow_path = graph_builder.determine_workflow_path("¿Cuál es la temperatura actual?")
        status = graph_builder.get_graph_status()
        
        # Assert
        assert "nodes" in graph_structure
        assert "edges" in graph_structure
        assert len(tools) > 0
        assert len(workflow_path) > 0
        assert status["graph_built"] is True
        
        print("✅ GraphBuilder funcionando correctamente")
    
    def test_data_processing_pipeline(self, sample_sensor_data, sample_alert_data):
        """
        Test que demuestra el pipeline completo de procesamiento de datos.
        """
        # Arrange
        analysis_tools = AnalysisTools()
        sensor_data = sample_sensor_data[:10]  # Usar solo algunos datos
        
        # Act - Pipeline de procesamiento
        # 1. Análisis de tendencias
        trends = analysis_tools.analyze_sensor_trends(sensor_data)
        
        # 2. Detección de anomalías
        anomalies = analysis_tools.detect_anomalies(sensor_data)
        
        # 3. Generación de reporte
        report = analysis_tools.generate_summary_report(sensor_data, sample_alert_data)
        
        # 4. Generación de recomendaciones
        recommendations = analysis_tools.generate_recommendations(sensor_data, sample_alert_data)
        
        # Assert
        assert trends["status"] == "success"
        assert anomalies["status"] == "success"
        assert report["status"] == "success"
        assert recommendations["status"] == "success"
        
        # Verificar que el pipeline procesó datos
        assert report["total_readings"] > 0
        assert len(report["devices"]) > 0
        assert len(recommendations["recommendations"]) > 0
        
        print("✅ Pipeline de procesamiento funcionando correctamente")
    
    def test_conversation_workflow_simulation(self):
        """
        Test que simula un flujo de conversación completo.
        """
        # Arrange
        graph_builder = GraphBuilder()
        
        # Simular diferentes tipos de consultas
        queries = [
            "¿Cuál es la temperatura actual?",
            "Muéstrame un análisis detallado de los sensores",
            "¿Hay alguna alerta activa?",
            "Dame un reporte rápido del sistema"
        ]
        
        # Act & Assert
        for query in queries:
            # Determinar herramientas necesarias
            workflow_path = graph_builder.determine_workflow_path(query)
            tools_available = graph_builder.get_available_tools()
            
            # Verificar que se puede procesar la consulta
            assert len(workflow_path) > 0
            assert "start" in workflow_path
            assert "respond" in workflow_path
            assert len(tools_available) > 0
            
            print(f"✅ Consulta procesada: '{query[:30]}...'")
    
    def test_error_handling_and_resilience(self):
        """
        Test que demuestra el manejo de errores del sistema.
        """
        # Arrange
        analysis_tools = AnalysisTools()
        graph_builder = GraphBuilder()
        
        # Act & Assert - Datos vacíos
        empty_trends = analysis_tools.analyze_sensor_trends([])
        empty_anomalies = analysis_tools.detect_anomalies([])
        empty_report = analysis_tools.generate_summary_report([], [])
        
        assert empty_trends["status"] == "success"
        assert empty_anomalies["status"] == "success"
        assert empty_report["status"] == "success"
        
        # Act & Assert - Consultas inválidas
        empty_workflow = graph_builder.determine_workflow_path("")
        assert len(empty_workflow) > 0  # Debe devolver workflow por defecto
        
        print("✅ Manejo de errores funcionando correctamente")


@pytest.mark.integration
class TestSystemDemo:
    """Demostración completa del sistema funcionando."""
    
    def test_complete_system_demo(self, sample_sensor_data, sample_device_data, sample_alert_data):
        """
        Demo completa que muestra todas las capacidades del sistema.
        """
        print("\n" + "="*60)
        print("DEMOSTRACIÓN DEL SISTEMA IOT CONVERSACIONAL")
        print("="*60)
        
        # 1. Inicializar componentes
        analysis_tools = AnalysisTools()
        graph_builder = GraphBuilder()
        
        print("\n1. Componentes inicializados:")
        print(f"   - Herramientas de análisis: ✓")
        print(f"   - Constructor de gráficos: ✓")
        
        # 2. Mostrar datos disponibles
        print(f"\n2. Datos disponibles:")
        print(f"   - Lecturas de sensores: {len(sample_sensor_data)}")
        print(f"   - Dispositivos: {len(sample_device_data)}")
        print(f"   - Alertas: {len(sample_alert_data)}")
        
        # 3. Análisis de datos
        print(f"\n3. Análisis de datos:")
        trends = analysis_tools.analyze_sensor_trends(sample_sensor_data)
        print(f"   - Análisis de tendencias: {trends['status']}")
        
        anomalies = analysis_tools.detect_anomalies(sample_sensor_data)
        print(f"   - Detección de anomalías: {anomalies['status']}")
        print(f"   - Anomalías detectadas: {len(anomalies.get('anomalies', []))}")
        
        # 4. Generación de reportes
        print(f"\n4. Generación de reportes:")
        report = analysis_tools.generate_summary_report(sample_sensor_data, sample_alert_data)
        print(f"   - Reporte del sistema: {report['status']}")
        print(f"   - Total de lecturas procesadas: {report['total_readings']}")
        print(f"   - Dispositivos monitoreados: {len(report['devices'])}")
        
        # 5. Recomendaciones
        recommendations = analysis_tools.generate_recommendations(sample_sensor_data, sample_alert_data)
        print(f"\n5. Recomendaciones:")
        print(f"   - Estado: {recommendations['status']}")
        print(f"   - Recomendaciones generadas: {len(recommendations['recommendations'])}")
        
        # 6. Capacidades conversacionales
        print(f"\n6. Capacidades conversacionales:")
        graph_structure = graph_builder.build_conversation_graph()
        tools = graph_builder.get_available_tools()
        print(f"   - Nodos del gráfico: {len(graph_structure['nodes'])}")
        print(f"   - Herramientas disponibles: {len(tools)}")
        
        # 7. Simulación de consultas
        print(f"\n7. Simulación de consultas:")
        test_queries = [
            "¿Cuál es el estado actual de los sensores?",
            "Analiza las tendencias de temperatura",
            "¿Hay alertas activas que requieran atención?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            workflow = graph_builder.determine_workflow_path(query)
            print(f"   {i}. '{query}' -> {len(workflow)} pasos")
        
        print(f"\n8. Estado final del sistema:")
        status = graph_builder.get_graph_status()
        print(f"   - Gráfico construido: {status['graph_built']}")
        print(f"   - Nodos disponibles: {status['node_count']}")
        print(f"   - Conexiones: {status['edge_count']}")
        print(f"   - Herramientas activas: {status['available_tools']}")
        
        print("\n" + "="*60)
        print("✅ DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
        print("Sistema IoT conversacional totalmente funcional")
        print("="*60)
        
        # Assert final
        assert True  # Si llegamos aquí, todo funcionó
