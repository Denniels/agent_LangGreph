#!/usr/bin/env python3
"""
Script de Actualización Forzada de URLs
=======================================

Script para forzar la actualización de todas las URLs hardcodeadas
de Cloudflare en el proyecto, independientemente del cache.

Este script reemplazará todas las instancias de URLs viejas con la nueva URL.
"""

import re
import json
from pathlib import Path
from typing import List, Dict

def force_update_all_urls():
    """Forzar actualización de todas las URLs en el proyecto."""
    
    # URLs a reemplazar (viejas)
    old_urls = [
        "https://replica-subscriber-permission-restricted.trycloudflare.com",
        "https://replica-subscriber-permission-restricted.trycloudflare.com",
        "https://replica-subscriber-permission-restricted.trycloudflare.com",
        "https://replica-subscriber-permission-restricted.trycloudflare.com",
    ]
    
    # Nueva URL
    new_url = "https://replica-subscriber-permission-restricted.trycloudflare.com"
    
    # Patrones de archivos a incluir
    include_patterns = ["*.py", "*.md", "*.json", "*.toml"]
    exclude_patterns = [
        "__pycache__", ".git", ".venv", "venv", "env",
        "node_modules", ".pytest_cache", "*.pyc",
        "cloudflare_url_config.json",  # No tocar archivo de configuración del manager
        "url_automation_config.json"   # No tocar archivo de configuración del automation
    ]
    
    project_root = Path.cwd()
    files_updated = 0
    total_replacements = 0
    
    print(f"🔄 ACTUALIZANDO URLs EN PROYECTO")
    print(f"📁 Directorio: {project_root}")
    print(f"🎯 Nueva URL: {new_url}")
    print(f"📝 URLs a reemplazar: {len(old_urls)}")
    print("=" * 60)
    
    # Encontrar archivos
    files_to_process = []
    for pattern in include_patterns:
        for file_path in project_root.rglob(pattern):
            # Verificar si debe excluirse
            should_exclude = False
            for exclude_pattern in exclude_patterns:
                if exclude_pattern in str(file_path):
                    should_exclude = True
                    break
            
            if not should_exclude and file_path.is_file():
                files_to_process.append(file_path)
    
    print(f"📊 Archivos a procesar: {len(files_to_process)}")
    
    # Procesar cada archivo
    for file_path in files_to_process:
        try:
            # Leer contenido
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            original_content = content
            
            # Reemplazar URLs
            file_replacements = 0
            for old_url in old_urls:
                if old_url in content:
                    # Reemplazar URL sin comillas
                    content = content.replace(old_url, new_url)
                    # Reemplazar URL con comillas dobles
                    content = content.replace(f'"{old_url}"', f'"{new_url}"')
                    # Reemplazar URL con comillas simples
                    content = content.replace(f"'{old_url}'", f"'{new_url}'")
                    
                    # Contar reemplazos
                    file_replacements += original_content.count(old_url)
            
            # Guardar si hubo cambios
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                files_updated += 1
                total_replacements += file_replacements
                print(f"✏️ {file_path.name}: {file_replacements} reemplazos")
        
        except Exception as e:
            print(f"❌ Error procesando {file_path.name}: {e}")
    
    print("=" * 60)
    print(f"✅ ACTUALIZACIÓN COMPLETADA")
    print(f"📁 Archivos actualizados: {files_updated}")
    print(f"🔄 Total de reemplazos: {total_replacements}")
    
    return files_updated > 0

if __name__ == "__main__":
    force_update_all_urls()