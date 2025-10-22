#!/usr/bin/env python3
"""
URL Update Automation Script
============================

Script automatizado para detectar cambios en la URL de Cloudflare y actualizar
automáticamente todos los archivos que contengan URLs hardcodeadas.

Este script puede:
1. Detectar automáticamente cuando cambia la URL de Cloudflare
2. Actualizar todos los archivos con la nueva URL
3. Crear commits y push automáticos (opcional)
4. Notificar sobre cambios detectados
5. Funcionar como servicio de monitoreo

Uso:
    python url_update_automation.py --monitor    # Monitoreo continuo
    python url_update_automation.py --update     # Actualización única
    python url_update_automation.py --scan       # Escanear archivos solamente

Autor: IoT Agent System
Fecha: 22 de octubre de 2025
"""

import os
import re
import json
import argparse
import time
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Set
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | URLAutomation | %(message)s'
)
logger = logging.getLogger(__name__)

class URLUpdateAutomation:
    """
    Automatización para actualizar URLs de Cloudflare en todo el proyecto.
    """
    
    def __init__(self, project_root: str = None):
        """
        Inicializar automatización.
        
        Args:
            project_root: Directorio raíz del proyecto
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.config_file = self.project_root / "url_automation_config.json"
        
        # Patrones de archivos a incluir/excluir
        self.include_patterns = [
            "*.py", "*.md", "*.json", "*.toml", "*.yaml", "*.yml"
        ]
        
        self.exclude_patterns = [
            "__pycache__", ".git", ".venv", "venv", "env",
            "node_modules", ".pytest_cache", "*.pyc"
        ]
        
        # Patrones de URLs de Cloudflare a buscar
        self.cloudflare_patterns = [
            r'https://[\w\-]+\.trycloudflare\.com',
            r'"https://[\w\-]+\.trycloudflare\.com"',
            r"'https://[\w\-]+\.trycloudflare\.com'",
        ]
        
        # URLs conocidas para reemplazar
        self.known_old_urls = [
            "https://replica-subscriber-permission-restricted.trycloudflare.com",
            "https://replica-subscriber-permission-restricted.trycloudflare.com",
        ]
        
        # Configuración
        self.config = self.load_config()
        
        # Estadísticas
        self.stats = {
            'files_scanned': 0,
            'files_with_urls': 0,
            'urls_found': 0,
            'files_updated': 0,
            'urls_replaced': 0
        }
    
    def load_config(self) -> Dict:
        """Cargar configuración desde archivo."""
        default_config = {
            'last_known_url': None,
            'auto_commit': False,
            'auto_push': False,
            'monitor_interval': 300,  # 5 minutos
            'backup_enabled': True,
            'notification_enabled': True,
            'excluded_files': [],
            'update_history': []
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge con default
                    default_config.update(config)
        except Exception as e:
            logger.warning(f"Error cargando configuración: {e}")
        
        return default_config
    
    def save_config(self):
        """Guardar configuración a archivo."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    def get_current_cloudflare_url(self) -> str:
        """
        Obtener la URL actual de Cloudflare usando el manager.
        
        Returns:
            URL actual de Cloudflare
        """
        try:
            # Intentar usar el manager de URLs
            import sys
            sys.path.append(str(self.project_root))
            
            from modules.utils.cloudflare_url_manager import get_jetson_url
            return get_jetson_url()
            
        except Exception as e:
            logger.warning(f"No se pudo obtener URL del manager: {e}")
            # Fallback a URL más reciente conocida
            return "https://replica-subscriber-permission-restricted.trycloudflare.com"
    
    def find_files_to_scan(self) -> List[Path]:
        """
        Encontrar todos los archivos que deben ser escaneados.
        
        Returns:
            Lista de archivos a escanear
        """
        files_to_scan = []
        
        for pattern in self.include_patterns:
            for file_path in self.project_root.rglob(pattern):
                # Verificar si debe excluirse
                should_exclude = False
                
                for exclude_pattern in self.exclude_patterns:
                    if exclude_pattern in str(file_path):
                        should_exclude = True
                        break
                
                # Excluir archivos específicos de la configuración
                if file_path.name in self.config.get('excluded_files', []):
                    should_exclude = True
                
                if not should_exclude and file_path.is_file():
                    files_to_scan.append(file_path)
        
        return sorted(set(files_to_scan))
    
    def scan_file_for_urls(self, file_path: Path) -> List[Tuple[int, str, str]]:
        """
        Escanear un archivo en busca de URLs de Cloudflare.
        
        Args:
            file_path: Archivo a escanear
            
        Returns:
            Lista de tuplas (número_línea, línea_completa, url_encontrada)
        """
        urls_found = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    for pattern in self.cloudflare_patterns:
                        matches = re.findall(pattern, line)
                        for match in matches:
                            # Limpiar comillas si las hay
                            clean_url = match.strip('"\'')
                            urls_found.append((line_num, line.strip(), clean_url))
                            
        except Exception as e:
            logger.warning(f"Error leyendo {file_path}: {e}")
        
        return urls_found
    
    def scan_all_files(self) -> Dict[str, List[Tuple[int, str, str]]]:
        """
        Escanear todos los archivos del proyecto.
        
        Returns:
            Diccionario con archivo -> lista de URLs encontradas
        """
        logger.info("🔍 Escaneando archivos en busca de URLs de Cloudflare...")
        
        files_to_scan = self.find_files_to_scan()
        results = {}
        
        for file_path in files_to_scan:
            self.stats['files_scanned'] += 1
            
            urls_found = self.scan_file_for_urls(file_path)
            
            if urls_found:
                self.stats['files_with_urls'] += 1
                self.stats['urls_found'] += len(urls_found)
                results[str(file_path)] = urls_found
                
                logger.debug(f"📄 {file_path.name}: {len(urls_found)} URLs")
        
        logger.info(f"✅ Escaneo completado: {self.stats['files_scanned']} archivos, "
                   f"{self.stats['files_with_urls']} con URLs, "
                   f"{self.stats['urls_found']} URLs encontradas")
        
        return results
    
    def update_file_urls(self, file_path: Path, old_url: str, new_url: str) -> bool:
        """
        Actualizar URLs en un archivo específico.
        
        Args:
            file_path: Archivo a actualizar
            old_url: URL antigua a reemplazar
            new_url: Nueva URL
            
        Returns:
            True si se realizaron cambios
        """
        try:
            # Crear backup si está habilitado
            if self.config.get('backup_enabled', True):
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                backup_path.write_bytes(file_path.read_bytes())
            
            # Leer contenido
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            original_content = content
            
            # Reemplazar todas las variantes de la URL
            url_variants = [
                old_url,
                f'"{old_url}"',
                f"'{old_url}'",
            ]
            
            new_url_variants = [
                new_url,
                f'"{new_url}"',
                f"'{new_url}'",
            ]
            
            replacements_made = 0
            for old_variant, new_variant in zip(url_variants, new_url_variants):
                if old_variant in content:
                    content = content.replace(old_variant, new_variant)
                    replacements_made += content.count(new_variant) - original_content.count(new_variant)
            
            # Guardar si hubo cambios
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                self.stats['files_updated'] += 1
                self.stats['urls_replaced'] += replacements_made
                logger.info(f"✏️ Actualizado {file_path.name}: {replacements_made} reemplazos")
                return True
        
        except Exception as e:
            logger.error(f"Error actualizando {file_path}: {e}")
        
        return False
    
    def update_all_urls(self, new_url: str) -> bool:
        """
        Actualizar todas las URLs en el proyecto.
        
        Args:
            new_url: Nueva URL de Cloudflare
            
        Returns:
            True si se realizaron actualizaciones
        """
        logger.info(f"🔄 Actualizando URLs a: {new_url}")
        
        # Escanear archivos actuales
        scan_results = self.scan_all_files()
        
        if not scan_results:
            logger.info("ℹ️ No se encontraron URLs para actualizar")
            return False
        
        # Obtener todas las URLs únicas encontradas
        found_urls = set()
        for file_results in scan_results.values():
            for _, _, url in file_results:
                found_urls.add(url)
        
        # Filtrar URLs que necesitan actualización
        urls_to_update = [url for url in found_urls if url != new_url]
        
        if not urls_to_update:
            logger.info("ℹ️ Todas las URLs ya están actualizadas")
            return False
        
        logger.info(f"🎯 URLs a actualizar: {urls_to_update}")
        
        # Actualizar archivos
        files_updated = []
        for file_path_str, _ in scan_results.items():
            file_path = Path(file_path_str)
            
            for old_url in urls_to_update:
                if self.update_file_urls(file_path, old_url, new_url):
                    if file_path not in files_updated:
                        files_updated.append(file_path)
        
        # Registrar actualización en historial
        self.config['update_history'].append({
            'timestamp': datetime.now().isoformat(),
            'old_urls': urls_to_update,
            'new_url': new_url,
            'files_updated': len(files_updated),
            'urls_replaced': self.stats['urls_replaced']
        })
        
        self.config['last_known_url'] = new_url
        self.save_config()
        
        logger.info(f"✅ Actualización completada: {len(files_updated)} archivos, "
                   f"{self.stats['urls_replaced']} reemplazos")
        
        return len(files_updated) > 0
    
    def commit_changes(self, message: str = None) -> bool:
        """
        Hacer commit de los cambios.
        
        Args:
            message: Mensaje de commit personalizado
            
        Returns:
            True si el commit fue exitoso
        """
        if not self.config.get('auto_commit', False):
            logger.info("ℹ️ Auto-commit deshabilitado")
            return False
        
        try:
            # Verificar si hay cambios
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if not result.stdout.strip():
                logger.info("ℹ️ No hay cambios para hacer commit")
                return False
            
            # Agregar archivos modificados
            subprocess.run(
                ['git', 'add', '.'],
                cwd=self.project_root,
                check=True
            )
            
            # Hacer commit
            if not message:
                current_url = self.get_current_cloudflare_url()
                message = f"🔄 Actualizar URL de Cloudflare a {current_url}"
            
            subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.project_root,
                check=True
            )
            
            logger.info(f"✅ Commit realizado: {message}")
            
            # Push si está habilitado
            if self.config.get('auto_push', False):
                subprocess.run(
                    ['git', 'push'],
                    cwd=self.project_root,
                    check=True
                )
                logger.info("✅ Push realizado")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error en git: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado en commit: {e}")
            return False
    
    def detect_url_change(self) -> Tuple[bool, str, str]:
        """
        Detectar si la URL de Cloudflare ha cambiado.
        
        Returns:
            Tupla (cambió, url_anterior, url_actual)
        """
        current_url = self.get_current_cloudflare_url()
        last_known_url = self.config.get('last_known_url')
        
        if last_known_url is None:
            # Primera ejecución
            self.config['last_known_url'] = current_url
            self.save_config()
            return False, None, current_url
        
        changed = last_known_url != current_url
        return changed, last_known_url, current_url
    
    def run_update_cycle(self) -> bool:
        """
        Ejecutar un ciclo completo de actualización.
        
        Returns:
            True si se realizaron cambios
        """
        logger.info("🔄 Iniciando ciclo de actualización...")
        
        # Detectar cambio de URL
        changed, old_url, current_url = self.detect_url_change()
        
        if not changed:
            logger.info(f"ℹ️ URL sin cambios: {current_url}")
            return False
        
        logger.info(f"🚨 Cambio de URL detectado: {old_url} → {current_url}")
        
        # Actualizar archivos
        if self.update_all_urls(current_url):
            # Hacer commit si está habilitado
            self.commit_changes()
            
            # Notificación
            if self.config.get('notification_enabled', True):
                self.send_notification(old_url, current_url)
            
            return True
        
        return False
    
    def send_notification(self, old_url: str, new_url: str):
        """
        Enviar notificación sobre cambio de URL.
        
        Args:
            old_url: URL anterior
            new_url: Nueva URL
        """
        message = f"🔄 URL de Cloudflare actualizada automáticamente:\n{old_url} → {new_url}"
        logger.info(f"📢 {message}")
        
        # Aquí se podría agregar integración con Slack, Discord, email, etc.
        # Por ahora solo log
    
    def monitor_mode(self):
        """Ejecutar en modo monitor continuo."""
        interval = self.config.get('monitor_interval', 300)
        logger.info(f"👁️ Iniciando monitoreo continuo (intervalo: {interval}s)")
        
        try:
            while True:
                self.run_update_cycle()
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Monitoreo detenido por usuario")
        except Exception as e:
            logger.error(f"Error en monitoreo: {e}")
    
    def print_scan_report(self):
        """Imprimir reporte del escaneo."""
        print("\n📊 REPORTE DE ESCANEO DE URLs")
        print("=" * 50)
        
        scan_results = self.scan_all_files()
        
        print(f"Archivos escaneados: {self.stats['files_scanned']}")
        print(f"Archivos con URLs: {self.stats['files_with_urls']}")
        print(f"URLs encontradas: {self.stats['urls_found']}")
        
        if scan_results:
            print(f"\n📄 ARCHIVOS CON URLs:")
            for file_path, urls in scan_results.items():
                print(f"\n  {Path(file_path).name}:")
                for line_num, line, url in urls:
                    print(f"    Línea {line_num}: {url}")
        
        # Mostrar URLs únicas
        all_urls = set()
        for urls in scan_results.values():
            for _, _, url in urls:
                all_urls.add(url)
        
        if all_urls:
            print(f"\n🌐 URLs ÚNICAS ENCONTRADAS:")
            for url in sorted(all_urls):
                print(f"  - {url}")
        
        print(f"\n🎯 URL ACTUAL: {self.get_current_cloudflare_url()}")


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Automatización para actualizar URLs de Cloudflare"
    )
    
    parser.add_argument(
        '--scan', 
        action='store_true',
        help='Escanear archivos sin hacer cambios'
    )
    
    parser.add_argument(
        '--update', 
        action='store_true',
        help='Realizar actualización única'
    )
    
    parser.add_argument(
        '--monitor', 
        action='store_true',
        help='Ejecutar en modo monitor continuo'
    )
    
    parser.add_argument(
        '--new-url',
        type=str,
        help='Especificar nueva URL manualmente'
    )
    
    parser.add_argument(
        '--project-root',
        type=str,
        help='Directorio raíz del proyecto'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Forzar actualización ignorando cache y estado actual'
    )
    
    args = parser.parse_args()
    
    # Crear instancia del automatizador
    automation = URLUpdateAutomation(args.project_root)
    
    if args.scan:
        automation.print_scan_report()
        
    elif args.update:
        if args.new_url:
            automation.update_all_urls(args.new_url)
        else:
            # Si force está habilitado, forzar actualización
            if args.force:
                current_url = automation.get_current_cloudflare_url()
                logger.info(f"🔄 Forzando actualización con URL: {current_url}")
                automation.update_all_urls(current_url)
            else:
                automation.run_update_cycle()
            
    elif args.monitor:
        automation.monitor_mode()
        
    else:
        # Modo por defecto: escaneo + actualización si es necesaria
        print("🚀 AUTOMATIZACIÓN DE URLs DE CLOUDFLARE")
        print("=" * 40)
        
        automation.print_scan_report()
        
        if input("\n¿Realizar actualización si es necesaria? (y/N): ").lower() == 'y':
            automation.run_update_cycle()


if __name__ == "__main__":
    main()