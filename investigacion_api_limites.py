import requests
import json
import time

base_url = 'https://respect-craps-lit-aged.trycloudflare.com'

print('🔍 INVESTIGACIÓN PROFUNDA DE LÍMITES DE API')
print('=' * 60)

# 1. Verificar documentación completa de la API
print('\n📄 1. DOCUMENTACIÓN DE API:')
try:
    response = requests.get(f'{base_url}/openapi.json')
    if response.status_code == 200:
        api_docs = response.json()
        
        # Buscar endpoints relacionados con datos
        data_endpoints = {}
        for path, methods in api_docs.get('paths', {}).items():
            if 'data' in path.lower():
                data_endpoints[path] = methods
        
        print(f'Endpoints de datos encontrados:')
        for endpoint, methods in data_endpoints.items():
            print(f'  {endpoint}: {list(methods.keys())}')
            
            # Ver parámetros disponibles
            for method, details in methods.items():
                params = details.get('parameters', [])
                if params:
                    print(f'    {method.upper()} parámetros:')
                    for param in params:
                        print(f'      - {param.get("name")}: {param.get("description", "Sin descripción")}')

except Exception as e:
    print(f'Error obteniendo documentación: {e}')

# 2. Probar diferentes estrategias con el límite
print(f'\n🧪 2. ANÁLISIS DETALLADO DEL LÍMITE:')
device_id = 'esp32_wifi_001'

# Estrategia A: Incremento gradual para encontrar límite exacto
print(f'\n🔍 A. Búsqueda binaria del límite máximo:')
working_limit = 10
max_tested = 50

for limit in [11, 12, 13, 14, 15, 20]:
    try:
        response = requests.get(f'{base_url}/data/{device_id}', 
                              params={'limit': limit}, 
                              timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                working_limit = limit
                print(f'  ✅ limit={limit}: {len(data["data"])} registros - FUNCIONA')
            else:
                print(f'  ❌ limit={limit}: {data.get("message", "Sin datos")} - FALLA')
                break
        else:
            print(f'  ❌ limit={limit}: HTTP {response.status_code} - FALLA')
            break
    except Exception as e:
        print(f'  ❌ limit={limit}: Error {str(e)[:40]}... - FALLA')
        break

print(f'\n📊 Límite máximo funcional encontrado: {working_limit}')

# 3. Probar parámetros alternativos
print(f'\n🔍 B. PARÁMETROS ALTERNATIVOS:')
alternative_params = [
    {'hours': 1},
    {'hours': 0.5}, 
    {'since': '2025-10-10'},
    {'from': '2025-10-10T00:00:00'},
    {'recent': True},
    {'all': True},
    {'page': 1, 'size': 50},
    {'page': 1, 'per_page': 50},
    {'offset': 0, 'limit': 50}
]

for params in alternative_params:
    try:
        response = requests.get(f'{base_url}/data/{device_id}', 
                              params=params, 
                              timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                print(f'  ✅ {params}: {len(data["data"])} registros')
            else:
                print(f'  ⚠️ {params}: {data.get("message", "Sin datos")}')
        else:
            print(f'  ❌ {params}: HTTP {response.status_code}')
    except Exception as e:
        print(f'  ❌ {params}: {str(e)[:40]}...')

# 4. Probar endpoints alternativos para datos históricos
print(f'\n🔍 C. ENDPOINTS ALTERNATIVOS:')
historical_endpoints = [
    f'/data/{device_id}/history',
    f'/data/{device_id}/range', 
    f'/historical/{device_id}',
    f'/sensors/{device_id}',
    f'/timeseries/{device_id}',
    f'/analytics/{device_id}',
    '/data/bulk',
    '/data/export'
]

for endpoint in historical_endpoints:
    try:
        response = requests.get(f'{base_url}{endpoint}', 
                              params={'limit': 100}, 
                              timeout=10)
        print(f'  {endpoint}: HTTP {response.status_code}')
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict) and data.get('data'):
                    print(f'    ✅ Datos disponibles: {len(data["data"])} registros')
            except:
                print(f'    📄 Respuesta texto (no JSON)')
    except Exception as e:
        print(f'  {endpoint}: {str(e)[:30]}...')

print(f'\n📝 RESUMEN DE HALLAZGOS:')
print(f'- Límite máximo funcional: {working_limit} registros')
print(f'- Para análisis de 24h necesitamos: ~1440 registros (1 por minuto)')
print(f'- Para análisis semanal necesitamos: ~10080 registros')
print(f'- Déficit actual: {1440 - working_limit} registros para 24h')