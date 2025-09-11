"""
Remote Data Collector Node - Versión para API de Jetson
Reemplaza la conexión local de base de datos por la API remota
"""

import sys
import os
from typing import Dict, List, Any
import logging

# Añadir el directorio padre al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from modules.tools.jetson_api_connector import JetsonAPIConnector

logger = logging.getLogger(__name__)

class RemoteDataCollectorNode:
    """
    Nodo para recolectar datos desde la API remota de Jetson
    Reemplaza la funcionalidad de modules.tools.database_tools
    """
    
    def __init__(self):
        """Inicializar el conector remoto"""
        self.api_connector = JetsonAPIConnector()
        logger.info("RemoteDataCollectorNode initialized with Jetson API")
    
    def get_all_sensor_data(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Obtener todos los datos de sensores
        
        Args:
            limit: Número máximo de registros
            
        Returns:
            Lista de registros de sensores
        """
        try:
            data = self.api_connector.get_sensor_data(limit=limit)
            logger.info(f"Retrieved {len(data)} sensor records from remote API")
            return data
        except Exception as e:
            logger.error(f"Error getting sensor data: {e}")
            return []
    
    def get_temperature_data(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Obtener solo datos de temperatura
        
        Args:
            limit: Número máximo de registros
            
        Returns:
            Lista de registros de temperatura
        """
        try:
            data = self.api_connector.get_temperature_data()
            # Limitar el número de registros
            limited_data = data[:limit] if len(data) > limit else data
            logger.info(f"Retrieved {len(limited_data)} temperature records from remote API")
            return limited_data
        except Exception as e:
            logger.error(f"Error getting temperature data: {e}")
            return []
    
    def get_device_specific_data(self, device_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        """
        Obtener datos de un dispositivo específico
        
        Args:
            device_id: ID del dispositivo
            limit: Número máximo de registros
            
        Returns:
            Lista de registros del dispositivo
        """
        try:
            data = self.api_connector.get_sensor_data(device_id=device_id, limit=limit)
            logger.info(f"Retrieved {len(data)} records for device {device_id} from remote API")
            return data
        except Exception as e:
            logger.error(f"Error getting data for device {device_id}: {e}")
            return []
    
    def get_latest_readings_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de las últimas lecturas
        
        Returns:
            Dict con resumen de sensores y dispositivos
        """
        try:
            summary = self.api_connector.get_sensor_summary()
            logger.info("Retrieved sensor summary from remote API")
            return summary
        except Exception as e:
            logger.error(f"Error getting sensor summary: {e}")
            return {}
    
    def format_data_for_analysis(self, data: List[Dict[str, Any]]) -> str:
        """
        Formatear datos para análisis por el LLM
        
        Args:
            data: Lista de registros
            
        Returns:
            String formateado
        """
        try:
            formatted = self.api_connector.format_data_for_llm(data)
            logger.info("Data formatted for LLM analysis")
            return formatted
        except Exception as e:
            logger.error(f"Error formatting data: {e}")
            return "Error al formatear datos de sensores."
    
    def check_api_health(self) -> Dict[str, Any]:
        """
        Verificar estado de salud de la API
        
        Returns:
            Dict con estado de salud
        """
        try:
            health = self.api_connector.get_health_status()
            system_status = self.api_connector.get_system_status()
            
            return {
                'api_health': health,
                'system_status': system_status,
                'status': 'healthy' if health.get('status') == 'healthy' else 'unhealthy'
            }
        except Exception as e:
            logger.error(f"Error checking API health: {e}")
            return {'status': 'error', 'error': str(e)}


# Función para ejecutar el nodo como parte del grafo LangGraph
def remote_data_collector_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Función del nodo para LangGraph que recolecta datos remotos
    
    Args:
        state: Estado actual del grafo
        
    Returns:
        Estado actualizado con datos recolectados
    """
    logger.info("Executing remote_data_collector_node")
    
    collector = RemoteDataCollectorNode()
    
    # Verificar salud de la API primero
    health_check = collector.check_api_health()
    if health_check.get('status') != 'healthy':
        logger.warning("API health check failed")
        state['data_collection_error'] = "API remota no disponible"
        state['raw_data'] = []
        return state
    
    # Obtener el query analizado para determinar qué datos recolectar
    analyzed_query = state.get('analyzed_query', {})
    query_type = analyzed_query.get('data_type', 'general')
    
    try:
        if query_type == 'temperature':
            # Obtener datos de temperatura específicamente
            data = collector.get_temperature_data(limit=50)
        elif query_type == 'device_specific':
            # Obtener datos de un dispositivo específico si se especifica
            device_id = analyzed_query.get('device_filter')
            if device_id:
                data = collector.get_device_specific_data(device_id, limit=40)
            else:
                data = collector.get_all_sensor_data(limit=50)
        else:
            # Obtener todos los datos de sensores
            data = collector.get_all_sensor_data(limit=50)
        
        # Formatear datos para el LLM
        formatted_data = collector.format_data_for_analysis(data)
        
        # Actualizar estado
        state['raw_data'] = data
        state['formatted_data'] = formatted_data
        state['data_source'] = 'jetson_api'
        state['data_collection_success'] = True
        state['data_collection_timestamp'] = health_check.get('api_health', {}).get('timestamp')
        
        logger.info(f"Successfully collected {len(data)} records from remote API")
        
    except Exception as e:
        logger.error(f"Error in remote data collection: {e}")
        state['data_collection_error'] = str(e)
        state['raw_data'] = []
        state['formatted_data'] = "Error al obtener datos de sensores remotos."
    
    return state


# Función de utilidad para obtener datos remotos directamente
def get_remote_sensor_data(query_type: str = 'all', limit: int = 50) -> Dict[str, Any]:
    """
    Función de utilidad para obtener datos remotos directamente
    
    Args:
        query_type: Tipo de consulta ('all', 'temperature', 'arduino', 'esp32')
        limit: Límite de registros
        
    Returns:
        Dict con datos y metadata
    """
    collector = RemoteDataCollectorNode()
    
    try:
        if query_type == 'temperature':
            data = collector.get_temperature_data(limit)
        elif query_type == 'arduino':
            data = collector.get_device_specific_data('arduino_eth_001', limit)
        elif query_type == 'esp32':
            data = collector.get_device_specific_data('esp32_wifi_001', limit)
        else:
            data = collector.get_all_sensor_data(limit)
        
        return {
            'success': True,
            'data': data,
            'count': len(data),
            'formatted': collector.format_data_for_analysis(data),
            'summary': collector.get_latest_readings_summary()
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': [],
            'count': 0
        }


if __name__ == "__main__":
    # Prueba del nodo de recolección remota
    print("🧪 PRUEBA DEL REMOTE DATA COLLECTOR NODE")
    print("=" * 60)
    
    # Configurar logging para la prueba
    logging.basicConfig(level=logging.INFO)
    
    # Crear instancia del collector
    collector = RemoteDataCollectorNode()
    
    # Test 1: Health check
    print("1️⃣ VERIFICANDO SALUD DE LA API...")
    health = collector.check_api_health()
    print(f"   Status: {health.get('status')}")
    
    # Test 2: Obtener datos de temperatura
    print("\n2️⃣ OBTENIENDO DATOS DE TEMPERATURA...")
    temp_data = collector.get_temperature_data(limit=10)
    print(f"   Registros de temperatura: {len(temp_data)}")
    if temp_data:
        print(f"   Último registro: {temp_data[0]}")
    
    # Test 3: Obtener datos del Arduino
    print("\n3️⃣ OBTENIENDO DATOS DEL ARDUINO...")
    arduino_data = collector.get_device_specific_data('arduino_eth_001', limit=5)
    print(f"   Registros del Arduino: {len(arduino_data)}")
    
    # Test 4: Obtener datos del ESP32
    print("\n4️⃣ OBTENIENDO DATOS DEL ESP32...")
    esp32_data = collector.get_device_specific_data('esp32_wifi_001', limit=5)
    print(f"   Registros del ESP32: {len(esp32_data)}")
    
    # Test 5: Resumen de sensores
    print("\n5️⃣ OBTENIENDO RESUMEN DE SENSORES...")
    summary = collector.get_latest_readings_summary()
    print(f"   Dispositivos online: {summary.get('devices_online', 0)}")
    print(f"   Total dispositivos: {summary.get('devices_total', 0)}")
    
    # Test 6: Datos formateados para LLM
    print("\n6️⃣ DATOS FORMATEADOS PARA LLM:")
    print("=" * 60)
    all_data = collector.get_all_sensor_data(limit=15)
    formatted = collector.format_data_for_analysis(all_data)
    print(formatted)
    
    print("\n" + "=" * 60)
    print("✅ PRUEBAS COMPLETADAS")
    print("🚀 Remote Data Collector listo para integración con LangGraph")
