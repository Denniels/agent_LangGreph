#!/usr/bin/env python3
"""Test simple del conector robusto"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.tools.jetson_api_connector import JetsonAPIConnector

print("🚀 PROBANDO CONECTOR ROBUSTO...")

try:
    # Crear conector
    connector = JetsonAPIConnector()
    print(f"✅ Conector creado")
    print(f"🔗 URL base: {connector.base_url}")
    print(f"⚙️ Modo robusto: {'SÍ' if hasattr(connector, 'manager') and connector.manager else 'NO'}")
    
    # Test de conectividad
    if hasattr(connector, 'manager') and connector.manager:
        print("\n🔍 PROBANDO CONECTIVIDAD ROBUSTA...")
        connectivity = connector.test_robust_connectivity()
        print(f"📡 Estado: {connectivity['connectivity']}")
        
    # Test simple de datos
    print("\n📊 PROBANDO DATOS...")
    try:
        devices = connector.get_devices()
        print(f"📱 Dispositivos encontrados: {len(devices)}")
        for device in devices:
            print(f"   - {device.get('device_id', 'unknown')}: {device.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ Error obteniendo dispositivos: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()