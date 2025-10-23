#!/usr/bin/env python3
"""
SOLUCIÓN DEFINITIVA: Local URL Change Detector + GitHub Auto-Updater
================================================================

Script que se ejecuta en el SERVIDOR LOCAL donde está la API de datos.
Detecta cambios en la URL de Cloudflare Tunnel y automáticamente 
actualiza el repositorio de GitHub.

FUNCIONALIDADES:
1. 🔍 Detecta la URL actual de Cloudflare Tunnel localmente
2. 📊 Compara con URLs conocidas para detectar cambios
3. 🔄 Actualiza archivos del repositorio automáticamente
4. 🚀 Hace commit y push automático a GitHub
5. 📱 Notifica a Streamlit Cloud para que se redepliegue

INSTALACIÓN EN SERVIDOR LOCAL:
1. Clonar repo: git clone https://github.com/Denniels/agent_LangGreph.git
2. Configurar token GitHub en variable de entorno: GITHUB_TOKEN
3. Ejecutar: python local_url_detector.py --monitor
4. O como cron job cada 5 minutos

REQUIERE:
- Git configurado en servidor local
- Token GitHub con permisos de escritura
- Acceso a internet para push a GitHub
"""

import os
import sys
import json
import time
import requests
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
import argparse
import socket
import platform

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | LocalURLDetector | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('url_detector.log')
    ]
)
logger = logging.getLogger(__name__)

