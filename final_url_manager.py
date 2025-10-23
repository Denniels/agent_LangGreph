#!/usr/bin/env python3
"""
Final URL Testing and Update Tool - Herramienta Final de Prueba y Actualización
=============================================================================

Herramienta definitiva que:
1. Descubre la URL actual que funciona
2. Actualiza todos los archivos de configuración
3. Valida que el sistema completo funcione
4. Genera reporte detallado
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalURLManager:
    """
    Manager definitivo para descubrir, validar y actualizar URLs de Cloudflare.
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.json_config_file = self.project_root / "cloudflare_urls.json"
        
        # URLs candidatas conocidas (agregar nuevas aquí)
        self.candidate_urls = [
            # URLs que hemos visto en las capturas
            "https://returned-convenience-tower-switched.trycloudflare.com",
            
            # URLs anteriores
            "https://reflect-wed-governmental-fisher.trycloudflare.com",
            "https://replica-subscriber-permission-restricted.trycloudflare.com",
        ]
        
        # Endpoints a probar para validación
        self.test_endpoints = [
            "/health",
            "/devices", 
            "/data"
        ]
        
        self.results = {
            'discovery': {},
            'validation': {},
            'updates': {},
            'timestamp': datetime.now().isoformat()
        }
    
    def test_url_comprehensive(self, url: str) -> dict:
        """
        Probar una URL de forma comprensiva.
        
        Args:
            url: URL a probar
            
        Returns:
            Diccionario con resultados detallados
        """
        print(f"🧪 Probando comprehensivamente: {url}")
        
        result = {
            'url': url,
            'accessible': False,
            'endpoints': {},
            'response_times': {},
            'errors': []
        }
        
        for endpoint in self.test_endpoints:
            test_url = f"{url}{endpoint}"
            print(f"  📡 Probando {endpoint}...")
            
            try:
                start_time = time.time()
                response = requests.get(
                    test_url,
                    timeout=15,
                    headers={'User-Agent': 'FinalURLManager/1.0'}
                )
                response_time = (time.time() - start_time) * 1000
                
                result['endpoints'][endpoint] = {
                    'status_code': response.status_code,
                    'accessible': response.status_code == 200,
                    'response_time_ms': round(response_time, 2)
                }
                
                result['response_times'][endpoint] = response_time
                
                if response.status_code == 200:
                    print(f"    ✅ {endpoint}: OK ({response_time:.1f}ms)")
                    result['accessible'] = True
                else:
                    print(f"    🟡 {endpoint}: HTTP {response.status_code}")
                
                # Para /data y /devices, intentar parsear JSON
                if endpoint in ['/data', '/devices'] and response.status_code == 200:
                    try:
                        data = response.json()
                        result['endpoints'][endpoint]['data_length'] = len(data)
                        print(f"    📊 Datos: {len(data)} elementos")
                    except:
                        print(f"    ⚠️ Respuesta no es JSON válido")
                        
            except requests.exceptions.ConnectTimeout:
                print(f"    ⏰ {endpoint}: TIMEOUT")
                result['endpoints'][endpoint] = {'error': 'timeout'}
                result['errors'].append(f"{endpoint}: timeout")
                
            except requests.exceptions.ConnectionError as e:
                if 'Failed to resolve' in str(e):
                    print(f"    🚫 {endpoint}: DNS_FAIL")
                    result['endpoints'][endpoint] = {'error': 'dns_fail'}
                    result['errors'].append(f"{endpoint}: dns_fail")
                else:
                    print(f"    🔴 {endpoint}: CONNECTION_ERROR")
                    result['endpoints'][endpoint] = {'error': 'connection_error'}
                    result['errors'].append(f"{endpoint}: connection_error")
                    
            except Exception as e:
                print(f"    ❌ {endpoint}: ERROR - {str(e)[:50]}")
                result['endpoints'][endpoint] = {'error': str(e)}
                result['errors'].append(f"{endpoint}: {str(e)}")
        
        # Calcular métricas generales
        if result['response_times']:
            result['avg_response_time'] = sum(result['response_times'].values()) / len(result['response_times'])
            result['max_response_time'] = max(result['response_times'].values())
        
        working_endpoints = sum(1 for ep in result['endpoints'].values() 
                              if ep.get('accessible', False))
        result['working_endpoints'] = working_endpoints
        result['total_endpoints'] = len(self.test_endpoints)
        result['health_score'] = working_endpoints / len(self.test_endpoints)
        
        if result['accessible']:
            print(f"  ✅ URL FUNCIONAL - {working_endpoints}/{len(self.test_endpoints)} endpoints OK")
        else:
            print(f"  ❌ URL NO FUNCIONAL - 0/{len(self.test_endpoints)} endpoints OK")
        
        return result
    
    def discover_working_url(self) -> tuple:
        """
        Descubrir qué URL funciona actualmente.
        
        Returns:
            Tupla (url_funcional, resultados_detallados)
        """
        print("🔍 INICIANDO DESCUBRIMIENTO DE URL FUNCIONAL")
        print("=" * 60)
        
        all_results = []
        working_url = None
        
        for url in self.candidate_urls:
            result = self.test_url_comprehensive(url)
            all_results.append(result)
            
            if result['accessible'] and not working_url:
                working_url = url
                print(f"\n🎯 PRIMERA URL FUNCIONAL ENCONTRADA: {url}")
        
        self.results['discovery'] = {
            'candidate_urls': self.candidate_urls,
            'all_results': all_results,
            'working_url': working_url,
            'total_tested': len(self.candidate_urls)
        }
        
        return working_url, all_results
    
    def update_configuration_files(self, working_url: str):
        """
        Actualizar todos los archivos de configuración con la nueva URL.
        
        Args:
            working_url: URL que funciona
        """
        print(f"\n📝 ACTUALIZANDO ARCHIVOS DE CONFIGURACIÓN CON: {working_url}")
        print("-" * 50)
        
        updates_made = []
        
        # 1. Actualizar cloudflare_urls.json
        try:
            if self.json_config_file.exists():
                with open(self.json_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            old_url = config.get('current_url')
            config.update({
                'current_url': working_url,
                'last_updated': datetime.now().isoformat(),
                'update_source': 'final_url_manager_discovery',
                'metadata': {
                    'detection_method': 'comprehensive_testing',
                    'confident': True,
                    'tested': True,
                    'previous_url': old_url
                }
            })
            
            # Actualizar backup_urls
            if 'backup_urls' not in config:
                config['backup_urls'] = []
            
            if working_url not in config['backup_urls']:
                config['backup_urls'].insert(0, working_url)
            
            config['backup_urls'] = config['backup_urls'][:5]  # Mantener solo 5
            
            with open(self.json_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            updates_made.append(f"✅ {self.json_config_file.name}: {old_url} → {working_url}")
            print(f"  ✅ Actualizado: {self.json_config_file.name}")
            
        except Exception as e:
            error_msg = f"❌ Error actualizando {self.json_config_file.name}: {e}"
            updates_made.append(error_msg)
            print(f"  {error_msg}")
        
        # 2. Actualizar hybrid_url_manager.py
        try:
            hybrid_file = self.project_root / "modules" / "utils" / "hybrid_url_manager.py"
            if hybrid_file.exists():
                content = hybrid_file.read_text(encoding='utf-8')
                
                # Buscar y actualizar la lista de URLs conocidas
                old_content = content
                
                # Pattern para encontrar la lista de URLs
                import re
                pattern = r'(self\.known_urls\s*=\s*\[)(.*?)(\])'
                
                def update_urls(match):
                    prefix = match.group(1)
                    suffix = match.group(3)
                    
                    # Crear nueva lista con la URL funcional primero
                    new_urls = [
                        f'            "{working_url}",  # URL actual detectada',
                        '            "https://reflect-wed-governmental-fisher.trycloudflare.com",  # URL anterior',
                        '            "https://replica-subscriber-permission-restricted.trycloudflare.com",  # URL más antigua'
                    ]
                    
                    return prefix + '\n' + '\n'.join(new_urls) + '\n        ' + suffix
                
                new_content = re.sub(pattern, update_urls, content, flags=re.DOTALL)
                
                if new_content != old_content:
                    hybrid_file.write_text(new_content, encoding='utf-8')
                    updates_made.append(f"✅ hybrid_url_manager.py: URL actualizada")
                    print(f"  ✅ Actualizado: hybrid_url_manager.py")
                else:
                    updates_made.append(f"ℹ️ hybrid_url_manager.py: No necesitaba cambios")
                    print(f"  ℹ️ No necesitaba cambios: hybrid_url_manager.py")
            
        except Exception as e:
            error_msg = f"❌ Error actualizando hybrid_url_manager.py: {e}"
            updates_made.append(error_msg)
            print(f"  {error_msg}")
        
        self.results['updates'] = {
            'working_url': working_url,
            'updates_made': updates_made,
            'files_updated': len([u for u in updates_made if u.startswith('✅')])
        }
    
    def validate_complete_system(self, working_url: str):
        """
        Validar que todo el sistema funcione con la nueva URL.
        
        Args:
            working_url: URL a validar
        """
        print(f"\n🔬 VALIDANDO SISTEMA COMPLETO CON: {working_url}")
        print("-" * 50)
        
        validations = {}
        
        # 1. Probar ultra_robust_cloudflare_manager
        try:
            print("  📦 Probando UltraRobustCloudflareURLManager...")
            from modules.utils.ultra_robust_cloudflare_manager import get_jetson_url_ultra_robust
            
            url = get_jetson_url_ultra_robust()
            validations['ultra_robust_manager'] = {
                'success': True,
                'url_returned': url,
                'matches_working_url': url == working_url
            }
            
            if url == working_url:
                print(f"    ✅ Retorna URL correcta: {url}")
            else:
                print(f"    ⚠️ URL diferente: {url} vs {working_url}")
                
        except Exception as e:
            validations['ultra_robust_manager'] = {
                'success': False,
                'error': str(e)
            }
            print(f"    ❌ Error: {e}")
        
        # 2. Probar hybrid_url_manager
        try:
            print("  📦 Probando HybridURLManager...")
            from modules.utils.hybrid_url_manager import get_jetson_url_hybrid
            
            url = get_jetson_url_hybrid()
            validations['hybrid_manager'] = {
                'success': True,
                'url_returned': url,
                'matches_working_url': url == working_url
            }
            
            if url == working_url:
                print(f"    ✅ Retorna URL correcta: {url}")
            else:
                print(f"    ⚠️ URL diferente: {url} vs {working_url}")
                
        except Exception as e:
            validations['hybrid_manager'] = {
                'success': False,
                'error': str(e)
            }
            print(f"    ❌ Error: {e}")
        
        # 3. Probar conectividad final
        try:
            print("  🌐 Probando conectividad final...")
            response = requests.get(f"{working_url}/health", timeout=10)
            
            validations['final_connectivity'] = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds()
            }
            
            if response.status_code == 200:
                print(f"    ✅ Conectividad OK ({response.elapsed.total_seconds():.2f}s)")
            else:
                print(f"    ❌ HTTP {response.status_code}")
                
        except Exception as e:
            validations['final_connectivity'] = {
                'success': False,
                'error': str(e)
            }
            print(f"    ❌ Error de conectividad: {e}")
        
        self.results['validation'] = validations
        
        # Calcular puntuación general
        successful_validations = sum(1 for v in validations.values() if v.get('success', False))
        total_validations = len(validations)
        success_rate = successful_validations / total_validations if total_validations > 0 else 0
        
        print(f"\n📊 PUNTUACIÓN DE VALIDACIÓN: {successful_validations}/{total_validations} ({success_rate:.1%})")
        
        return success_rate >= 0.7  # 70% de éxito mínimo
    
    def generate_final_report(self):
        """Generar reporte final detallado."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.project_root / f"final_url_update_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 REPORTE DETALLADO GUARDADO: {report_file.name}")
        
        return report_file
    
    def run_complete_process(self):
        """Ejecutar el proceso completo de descubrimiento y actualización."""
        print("🚀 INICIANDO PROCESO COMPLETO DE ACTUALIZACIÓN DE URL")
        print("=" * 70)
        
        # 1. Descubrir URL funcional
        working_url, discovery_results = self.discover_working_url()
        
        if not working_url:
            print("\n❌ NO SE ENCONTRÓ NINGUNA URL FUNCIONAL")
            print("💡 Posibles causas:")
            print("  - El servidor Jetson no está ejecutándose")
            print("  - La URL cambió a una desconocida")
            print("  - Problemas de conectividad")
            print("  - Necesita reiniciar el túnel de Cloudflare")
            
            self.generate_final_report() 
            return False
        
        # 2. Actualizar archivos de configuración
        self.update_configuration_files(working_url)
        
        # 3. Validar sistema completo
        system_valid = self.validate_complete_system(working_url)
        
        # 4. Generar reporte
        report_file = self.generate_final_report()
        
        # 5. Resumen final
        print(f"\n🎉 PROCESO COMPLETADO")
        print("=" * 30)
        print(f"✅ URL funcional: {working_url}")
        print(f"📝 Archivos actualizados: {self.results['updates']['files_updated']}")
        print(f"🔬 Validación del sistema: {'✅ EXITOSA' if system_valid else '⚠️ PARCIAL'}")
        print(f"📋 Reporte detallado: {report_file.name}")
        
        if system_valid:
            print(f"\n💯 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
            print(f"🔗 URL lista para usar: {working_url}")
        else:
            print(f"\n⚠️ Sistema parcialmente funcional. Revisar validaciones en el reporte.")
        
        return system_valid


if __name__ == "__main__":
    print("🔧 FINAL URL TESTING AND UPDATE TOOL")
    print("=" * 50)
    print("Esta herramienta va a:")
    print("1. 🔍 Descubrir qué URL de Cloudflare funciona actualmente")
    print("2. 📝 Actualizar todos los archivos de configuración")
    print("3. 🔬 Validar que todo el sistema funcione")
    print("4. 📋 Generar reporte detallado")
    print()
    
    proceed = input("¿Continuar? (y/N): ").lower().strip()
    if proceed != 'y':
        print("❌ Operación cancelada")
        exit(1)
    
    manager = FinalURLManager()
    success = manager.run_complete_process()
    
    exit(0 if success else 1)