#!/usr/bin/env python3
"""
JETSON API CONNECTOR ROBUSTO V2
===============================

Versión robusta que maneja automáticamente:
- Reconexión tras interrupciones
- URLs cambiantes de Cloudflare
- Errores de red y timeouts
- Cache inteligente de configuración
"""

import logging
from typing import Dict, List, Optional, Any
from modules.utils.jetson_api_manager import get_jetson_manager

logger = logging.getLogger(__name__)

class RobustJetsonAPIConnector:
    """
    Conector robusto para API de Jetson que maneja automáticamente
    todos los problemas de conectividad y configuración.
    """
    
    def __init__(self, fallback_url: str = None):
        """
        Inicializar conector robusto
        
        Args:
            fallback_url: URL de respaldo (opcional)
        """
        self.manager = get_jetson_manager()
        
        # Agregar URL de respaldo si se proporciona
        if fallback_url and fallback_url not in self.manager.candidate_urls:
            self.manager.candidate_urls.append(fallback_url)
        
        # Configurar logging
        self.setup_logging()
        
        logger.info("🚀 RobustJetsonAPIConnector inicializado")
    
    def setup_logging(self):
        """Configurar logging específico"""
        # El logging ya está configurado globalmente
        pass
    
    @property
    def base_url(self) -> Optional[str]:
        """Obtener URL base actual (compatible con código existente)"""
        return self.manager.active_url
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Obtener estado de salud del sistema con reconexión automática
        
        Returns:
            Dict con el estado de salud
        """
        logger.debug("🏥 Obteniendo estado de salud...")
        
        response = self.manager.make_robust_request('/health')
        
        if response:
            logger.info(f"✅ Sistema saludable: {response.get('devices_count', 0)} dispositivos")
            return response
        else:
            logger.error("❌ Sistema no disponible")
            return {
                'status': 'unhealthy',
                'error': 'No se pudo conectar a la API de Jetson',
                'devices_count': 0
            }
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """
        Obtener lista de dispositivos con reconexión automática
        
        Returns:
            Lista de dispositivos disponibles
        """
        logger.debug("📱 Obteniendo lista de dispositivos...")
        
        response = self.manager.make_robust_request('/devices')
        
        if response is None:
            logger.warning("⚠️ No se pudieron obtener dispositivos")
            return []
        
        # Manejar ambos formatos de respuesta
        devices = []
        if isinstance(response, list):
            devices = response
        elif isinstance(response, dict):
            if 'success' in response and response.get('success') and 'data' in response:
                devices = response['data']
            elif 'devices' in response:
                devices = response['devices']
        
        logger.info(f"📱 Dispositivos obtenidos: {len(devices)}")
        for device in devices:
            logger.debug(f"   - {device.get('device_id', 'unknown')}: {device.get('status', 'unknown')}")
        
        return devices
    
    def get_sensor_data(self, 
                       device_id: Optional[str] = None, 
                       limit: int = 50, 
                       sensor_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtener datos de sensores con reconexión automática
        
        Args:
            device_id: ID del dispositivo (opcional)
            limit: Límite de registros
            sensor_type: Tipo de sensor específico (opcional)
            
        Returns:
            Lista de registros de sensores
        """
        # Determinar endpoint
        if device_id:
            endpoint = f'/data/{device_id}'
            logger.debug(f"📊 Obteniendo datos de {device_id} (límite: {limit})...")
        else:
            endpoint = '/data'
            logger.debug(f"📊 Obteniendo datos generales (límite: {limit})...")
        
        # Preparar parámetros
        params = {'limit': limit}
        
        # Hacer request robusto
        response = self.manager.make_robust_request(endpoint, params)
        
        if response is None:
            logger.warning("⚠️ No se pudieron obtener datos de sensores")
            return []
        
        # Procesar respuesta (manejar ambos formatos)
        data = []
        if isinstance(response, list):
            data = response
        elif isinstance(response, dict):
            if 'success' in response and response.get('success') and 'data' in response:
                data = response['data']
            elif 'sensors' in response:
                data = response['sensors']
        
        # Filtrar por tipo de sensor si se especifica
        if sensor_type and data:
            data = [record for record in data if record.get('sensor_type') == sensor_type]
            logger.debug(f"   Filtrado por {sensor_type}: {len(data)} registros")
        
        logger.info(f"📊 Datos obtenidos: {len(data)} registros")
        if data:
            logger.debug(f"   Primer registro: {data[0].get('device_id')} - {data[0].get('sensor_type')} = {data[0].get('value')}")
        
        return data
    
    def get_latest_readings(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtener las últimas lecturas organizadas por dispositivo y tipo
        
        Args:
            device_id: ID del dispositivo específico (opcional)
            
        Returns:
            Dict organizado por dispositivo y tipo de sensor
        """
        logger.debug("📈 Obteniendo últimas lecturas...")
        
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
        
        logger.info(f"📈 Lecturas organizadas para {len(organized_data)} dispositivos")
        return organized_data
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Probar conexión completa y devolver información detallada
        
        Returns:
            Dict con información detallada de la conexión
        """
        logger.info("🧪 Iniciando test de conexión completa...")
        
        test_results = {
            'timestamp': logger.handlers[0].formatter.formatTime() if logger.handlers else 'unknown',
            'url_discovery': False,
            'health_check': False,
            'devices_available': False,
            'data_accessible': False,
            'active_url': None,
            'devices_count': 0,
            'data_records': 0,
            'details': []
        }
        
        try:
            # 1. Descubrir URL funcional
            url = self.manager.get_working_url(force_refresh=True)
            if url:
                test_results['url_discovery'] = True
                test_results['active_url'] = url
                test_results['details'].append(f"✅ URL encontrada: {url}")
            else:
                test_results['details'].append("❌ No se encontró URL funcional")
                return test_results
            
            # 2. Health check
            health = self.get_health_status()
            if health.get('status') == 'healthy':
                test_results['health_check'] = True
                test_results['details'].append(f"✅ Health check OK: {health.get('devices_count', 0)} dispositivos")
            else:
                test_results['details'].append("❌ Health check falló")
                return test_results
            
            # 3. Obtener dispositivos
            devices = self.get_devices()
            if devices:
                test_results['devices_available'] = True
                test_results['devices_count'] = len(devices)
                test_results['details'].append(f"✅ Dispositivos: {len(devices)} encontrados")
                
                # 4. Obtener datos
                data = self.get_sensor_data(limit=10)
                if data:
                    test_results['data_accessible'] = True
                    test_results['data_records'] = len(data)
                    test_results['details'].append(f"✅ Datos: {len(data)} registros obtenidos")
                else:
                    test_results['details'].append("⚠️ No se obtuvieron datos de sensores")
            else:
                test_results['details'].append("❌ No se encontraron dispositivos")
        
        except Exception as e:
            test_results['details'].append(f"❌ Error en test: {e}")
            logger.error(f"Error en test de conexión: {e}")
        
        # Determinar éxito general
        success = all([
            test_results['url_discovery'],
            test_results['health_check'],
            test_results['devices_available']
        ])
        
        test_results['success'] = success
        
        if success:
            logger.info("✅ Test de conexión completado exitosamente")
        else:
            logger.warning("⚠️ Test de conexión falló parcialmente")
        
        return test_results

# Función de compatibilidad con código existente
def create_jetson_connector() -> RobustJetsonAPIConnector:
    """Crear instancia del conector robusto (compatible con código existente)"""
    return RobustJetsonAPIConnector()

# Alias para mantener compatibilidad
JetsonAPIConnector = RobustJetsonAPIConnector

if __name__ == "__main__":
    # Test del conector robusto
    print("🧪 TESTING ROBUST JETSON API CONNECTOR")
    print("=" * 60)
    
    connector = RobustJetsonAPIConnector()
    
    # Test completo
    results = connector.test_connection()
    
    print("\n📊 RESULTADOS DEL TEST:")
    print("-" * 30)
    for detail in results['details']:
        print(f"   {detail}")
    
    print(f"\n🎯 ÉXITO GENERAL: {'✅ SÍ' if results['success'] else '❌ NO'}")
    print(f"📱 Dispositivos: {results['devices_count']}")
    print(f"📊 Registros: {results['data_records']}")
    print(f"🌐 URL activa: {results['active_url']}")