class LocalURLDetector:
    """
    Detector de URLs que se ejecuta en el servidor local donde está la API.
    """
    
    def __init__(self, repo_path: str = ".", github_token: str = None):
        """
        Inicializar detector.
        
        Args:
            repo_path: Ruta al repositorio local
            github_token: Token de GitHub para push automático
        """
        self.repo_path = Path(repo_path).resolve()
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        
        # Archivos a actualizar
        self.files_to_update = [
            'cloudflare_urls.json',
            'modules/utils/hybrid_url_manager.py'
        ]
        
        # URLs para detectar localmente
        self.local_detection_urls = [
            'http://localhost:8000',
            'http://127.0.0.1:8000',
            'http://0.0.0.0:8000',
        ]
        
        # Cache
        self.cache_file = Path('url_detector_cache.json')
        self.cache = self._load_cache()
        
        logger.info(f"🔍 LocalURLDetector inicializado en: {self.repo_path}")
        logger.info(f"💻 Sistema: {platform.system()} {platform.release()}")
        logger.info(f"🌐 Hostname: {socket.gethostname()}")
    
    def _load_cache(self) -> Dict:
        """Cargar cache del detector."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.debug(f"Error cargando cache: {e}")
        
        return {
            'last_known_url': None,
            'last_check': None,
            'check_count': 0,
            'successful_updates': 0,
            'failed_attempts': 0
        }
    
    def _save_cache(self):
        """Guardar cache."""
        try:
            self.cache['last_check'] = datetime.now().isoformat()
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error guardando cache: {e}")
    
    def detect_local_api_url(self) -> Optional[str]:
        """
        Detectar URL de la API local consultando endpoints locales.
        
        Returns:
            URL de Cloudflare detectada o None
        """
        logger.debug("🔍 Detectando URL local de la API...")
        
        for local_url in self.local_detection_urls:
            try:
                # Intentar obtener información del tunnel desde la API local
                endpoints_to_try = [
                    f"{local_url}/tunnel-info",
                    f"{local_url}/cloudflare-url", 
                    f"{local_url}/public-url",
                    f"{local_url}/health",
                    f"{local_url}/"
                ]
                
                for endpoint in endpoints_to_try:
                    try:
                        response = requests.get(endpoint, timeout=5)
                        if response.status_code == 200:
                            
                            # Buscar URL de Cloudflare en respuesta JSON
                            try:
                                data = response.json()
                                if 'public_url' in data:
                                    url = data['public_url']
                                    if '.trycloudflare.com' in url:
                                        logger.info(f"✅ URL detectada desde {endpoint}: {url}")
                                        return url
                                        
                                if 'tunnel_url' in data:
                                    url = data['tunnel_url']
                                    if '.trycloudflare.com' in url:
                                        logger.info(f"✅ URL detectada desde {endpoint}: {url}")
                                        return url
                            except:
                                pass
                            
                            # Buscar URL en texto de respuesta
                            import re
                            cloudflare_match = re.search(r'https://[\w\-]+\.trycloudflare\.com', response.text)
                            if cloudflare_match:
                                url = cloudflare_match.group(0)
                                logger.info(f"✅ URL detectada desde {endpoint}: {url}")
                                return url
                                
                    except Exception as e:
                        logger.debug(f"Endpoint {endpoint} falló: {e}")
                        continue
                        
            except Exception as e:
                logger.debug(f"URL local {local_url} no accesible: {e}")
                continue
        
        return None
    
    def detect_cloudflare_url_via_logs(self) -> Optional[str]:
        """
        Detectar URL leyendo logs de Cloudflare tunnel.
        
        Returns:
            URL detectada desde logs
        """
        logger.debug("📋 Buscando URL en logs de Cloudflare...")
        
        # Posibles ubicaciones de logs
        log_paths = [
            'cloudflared.log',
            '/var/log/cloudflared.log',
            '~/.cloudflared/cloudflared.log',
            './logs/cloudflared.log'
        ]
        
        for log_path in log_paths:
            try:
                log_file = Path(log_path).expanduser()
                if log_file.exists():
                    # Leer últimas líneas del log
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-50:]  # Últimas 50 líneas
                    
                    # Buscar URL en logs
                    import re
                    for line in reversed(lines):
                        if 'trycloudflare.com' in line:
                            match = re.search(r'https://[\w\-]+\.trycloudflare\.com', line)
                            if match:
                                url = match.group(0)
                                logger.info(f"✅ URL detectada desde logs: {url}")
                                return url
                                
            except Exception as e:
                logger.debug(f"Error leyendo log {log_path}: {e}")
                continue
        
        return None
    
    def detect_current_cloudflare_url(self) -> Optional[str]:
        """
        Detectar URL actual de Cloudflare usando múltiples métodos.
        
        Returns:
            URL actual detectada
        """
        logger.info("🔍 Detectando URL actual de Cloudflare...")
        
        # Método 1: API local
        url = self.detect_local_api_url()
        if url:
            return url
        
        # Método 2: Logs de Cloudflare
        url = self.detect_cloudflare_url_via_logs()
        if url:
            return url
        
        # Método 3: Consulta externa (si tenemos URL previa)
        if self.cache.get('last_known_url'):
            try:
                response = requests.get(f"{self.cache['last_known_url']}/health", timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ URL anterior sigue funcionando: {self.cache['last_known_url']}")
                    return self.cache['last_known_url']
            except:
                logger.debug("URL anterior ya no funciona")
        
        logger.warning("⚠️ No se pudo detectar URL actual")
        return None
    
    def validate_url(self, url: str) -> bool:
        """
        Validar que una URL funcione correctamente.
        
        Args:
            url: URL a validar
            
        Returns:
            True si la URL es válida
        """
        try:
            response = requests.get(f"{url}/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def update_json_file(self, new_url: str) -> bool:
        """
        Actualizar archivo JSON con nueva URL.
        
        Args:
            new_url: Nueva URL a configurar
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            json_file = self.repo_path / 'cloudflare_urls.json'
            
            # Cargar configuración actual
            if json_file.exists():
                with open(json_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Actualizar configuración
            old_url = config.get('current_url')
            config.update({
                'current_url': new_url,
                'backup_urls': [new_url] + [u for u in config.get('backup_urls', []) if u != new_url][:2],
                'last_updated': datetime.now().isoformat(),
                'update_source': 'local_auto_detection',
                'metadata': {
                    'detection_method': 'local_server_detection',
                    'confident': True,
                    'tested': True,
                    'previous_url': old_url,
                    'hostname': socket.gethostname(),
                    'platform': platform.system()
                }
            })
            
            # Guardar archivo
            with open(json_file, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ JSON actualizado: {old_url} → {new_url}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error actualizando JSON: {e}")
            return False
    
    def update_python_files(self, new_url: str) -> bool:
        """
        Actualizar archivos Python con nueva URL.
        
        Args:
            new_url: Nueva URL
            
        Returns:
            True si se actualizaron correctamente
        """
        try:
            # Actualizar hybrid_url_manager.py
            manager_file = self.repo_path / 'modules/utils/hybrid_url_manager.py'
            
            if manager_file.exists():
                content = manager_file.read_text(encoding='utf-8')
                
                # Reemplazar URL en la lista de URLs conocidas
                import re
                pattern = r'(self\.known_urls = \[\s*)"[^"]*\.trycloudflare\.com"'
                replacement = f'\\1"{new_url}"'
                
                new_content = re.sub(pattern, replacement, content)
                
                if new_content != content:
                    manager_file.write_text(new_content, encoding='utf-8')
                    logger.info(f"✅ Archivo Python actualizado: {manager_file.name}")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Error actualizando archivos Python: {e}")
            return False
    
    def commit_and_push_changes(self, new_url: str) -> bool:
        """
        Hacer commit y push de los cambios.
        
        Args:
            new_url: Nueva URL para el mensaje de commit
            
        Returns:
            True si el push fue exitoso
        """
        try:
            # Verificar que estamos en un repositorio git
            result = subprocess.run(['git', 'status'], 
                                  cwd=self.repo_path, 
                                  capture_output=True, 
                                  text=True)
            
            if result.returncode != 0:
                logger.error("❌ No es un repositorio git válido")
                return False
            
            # Agregar archivos modificados
            subprocess.run(['git', 'add'] + self.files_to_update, 
                          cwd=self.repo_path, check=True)
            
            # Crear mensaje de commit
            commit_msg = f"🔄 Auto-update Cloudflare URL to {new_url}\n\n- Detected by local server\n- Updated at {datetime.now().isoformat()}\n- Host: {socket.gethostname()}"
            
            # Hacer commit
            subprocess.run(['git', 'commit', '-m', commit_msg], 
                          cwd=self.repo_path, check=True)
            
            # Push a GitHub
            subprocess.run(['git', 'push'], 
                          cwd=self.repo_path, check=True)
            
            logger.info(f"✅ Cambios enviados a GitHub: {new_url}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error en git: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            return False
    
    def check_for_url_change(self) -> bool:
        """
        Verificar si la URL ha cambiado y actualizar si es necesario.
        
        Returns:
            True si se detectó y procesó un cambio
        """
        self.cache['check_count'] = self.cache.get('check_count', 0) + 1
        
        logger.info(f"🔍 Verificación #{self.cache['check_count']} - Detectando cambios de URL...")
        
        # Detectar URL actual
        current_url = self.detect_current_cloudflare_url()
        
        if not current_url:
            logger.warning("⚠️ No se pudo detectar URL actual")
            self.cache['failed_attempts'] = self.cache.get('failed_attempts', 0) + 1
            self._save_cache()
            return False
        
        # Comparar con URL conocida
        last_known_url = self.cache.get('last_known_url')
        
        if current_url == last_known_url:
            logger.info(f"ℹ️ URL sin cambios: {current_url}")
            self._save_cache()
            return False
        
        # ¡Cambio detectado!
        logger.info(f"🚨 CAMBIO DE URL DETECTADO!")
        logger.info(f"   Anterior: {last_known_url}")
        logger.info(f"   Actual:   {current_url}")
        
        # Validar nueva URL
        if not self.validate_url(current_url):
            logger.error(f"❌ Nueva URL no responde correctamente: {current_url}")
            return False
        
        # Actualizar archivos
        success = True
        success &= self.update_json_file(current_url)
        success &= self.update_python_files(current_url)
        
        if success:
            # Commit y push
            if self.commit_and_push_changes(current_url):
                logger.info(f"🎉 URL actualizada exitosamente: {current_url}")
                self.cache['last_known_url'] = current_url
                self.cache['successful_updates'] = self.cache.get('successful_updates', 0) + 1
                self._save_cache()
                return True
            else:
                logger.error("❌ Error enviando cambios a GitHub")
        
        return False
    
    def monitor_mode(self, interval: int = 300):
        """
        Ejecutar en modo monitor continuo.
        
        Args:
            interval: Intervalo en segundos entre verificaciones
        """
        logger.info(f"👁️ Iniciando monitor continuo (cada {interval}s)...")
        logger.info(f"💾 Cache: {self.cache}")
        
        try:
            while True:
                try:
                    self.check_for_url_change()
                except Exception as e:
                    logger.error(f"Error en verificación: {e}")
                
                logger.debug(f"😴 Esperando {interval}s hasta próxima verificación...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Monitor detenido por usuario")
        except Exception as e:
            logger.error(f"Error crítico en monitor: {e}")
    
    def print_status(self):
        """Imprimir estado actual del detector."""
        print("\n🚀 LOCAL URL DETECTOR - ESTADO")
        print("=" * 40)
        print(f"📁 Repositorio: {self.repo_path}")
        print(f"🔑 GitHub Token: {'✅ Configurado' if self.github_token else '❌ No configurado'}")
        print(f"💻 Sistema: {platform.system()} {platform.release()}")
        print(f"🌐 Hostname: {socket.gethostname()}")
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   Verificaciones: {self.cache.get('check_count', 0)}")
        print(f"   Actualizaciones exitosas: {self.cache.get('successful_updates', 0)}")
        print(f"   Intentos fallidos: {self.cache.get('failed_attempts', 0)}")
        print(f"   Última URL conocida: {self.cache.get('last_known_url', 'Ninguna')}")
        print(f"   Última verificación: {self.cache.get('last_check', 'Nunca')}")
        
        # Probar detección actual
        print(f"\n🔍 PRUEBA DE DETECCIÓN ACTUAL:")
        current_url = self.detect_current_cloudflare_url()
        if current_url:
            print(f"   ✅ URL detectada: {current_url}")
            is_valid = self.validate_url(current_url)
            print(f"   {'✅' if is_valid else '❌'} Validación: {'OK' if is_valid else 'FALLA'}")
        else:
            print(f"   ❌ No se pudo detectar URL")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Detector local de cambios de URL de Cloudflare")
    
    parser.add_argument('--monitor', action='store_true', help='Ejecutar en modo monitor continuo')
    parser.add_argument('--check', action='store_true', help='Verificar una sola vez')
    parser.add_argument('--status', action='store_true', help='Mostrar estado actual')
    parser.add_argument('--interval', type=int, default=300, help='Intervalo en segundos (default: 300)')
    parser.add_argument('--repo-path', type=str, default='.', help='Ruta al repositorio')
    
    args = parser.parse_args()
    
    # Crear detector
    detector = LocalURLDetector(repo_path=args.repo_path)
    
    if args.status:
        detector.print_status()
    elif args.check:
        result = detector.check_for_url_change()
        print(f"✅ Cambio detectado y procesado" if result else "ℹ️ Sin cambios")
    elif args.monitor:
        detector.monitor_mode(args.interval)
    else:
        # Modo interactivo
        detector.print_status()
        
        choice = input("\n¿Qué deseas hacer?\n1. Verificar una vez\n2. Monitor continuo\n3. Solo mostrar estado\nElige (1-3): ")
        
        if choice == '1':
            result = detector.check_for_url_change()
            print(f"✅ Cambio detectado y procesado" if result else "ℹ️ Sin cambios")
        elif choice == '2':
            detector.monitor_mode(args.interval)
        else:
            print("👋 ¡Hasta luego!")


if __name__ == "__main__":
    main()