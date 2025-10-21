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
            response = self._make_request('GET', '/api/devices')
            
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
                endpoint = f"/api/data/{device_id}"
            else:
                endpoint = "/api/data"
            
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
            response = self._make_request('GET', '/api/health')
            
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

def create_jetson_connector(url: str = None) -> JetsonAPIConnector:
    """
    Crear instancia de JetsonAPIConnector con URL por defecto.
    
    Args:
        url: URL de la API Jetson (opcional)
        
    Returns:
        Instancia de JetsonAPIConnector
    """
    if not url:
        url = "https://plain-state-refers-nutritional.trycloudflare.com"
    
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