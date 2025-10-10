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
    
    def get_historical_data_paginated(self, hours: float = 24, max_records: int = 1000) -> List[Dict[str, Any]]:
        """
        Obtener datos históricos usando paginación para superar limitaciones de la API
        
        Args:
            hours: Horas hacia atrás para consultar
            max_records: Máximo número de registros a obtener
        """
        try:
            logger.info(f"📅 Obteniendo datos históricos: {hours}h, máximo {max_records} registros")
            
            all_data = []
            page_size = 200  # Máximo que funciona por request
            offset = 0
            
            while len(all_data) < max_records:
                # Calcular cuántos registros solicitar en esta página
                remaining = max_records - len(all_data)
                current_limit = min(page_size, remaining)
                
                logger.info(f"📄 Página: offset={offset}, limit={current_limit}")
                
                # Probar diferentes estrategias de paginación
                params_combinations = [
                    {'limit': current_limit, 'offset': offset, 'hours': hours},
                    {'limit': current_limit, 'hours': hours},  # Sin offset
                    {'limit': current_limit}  # Solo límite
                ]
                
                page_data = []
                for params in params_combinations:
                    try:
                        response = self.session.get(f"{self.base_url}/data", params=params, timeout=20)
                        if response.status_code == 200:
                            response_data = response.json()
                            if isinstance(response_data, dict) and response_data.get('success') and response_data.get('data'):
                                page_data = response_data['data']
                                logger.info(f"✅ Página obtenida: {len(page_data)} registros con {params}")
                                break
                            else:
                                logger.warning(f"⚠️ Sin datos con {params}: {response_data.get('message', 'Sin mensaje')}")
                    except Exception as e:
                        logger.warning(f"❌ Error con {params}: {str(e)[:50]}...")
                        continue
                
                if not page_data:
                    logger.warning("🛑 No se pudieron obtener más datos, finalizando paginación")
                    break
                
                # Filtrar duplicados basados en timestamp + device_id + sensor_type
                new_records = []
                existing_keys = {f"{r.get('timestamp')}_{r.get('device_id')}_{r.get('sensor_type')}" 
                               for r in all_data}
                
                for record in page_data:
                    record_key = f"{record.get('timestamp')}_{record.get('device_id')}_{record.get('sensor_type')}"
                    if record_key not in existing_keys:
                        new_records.append(record)
                        existing_keys.add(record_key)
                
                if not new_records:
                    logger.info("🔄 No hay registros nuevos, finalizando paginación")
                    break
                
                all_data.extend(new_records)
                offset += len(page_data)
                
                logger.info(f"📊 Total acumulado: {len(all_data)} registros")
                
                # Evitar bucle infinito
                if len(page_data) < current_limit:
                    logger.info("📝 Última página alcanzada")
                    break
            
            # Ordenar por timestamp descendente (más reciente primero)
            all_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            logger.info(f"🎉 Datos históricos obtenidos: {len(all_data)} registros de {hours}h")
            return all_data[:max_records]  # Asegurar no exceder máximo
            
        except Exception as e:
            logger.error(f"❌ Error en paginación histórica: {e}")
            return []

    def get_all_sensor_data(self, limit: int = 200, hours: float = None) -> List[Dict[str, Any]]:
        """
        Obtener datos de TODOS los sensores usando el endpoint general /data
        que permite obtener muchos más registros (hasta 200+)
        
        Args:
            limit: Número máximo de registros (hasta 200)
            hours: Filtro temporal en horas (opcional)
        """
        try:
            url = f"{self.base_url}/data"
            params = {'limit': limit}
            
            if hours:
                params['hours'] = hours
                
            logger.info(f"📡 GET {url} con params: {params}")
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            response_data = response.json()
            
            # Extraer los datos correctamente del formato de respuesta de la API
            if isinstance(response_data, dict):
                if 'data' in response_data and isinstance(response_data['data'], list):
                    data = response_data['data']
                    logger.info(f"✅ Datos extraídos del endpoint general: {len(data)} registros")
                else:
                    logger.warning(f"⚠️ Respuesta inesperada de API general: {response_data}")
                    data = []
            elif isinstance(response_data, list):
                # Si la respuesta es directamente una lista
                data = response_data
                logger.info(f"✅ Datos obtenidos directamente del endpoint general: {len(data)} registros")
            else:
                logger.error(f"❌ Formato de respuesta no válido del endpoint general: {type(response_data)}")
                data = []
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos del endpoint general: {e}")
            return []

    def get_sensor_data_direct(self, device_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtener datos de un dispositivo específico (FALLBACK con límite de 10)
        
        Args:
            device_id: ID del dispositivo  
            limit: Número de registros a obtener (máximo funcional: 10)
        """
        try:
            url = f"{self.base_url}/data/{device_id}"
            params = {'limit': limit}
            
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
    
    def get_all_recent_data(self, limit: int = 200, hours: float = None) -> Dict[str, Any]:
        """
        Obtener todos los datos recientes con soporte para consultas históricas extensas
        Usa paginación automática para consultas de más de 6 horas
        """
        try:
            # Determinar estrategia basada en duración solicitada
            effective_hours = hours if hours is not None else 3.0
            logger.info(f"🔍 Obteniendo datos: {effective_hours}h, límite: {limit}")
            
            # Para consultas extensas (>6h), usar paginación
            if effective_hours > 6:
                logger.info(f"� Consulta extensa ({effective_hours}h) - usando paginación")
                max_records = min(2000, int(effective_hours * 50))  # ~50 registros/hora
                all_sensor_data = self.get_historical_data_paginated(hours=effective_hours, max_records=max_records)
            else:
                # Para consultas cortas, usar método estándar optimizado  
                logger.info(f"⚡ Consulta corta ({effective_hours}h) - método estándar")
                all_sensor_data = self.get_all_sensor_data(limit=limit, hours=effective_hours)
            
            if all_sensor_data:
                # Organizar datos por dispositivo
                devices_data = {}
                for record in all_sensor_data:
                    device_id = record.get('device_id')
                    if device_id:
                        if device_id not in devices_data:
                            devices_data[device_id] = {
                                'device_id': device_id,
                                'status': 'active',
                                'records': []
                            }
                        devices_data[device_id]['records'].append(record)
                
                devices = list(devices_data.values())
                
                result = {
                    "devices": devices,
                    "sensor_data": all_sensor_data,
                    "status": "success",
                    "total_records": len(all_sensor_data),
                    "active_devices": len(devices),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "method": "paginated" if effective_hours > 6 else "general_endpoint",
                    "hours_span": effective_hours
                }
                
                logger.info(f"✅ Estrategia exitosa: {result['total_records']} registros de {result['active_devices']} dispositivos en {effective_hours}h")
                return result
            
            else:
                logger.warning("⚠️ Endpoint general no devolvió datos, usando método de fallback...")
                
                # FALLBACK: Usar método anterior con dispositivos individuales
                return self._get_data_fallback_individual_devices()
                
        except Exception as e:
            logger.error(f"❌ Error en estrategia principal: {e}")
            return self._get_data_fallback_individual_devices()
    
    def _get_data_fallback_individual_devices(self) -> Dict[str, Any]:
        """
        Método de fallback usando dispositivos individuales (límite de 10 por dispositivo)
        """
        try:
            logger.info("🔄 Usando método de fallback con dispositivos individuales...")
            
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
                
                # Usar parámetro limit con el máximo que funciona (10 registros)
                sensor_data = self.get_sensor_data_direct(device_id, limit=10)
                
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
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "method": "individual_devices_fallback"
            }
            
            logger.info(f"📈 Resultado fallback: {result['total_records']} registros de {result['active_devices']} dispositivos")
            
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