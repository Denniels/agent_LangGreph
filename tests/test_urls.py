#!/usr/bin/env python3
"""Test rápido de conectividad Jetson"""

import requests

urls = [
    "https://wonder-sufficiently-generator-click.trycloudflare.com"
]

for url in urls:
    try:
        print(f"🔍 Probando: {url}")
        response = requests.get(f"{url}/health", timeout=5)
        print(f"✅ {url} - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   📋 Datos: {response.json()}")
        break
    except Exception as e:
        print(f"❌ {url} - Error: {e}")