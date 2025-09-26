"""
JetsonAPIConnector - Adaptador para conectar el agente a la API de Jetson
Reemplaza la conexión local de base de datos por conexión remota
"""

import requests
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JetsonAPIConnector:
    """Conector para la API del Jetson remoto via Cloudflare tunnel"""
    
    def __init__(self, base_url: str = "https://personnel-newsletters-jade-insertion.trycloudflare.com"):
        """
        Inicializar el conector
        
        Args:
            base_url: URL base de la API del Jetson
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 10
        
        # Headers por defecto
        self.session.headers.update({
            'User-Agent': 'LangGraph-Agent/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        logger.info(f"JetsonAPIConnector initialized for {self.base_url}")
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Hacer una petición a la API
        
        Args:
            endpoint: Endpoint de la API (ej: '/data', '/devices')
            params: Parámetros de la petición
            
        Returns:
            Dict con la respuesta de la API
            
        Raises:
            Exception: Si hay error en la petición
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"Making request to {url} with params {params}")
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Request successful: {response.status_code}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode failed: {e}")
            raise Exception(f"Invalid JSON response: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Obtener estado de salud del sistema
        
        Returns:
            Dict con el estado de salud
        """
        return self._make_request('/health')
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtener estado del sistema
        
        Returns:
            Dict con el estado del sistema
        """
        return self._make_request('/status')
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """
        Obtener lista de dispositivos disponibles
        
        Returns:
            Lista de dispositivos
        """
        response = self._make_request('/devices')
        if response.get('success') and 'data' in response:
            return response['data']
        return []
    
    def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """
        Obtener información detallada de un dispositivo específico
        
        Args:
            device_id: ID del dispositivo
            
        Returns:
            Dict con información del dispositivo
        """
        response = self._make_request(f'/devices/{device_id}')
        if response.get('success') and 'data' in response:
            return response['data']
        return {}
    
    def get_sensor_data(self, 
                       device_id: Optional[str] = None, 
                       limit: int = 50, 
                       sensor_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtener datos de sensores
        
        Args:
            device_id: ID del dispositivo (opcional, si no se especifica trae todos)
            limit: Límite de registros a obtener
            sensor_type: Tipo de sensor específico (opcional)
            
        Returns:
            Lista de registros de sensores
        """
        params = {'limit': limit}
        
        if device_id:
            endpoint = f'/data/{device_id}'
        else:
            endpoint = '/data'
            
        response = self._make_request(endpoint, params)
        
        if response.get('success') and 'data' in response:
            data = response['data']
            
            # Filtrar por tipo de sensor si se especifica
            if sensor_type:
                data = [record for record in data if record.get('sensor_type') == sensor_type]
            
            return data
        return []
    
    def get_latest_readings(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtener las últimas lecturas de sensores organizadas por dispositivo y tipo
        
        Args:
            device_id: ID del dispositivo específico (opcional)
            
        Returns:
            Dict organizado por dispositivo y tipo de sensor
        """
        data = self.get_sensor_data(device_id=device_id, limit=50)
        
        # Organizar datos por dispositivo y tipo de sensor
        organized_data = {}
        
        for record in data:
            dev_id = record.get('device_id')
            sensor_type = record.get('sensor_type')
            
            if dev_id not in organized_data:
                organized_data[dev_id] = {}
            
            # Solo guardar la lectura más reciente de cada tipo de sensor
            if sensor_type not in organized_data[dev_id]:
                organized_data[dev_id][sensor_type] = {
                    'value': record.get('value'),
                    'unit': record.get('unit', ''),
                    'timestamp': record.get('timestamp'),
                    'raw_data': record.get('raw_data')
                }
        
        return organized_data
    
    def get_temperature_data(self) -> List[Dict[str, Any]]:
        """
        Obtener datos específicos de temperatura de todos los dispositivos
        
        Returns:
            Lista de registros de temperatura
        """
        all_data = []
        
        # Obtener datos de Arduino (sensores: t1, t2, avg)
        arduino_data = self.get_sensor_data(device_id='arduino_eth_001', limit=20)
        temp_sensors = ['t1', 't2', 'avg']
        arduino_temp = [record for record in arduino_data if record.get('sensor_type') in temp_sensors]
        all_data.extend(arduino_temp)
        
        # Obtener datos de ESP32 (sensores: ntc_entrada, ntc_salida) 
        esp32_data = self.get_sensor_data(device_id='esp32_wifi_001', limit=20)
        ntc_sensors = ['ntc_entrada', 'ntc_salida']
        esp32_temp = [record for record in esp32_data if record.get('sensor_type') in ntc_sensors]
        all_data.extend(esp32_temp)
        
        return all_data
    
    def get_sensor_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de sensores disponibles y sus últimas lecturas
        
        Returns:
            Dict con resumen de sensores
        """
        devices = self.get_devices()
        latest_readings = self.get_latest_readings()
        
        summary = {
            'devices_online': len([d for d in devices if d.get('status') == 'online']),
            'devices_total': len(devices),
            'last_update': datetime.now(timezone.utc).isoformat(),
            'sensors': {}
        }
        
        # Añadir información de sensores
        for device_id, sensors in latest_readings.items():
            device_info = next((d for d in devices if d.get('device_id') == device_id), {})
            
            summary['sensors'][device_id] = {
                'device_type': device_info.get('device_type', 'unknown'),
                'ip_address': device_info.get('ip_address', 'unknown'),
                'status': device_info.get('status', 'unknown'),
                'last_seen': device_info.get('last_seen'),
                'sensors': sensors
            }
        
        return summary
    
    def format_data_for_llm(self, data: List[Dict[str, Any]]) -> str:
        """
        Formatear datos para el LLM de forma legible
        
        Args:
            data: Lista de registros de sensores
            
        Returns:
            String formateado para el LLM
        """
        if not data:
            return "No hay datos de sensores disponibles."
        
        # Organizar por dispositivo
        by_device = {}
        for record in data:
            device_id = record.get('device_id')
            if device_id not in by_device:
                by_device[device_id] = []
            by_device[device_id].append(record)
        
        formatted_lines = []
        formatted_lines.append("=== DATOS DE SENSORES IoT (TIEMPO REAL) ===")
        
        for device_id, records in by_device.items():
            formatted_lines.append(f"\n📱 DISPOSITIVO: {device_id}")
            
            # Agrupar por tipo de sensor
            by_sensor = {}
            for record in records[:10]:  # Último 10 registros por dispositivo
                sensor_type = record.get('sensor_type')
                if sensor_type not in by_sensor:
                    by_sensor[sensor_type] = []
                by_sensor[sensor_type].append(record)
            
            for sensor_type, sensor_records in by_sensor.items():
                latest = sensor_records[0]  # El más reciente
                value = latest.get('value')
                unit = latest.get('unit', '')
                timestamp = latest.get('timestamp', '')
                
                # Determinar unidad apropiada
                if sensor_type in ['t1', 't2', 'avg', 'ntc_entrada', 'ntc_salida']:
                    unit = '°C'
                elif sensor_type == 'ldr':
                    unit = ' (sensor luz)'
                
                formatted_lines.append(f"  🌡️ {sensor_type}: {value}{unit} (actualizado: {timestamp})")
        
        formatted_lines.append(f"\n⏰ Consultado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(formatted_lines)


# Función de utilidad para crear instancia global
def create_jetson_connector() -> JetsonAPIConnector:
    """Crear instancia del conector de Jetson"""
    return JetsonAPIConnector()


# Clase de prueba para verificar conectividad
class JetsonAPITester:
    """Clase para probar la conectividad de la API"""
    
    def __init__(self, connector: JetsonAPIConnector):
        self.connector = connector
    
    def run_connectivity_test(self) -> Dict[str, Any]:
        """
        Ejecutar prueba completa de conectividad
        
        Returns:
            Dict con resultados de las pruebas
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'overall_status': 'unknown'
        }
        
        try:
            # Test 1: Health check
            health = self.connector.get_health_status()
            results['tests']['health'] = {
                'status': 'pass' if health.get('status') == 'healthy' else 'fail',
                'data': health
            }
            
            # Test 2: Get devices
            devices = self.connector.get_devices()
            results['tests']['devices'] = {
                'status': 'pass' if devices else 'fail',
                'count': len(devices),
                'data': devices
            }
            
            # Test 3: Get sensor data
            sensor_data = self.connector.get_sensor_data(limit=5)
            results['tests']['sensor_data'] = {
                'status': 'pass' if sensor_data else 'fail',
                'count': len(sensor_data),
                'sample': sensor_data[0] if sensor_data else None
            }
            
            # Test 4: Get temperature data
            temp_data = self.connector.get_temperature_data()
            results['tests']['temperature_data'] = {
                'status': 'pass' if temp_data else 'fail',
                'count': len(temp_data),
                'sample': temp_data[0] if temp_data else None
            }
            
            # Determinar estado general
            all_tests_passed = all(
                test.get('status') == 'pass' 
                for test in results['tests'].values()
            )
            results['overall_status'] = 'pass' if all_tests_passed else 'fail'
            
        except Exception as e:
            results['tests']['error'] = {
                'status': 'fail',
                'error': str(e)
            }
            results['overall_status'] = 'fail'
        
        return results


if __name__ == "__main__":
    # Prueba básica del conector
    print("🧪 PRUEBA DEL JETSON API CONNECTOR")
    print("=" * 50)
    
    connector = create_jetson_connector()
    tester = JetsonAPITester(connector)
    
    # Ejecutar pruebas
    results = tester.run_connectivity_test()
    
    print(f"📊 Estado general: {results['overall_status']}")
    print(f"⏰ Timestamp: {results['timestamp']}")
    
    for test_name, test_data in results['tests'].items():
        status_emoji = "✅" if test_data.get('status') == 'pass' else "❌"
        print(f"{status_emoji} {test_name}: {test_data.get('status')}")
        
        if 'count' in test_data:
            print(f"   📊 Count: {test_data['count']}")
        
        if 'error' in test_data:
            print(f"   🔥 Error: {test_data['error']}")
    
    # Mostrar datos formateados para LLM
    print("\n" + "=" * 50)
    print("📝 DATOS FORMATEADOS PARA LLM:")
    print("=" * 50)
    
    try:
        sensor_data = connector.get_sensor_data(limit=10)
        formatted = connector.format_data_for_llm(sensor_data)
        print(formatted)
    except Exception as e:
        print(f"❌ Error formateando datos: {e}")
