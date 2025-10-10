"""
JetsonAPIConnector - Versión SIMPLIFICADA para Streamlit Cloud

OPTIMIZADO PARA STREAMLIT CLOUD:
- Sin dependencias complejas
- Manejo de errores robusto
- Compatible con código existente
"""

import requests
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

# Configurar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JetsonAPIConnector:
    """
    Conector simplificado para la API del Jetson remoto via Cloudflare tunnel
    """
    
    def __init__(self, base_url: str):
        """
        Inicializar conector con URL base.
        
        Args:
            base_url: URL base de la API Jetson (ej: https://domain.trycloudflare.com)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = (10, 30)  # (conexión, lectura)
        
        # Headers por defecto
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'IoT-Agent/1.0'
        })
        
        logger.info(f"🔧 JetsonAPIConnector inicializado con URL: {self.base_url}")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Realizar petición HTTP con manejo robusto de errores.
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint de la API
            **kwargs: Argumentos adicionales para requests
            
        Returns:
            Respuesta JSON de la API
            
        Raises:
            Exception: Si la petición falla
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"🌐 {method} {url}")
            
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Intentar parsear JSON
            try:
                data = response.json()
                logger.debug(f"✅ Respuesta exitosa: {len(str(data))} caracteres")
                return data
            except json.JSONDecodeError:
                # Si no es JSON, devolver texto
                return {"response": response.text, "status": "success"}
                
        except requests.exceptions.Timeout:
            logger.error(f"⏰ Timeout en {url}")
            raise Exception(f"Timeout conectando a Jetson API: {url}")
            
        except requests.exceptions.ConnectionError:
            logger.error(f"🔌 Error de conexión a {url}")
            raise Exception(f"No se puede conectar a Jetson API: {url}")
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"🔴 HTTP Error {e.response.status_code}: {url}")
            raise Exception(f"Error HTTP {e.response.status_code}: {e.response.text}")
            
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            raise Exception(f"Error en petición a Jetson API: {str(e)}")
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """
        Obtener lista de dispositivos IoT conectados.
        
        Returns:
            Lista de dispositivos
        """
        try:
            response = self._make_request('GET', '/devices')
            
            # Manejar diferentes formatos de respuesta
            if isinstance(response, list):
                devices = response
            elif isinstance(response, dict) and 'devices' in response:
                devices = response['devices']
            elif isinstance(response, dict) and 'data' in response:
                devices = response['data']
            else:
                # Asumir que la respuesta es la lista de dispositivos
                devices = [response] if response else []
            
            logger.info(f"📱 Dispositivos obtenidos: {len(devices)}")
            return devices
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo dispositivos: {e}")
            # Devolver estructura por defecto para evitar crashes
            return [
                {"device_id": "esp32_wifi_001", "status": "unknown", "last_seen": "unknown"},
                {"device_id": "arduino_eth_001", "status": "unknown", "last_seen": "unknown"}
            ]
    
    def get_sensor_data(self, device_id: str = None, sensor_type: str = None, 
                       limit: int = 100, hours: float = None) -> List[Dict[str, Any]]:
        """
        Obtener datos de sensores.
        
        Args:
            device_id: ID del dispositivo (opcional)
            sensor_type: Tipo de sensor (opcional)
            limit: Límite de registros
            hours: Horas hacia atrás para filtrar
            
        Returns:
            Lista de registros de sensores
        """
        try:
            # Construir parámetros
            params = {}
            if limit:
                params['limit'] = limit
            if hours:
                params['hours'] = hours
            
            # Construir endpoint
            if device_id:
                endpoint = f"/data/{device_id}"
            else:
                endpoint = "/data"
            
            # Hacer petición
            response = self._make_request('GET', endpoint, params=params)
            
            # Procesar respuesta
            if isinstance(response, list):
                data = response
            elif isinstance(response, dict) and 'data' in response:
                data = response['data']
            elif isinstance(response, dict) and 'records' in response:
                data = response['records']
            else:
                data = []
            
            # Filtrar por sensor_type si se especifica
            if sensor_type and data:
                data = [record for record in data if record.get('sensor_type') == sensor_type]
            
            logger.info(f"📊 Datos obtenidos: {len(data)} registros para {device_id or 'todos'}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos de sensores: {e}")
            return []
    
    def get_health(self) -> Dict[str, Any]:
        """
        Verificar estado de salud de la API.
        
        Returns:
            Estado de salud de la API
        """
        try:
            response = self._make_request('GET', '/health')
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "api_url": self.base_url,
                "response": response
            }
            
        except Exception as e:
            logger.error(f"❌ Error en health check: {e}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "api_url": self.base_url,
                "error": str(e)
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Probar conexión a la API Jetson.
        
        Returns:
            Resultado de la prueba de conexión
        """
        try:
            logger.info("🧪 Probando conexión a Jetson API...")
            
            # Probar health check
            health = self.get_health()
            
            # Probar obtener dispositivos
            devices = self.get_devices()
            
            # Probar obtener algunos datos
            sample_data = self.get_sensor_data(limit=5)
            
            result = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "api_url": self.base_url,
                "health": health,
                "devices_count": len(devices),
                "sample_data_count": len(sample_data),
                "devices": devices[:2] if devices else []  # Mostrar máximo 2 dispositivos
            }
            
            logger.info("✅ Prueba de conexión exitosa")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en prueba de conexión: {e}")
            return {
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "api_url": self.base_url,
                "error": str(e)
            }

    def get_health_status(self) -> Dict[str, Any]:
        """
        Obtener estado de salud del sistema
        
        Returns:
            Dict con el estado de salud
        """
        return self.get_health()
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtener estado del sistema
        
        Returns:
            Dict con el estado del sistema
        """
        try:
            response = self._make_request('GET', '/status')
            return response
        except Exception:
            return self.get_health()
    
    def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """
        Obtener información detallada de un dispositivo específico
        
        Args:
            device_id: ID del dispositivo
            
        Returns:
            Dict con información del dispositivo
        """
        try:
            response = self._make_request('GET', f'/devices/{device_id}')
            if response.get('success') and 'data' in response:
                return response['data']
            return response
        except Exception as e:
            logger.error(f"❌ Error obteniendo info del dispositivo {device_id}: {e}")
            return {}
    
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

def create_jetson_connector(url: str = None) -> JetsonAPIConnector:
    """
    Crear instancia de JetsonAPIConnector con URL por defecto.
    
    Args:
        url: URL de la API Jetson (opcional)
        
    Returns:
        Instancia de JetsonAPIConnector
    """
    if not url:
        url = "https://respect-craps-lit-aged.trycloudflare.com"
    
    return JetsonAPIConnector(url)

# Test de conectividad cuando se ejecuta directamente
if __name__ == "__main__":
    print("🧪 PRUEBA DE JETSON API CONNECTOR")
    print("=" * 50)
    
    # Crear conector
    connector = create_jetson_connector()
    
    # Probar conexión
    result = connector.test_connection()
    
    if result["success"]:
        print("✅ Conexión exitosa!")
        print(f"📱 Dispositivos: {result['devices_count']}")
        print(f"📊 Datos de muestra: {result['sample_data_count']}")
        
        for device in result.get("devices", []):
            print(f"  - {device.get('device_id', 'N/A')}")
    else:
        print("❌ Error en conexión:")
        print(f"   {result.get('error', 'Error desconocido')}")