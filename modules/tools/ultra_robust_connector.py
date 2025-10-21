"""
Conector Ultra-Robusto para API Jetson
=====================================

Sistema de conexión con múltiples estrategias de fallback que garantiza
acceso a los datos incluso en condiciones adversas.
"""

import requests
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import time
import json

logger = logging.getLogger(__name__)

class UltraRobustJetsonConnector:
    """
    Conector ultra-robusto que garantiza acceso a los datos de la API Jetson
    mediante múltiples estrategias de conexión y fallback.
    """
    
    def __init__(self, base_url: str, max_retries: int = 5, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Configuración de sesión HTTP robusta
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'IoTAgent/2.0 (Robust-Connector)',
            'Accept': 'application/json',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        })
        
        # URLs de endpoints críticos - ACTUALIZADOS CON ENDPOINTS REALES
        self.endpoints = {
            'health': '/health',
            'devices': '/devices',
            'data': '/data',  # ENDPOINT PRINCIPAL - CONFIRMADO FUNCIONANDO
            'data_all': '/data',  # Alias para claridad
            'data_esp32': '/data/esp32_wifi_001',
            'data_arduino': '/data/arduino_eth_001',
            'data_bulk': '/bulk_data',
            'latest': '/latest_data'
        }
        
        logger.info(f"🔧 UltraRobustJetsonConnector inicializado: {base_url}")
    
    def _make_robust_request(self, endpoint: str, params: Dict = None) -> Tuple[bool, Any]:
        """
        Realizar petición HTTP con reintentos automáticos y manejo robusto de errores.
        
        Returns:
            Tuple[bool, Any]: (success, data/error_message)
        """
        url = f"{self.base_url}{endpoint}"
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"🔄 Intento {attempt + 1}/{self.max_retries}: {url}")
                
                response = self.session.get(
                    url, 
                    params=params or {},
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                # Verificar status code
                if response.status_code == 200:
                    try:
                        data = response.json()
                        logger.debug(f"✅ Éxito en intento {attempt + 1}: {len(str(data))} chars")
                        return True, data
                    except json.JSONDecodeError as json_error:
                        logger.warning(f"❌ JSON inválido en intento {attempt + 1}: {json_error}")
                        last_error = f"Invalid JSON response: {json_error}"
                else:
                    logger.warning(f"❌ HTTP {response.status_code} en intento {attempt + 1}")
                    last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ Timeout en intento {attempt + 1}")
                last_error = "Request timeout"
                
            except requests.exceptions.ConnectionError:
                logger.warning(f"🔌 Error de conexión en intento {attempt + 1}")
                last_error = "Connection error"
                
            except Exception as e:
                logger.warning(f"❌ Error inesperado en intento {attempt + 1}: {e}")
                last_error = str(e)
            
            # Esperar antes del siguiente intento (backoff exponencial)
            if attempt < self.max_retries - 1:
                wait_time = (2 ** attempt) + 1
                logger.debug(f"⏳ Esperando {wait_time}s antes del siguiente intento...")
                time.sleep(wait_time)
        
        logger.error(f"💥 Todos los intentos fallaron para {endpoint}: {last_error}")
        return False, last_error
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verificar el estado de salud de la API con información detallada.
        """
        logger.info("🏥 Ejecutando health check robusto...")
        
        success, data = self._make_robust_request('/health')
        
        if success:
            logger.info("✅ Health check exitoso")
            return {
                'status': 'healthy',
                'api_available': True,
                'response_data': data,
                'timestamp': datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ Health check falló: {data}")
            return {
                'status': 'unhealthy',
                'api_available': False,
                'error': data,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_real_data(self, limit: int = 200) -> List[Dict[str, Any]]:
        """
        Obtener datos REALES del endpoint /data (CONFIRMADO FUNCIONANDO).
        
        Args:
            limit: Límite de registros (API devuelve últimos 200 por defecto)
            
        Returns:
            Lista de registros de sensores con datos reales
        """
        logger.info(f"📊 Obteniendo datos REALES del endpoint /data...")
        
        success, response_data = self._make_robust_request('/data')
        
        if success and isinstance(response_data, dict):
            if response_data.get('success') and 'data' in response_data:
                real_data = response_data['data']
                logger.info(f"✅ DATOS REALES obtenidos: {len(real_data)} registros")
                
                # Log de estadísticas de datos reales
                if real_data:
                    devices = set(record.get('device_id') for record in real_data if record.get('device_id'))
                    sensors = set(record.get('sensor_type') for record in real_data if record.get('sensor_type'))
                    logger.info(f"📱 Dispositivos reales: {list(devices)}")
                    logger.info(f"🔬 Sensores reales: {list(sensors)}")
                    
                    # Verificar timestamps recientes
                    recent_count = 0
                    for record in real_data:
                        timestamp_str = record.get('timestamp')
                        if timestamp_str and '2025-10-21' in timestamp_str:
                            recent_count += 1
                    
                    logger.info(f"⏰ Registros de hoy: {recent_count}/{len(real_data)}")
                
                return real_data[:limit] if limit and len(real_data) > limit else real_data
            else:
                logger.warning(f"⚠️ Respuesta exitosa pero formato inesperado: {response_data}")
                return []
        else:
            logger.error(f"❌ Error obteniendo datos reales: {response_data}")
            return []
    
    def get_devices_robust(self) -> List[Dict[str, Any]]:
        """
        Obtener lista de dispositivos con estrategia ultra-robusta.
        """
        logger.info("📱 Obteniendo dispositivos con estrategia robusta...")
        
        # Estrategia 1: Endpoint principal de dispositivos
        success, data = self._make_robust_request('/devices')
        if success and isinstance(data, list) and len(data) > 0:
            devices = [d for d in data if d.get('device_id')]
            if devices:
                logger.info(f"✅ Dispositivos obtenidos via /devices: {len(devices)}")
                return devices
        
        # Estrategia 2: Intentar endpoints específicos de dispositivos
        logger.info("🔄 Estrategia 2: Endpoints específicos...")
        devices = []
        
        # Probar ESP32
        success_esp, data_esp = self._make_robust_request('/data/esp32_wifi_001', {'limit': 1})
        if success_esp and isinstance(data_esp, list) and len(data_esp) > 0:
            devices.append({
                'device_id': 'esp32_wifi_001',
                'status': 'active',
                'last_seen': data_esp[0].get('timestamp', 'unknown'),
                'method': 'endpoint_detection'
            })
            logger.info("✅ ESP32 detectado via endpoint específico")
        
        # Probar Arduino
        success_ard, data_ard = self._make_robust_request('/data/arduino_eth_001', {'limit': 1})
        if success_ard and isinstance(data_ard, list) and len(data_ard) > 0:
            devices.append({
                'device_id': 'arduino_eth_001',
                'status': 'active',
                'last_seen': data_ard[0].get('timestamp', 'unknown'),
                'method': 'endpoint_detection'
            })
            logger.info("✅ Arduino detectado via endpoint específico")
        
        if devices:
            logger.info(f"✅ Dispositivos detectados via estrategia alternativa: {len(devices)}")
            return devices
        
        # Estrategia 3: Lista hardcodeada como último recurso
        logger.warning("⚠️ Usando lista de dispositivos hardcodeada como fallback")
        return [
            {
                'device_id': 'esp32_wifi_001',
                'status': 'assumed_active',
                'method': 'hardcoded_fallback'
            },
            {
                'device_id': 'arduino_eth_001', 
                'status': 'assumed_active',
                'method': 'hardcoded_fallback'
            }
        ]
    
    def get_sensor_data_robust(self, device_id: str, limit: int = 100, hours: float = 24.0) -> List[Dict[str, Any]]:
        """
        Obtener datos de sensores con múltiples estrategias de fallback.
        """
        logger.info(f"📊 Obteniendo datos de {device_id} (limit={limit}, hours={hours})")
        
        # Calcular timestamp para filtro temporal
        time_threshold = datetime.now() - timedelta(hours=hours)
        
        # Estrategia 1: Endpoint específico del dispositivo
        endpoint = f'/data/{device_id}'
        params = {'limit': limit * 2}  # Pedir más para filtrar después
        
        success, data = self._make_robust_request(endpoint, params)
        
        if success and isinstance(data, list) and len(data) > 0:
            # Filtrar por tiempo si es necesario
            filtered_data = []
            for record in data:
                try:
                    timestamp_str = record.get('timestamp', '')
                    if timestamp_str:
                        # Convertir timestamp a datetime
                        record_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        if record_time >= time_threshold:
                            filtered_data.append(record)
                    else:
                        # Si no hay timestamp, incluir el registro
                        filtered_data.append(record)
                except:
                    # Si hay error parseando timestamp, incluir el registro
                    filtered_data.append(record)
            
            # Limitar resultados
            final_data = filtered_data[:limit] if len(filtered_data) > limit else filtered_data
            
            if final_data:
                logger.info(f"✅ Datos obtenidos para {device_id}: {len(final_data)} registros")
                return final_data
        
        # Estrategia 2: Bulk data endpoint
        logger.info(f"🔄 Estrategia 2: Bulk data para {device_id}")
        success, bulk_data = self._make_robust_request('/bulk_data', {'device': device_id, 'limit': limit})
        
        if success and isinstance(bulk_data, list) and len(bulk_data) > 0:
            device_data = [r for r in bulk_data if r.get('device_id') == device_id]
            if device_data:
                logger.info(f"✅ Datos obtenidos via bulk para {device_id}: {len(device_data)} registros")
                return device_data[:limit]
        
        # Estrategia 3: Latest data endpoint
        logger.info(f"🔄 Estrategia 3: Latest data para {device_id}")
        success, latest_data = self._make_robust_request('/latest_data')
        
        if success and isinstance(latest_data, dict):
            device_data = latest_data.get(device_id, [])
            if device_data and isinstance(device_data, list):
                logger.info(f"✅ Datos obtenidos via latest para {device_id}: {len(device_data)} registros")
                return device_data[:limit]
        
        logger.warning(f"⚠️ No se pudieron obtener datos para {device_id}")
        return []
    
    def get_all_data_comprehensive(self, hours: float = 24.0, max_records_per_device: int = 200) -> List[Dict[str, Any]]:
        """
        Obtener TODOS los datos disponibles de forma comprehensiva y robusta.
        PRIORIDAD: Usar endpoint /data REAL con filtros temporales confirmados funcionando.
        """
        logger.info(f"🚀 Iniciando recolección comprehensiva REAL de datos ({hours}h, max {max_records_per_device}/device)")
        
        # ESTRATEGIA 1: ENDPOINT REAL /data CON FILTROS TEMPORALES - CONFIRMADO FUNCIONANDO
        logger.info("📊 ESTRATEGIA 1: Usando endpoint REAL /data con filtros temporales...")
        
        # Determinar parámetros de consulta óptimos
        params = {'limit': max_records_per_device}
        
        if hours <= 24:
            params['hours'] = hours
            time_desc = f"{hours} horas"
        elif hours <= 168:  # 7 días
            params['days'] = int(hours / 24)
            time_desc = f"{int(hours / 24)} días"
        else:
            params['days'] = min(30, int(hours / 24))  # Máximo 30 días
            time_desc = f"{min(30, int(hours / 24))} días"
        
        logger.info(f"📋 Parámetros de consulta: {params} ({time_desc})")
        
        success, response_data = self._make_robust_request('/data', params=params)
        
        if success and isinstance(response_data, dict):
            if response_data.get('success') and 'data' in response_data:
                real_data = response_data['data']
                logger.info(f"✅ ÉXITO con endpoint REAL con filtros: {len(real_data)} registros obtenidos")
                
                # Log de estadísticas de datos reales
                if real_data:
                    devices = set(record.get('device_id') for record in real_data if record.get('device_id'))
                    sensors = set(record.get('sensor_type') for record in real_data if record.get('sensor_type'))
                    logger.info(f"📱 Dispositivos reales: {list(devices)}")
                    logger.info(f"🔬 Sensores reales: {list(sensors)}")
                    
                    # Verificar timestamps
                    timestamps = [r.get('timestamp') for r in real_data if r.get('timestamp')]
                    if timestamps:
                        logger.info(f"⏰ Rango temporal: {timestamps[-1][:19]} → {timestamps[0][:19]}")
                
                # Validar registros
                valid_records = []
                for record in real_data:
                    if self._validate_record(record):
                        valid_records.append(record)
                
                logger.info(f"🎯 DATOS REALES OBTENIDOS: {len(valid_records)} registros válidos")
                return valid_records
            else:
                logger.warning(f"⚠️ Respuesta exitosa pero formato inesperado: {response_data}")
        else:
            logger.error(f"❌ Error con endpoint /data con filtros: {response_data}")
        
        # ESTRATEGIA 2: FALLBACK - Endpoint /data sin filtros
        logger.warning("⚠️ Endpoint con filtros falló, usando /data sin filtros...")
        real_data = self.get_real_data(limit=max_records_per_device)
        
        if real_data and len(real_data) > 0:
            logger.info(f"✅ FALLBACK exitoso: {len(real_data)} registros obtenidos")
            
            # Filtrar por timeframe manualmente
            filtered_data = []
            now = datetime.now()
            cutoff = now - timedelta(hours=hours)
            
            for record in real_data:
                timestamp_str = record.get('timestamp')
                if timestamp_str:
                    try:
                        # Parsear timestamp (formato: "2025-10-21T11:22:20.185393-03:00")
                        record_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        if record_time >= cutoff:
                            filtered_data.append(record)
                    except:
                        # Si no se puede parsear, incluir el registro
                        filtered_data.append(record)
                else:
                    # Si no tiene timestamp, incluir el registro
                    filtered_data.append(record)
            
            logger.info(f"✅ Datos filtrados manualmente: {len(filtered_data)} registros en últimas {hours}h")
            
            # Validar registros
            valid_records = []
            for record in filtered_data:
                if self._validate_record(record):
                    valid_records.append(record)
            
            logger.info(f"🎯 DATOS REALES (FALLBACK): {len(valid_records)} registros válidos")
            return valid_records
        
        # FALLBACK: Método anterior solo si el endpoint real falla
        logger.warning("⚠️ Endpoint REAL /data falló, usando fallback por dispositivos...")
        
        all_data = []
        
        # 1. Obtener dispositivos
        devices = self.get_devices_robust()
        logger.info(f"📱 Dispositivos detectados: {len(devices)}")
        
        # 2. Recolectar datos de cada dispositivo
        for device in devices:
            device_id = device.get('device_id')
            if device_id:
                logger.info(f"📊 Recolectando datos de {device_id}...")
                device_data = self.get_sensor_data_robust(device_id, max_records_per_device, hours)
                
                if device_data:
                    all_data.extend(device_data)
                    logger.info(f"✅ {device_id}: {len(device_data)} registros añadidos")
                else:
                    logger.warning(f"⚠️ {device_id}: Sin datos obtenidos")
        
        # 3. Verificar calidad de datos
        valid_records = []
        for record in all_data:
            if self._validate_record(record):
                valid_records.append(record)
        
        logger.info(f"🎯 Recolección fallback completada: {len(valid_records)}/{len(all_data)} registros válidos")
        
        # 4. Ordenar por timestamp
        try:
            valid_records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        except:
            logger.warning("⚠️ No se pudo ordenar por timestamp")
        
        return valid_records
    
    def _validate_record(self, record: Dict[str, Any]) -> bool:
        """
        Validar que un registro tenga la estructura mínima requerida.
        """
        required_fields = ['device_id', 'sensor_type', 'value']
        return all(field in record and record[field] is not None for field in required_fields)
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtener estado comprehensivo del sistema.
        """
        logger.info("🔍 Obteniendo estado comprehensivo del sistema...")
        
        # Health check
        health = self.health_check()
        
        # Contar dispositivos
        devices = self.get_devices_robust()
        active_devices = [d for d in devices if d.get('status', '').startswith('active')]
        
        # Obtener muestra de datos
        sample_data = self.get_all_data_comprehensive(hours=1.0, max_records_per_device=10)
        
        # Análisis de datos por dispositivo
        device_stats = {}
        for device in devices:
            device_id = device.get('device_id')
            device_records = [r for r in sample_data if r.get('device_id') == device_id]
            
            device_stats[device_id] = {
                'status': device.get('status', 'unknown'),
                'records_last_hour': len(device_records),
                'sensors': list(set(r.get('sensor_type', 'unknown') for r in device_records)),
                'last_update': max([r.get('timestamp', '') for r in device_records], default='never')
            }
        
        status = {
            'api_health': health,
            'total_devices': len(devices),
            'active_devices': len(active_devices),
            'sample_records': len(sample_data),
            'device_details': device_stats,
            'timestamp': datetime.now().isoformat(),
            'connector_version': 'UltraRobust-v2.0'
        }
        
        logger.info(f"✅ Estado del sistema: {len(devices)} dispositivos, {len(sample_data)} registros de muestra")
        return status
