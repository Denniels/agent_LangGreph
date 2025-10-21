#!/usr/bin/env python3
"""
CONFIGURADOR AUTOMÁTICO DE API JETSON
====================================

Sistema robusto que maneja automáticamente:
- Detección de URLs de Jetson cambiantes
- Reconexión automática tras interrupciones
- Configuración dinámica sin necesidad de redepliegue
- Manejo de errores de red robustos
"""

import os
import json
import requests
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class JetsonAPIManager:
    """
    Gestor robusto de API de Jetson que maneja automáticamente
    cambios de URL, reconexiones y fallos de red.
    """
    
    def __init__(self):
        # URLs candidatas (orden de prioridad)
        self.candidate_urls = [
            "https://wonder-sufficiently-generator-click.trycloudflare.com",       # URL verificada que funciona
            "https://dpi-opportunity-hybrid-manufacturer.trycloudflare.com",  # URL alternativa
            # Agregar aquí otras URLs conocidas o patrones
            # "https://another-tunnel-name.trycloudflare.com",
        ]
        
        # URL activa actual
        self.active_url = None
        self.last_successful_connection = None
        self.consecutive_failures = 0
        self.max_failures = 3
        
        # Cache de configuración
        self.config_file = "jetson_api_config.json"
        self.load_config()
        
        # Configuración de timeouts robustos
        self.connection_timeout = 10  # 10 segundos para conectar (aumentado)
        self.read_timeout = 30        # 30 segundos para leer datos
        self.retry_delay = 3          # 3 segundos entre reintentos (aumentado)
        
    def load_config(self):
        """Cargar configuración guardada"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.active_url = config.get('active_url')
                    self.last_successful_connection = config.get('last_connection')
                    # Agregar URL conocida a candidatas si no está
                    if self.active_url and self.active_url not in self.candidate_urls:
                        self.candidate_urls.insert(0, self.active_url)
        except Exception as e:
            logger.warning(f"No se pudo cargar configuración: {e}")
    
    def save_config(self):
        """Guardar configuración actual"""
        try:
            config = {
                'active_url': self.active_url,
                'last_connection': datetime.now().isoformat(),
                'candidate_urls': self.candidate_urls[:5]  # Guardar solo las 5 mejores
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.warning(f"No se pudo guardar configuración: {e}")
    
    def test_url_connectivity(self, url: str) -> Tuple[bool, Dict]:
        """
        Probar conectividad de una URL específica
        
        Returns:
            Tuple[bool, Dict]: (éxito, info_respuesta)
        """
        try:
            # Test básico de health
            response = requests.get(
                f"{url}/health",
                timeout=(self.connection_timeout, self.read_timeout),
                headers={'User-Agent': 'LangGraph-Agent/2.0'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    # Test de datos reales
                    devices_response = requests.get(
                        f"{url}/devices",
                        timeout=(self.connection_timeout, self.read_timeout)
                    )
                    
                    if devices_response.status_code == 200:
                        devices_data = devices_response.json()
                        
                        # Manejar formato encapsulado o directo
                        if isinstance(devices_data, dict) and 'data' in devices_data:
                            devices = devices_data['data']
                        else:
                            devices = devices_data
                            
                        device_count = len(devices) if isinstance(devices, list) else 0
                        
                        if device_count > 0:
                            # Test final: obtener datos de sensores
                            data_response = requests.get(
                                f"{url}/data",
                                params={'limit': 1},
                                timeout=(self.connection_timeout, self.read_timeout)
                            )
                            
                            if data_response.status_code == 200:
                                sensor_response = data_response.json()
                                
                                # Manejar formato encapsulado o directo
                                if isinstance(sensor_response, dict) and 'data' in sensor_response:
                                    sensor_data = sensor_response['data']
                                else:
                                    sensor_data = sensor_response
                                    
                                record_count = len(sensor_data) if isinstance(sensor_data, list) else 0
                                
                                return True, {
                                    'devices': device_count,
                                    'has_data': record_count > 0,
                                    'response_time': response.elapsed.total_seconds(),
                                    'status': 'fully_functional'
                                }
            
            return False, {'error': 'Health check failed', 'status_code': response.status_code}
            
        except requests.exceptions.ConnectTimeout:
            return False, {'error': 'Connection timeout'}
        except requests.exceptions.ReadTimeout:
            return False, {'error': 'Read timeout'}
        except requests.exceptions.ConnectionError:
            return False, {'error': 'Connection error'}
        except Exception as e:
            return False, {'error': str(e)}
    
    def discover_working_url(self) -> Optional[str]:
        """
        Descubrir automáticamente una URL que funcione
        
        Returns:
            str: URL funcional encontrada o None
        """
        logger.info("🔍 Buscando URL de Jetson funcional...")
        
        # Priorizar URL activa si existe
        urls_to_test = []
        if self.active_url:
            urls_to_test.append(self.active_url)
        
        # Agregar otras candidatas
        for url in self.candidate_urls:
            if url not in urls_to_test:
                urls_to_test.append(url)
        
        for url in urls_to_test:
            logger.info(f"   Probando: {url}")
            is_working, info = self.test_url_connectivity(url)
            
            if is_working:
                logger.info(f"   ✅ URL funcional encontrada: {url}")
                logger.info(f"   📊 Info: {info}")
                
                # Actualizar configuración
                self.active_url = url
                self.consecutive_failures = 0
                self.save_config()
                
                return url
            else:
                logger.warning(f"   ❌ URL no funcional: {info.get('error', 'Unknown error')}")
        
        logger.error("❌ No se encontró ninguna URL funcional")
        return None
    
    def get_working_url(self, force_refresh: bool = False) -> Optional[str]:
        """
        Obtener URL funcional con cache inteligente
        
        Args:
            force_refresh: Forzar redescubrimiento
            
        Returns:
            str: URL funcional o None
        """
        # Si hay muchos fallos consecutivos, forzar redescubrimiento
        if self.consecutive_failures >= self.max_failures:
            force_refresh = True
            logger.warning(f"🔄 Forzando redescubrimiento tras {self.consecutive_failures} fallos")
        
        # Si se solicita refresh o no hay URL activa
        if force_refresh or not self.active_url:
            return self.discover_working_url()
        
        # Probar URL activa primero
        is_working, info = self.test_url_connectivity(self.active_url)
        
        if is_working:
            self.consecutive_failures = 0
            return self.active_url
        else:
            logger.warning(f"⚠️ URL activa falló: {info.get('error')}")
            self.consecutive_failures += 1
            
            # Si falló, buscar nueva URL
            return self.discover_working_url()
    
    def make_robust_request(self, endpoint: str, params: Optional[Dict] = None, retries: int = 3) -> Optional[Dict]:
        """
        Hacer request robusto con reconexión automática
        
        Args:
            endpoint: Endpoint a consultar (ej: '/devices', '/data')
            params: Parámetros de la consulta
            retries: Número de reintentos
            
        Returns:
            Dict: Respuesta de la API o None si falla
        """
        for attempt in range(retries):
            # Obtener URL funcional
            working_url = self.get_working_url(force_refresh=attempt > 0)
            
            if not working_url:
                logger.error(f"❌ No hay URL funcional disponible (intento {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(self.retry_delay)
                continue
            
            try:
                full_url = f"{working_url}{endpoint}"
                logger.debug(f"🌐 Request a: {full_url}")
                
                response = requests.get(
                    full_url,
                    params=params or {},
                    timeout=(self.connection_timeout, self.read_timeout),
                    headers={'User-Agent': 'LangGraph-Agent/2.0'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.consecutive_failures = 0
                    return data
                else:
                    logger.warning(f"⚠️ HTTP {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Error en request (intento {attempt + 1}/{retries}): {e}")
                self.consecutive_failures += 1
            
            # Esperar antes del siguiente intento
            if attempt < retries - 1:
                time.sleep(self.retry_delay)
        
        logger.error(f"❌ Falló request a {endpoint} tras {retries} intentos")
        return None

# Instancia global del manager
jetson_manager = JetsonAPIManager()

def get_jetson_manager() -> JetsonAPIManager:
    """Obtener instancia global del manager"""
    return jetson_manager

def test_jetson_manager():
    """Test del manager robusto"""
    print("🧪 TESTING JETSON API MANAGER ROBUSTO")
    print("=" * 50)
    
    manager = get_jetson_manager()
    
    # Test 1: Descubrir URL
    print("\n1️⃣ Descubriendo URL funcional...")
    url = manager.get_working_url(force_refresh=True)
    print(f"   URL encontrada: {url}")
    
    if url:
        # Test 2: Request robusto de dispositivos
        print("\n2️⃣ Probando request robusto de dispositivos...")
        devices = manager.make_robust_request('/devices')
        print(f"   Dispositivos: {len(devices) if devices else 0}")
        
        # Test 3: Request robusto de datos
        print("\n3️⃣ Probando request robusto de datos...")
        data = manager.make_robust_request('/data', {'limit': 5})
        print(f"   Registros: {len(data) if data else 0}")
        
        if data:
            print(f"   Primer registro: {data[0]}")
    
    print("\n✅ Test completado")

if __name__ == "__main__":
    test_jetson_manager()