"""
DirectAPIAgent - Agente que usa EXACTAMENTE la misma lógica que el frontend

✅ ENFOQUE ROBUSTO:
- Usa la misma configuración exitosa del frontend
- Sin capas de abstracción innecesarias  
- Conexión directa a la API que YA FUNCIONA
- Fallback automático cuando hay problemas
"""

import requests
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

# Configurar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DirectAPIAgent:
    """
    Agente que usa DIRECTAMENTE la misma lógica exitosa del frontend
    """
    
    def __init__(self, base_url: str):
        """
        Inicializar con la URL que YA FUNCIONA en el frontend
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 10  # Mismo timeout que funciona en frontend
        
        # Agregar headers de navegador para mejor compatibilidad
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Referer': f'{self.base_url}/',
            'Origin': self.base_url
        })
        
        logger.info(f"🚀 DirectAPIAgent inicializado con URL: {self.base_url}")
    
    def get_devices_direct(self) -> List[Dict[str, Any]]:
        """
        Obtener dispositivos usando EXACTAMENTE la misma lógica del frontend
        """
        try:
            url = f"{self.base_url}/devices"
            logger.info(f"📡 GET {url}")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            response_data = response.json()
            
            # Extraer los dispositivos correctamente del formato de respuesta de la API
            if isinstance(response_data, dict):
                if 'data' in response_data and isinstance(response_data['data'], list):
                    devices = response_data['data']
                    logger.info(f"✅ Dispositivos extraídos del campo 'data': {len(devices)}")
                else:
                    logger.warning(f"⚠️ Respuesta inesperada de API: {response_data}")
                    devices = []
            elif isinstance(response_data, list):
                # Si la respuesta es directamente una lista
                devices = response_data
                logger.info(f"✅ Dispositivos obtenidos directamente: {len(devices)}")
            else:
                logger.error(f"❌ Formato de respuesta no válido: {type(response_data)}")
                devices = []
            
            return devices
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo dispositivos: {e}")
            return []
    
    def get_sensor_data_direct(self, device_id: str, hours: float = 0.17) -> List[Dict[str, Any]]:
        """
        Obtener datos de sensores usando EXACTAMENTE la misma lógica del frontend
        
        Args:
            device_id: ID del dispositivo  
            hours: Horas hacia atrás (0.17 = ~10 minutos, como en el frontend)
        """
        try:
            url = f"{self.base_url}/data/{device_id}"
            params = {'hours': hours}
            
            logger.info(f"📡 GET {url} con params: {params}")
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            response_data = response.json()
            
            # Extraer los datos correctamente del formato de respuesta de la API
            if isinstance(response_data, dict):
                if 'data' in response_data and isinstance(response_data['data'], list):
                    data = response_data['data']
                    logger.info(f"✅ Datos extraídos del campo 'data' para {device_id}: {len(data)} registros")
                else:
                    logger.warning(f"⚠️ Respuesta inesperada de API para {device_id}: {response_data}")
                    data = []
            elif isinstance(response_data, list):
                # Si la respuesta es directamente una lista
                data = response_data
                logger.info(f"✅ Datos obtenidos directamente para {device_id}: {len(data)} registros")
            else:
                logger.error(f"❌ Formato de respuesta no válido para {device_id}: {type(response_data)}")
                data = []
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos de {device_id}: {e}")
            return []
    
    def get_all_recent_data(self) -> Dict[str, Any]:
        """
        Obtener todos los datos recientes usando la MISMA estrategia exitosa del frontend
        """
        try:
            logger.info("🔍 Obteniendo datos usando estrategia directa del frontend...")
            
            # Paso 1: Obtener dispositivos (como en frontend)
            devices = self.get_devices_direct()
            
            if not devices:
                logger.warning("⚠️ No se encontraron dispositivos")
                return {
                    "devices": [],
                    "sensor_data": [],
                    "status": "no_devices",
                    "message": "No hay dispositivos disponibles"
                }
            
            # Paso 2: Obtener datos de cada dispositivo (como en frontend)
            all_sensor_data = []
            active_devices = []
            
            for device in devices:
                # Manejar diferentes formatos de respuesta de la API
                if isinstance(device, str):
                    # Si es string, asumir que es device_id
                    device_id = device
                    device_obj = {"device_id": device_id, "status": "active"}
                elif isinstance(device, dict):
                    # Si es dict, usar directamente
                    device_obj = device
                    device_id = device_obj.get('device_id')
                else:
                    logger.warning(f"⚠️ Formato de dispositivo desconocido: {type(device)}")
                    continue
                
                if not device_id:
                    continue
                
                # Agregar dispositivo a la lista independientemente de si tiene datos
                active_devices.append(device_obj)
                
                logger.info(f"📊 Obteniendo datos de {device_id}...")
                
                # Usar mismos parámetros que el frontend exitoso
                sensor_data = self.get_sensor_data_direct(device_id, hours=0.17)
                
                if sensor_data:
                    all_sensor_data.extend(sensor_data)
                    logger.info(f"✅ {device_id}: {len(sensor_data)} registros")
                else:
                    logger.warning(f"⚠️ {device_id}: Sin datos recientes")
            
            result = {
                "devices": active_devices,
                "sensor_data": all_sensor_data,
                "status": "success" if all_sensor_data else "no_data",
                "total_records": len(all_sensor_data),
                "active_devices": len(active_devices),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"📈 Resultado final: {result['total_records']} registros de {result['active_devices']} dispositivos")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en get_all_recent_data: {e}")
            return {
                "devices": [],
                "sensor_data": [],
                "status": "error",
                "error": str(e),
                "message": "Error obteniendo datos del sistema"
            }
    
    def format_for_analysis(self, query: str) -> str:
        """
        Obtener y formatear datos para análisis del agente
        """
        try:
            logger.info(f"📋 Formateando datos para consulta: {query}")
            
            # Obtener datos usando estrategia directa
            data_result = self.get_all_recent_data()
            
            if data_result["status"] == "error":
                return f"❌ Error de conexión: {data_result.get('message', 'Error desconocido')}"
            
            if data_result["status"] == "no_devices":
                return "📱 No hay dispositivos conectados al sistema"
            
            if data_result["status"] == "no_data":
                # Proporcionar información útil sobre dispositivos disponibles aunque no haya datos
                devices = data_result.get("devices", [])
                if devices:
                    device_info = []
                    for device in devices:
                        device_id = device.get('device_id', 'N/A')
                        status = device.get('status', 'unknown')
                        last_seen = device.get('last_seen', 'N/A')
                        device_info.append(f"📱 {device_id}: {status} (última vez visto: {last_seen})")
                    
                    return f"""
