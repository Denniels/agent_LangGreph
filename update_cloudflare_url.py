#!/usr/bin/env python3
"""
Cloudflare URL Auto-Updater - Solución Final
==========================================

Script que actualiza automáticamente las URLs en el repositorio
cuando se proporciona una nueva URL de Cloudflare.

Diseñado para ser ejecutado desde GitHub Actions o manualmente.
"""

import json
import re
import os
import sys
import requests
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

class CloudflareURLUpdater:
    """Actualizador automático de URLs de Cloudflare."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.files_to_update = [
            'cloudflare_urls.json',
            'modules/utils/hybrid_url_manager.py',
            '.github/workflows/cloudflare-url-update.yml'
        ]
    
    def validate_cloudflare_url(self, url: str) -> bool:
        """Validar que una URL de Cloudflare funcione."""
        try:
            if not url.startswith('https://') or '.trycloudflare.com' not in url:
                return False
            
            response = requests.get(f"{url}/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def detect_known_working_urls(self) -> List[str]:
        """Detectar URLs que funcionan de las conocidas."""
        known_urls = [
            "https://along-critical-decorative-physics.trycloudflare.com",
            "https://roof-imposed-noticed-fire.trycloudflare.com", 
            "https://returned-convenience-tower-switched.trycloudflare.com",
            "https://reflect-wed-governmental-fisher.trycloudflare.com"
        ]
        
        working_urls = []
        for url in known_urls:
            if self.validate_cloudflare_url(url):
                working_urls.append(url)
                print(f"✅ URL funcionando: {url}")
            else:
                print(f"❌ URL no funciona: {url}")
        
        return working_urls
    
    def update_json_config(self, new_url: str) -> bool:
        """Actualizar cloudflare_urls.json."""
        try:
            json_file = self.repo_path / 'cloudflare_urls.json'
            
            # Cargar configuración actual
            if json_file.exists():
                with open(json_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Actualizar con nueva URL
            old_url = config.get('current_url')
            config.update({
                'current_url': new_url,
                'backup_urls': [new_url] + [u for u in config.get('backup_urls', []) if u != new_url][:3],
                'last_updated': datetime.now().isoformat(),
                'update_source': 'auto_updater_script',
                'metadata': {
                    'detection_method': 'manual_or_script_update',
                    'confident': True,
                    'tested': True,
                    'previous_url': old_url
                }
            })
            
            # Guardar
            with open(json_file, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ JSON actualizado: {old_url} → {new_url}")
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando JSON: {e}")
            return False
    
    def update_hybrid_manager(self, new_url: str) -> bool:
        """Actualizar modules/utils/hybrid_url_manager.py."""
        try:
            manager_file = self.repo_path / 'modules/utils/hybrid_url_manager.py'
            
            if not manager_file.exists():
                print(f"⚠️ Archivo no encontrado: {manager_file}")
                return False
            
            content = manager_file.read_text(encoding='utf-8')
            
            # Buscar la sección de known_urls y actualizar
            pattern = r'(self\.known_urls = \[\s*)"[^"]*\.trycloudflare\.com"'
            replacement = f'\\1"{new_url}"'
            
            new_content = re.sub(pattern, replacement, content)
            
            if new_content != content:
                manager_file.write_text(new_content, encoding='utf-8')
                print(f"✅ hybrid_url_manager.py actualizado")
                return True
            else:
                print(f"ℹ️ hybrid_url_manager.py no necesita cambios")
                return True
                
        except Exception as e:
            print(f"❌ Error actualizando hybrid_url_manager.py: {e}")
            return False
    
    def update_github_actions(self, new_url: str) -> bool:
        """Actualizar .github/workflows/cloudflare-url-update.yml."""
        try:
            workflow_file = self.repo_path / '.github/workflows/cloudflare-url-update.yml'
            
            if not workflow_file.exists():
                print(f"⚠️ Archivo workflow no encontrado: {workflow_file}")
                return False
            
            content = workflow_file.read_text(encoding='utf-8')
            
            # Buscar la sección de candidate_urls y agregar la nueva URL al inicio
            pattern = r'(candidate_urls = \[\s*)"[^"]*\.trycloudflare\.com"'
            replacement = f'\\1"{new_url}",  # URL ACTUAL CONFIRMADA\n                "{new_url}"'
            
            # Si no funciona el patrón anterior, buscar de otra forma
            if 'candidate_urls' in content:
                lines = content.split('\n')
                new_lines = []
                in_candidate_urls = False
                
                for line in lines:
                    if 'candidate_urls = [' in line:
                        in_candidate_urls = True
                        new_lines.append(line)
                        # Agregar la nueva URL como primera en la lista
                        indent = ' ' * (len(line) - len(line.lstrip()) + 4)
                        new_lines.append(f'{indent}"{new_url}",  # URL ACTUAL CONFIRMADA')
                    elif in_candidate_urls and line.strip().startswith('"https://') and '.trycloudflare.com' in line:
                        # Verificar si ya existe esta URL
                        if new_url not in line:
                            new_lines.append(line)
                    elif in_candidate_urls and ']' in line:
                        in_candidate_urls = False
                        new_lines.append(line)
                    else:
                        new_lines.append(line)
                
                new_content = '\n'.join(new_lines)
            else:
                new_content = content
            
            if new_content != content:
                workflow_file.write_text(new_content, encoding='utf-8')
                print(f"✅ GitHub Actions workflow actualizado")
                return True
            else:
                print(f"ℹ️ GitHub Actions workflow no necesita cambios")
                return True
                
        except Exception as e:
            print(f"❌ Error actualizando workflow: {e}")
            return False
    
    def commit_and_push(self, new_url: str) -> bool:
        """Hacer commit y push de los cambios."""
        try:
            # Verificar que estamos en un repo git
            result = subprocess.run(['git', 'status'], 
                                  cwd=self.repo_path, 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print("⚠️ No es un repositorio git o hay problemas")
                return False
            
            # Agregar archivos
            subprocess.run(['git', 'add'] + self.files_to_update, 
                          cwd=self.repo_path, check=True)
            
            # Verificar si hay cambios
            result = subprocess.run(['git', 'diff', '--cached', '--quiet'], 
                                  cwd=self.repo_path, capture_output=True)
            
            if result.returncode == 0:
                print("ℹ️ No hay cambios para hacer commit")
                return True
            
            # Hacer commit
            commit_msg = f"🔄 Auto-update Cloudflare URL to {new_url}\n\nUpdated by CloudflareURLUpdater\nTimestamp: {datetime.now().isoformat()}"
            
            subprocess.run(['git', 'commit', '-m', commit_msg], 
                          cwd=self.repo_path, check=True)
            
            # Push
            subprocess.run(['git', 'push'], 
                          cwd=self.repo_path, check=True)
            
            print(f"✅ Cambios enviados a GitHub")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error en git: {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return False
    
    def update_all(self, new_url: str, commit: bool = True) -> bool:
        """Actualizar todo el sistema con la nueva URL."""
        print(f"🔄 Actualizando sistema con URL: {new_url}")
        
        # Validar URL
        if not self.validate_cloudflare_url(new_url):
            print(f"❌ URL no válida o no responde: {new_url}")
            return False
        
        # Actualizar archivos
        success = True
        success &= self.update_json_config(new_url)
        success &= self.update_hybrid_manager(new_url)
        success &= self.update_github_actions(new_url)
        
        if not success:
            print("❌ Error actualizando algunos archivos")
            return False
        
        # Commit y push si se solicita
        if commit:
            return self.commit_and_push(new_url)
        
        return True


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Actualizador automático de URLs de Cloudflare")
    parser.add_argument('--url', type=str, help='Nueva URL de Cloudflare')
    parser.add_argument('--detect', action='store_true', help='Detectar URL funcionando automáticamente')
    parser.add_argument('--no-commit', action='store_true', help='No hacer commit automático')
    parser.add_argument('--repo-path', type=str, default='.', help='Ruta al repositorio')
    
    args = parser.parse_args()
    
    updater = CloudflareURLUpdater(args.repo_path)
    
    # Determinar URL a usar
    if args.url:
        new_url = args.url
        print(f"🎯 Usando URL proporcionada: {new_url}")
    elif args.detect:
        print("🔍 Detectando URL funcionando...")
        working_urls = updater.detect_known_working_urls()
        if working_urls:
            new_url = working_urls[0]
            print(f"🎯 URL detectada: {new_url}")
        else:
            print("❌ No se encontraron URLs funcionando")
            return False
    else:
        print("❌ Debe proporcionar --url o usar --detect")
        return False
    
    # Actualizar sistema
    success = updater.update_all(new_url, commit=not args.no_commit)
    
    if success:
        print("🎉 ¡Actualización completada exitosamente!")
        return True
    else:
        print("❌ Falló la actualización")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)