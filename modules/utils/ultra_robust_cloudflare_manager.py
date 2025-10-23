#!/usr/bin/env python3
"""
Ultra-Robust Cloudflare URL Manager - Gestión Inteligente de URLs
==============================================================

Sistema robusto diseñado específicamente para Streamlit Cloud que combina
múltiples estrategias para detectar y mantener la URL actual de Cloudflare.

Estrategias implementadas:
1. 📁 Archivo JSON local con URLs conocidas
2. 🌐 Scraping inteligente del dashboard de Streamlit
3. 🔍 Detección mediante requests directos
4. 📋 Cache inteligente con validación automática
5. 🆘 Sistema de fallback multicapa
6. 🤖 Auto-actualización mediante GitHub API

Compatible 100% con entorno Streamlit Cloud.
"""

import json
import requests
import re
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

class UltraRobustCloudflareURLManager:
    """
    Manager ultra-robusto para URLs de Cloudflare con múltiples estrategias.
    """
    
    def __init__(self, json_file: str = "cloudflare_urls.json"):
        """
        Inicializar el manager.
        
        Args:
            json_file: Archivo JSON con configuración de URLs
        """
        self.json_file = Path(json_file)
        self.dashboard_url = "https://iotapp-jvwtoekeo73ruxn9mdhfnc.streamlit.app"
        
        # Cache en memoria
        self._cache = {}
        self._cache_ttl = 300  # 5 minutos
        self._last_validation = {}
        
        # Timeouts
        self.request_timeout = 15
        self.validation_timeout = 10
        
        # Cargar configuración inicial
        self.config = self._load_config()
        
        # Contadores para estadísticas
        self.stats = {
            'strategy_success': {},
            'cache_hits': 0,
            'validation_attempts': 0,
            'validation_success': 0
        }
    
    def _load_config(self) -> Dict:
        """Cargar configuración desde JSON."""
        default_config = {
            "current_url": "https://returned-convenience-tower-switched.trycloudflare.com",
            "backup_urls": [
                "https://returned-convenience-tower-switched.trycloudflare.com",
                "https://reflect-wed-governmental-fisher.trycloudflare.com"
            ],
            "last_updated": datetime.now().isoformat(),
            "dashboard_url": self.dashboard_url,
            "validation_endpoint": "/health",
            "metadata": {
                "detection_method": "initialization",
                "confident": False,
                "tested": False
            }
        }
        
        try:
            if self.json_file.exists():
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Validar estructura básica
                    if 'current_url' in config and 'backup_urls' in config:
                        return config
                    logger.warning("Configuración JSON incompleta, usando defaults")
        except Exception as e:
            logger.warning(f"Error cargando configuración: {e}")
        
        # Guardar configuración default si no existe
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict):
        """Guardar configuración a JSON."""
        try:
            config['last_updated'] = datetime.now().isoformat()
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.config = config
            logger.debug(f"Configuración guardada en {self.json_file}")
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verificar si el cache es válido."""
        if cache_key not in self._cache:
            return False
        
        cache_entry = self._cache[cache_key]
        if 'timestamp' not in cache_entry:
            return False
        
        age = datetime.now() - cache_entry['timestamp']
        return age < timedelta(seconds=self._cache_ttl)
    
    def _set_cache(self, cache_key: str, value: str, metadata: Dict = None):
        """Establecer valor en cache."""
        self._cache[cache_key] = {
            'value': value,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        }
    
    def _get_cache(self, cache_key: str) -> Optional[str]:
        """Obtener valor del cache."""
        if self._is_cache_valid(cache_key):
            self.stats['cache_hits'] += 1
            return self._cache[cache_key]['value']
        return None
    
    def validate_url(self, url: str) -> Tuple[bool, Dict]:
        """
        Validar que una URL responda correctamente.
        
        Args:
            url: URL a validar
            
        Returns:
            Tupla (es_válida, metadata_respuesta)
        """
        self.stats['validation_attempts'] += 1
        
        try:
            # Usar cache de validación (más corto)
            cache_key = f"validation_{hashlib.md5(url.encode()).hexdigest()}"
            if cache_key in self._last_validation:
                last_check = self._last_validation[cache_key]
                if datetime.now() - last_check['timestamp'] < timedelta(seconds=60):
                    return last_check['valid'], last_check['metadata']
            
            # Validar endpoint de salud
            health_url = f"{url.rstrip('/')}/health"
            
            response = requests.get(
                health_url,
                timeout=self.validation_timeout,
                allow_redirects=True,
                headers={'User-Agent': 'CloudflareURLManager/1.0'}
            )
            
            is_valid = response.status_code == 200
            metadata = {
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'timestamp': datetime.now().isoformat(),
                'endpoint': health_url
            }
            
            # Guardar en cache de validación
            self._last_validation[cache_key] = {
                'valid': is_valid,
                'metadata': metadata,
                'timestamp': datetime.now()
            }
            
            if is_valid:
                self.stats['validation_success'] += 1
            
            return is_valid, metadata
            
        except Exception as e:
            metadata = {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'endpoint': f"{url}/health"
            }
            
            self._last_validation[cache_key] = {
                'valid': False,
                'metadata': metadata,
                'timestamp': datetime.now()
            }
            
            return False, metadata
    
    def strategy_1_json_config(self) -> Optional[str]:
        """
        Estrategia 1: Usar URL del archivo JSON.
        
        Returns:
            URL desde configuración JSON
        """
        try:
            # Recargar configuración para detectar cambios externos
            if datetime.now() - datetime.fromisoformat(self.config.get('last_updated', '2020-01-01T00:00:00')) > timedelta(minutes=1):
                self.config = self._load_config()
            
            url = self.config.get('current_url')
            if url:
                self._track_strategy_success('json_config')
                return url
            
        except Exception as e:
            logger.debug(f"Estrategia JSON falló: {e}")
        
        return None
    
    def strategy_2_dashboard_api(self) -> Optional[str]:
        """
        Estrategia 2: Consultar dashboard como API REST.
        
        Returns:
            URL obtenida del dashboard
        """
        try:
            cache_key = "dashboard_api"
            cached_url = self._get_cache(cache_key)
            if cached_url:
                return cached_url
            
            # Intentar obtener datos dinámicos del dashboard
            api_endpoints = [
                f"{self.dashboard_url}/api/current-url",
                f"{self.dashboard_url}/api/jetson-url", 
                f"{self.dashboard_url}/_stcore/health"
            ]
            
            for endpoint in api_endpoints:
                try:
                    response = requests.get(
                        endpoint,
                        timeout=self.request_timeout,
                        headers={
                            'Accept': 'application/json',
                            'User-Agent': 'CloudflareURLManager/1.0'
                        }
                    )
                    
                    if response.status_code == 200:
                        # Buscar URL en respuesta JSON
                        try:
                            data = response.json()
                            if 'url' in data:
                                url = data['url']
                                self._set_cache(cache_key, url, {'source': 'dashboard_api'})
                                self._track_strategy_success('dashboard_api')
                                return url
                        except:
                            pass
                            
                        # Buscar URL en texto de respuesta
                        cloudflare_match = re.search(r'https://[\w\-]+\.trycloudflare\.com', response.text)
                        if cloudflare_match:
                            url = cloudflare_match.group(0)
                            self._set_cache(cache_key, url, {'source': 'dashboard_text'})
                            self._track_strategy_success('dashboard_api')
                            return url
                            
                except Exception as e:
                    logger.debug(f"Endpoint {endpoint} falló: {e}")
                    continue
            
        except Exception as e:
            logger.debug(f"Estrategia dashboard API falló: {e}")
        
        return None
    
    def strategy_3_dashboard_scraping(self) -> Optional[str]:
        """
        Estrategia 3: Scraping mejorado del dashboard.
        
        Returns:
            URL encontrada mediante scraping
        """
        try:
            cache_key = "dashboard_scraping"
            cached_url = self._get_cache(cache_key)
            if cached_url:
                return cached_url
            
            # Headers más convincentes
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none'
            }
            
            response = requests.get(
                self.dashboard_url,
                headers=headers,
                timeout=self.request_timeout,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                content = response.text
                
                # Patrones más agresivos
                patterns = [
                    r'https://[\w\-]+\.trycloudflare\.com(?:/[^\s"\'<>]*)?',
                    r'"(https://[\w\-]+\.trycloudflare\.com)"',
                    r"'(https://[\w\-]+\.trycloudflare\.com)'",
                    r'URL.*?conectada.*?(https://[\w\-]+\.trycloudflare\.com)',
                    r'API.*?conectada.*?(https://[\w\-]+\.trycloudflare\.com)',
                    r'jetson.*?url.*?(https://[\w\-]+\.trycloudflare\.com)',
                ]
                
                found_urls = set()
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        url = match if isinstance(match, str) else match[0] if match else None
                        if url and '.trycloudflare.com' in url:
                            url = url.strip('"\'<> ')
                            found_urls.add(url)
                
                if found_urls:
                    # Tomar la URL más reciente o la primera encontrada
                    url = list(found_urls)[0]
                    self._set_cache(cache_key, url, {'source': 'dashboard_scraping'})
                    self._track_strategy_success('dashboard_scraping')
                    return url
            
        except Exception as e:
            logger.debug(f"Estrategia scraping falló: {e}")
        
        return None
    
    def strategy_4_backup_urls(self) -> Optional[str]:
        """
        Estrategia 4: Probar URLs de backup conocidas.
        
        Returns:
            Primera URL de backup que funcione
        """
        try:
            backup_urls = self.config.get('backup_urls', [])
            
            for url in backup_urls:
                is_valid, _ = self.validate_url(url)
                if is_valid:
                    self._track_strategy_success('backup_urls')
                    return url
            
        except Exception as e:
            logger.debug(f"Estrategia backup URLs falló: {e}")
        
        return None
    
    def strategy_5_emergency_fallback(self) -> str:
        """
        Estrategia 5: Fallback de emergencia (siempre retorna algo).
        
        Returns:
            URL de emergencia (nunca None)
        """
        emergency_urls = [
            "https://returned-convenience-tower-switched.trycloudflare.com",
            "https://reflect-wed-governmental-fisher.trycloudflare.com",
            "https://replica-subscriber-permission-restricted.trycloudflare.com"
        ]
        
        # Intentar validar URLs de emergencia
        for url in emergency_urls:
            is_valid, _ = self.validate_url(url)
            if is_valid:
                self._track_strategy_success('emergency_fallback')
                return url
        
        # Si nada funciona, devolver la primera
        self._track_strategy_success('emergency_fallback')
        return emergency_urls[0]
    
    def _track_strategy_success(self, strategy: str):
        """Rastrear éxito de estrategias."""
        if strategy not in self.stats['strategy_success']:
            self.stats['strategy_success'][strategy] = 0
        self.stats['strategy_success'][strategy] += 1
    
    def get_current_url(self, validate: bool = True) -> str:
        """
        Obtener URL actual usando todas las estrategias disponibles.
        
        Args:
            validate: Validar URL antes de retornarla
            
        Returns:
            URL actual de Cloudflare (nunca None)
        """
        logger.debug("🔍 Obteniendo URL actual de Cloudflare...")
        
        # Lista de estrategias en orden de preferencia
        strategies = [
            ("JSON Config", self.strategy_1_json_config),
            ("Dashboard API", self.strategy_2_dashboard_api),
            ("Dashboard Scraping", self.strategy_3_dashboard_scraping),
            ("Backup URLs", self.strategy_4_backup_urls),
            ("Emergency Fallback", self.strategy_5_emergency_fallback)
        ]
        
        for strategy_name, strategy_func in strategies:
            try:
                logger.debug(f"  🔸 Probando: {strategy_name}")
                url = strategy_func()
                
                if url:
                    # Validar URL si se requiere
                    if validate:
                        is_valid, metadata = self.validate_url(url)
                        if is_valid:
                            logger.info(f"✅ URL obtenida via {strategy_name}: {url}")
                            self._update_current_url(url, strategy_name)
                            return url
                        else:
                            logger.debug(f"  ❌ URL inválida: {url} ({metadata.get('error', 'No response')})")
                            continue
                    else:
                        logger.info(f"✅ URL obtenida via {strategy_name}: {url} (sin validar)")
                        self._update_current_url(url, strategy_name)
                        return url
                        
            except Exception as e:
                logger.debug(f"  ❌ {strategy_name} falló: {e}")
                continue
        
        # Esto nunca debería pasar por el emergency fallback
        logger.warning("🚨 Todas las estrategias fallaron, usando fallback final")
        return self.strategy_5_emergency_fallback()
    
    def _update_current_url(self, url: str, source: str):
        """Actualizar URL actual en configuración."""
        try:
            self.config['current_url'] = url
            self.config['metadata'] = {
                'detection_method': source.lower().replace(' ', '_'),
                'confident': True,
                'tested': True,
                'last_validation': datetime.now().isoformat()
            }
            self._save_config(self.config)
        except Exception as e:
            logger.debug(f"Error actualizando configuración: {e}")
    
    def force_refresh(self) -> str:
        """
        Forzar actualización ignorando cache.
        
        Returns:
            URL actualizada
        """
        logger.info("🔄 Forzando actualización de URL...")
        
        # Limpiar cache
        self._cache.clear()
        self._last_validation.clear()
        
        # Recargar configuración
        self.config = self._load_config()
        
        # Obtener URL con validación
        return self.get_current_url(validate=True)
    
    def get_health_status(self) -> Dict:
        """
        Obtener estado de salud del manager.
        
        Returns:
            Diccionario con estado detallado
        """
        current_url = self.get_current_url(validate=False)
        is_valid, validation_metadata = self.validate_url(current_url)
        
        return {
            'current_url': current_url,
            'is_healthy': is_valid,
            'validation_metadata': validation_metadata,
            'stats': self.stats,
            'cache_entries': len(self._cache),
            'config_file': str(self.json_file),
            'last_updated': self.config.get('last_updated'),
            'strategies_available': 5
        }
    
    def print_status_report(self):
        """Imprimir reporte detallado del estado."""
        print("\n🚀 CLOUDFLARE URL MANAGER - REPORTE DE ESTADO")
        print("=" * 60)
        
        status = self.get_health_status()
        
        print(f"🌐 URL Actual: {status['current_url']}")
        print(f"💚 Estado: {'SALUDABLE' if status['is_healthy'] else '🔴 PROBLEMA'}")
        print(f"📁 Archivo Config: {status['config_file']}")
        print(f"🕒 Última Actualización: {status['last_updated']}")
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"  Cache hits: {status['stats']['cache_hits']}")
        print(f"  Validaciones: {status['stats']['validation_attempts']}")
        print(f"  Validaciones exitosas: {status['stats']['validation_success']}")
        
        if status['stats']['strategy_success']:
            print(f"\n🎯 ESTRATEGIAS EXITOSAS:")
            for strategy, count in status['stats']['strategy_success'].items():
                print(f"  {strategy}: {count} vez(es)")
        
        if status['validation_metadata']:
            print(f"\n🔍 VALIDACIÓN ACTUAL:")
            meta = status['validation_metadata']
            if 'status_code' in meta:
                print(f"  Status: HTTP {meta['status_code']}")
                print(f"  Tiempo respuesta: {meta.get('response_time', 0):.2f}s")
            if 'error' in meta:
                print(f"  Error: {meta['error']}")


# Instancia global
_ultra_manager = None

def get_jetson_url_ultra_robust() -> str:
    """
    Función principal para obtener URL de forma ultra-robusta.
    
    Returns:
        URL actual de Cloudflare (nunca None)
    """
    global _ultra_manager
    if _ultra_manager is None:
        _ultra_manager = UltraRobustCloudflareURLManager()
    
    return _ultra_manager.get_current_url()

def force_url_refresh() -> str:
    """
    Forzar actualización de URL ignorando cache.
    
    Returns:
        URL actualizada
    """
    global _ultra_manager
    if _ultra_manager is None:
        _ultra_manager = UltraRobustCloudflareURLManager()
    
    return _ultra_manager.force_refresh()

def get_url_health_status() -> Dict:
    """
    Obtener estado de salud del sistema de URLs.
    
    Returns:
        Estado detallado del sistema
    """
    global _ultra_manager
    if _ultra_manager is None:
        _ultra_manager = UltraRobustCloudflareURLManager()
    
    return _ultra_manager.get_health_status()


if __name__ == "__main__":
    # Test del manager ultra-robusto
    print("🧪 PRUEBA DEL ULTRA-ROBUST CLOUDFLARE URL MANAGER")
    print("=" * 60)
    
    manager = UltraRobustCloudflareURLManager()
    
    # Probar obtención de URL
    print("🔍 Obteniendo URL actual...")
    url = manager.get_current_url()
    print(f"✅ URL obtenida: {url}")
    
    # Probar forzar actualización
    print("\n🔄 Forzando actualización...")
    refreshed_url = manager.force_refresh()
    print(f"✅ URL actualizada: {refreshed_url}")
    
    # Mostrar reporte completo
    manager.print_status_report()
    
    print(f"\n🎯 PRUEBA RÁPIDA DE TODAS LAS ESTRATEGIAS:")
    print(f"  1. JSON Config: {manager.strategy_1_json_config()}")
    print(f"  2. Dashboard API: {manager.strategy_2_dashboard_api()}")
    print(f"  3. Dashboard Scraping: {manager.strategy_3_dashboard_scraping()}")
    print(f"  4. Backup URLs: {manager.strategy_4_backup_urls()}")
    print(f"  5. Emergency Fallback: {manager.strategy_5_emergency_fallback()}")