#!/usr/bin/env python3
"""Test import del jetson_api_manager"""

try:
    from modules.utils.jetson_api_manager import get_jetson_manager
    print("✅ Import del jetson_api_manager exitoso")
    
    # Probar crear instancia
    manager = get_jetson_manager()
    print(f"✅ Manager creado: {type(manager)}")
    print(f"📋 URLs candidatas: {manager.candidate_urls}")
    
except Exception as e:
    print(f"❌ Error en import: {e}")
    import traceback
    traceback.print_exc()