"""
JetsonAPIConnector - Adaptador ROBUSTO para conectar el agente a la API de Jetson

VERSIÓN 2.0 - ROBUSTA Y AUTORECUPERABLE:
- Reconexión automática tras cortes de energía  
- Detección automática de URLs cambiantes
- Manejo robusto de errores de red
- Cache inteligente de configuración
- Compatible 100% con código existente
"""

import requests
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

# Importar manager robusto
try:
    print("🔍 Intentando importar jetson_api_manager...")
    
    # Agregar path para imports cuando se ejecuta directamente
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(os.path.dirname(current_dir))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from modules.utils.jetson_api_manager import get_jetson_manager
    print("✅ Import del jetson_api_manager exitoso")
    ROBUST_MODE = True
    
except Exception as e:
    print(f"❌ Error en import: {e}")
    ROBUST_MODE = False
    
# Configurar logger
logger = logging.getLogger(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JetsonAPIConnector:
    """
    Conector ROBUSTO para la API del Jetson remoto via Cloudflare tunnel
    
    VERSIÓN 2.0 - CARACTERÍSTICAS ROBUSTAS:
    ✅ Reconexión automática tras cortes de energía
    ✅ Detección automática de URLs cambiantes  
    ✅ Reintentos inteligentes con backoff
    ✅ Cache de configuración persistente
    ✅ 100% compatible con código existente
    """
    
    def __init__(self, base_url: str = "https://couples-mario-repository-alive.trycloudflare.com"):
        """
        Inicializar el conector ROBUSTO con autorecuperación
        
        Args:
            base_url: URL base de la API del Jetson
        """
        # ⚡ MODO ROBUSTO - AUTORECUPERABLE ⚡
        if ROBUST_MODE:
            logger.info("🚀 Iniciando JetsonAPIConnector ROBUSTO v2.0")
            self.manager = get_jetson_manager()
            
            # Agregar URL como candidata (si no está ya)
            if base_url not in self.manager.candidate_urls:
                self.manager.candidate_urls.insert(0, base_url)
            
            # Descubrir URL que funciona
            working_url = self.manager.discover_working_url()
            if working_url:
                self.base_url = working_url.rstrip('/')
                logger.info(f"✅ URL operativa detectada: {working_url}")
            else:
                logger.warning("⚠️ Usando URL proporcionada - sin verificación")
                self.base_url = base_url.rstrip('/')
        else:
            # Modo legacy
            logger.warning("⚠️ Modo legacy - funcionalidad reducida")
            self.manager = None
            self.base_url = base_url.rstrip('/')
        
        # Configurar sesión HTTP
        self.session = requests.Session()
        self.session.timeout = 10
        
        # Headers por defecto
        self.session.headers.update({
            'User-Agent': 'LangGraph-Agent-v2.0/Robust',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        logger.info(f"🔗 JetsonAPIConnector iniciado en: {self.base_url}")
        logger.info(f"⚙️ Modo robusto: {'✅ ACTIVO' if ROBUST_MODE else '❌ INACTIVO'}")
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Hacer una petición ROBUSTA a la API con autorecuperación
        
        Args:
            endpoint: Endpoint de la API (ej: '/data', '/devices')
            params: Parámetros de la petición
            
        Returns:
            Dict con la respuesta de la API
            
        Raises:
            Exception: Si hay error en la petición tras reintentos
        """
        # ⚡ MODO ROBUSTO CON AUTORECUPERACIÓN ⚡
        if ROBUST_MODE and self.manager:
            logger.info(f"🚀 Petición robusta a {endpoint}")
            try:
                # Usar el manager robusto que maneja reintentos y reconexión
                response_data = self.manager.make_robust_request(endpoint, params)
                
                if response_data is not None:
                    logger.info(f"✅ Petición robusta exitosa: {endpoint}")
                    return response_data
                else:
                    # Si el manager robusto devuelve None, lanzar excepción
                    logger.error(f"💥 Petición robusta devolvió None: {endpoint}")
                    raise Exception(f"Robust request returned None for {endpoint}")
                    
            except Exception as e:
                logger.error(f"💥 Petición robusta falló tras reintentos: {e}")
                raise Exception(f"API request failed after robust retries: {e}")
        
        # Modo legacy (sin robustez)
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"📡 Petición legacy a {url} con params {params}")
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Petición legacy exitosa: {response.status_code}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Petición legacy falló: {e}")
            raise Exception(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode failed: {e}")
            raise Exception(f"Invalid JSON response: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Obtener estado de salud del sistema con verificación robusta
        
        Returns:
            Dict con el estado de salud
        """
        return self._make_request('/health')
    
    def test_robust_connectivity(self) -> Dict[str, Any]:
        """
        Probar conectividad robusta con autorecuperación
        
        Returns:
            Dict con resultados de conectividad
        """
        result = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'robust_mode': ROBUST_MODE,
            'base_url': self.base_url,
            'connectivity': 'unknown',
            'details': {}
        }
        
        if ROBUST_MODE and self.manager:
            try:
                # Probar conectividad usando manager robusto
                connectivity_result = self.manager.test_url_connectivity(self.base_url)
                result['connectivity'] = 'success' if connectivity_result['success'] else 'failed'
                result['details'] = connectivity_result
                
                # Si falló, intentar redescubrir
                if not connectivity_result['success']:
                    logger.warning("🔄 Reconectividad falló - intentando redescubrir...")
                    new_url = self.manager.discover_working_url()
                    if new_url and new_url != self.base_url:
                        self.base_url = new_url
                        result['base_url'] = new_url
                        result['details']['rediscovered_url'] = new_url
                        logger.info(f"🆕 Nueva URL detectada: {new_url}")
                
            except Exception as e:
                result['connectivity'] = 'error'
                result['details']['error'] = str(e)
        else:
            # Test básico en modo legacy
            try:
                health = self.get_health_status()
                result['connectivity'] = 'success' if health else 'failed'
                result['details'] = {'health_check': health}
            except Exception as e:
                result['connectivity'] = 'error'
                result['details']['error'] = str(e)
        
        return result
    
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
        
        # Manejar ambos formatos de respuesta:
        # 1. Formato encapsulado: {"success": true, "data": [...]}
        # 2. Formato directo: [...]
        if isinstance(response, list):
            # Respuesta directa (formato actual de la API)
            return response
        elif response.get('success') and 'data' in response:
            # Respuesta encapsulada
            return response['data']
        elif isinstance(response, dict) and 'devices' in response:
            # Otro formato posible
            return response['devices']
        
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
        
        # Manejar ambos formatos de respuesta:
        # 1. Formato encapsulado: {"success": true, "data": [...]}
        # 2. Formato directo: [...]
        data = []
        if isinstance(response, list):
            # Respuesta directa (formato actual de la API)
            data = response
        elif response.get('success') and 'data' in response:
            # Respuesta encapsulada
            data = response['data']
        elif isinstance(response, dict) and 'sensors' in response:
            # Otro formato posible
            data = response['sensors']
        
        # Filtrar por tipo de sensor si se especifica
        if sensor_type and data:
            data = [record for record in data if record.get('sensor_type') == sensor_type]
        
        return data
    
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
    
    def get_temperature_data(self, limit: int = 200) -> List[Dict[str, Any]]:
        """
        Obtener datos específicos de temperatura de todos los dispositivos
        
        Args:
            limit: Número máximo de registros por dispositivo (default: 200 para cubrir últimos 10 min)
        
        Returns:
            Lista de registros de temperatura
        """
        all_data = []
        
        # Obtener datos de Arduino (sensores: temperature_1, temperature_2, temperature_avg)
        arduino_data = self.get_sensor_data(device_id='arduino_eth_001', limit=limit)
        temp_sensors = ['temperature_1', 'temperature_2', 'temperature_avg']
        arduino_temp = [record for record in arduino_data if record.get('sensor_type') in temp_sensors]
        all_data.extend(arduino_temp)
        
        # Obtener datos de ESP32 (sensores: ntc_entrada, ntc_salida) 
        esp32_data = self.get_sensor_data(device_id='esp32_wifi_001', limit=limit)
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
                if sensor_type in ['temperature_1', 'temperature_2', 'temperature_avg', 'ntc_entrada', 'ntc_salida']:
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
    # Prueba ROBUSTA del conector
    print("🧪 PRUEBA DEL JETSON API CONNECTOR v2.0 ROBUSTO")
    print("=" * 60)
    
    connector = create_jetson_connector()
    tester = JetsonAPITester(connector)
    
    # Test de conectividad robusta
    print("🚀 INICIANDO TESTS DE ROBUSTEZ...")
    robust_test = connector.test_robust_connectivity()
    
    print(f"⚙️ Modo robusto: {'✅ ACTIVO' if robust_test['robust_mode'] else '❌ INACTIVO'}")
    print(f"🔗 URL actual: {robust_test['base_url']}")
    print(f"📡 Conectividad: {robust_test['connectivity']}")
    
    if 'rediscovered_url' in robust_test['details']:
        print(f"🆕 URL redescubierta: {robust_test['details']['rediscovered_url']}")
    
    # Ejecutar pruebas estándar
    print("\n🔬 EJECUTANDO TESTS ESTÁNDAR...")
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
    print("\n" + "=" * 60)
    print("📝 DATOS FORMATEADOS PARA LLM:")
    print("=" * 60)
    
    try:
        sensor_data = connector.get_sensor_data(limit=10)
        formatted = connector.format_data_for_llm(sensor_data)
        print(formatted)
    except Exception as e:
        print(f"❌ Error formateando datos: {e}")
        
    # Resumen de robustez
    print("\n" + "=" * 60)
    print("🛡️ RESUMEN DE ROBUSTEZ:")
    print("=" * 60)
    print(f"✅ Reconexión automática: {'SÍ' if robust_test['robust_mode'] else 'NO'}")
    print(f"✅ Detección de URL: {'SÍ' if robust_test['robust_mode'] else 'NO'}")
    print(f"✅ Reintentos inteligentes: {'SÍ' if robust_test['robust_mode'] else 'NO'}")
    print(f"✅ Cache de configuración: {'SÍ' if robust_test['robust_mode'] else 'NO'}")
    print(f"✅ Autorecuperación: {'SÍ' if robust_test['robust_mode'] else 'NO'}")
    
    if robust_test['robust_mode']:
        print("\n🚀 SISTEMA COMPLETAMENTE ROBUSTO - Resistente a:")
        print("   💡 Cortes de energía")
        print("   🔄 Cambios de URL de Cloudflare")  
        print("   🌐 Interrupciones de red")
        print("   ⚡ Reconexión automática")
    else:
        print("\n⚠️ MODO LEGACY - Funcionalidad básica sin robustez")
