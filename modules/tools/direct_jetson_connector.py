"""
Conector DIRECTO y ROBUSTO para la API Jetson
===========================================

Implementación ultra-simple que replica exactamente cómo se conecta el dashboard exitoso.
Sin abstracciones innecesarias, sin fallbacks engañosos.
"""

import requests
import json
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DirectJetsonConnector:
    """
    Conector DIRECTO que replica exactamente la lógica del dashboard que funciona.
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        logger.info(f"🔧 DirectJetsonConnector inicializado: {self.base_url}")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test básico de conexión - igual que hace el dashboard
        """
        try:
            url = f"{self.base_url}/health"
            logger.info(f"🔍 Testing conexión: {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = {
                "status": "connected",
                "url": url,
                "response_code": response.status_code,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Conexión exitosa: {response.status_code}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "url": f"{self.base_url}/health",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_devices_direct(self) -> List[Dict[str, Any]]:
        """
        Obtener dispositivos usando el método DIRECTO que funciona en el dashboard
        """
        try:
            url = f"{self.base_url}/devices"
            logger.info(f"📱 Obteniendo dispositivos: {url}")
            
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Respuesta recibida: {type(data)} - {len(str(data))} chars")
            
            # Procesar la respuesta igual que el dashboard
            if isinstance(data, list):
                devices = data
            elif isinstance(data, dict):
                if 'devices' in data:
                    devices = data['devices']
                elif 'data' in data:
                    devices = data['data']
                else:
                    # Si es un dict pero no tiene 'devices' o 'data', tratarlo como un solo dispositivo
                    devices = [data]
            else:
                devices = []
            
            logger.info(f"📱 Dispositivos procesados: {len(devices)}")
            
            # Agregar timestamp de consulta
            for device in devices:
                device['query_timestamp'] = datetime.now().isoformat()
                # Asegurar que tengan los campos necesarios
                if 'device_id' not in device and 'id' in device:
                    device['device_id'] = device['id']
                if 'status' not in device:
                    device['status'] = 'active'  # Si responde, está activo
            
            return devices
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo dispositivos: {e}")
            # NO devolver datos falsos - fallar claramente
            raise Exception(f"No se pudo obtener dispositivos de {url}: {str(e)}")
    
    def get_sensor_data_direct(self, device_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtener datos de sensores usando método DIRECTO
        """
        try:
            # Construir URL igual que el dashboard
            if device_id:
                url = f"{self.base_url}/data/{device_id}"
                params = {"limit": limit}
            else:
                url = f"{self.base_url}/data"
                params = {"limit": limit}
            
            logger.info(f"📊 Obteniendo datos: {url} - params: {params}")
            
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Datos recibidos: {type(data)} - {len(str(data))} chars")
            
            # Procesar igual que el dashboard
            if isinstance(data, list):
                sensor_data = data
            elif isinstance(data, dict):
                if 'data' in data:
                    sensor_data = data['data']
                elif 'sensors' in data:
                    sensor_data = data['sensors']
                else:
                    sensor_data = [data]
            else:
                sensor_data = []
            
            logger.info(f"📊 Registros de sensores: {len(sensor_data)}")
            return sensor_data
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos de sensores: {e}")
            raise Exception(f"No se pudo obtener datos de sensores: {str(e)}")
    
    def get_all_data_simple(self) -> Dict[str, Any]:
        """
        Método simple que obtiene TODO igual que el dashboard
        """
        try:
            logger.info("🚀 Iniciando obtención completa de datos...")
            
            # 1. Test de conexión
            connection_test = self.test_connection()
            if connection_test["status"] != "connected":
                raise Exception(f"Test de conexión falló: {connection_test.get('error', 'Unknown')}")
            
            # 2. Obtener dispositivos
            devices = self.get_devices_direct()
            
            # 3. Obtener datos de cada dispositivo
            all_sensor_data = []
            device_stats = {}
            
            for device in devices:
                device_id = device.get('device_id')
                if device_id:
                    try:
                        device_data = self.get_sensor_data_direct(device_id, limit=200)
                        all_sensor_data.extend(device_data)
                        device_stats[device_id] = len(device_data)
                        logger.info(f"📱 {device_id}: {len(device_data)} registros")
                    except Exception as e:
                        logger.warning(f"⚠️ Error con {device_id}: {e}")
                        device_stats[device_id] = 0
            
            result = {
                "status": "success",
                "connection": connection_test,
                "devices": devices,
                "sensor_data": all_sensor_data,
                "stats": {
                    "total_devices": len(devices),
                    "total_records": len(all_sensor_data),
                    "device_records": device_stats,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            logger.info(f"🎉 Datos completos obtenidos: {len(devices)} dispositivos, {len(all_sensor_data)} registros")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en obtención completa: {e}")
            raise Exception(f"Fallo en obtención completa de datos: {str(e)}")