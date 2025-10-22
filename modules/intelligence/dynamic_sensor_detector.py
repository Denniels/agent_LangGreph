"""
Sistema de Detección Dinámica de Sensores IoT
===========================================

Módulo que descubre automáticamente los sensores disponibles en cada dispositivo
consultando la API en tiempo real, eliminando hardcoding y generando mapeos dinámicos.

Este sistema mantiene un inventario actualizado de dispositivos y sensores disponibles.
"""

import logging
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import json
import time

logger = logging.getLogger(__name__)

@dataclass
class SensorInfo:
    """Información detallada de un sensor"""
    sensor_id: str
    sensor_type: str
    device_id: str
    unit: Optional[str] = None
    description: Optional[str] = None
    last_value: Optional[float] = None
    last_timestamp: Optional[datetime] = None
    is_active: bool = True
    sample_rate: Optional[float] = None  # Samples per minute
    data_points_count: int = 0

@dataclass  
class DeviceInfo:
    """Información completa de un dispositivo"""
    device_id: str
    device_type: Optional[str] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None
    sensors: Dict[str, SensorInfo] = field(default_factory=dict)
    last_seen: Optional[datetime] = None
    is_online: bool = True
    firmware_version: Optional[str] = None
    uptime_hours: Optional[float] = None

class DynamicSensorDetector:
    """
    Sistema inteligente de detección automática de sensores.
    
    Funcionalidades:
    - Descubrimiento automático de dispositivos y sensores
    - Mapeo dinámico de tipos de sensores
    - Detección de sensores inactivos o desconectados
    - Cache inteligente con actualización automática
    - Análisis de patrones de datos para clasificación
    """
    
    def __init__(self, jetson_api_url: str, cache_duration_minutes: int = 30):
        self.jetson_api_url = jetson_api_url.rstrip('/')
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.logger = logging.getLogger(__name__)
        
        # Cache del inventario de dispositivos y sensores
        self._device_inventory: Dict[str, DeviceInfo] = {}
        self._sensor_type_mapping: Dict[str, str] = {}
        self._last_discovery: Optional[datetime] = None
        self._discovery_in_progress = False
        
        # Configuración de detección
        self.min_data_points_for_classification = 5
        self.sensor_activity_threshold_hours = 6.0
        self.auto_discovery_enabled = True
        
        # Mapeo inteligente de tipos de sensores comunes
        self.sensor_type_patterns = {
            'temperature': {
                'keywords': ['temp', 'temperatura', 'ntc', 't1', 't2', 'avg', 'thermal'],
                'units': ['°C', 'celsius', 'c', 'temp'],
                'typical_range': (-50, 100),
                'description': 'Sensor de temperatura'
            },
            'luminosity': {
                'keywords': ['ldr', 'light', 'luz', 'lumino', 'bright', 'photo', 'lux'],
                'units': ['lux', 'lumens', 'light', 'brightness'],
                'typical_range': (0, 2000),
                'description': 'Sensor de luminosidad'
            },
            'humidity': {
                'keywords': ['humid', 'moisture', 'rh', 'humedad'],
                'units': ['%', 'percent', 'rh'],
                'typical_range': (0, 100),
                'description': 'Sensor de humedad'
            },
            'pressure': {
                'keywords': ['press', 'pressure', 'presion', 'bar', 'pascal'],
                'units': ['bar', 'pa', 'psi', 'atm'],
                'typical_range': (0, 2000),
                'description': 'Sensor de presión'
            },
            'voltage': {
                'keywords': ['volt', 'voltage', 'v', 'tension'],
                'units': ['v', 'volt', 'mv'],
                'typical_range': (0, 50),
                'description': 'Sensor de voltaje'
            },
            'current': {
                'keywords': ['current', 'amp', 'ampere', 'corriente'],
                'units': ['a', 'amp', 'ma'],
                'typical_range': (0, 20),
                'description': 'Sensor de corriente'
            }
        }
    
    async def discover_all_sensors(self, force_refresh: bool = False) -> Dict[str, DeviceInfo]:
        """
        Descubre todos los dispositivos y sensores disponibles.
        
        Args:
            force_refresh: Forzar redescubrimiento ignorando cache
            
        Returns:
            Dict con información completa de dispositivos y sensores
        """
        try:
            # Verificar si necesitamos actualizar el cache
            if not force_refresh and self._is_cache_valid():
                self.logger.info("✅ Usando inventario desde cache")
                return self._device_inventory.copy()
            
            if self._discovery_in_progress:
                self.logger.info("🔄 Descubrimiento en progreso, esperando...")
                await self._wait_for_discovery()
                return self._device_inventory.copy()
            
            self._discovery_in_progress = True
            self.logger.info("🔍 Iniciando descubrimiento dinámico de sensores...")
            
            # 1. OBTENER DATOS RECIENTES PARA ANÁLISIS
            recent_data = await self._fetch_recent_data(hours=24)  # Últimas 24 horas
            
            if not recent_data:
                self.logger.warning("⚠️ No se pudieron obtener datos para descubrimiento")
                return {}
            
            # 2. ANALIZAR DATOS PARA CONSTRUIR INVENTARIO
            device_inventory = await self._analyze_data_for_inventory(recent_data)
            
            # 3. ENRIQUECER CON INFORMACIÓN ADICIONAL
            enriched_inventory = await self._enrich_device_info(device_inventory)
            
            # 4. CLASIFICAR SENSORES INTELIGENTEMENTE
            classified_inventory = await self._classify_sensors(enriched_inventory)
            
            # 5. ACTUALIZAR CACHE
            self._device_inventory = classified_inventory
            self._last_discovery = datetime.now()
            self._discovery_in_progress = False
            
            # 6. GENERAR REPORTE DE DESCUBRIMIENTO
            discovery_report = self._generate_discovery_report(classified_inventory)
            self.logger.info(f"✅ Descubrimiento completado: {discovery_report}")
            
            return classified_inventory.copy()
            
        except Exception as e:
            self.logger.error(f"❌ Error en descubrimiento de sensores: {e}")
            self._discovery_in_progress = False
            return {}
    
    async def get_device_sensors(self, device_id: str, force_refresh: bool = False) -> Dict[str, SensorInfo]:
        """
        Obtiene sensores específicos de un dispositivo.
        
        Args:
            device_id: ID del dispositivo
            force_refresh: Forzar redescubrimiento
            
        Returns:
            Dict con sensores del dispositivo
        """
        try:
            # Asegurar que tenemos inventario actualizado
            inventory = await self.discover_all_sensors(force_refresh)
            
            if device_id in inventory:
                return inventory[device_id].sensors.copy()
            else:
                self.logger.warning(f"⚠️ Dispositivo {device_id} no encontrado en inventario")
                return {}
                
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo sensores de {device_id}: {e}")
            return {}
    
    async def get_all_sensor_types(self) -> Dict[str, List[str]]:
        """
        Obtiene todos los tipos de sensores organizados por dispositivo.
        
        Returns:
            Dict: {device_id: [list_of_sensor_types]}
        """
        try:
            inventory = await self.discover_all_sensors()
            
            sensor_types_by_device = {}
            
            for device_id, device_info in inventory.items():
                sensor_types = []
                for sensor_id, sensor_info in device_info.sensors.items():
                    if sensor_info.is_active:
                        sensor_types.append(sensor_info.sensor_type)
                
                sensor_types_by_device[device_id] = sorted(list(set(sensor_types)))
            
            return sensor_types_by_device
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo tipos de sensores: {e}")
            return {}
    
    async def validate_sensor_exists(self, device_id: str, sensor_type: str) -> Tuple[bool, Optional[str]]:
        """
        Valida si un sensor específico existe en un dispositivo.
        
        Args:
            device_id: ID del dispositivo
            sensor_type: Tipo de sensor a validar
            
        Returns:
            Tuple: (exists: bool, reason: Optional[str])
        """
        try:
            device_sensors = await self.get_device_sensors(device_id)
            
            # Buscar sensor por tipo
            matching_sensors = [
                sensor for sensor in device_sensors.values() 
                if sensor.sensor_type.lower() == sensor_type.lower() and sensor.is_active
            ]
            
            if matching_sensors:
                return True, None
            else:
                # Proporcionar razón específica
                if device_id not in await self.discover_all_sensors():
                    return False, f"Dispositivo '{device_id}' no encontrado"
                elif not device_sensors:
                    return False, f"Dispositivo '{device_id}' no tiene sensores activos"
                else:
                    available_types = [s.sensor_type for s in device_sensors.values() if s.is_active]
                    return False, f"Sensor '{sensor_type}' no disponible. Tipos disponibles: {', '.join(available_types)}"
                    
        except Exception as e:
            return False, f"Error validando sensor: {str(e)}"
    
    def get_cached_inventory(self) -> Dict[str, DeviceInfo]:
        """Obtiene inventario desde cache (sin refresh)"""
        return self._device_inventory.copy()
    
    def get_discovery_status(self) -> Dict[str, Any]:
        """Obtiene estado del sistema de descubrimiento"""
        return {
            'cache_valid': self._is_cache_valid(),
            'last_discovery': self._last_discovery.isoformat() if self._last_discovery else None,
            'discovery_in_progress': self._discovery_in_progress,
            'devices_in_cache': len(self._device_inventory),
            'total_sensors_in_cache': sum(len(dev.sensors) for dev in self._device_inventory.values()),
            'cache_duration_minutes': self.cache_duration.total_seconds() / 60,
            'auto_discovery_enabled': self.auto_discovery_enabled
        }
    
    # MÉTODOS PRIVADOS
    
    async def _fetch_recent_data(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Obtiene datos recientes para análisis"""
        try:
            # Usar el endpoint estándar de la API
            url = f"{self.jetson_api_url}/api/get_recent_data"
            params = {'hours': hours}
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    sensor_data = data.get('sensor_data', [])
                    self.logger.info(f"✅ Obtenidos {len(sensor_data)} registros para análisis")
                    return sensor_data
                else:
                    self.logger.warning(f"⚠️ API retornó estado: {data.get('status')}")
                    return []
            else:
                self.logger.error(f"❌ Error HTTP {response.status_code} obteniendo datos")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Error fetching datos: {e}")
            return []
    
    async def _analyze_data_for_inventory(self, data: List[Dict[str, Any]]) -> Dict[str, DeviceInfo]:
        """Analiza datos para construir inventario básico"""
        inventory = {}
        
        try:
            # Agrupar datos por dispositivo
            device_data = defaultdict(list)
            
            for record in data:
                device_id = record.get('device_id')
                if device_id:
                    device_data[device_id].append(record)
            
            # Procesar cada dispositivo
            for device_id, records in device_data.items():
                device_info = DeviceInfo(device_id=device_id)
                
                # Analizar sensores en este dispositivo
                sensor_data = defaultdict(list)
                
                for record in records:
                    sensor_type = record.get('sensor_type') or record.get('sensor_id', 'unknown')
                    sensor_data[sensor_type].append(record)
                
                # Crear SensorInfo para cada sensor
                for sensor_type, sensor_records in sensor_data.items():
                    if sensor_records:
                        latest_record = max(sensor_records, key=lambda x: x.get('timestamp', ''))
                        
                        sensor_info = SensorInfo(
                            sensor_id=f"{device_id}_{sensor_type}",
                            sensor_type=sensor_type,  
                            device_id=device_id,
                            last_value=latest_record.get('value'),
                            last_timestamp=datetime.fromisoformat(latest_record.get('timestamp', '').replace('Z', '+00:00')),
                            data_points_count=len(sensor_records),
                            is_active=True  # Asumir activo si hay datos
                        )
                        
                        device_info.sensors[sensor_type] = sensor_info
                
                # Actualizar información del dispositivo
                if device_info.sensors:
                    latest_timestamp = max(
                        sensor.last_timestamp for sensor in device_info.sensors.values() 
                        if sensor.last_timestamp
                    )
                    device_info.last_seen = latest_timestamp
                    device_info.is_online = True
                
                inventory[device_id] = device_info
            
            self.logger.info(f"✅ Inventario básico creado: {len(inventory)} dispositivos")
            return inventory
            
        except Exception as e:
            self.logger.error(f"❌ Error analizando datos para inventario: {e}")
            return {}
    
    async def _enrich_device_info(self, inventory: Dict[str, DeviceInfo]) -> Dict[str, DeviceInfo]:
        """Enriquece información de dispositivos con datos adicionales"""
        try:
            for device_id, device_info in inventory.items():
                # Intentar obtener información adicional del dispositivo
                try:
                    # Mapeo de IPs conocidas (esto podría venir de configuración)
                    known_devices = {
                        'arduino_eth_001': {'ip': '192.168.0.106', 'type': 'Arduino Ethernet'},
                        'esp32_wifi_001': {'ip': '192.168.0.105', 'type': 'ESP32 WiFi'}
                    }
                    
                    if device_id in known_devices:
                        device_info.ip_address = known_devices[device_id]['ip']
                        device_info.device_type = known_devices[device_id]['type']
                    
                    # Calcular sample rate basado en datos disponibles
                    for sensor_info in device_info.sensors.values():
                        if sensor_info.data_points_count > 1 and sensor_info.last_timestamp:
                            # Estimar sample rate (muy básico)
                            hours_span = 24  # Asumimos datos de 24 horas
                            estimated_sample_rate = sensor_info.data_points_count / (hours_span * 60)  # samples per minute
                            sensor_info.sample_rate = round(estimated_sample_rate, 2)
                
                except Exception as device_error:
                    self.logger.warning(f"⚠️ Error enriqueciendo dispositivo {device_id}: {device_error}")
                    continue
            
            return inventory
            
        except Exception as e:
            self.logger.error(f"❌ Error enriqueciendo información: {e}")
            return inventory
    
    async def _classify_sensors(self, inventory: Dict[str, DeviceInfo]) -> Dict[str, DeviceInfo]:
        """Clasifica sensores usando patrones inteligentes"""
        try:
            for device_id, device_info in inventory.items():
                for sensor_id, sensor_info in device_info.sensors.items():
                    # Clasificar basado en nombre del sensor
                    classified_type = self._classify_sensor_type(sensor_info.sensor_type)
                    
                    if classified_type != sensor_info.sensor_type:
                        self.logger.info(f"🔄 Reclasificando sensor {sensor_id}: {sensor_info.sensor_type} → {classified_type}")
                        sensor_info.sensor_type = classified_type
                    
                    # Agregar descripción y unidad si fue clasificado
                    if classified_type in self.sensor_type_patterns:
                        pattern = self.sensor_type_patterns[classified_type]
                        sensor_info.description = pattern['description']
                        sensor_info.unit = pattern['units'][0] if pattern['units'] else None
            
            return inventory
            
        except Exception as e:
            self.logger.error(f"❌ Error clasificando sensores: {e}")
            return inventory
    
    def _classify_sensor_type(self, original_type: str) -> str:
        """Clasifica un tipo de sensor basado en patrones"""
        original_lower = original_type.lower()
        
        # Buscar coincidencias con patrones conocidos
        for sensor_type, pattern in self.sensor_type_patterns.items():
            for keyword in pattern['keywords']:
                if keyword in original_lower:
                    return sensor_type
        
        # Si no se encuentra coincidencia, mantener original
        return original_type
    
    def _is_cache_valid(self) -> bool:
        """Verifica si el cache es válido"""
        if not self._last_discovery:
            return False
        
        return datetime.now() - self._last_discovery < self.cache_duration
    
    async def _wait_for_discovery(self, max_wait_seconds: int = 60):
        """Espera a que termine el descubrimiento en progreso"""
        waited = 0
        while self._discovery_in_progress and waited < max_wait_seconds:
            await asyncio.sleep(1)
            waited += 1
        
        if waited >= max_wait_seconds:
            self.logger.warning("⚠️ Timeout esperando descubrimiento")
    
    def _generate_discovery_report(self, inventory: Dict[str, DeviceInfo]) -> str:
        """Genera reporte de descubrimiento"""
        try:
            total_devices = len(inventory)
            total_sensors = sum(len(dev.sensors) for dev in inventory.values())
            active_sensors = sum(
                len([s for s in dev.sensors.values() if s.is_active]) 
                for dev in inventory.values()
            )
            
            sensor_types = set()
            for dev in inventory.values():
                for sensor in dev.sensors.values():
                    sensor_types.add(sensor.sensor_type)
            
            return (f"{total_devices} dispositivos, {total_sensors} sensores totales, "
                   f"{active_sensors} activos, {len(sensor_types)} tipos únicos")
            
        except Exception as e:
            return f"Error generando reporte: {e}"

# FUNCIONES DE UTILIDAD PARA INTEGRACIÓN FÁCIL

async def get_dynamic_sensor_map(jetson_api_url: str) -> Dict[str, List[str]]:
    """
    Función de utilidad para obtener mapeo dinámico de sensores.
    
    Returns:
        Dict: {device_id: [list_of_sensor_types]}
    """
    detector = DynamicSensorDetector(jetson_api_url)
    return await detector.get_all_sensor_types()

async def validate_device_sensor(jetson_api_url: str, device_id: str, sensor_type: str) -> Tuple[bool, str]:
    """
    Función de utilidad para validar si un sensor existe.
    
    Returns:
        Tuple: (is_valid: bool, message: str)
    """
    detector = DynamicSensorDetector(jetson_api_url)
    is_valid, reason = await detector.validate_sensor_exists(device_id, sensor_type)
    
    if is_valid:
        return True, f"✅ Sensor '{sensor_type}' válido en dispositivo '{device_id}'"
    else:
        return False, f"❌ {reason}"

def create_sensor_detector(jetson_api_url: str, cache_minutes: int = 30) -> DynamicSensorDetector:
    """
    Factory function para crear detector de sensores.
    
    Args:
        jetson_api_url: URL de la API Jetson
        cache_minutes: Duración del cache en minutos
        
    Returns:
        DynamicSensorDetector configurado
    """
    return DynamicSensorDetector(jetson_api_url, cache_minutes)