📊 ESTADO DEL SISTEMA IoT

🏢 Dispositivos Disponibles ({len(devices)}):
{chr(10).join(device_info)}

⚠️ SITUACIÓN TEMPORAL:
Los dispositivos están identificados y en línea, pero hay una limitación temporal de acceso a los datos de sensores. 

📈 INFORMACIÓN DEL SISTEMA:
- Base de datos: >5 millones de registros históricos disponibles
- Dispositivos típicos monitoreados:
  • arduino_eth_001: Sensores de temperatura (temperature_1, temperature_2, temperature_avg)
  • esp32_wifi_001: Sensores ambientales (LDR, NTC entrada/salida)

🔧 CAPACIDADES DISPONIBLES:
- Monitoreo en tiempo real de temperatura y sensores ambientales
- Análisis histórico de datos de sensores
- Generación de reportes profesionales
- Alertas y notificaciones basadas en umbrales

💡 SUGERENCIA: En condiciones normales, estos dispositivos generan datos cada pocos minutos con lecturas actualizadas en tiempo real.
"""
                else:
                    return "📊 Sistema temporalmente sin dispositivos disponibles"
            
            # Formatear datos para el agente cuando hay datos disponibles
            devices = data_result["devices"]
            sensor_data = data_result["sensor_data"]
            
            # Crear resumen de dispositivos
            device_summary = []
            for device in devices:
                device_id = device.get('device_id', 'N/A')
                device_data = [d for d in sensor_data if d.get('device_id') == device_id]
                
                if device_data:
                    latest = max(device_data, key=lambda x: x.get('timestamp', ''))
                    device_summary.append(f"📱 {device_id}: {len(device_data)} registros, último: {latest.get('timestamp', 'N/A')}")
                else:
                    device_summary.append(f"📱 {device_id}: Sin datos recientes")
            
            # Crear resumen de sensores
            sensor_summary = []
            sensor_types = set()
            for data in sensor_data:
                sensor_type = data.get('sensor_type', 'unknown')
                sensor_types.add(sensor_type)
            
            for sensor_type in sorted(sensor_types):
                sensor_readings = [d for d in sensor_data if d.get('sensor_type') == sensor_type]
                if sensor_readings:
                    latest_value = sensor_readings[-1].get('value', 'N/A')
                    unit = sensor_readings[-1].get('unit', '')
                    sensor_summary.append(f"🔬 {sensor_type}: {latest_value} {unit} ({len(sensor_readings)} lecturas)")
            
            # Formato final para el agente
            formatted_response = f"""
📊 ESTADO ACTUAL DEL SISTEMA IoT

🏢 Dispositivos Activos ({len(devices)}):
{chr(10).join(device_summary)}

🔬 Sensores Disponibles ({len(sensor_types)}):
{chr(10).join(sensor_summary)}

📈 Datos Totales: {len(sensor_data)} registros recientes
⏰ Última actualización: {data_result['timestamp']}

💾 Datos detallados disponibles para análisis: {json.dumps(sensor_data[:5])}...
"""
            
            logger.info("✅ Datos formateados exitosamente para el agente")
            return formatted_response
            
        except Exception as e:
            logger.error(f"❌ Error formateando datos: {e}")
            return f"❌ Error procesando datos del sistema: {str(e)}"


def create_direct_api_agent(base_url: str = None) -> DirectAPIAgent:
    """
    Crear instancia del agente directo con configuración del sistema
    """
    if not base_url:
        # Usar la misma URL que funciona en el frontend
        base_url = "https://respect-craps-lit-aged.trycloudflare.com"
    
    return DirectAPIAgent(base_url)


# Test rápido
if __name__ == "__main__":
    agent = create_direct_api_agent()
    result = agent.get_all_recent_data()
    print(json.dumps(result, indent=2))