import requests
import json

base_url = 'https://replica-subscriber-permission-restricted.trycloudflare.com'

print('🔍 EXPLORANDO ENDPOINTS PROMETEDORES')
print('=' * 50)

# 1. Explorar /data/bulk
print('\n📦 1. ENDPOINT /data/bulk:')
try:
    response = requests.get(f'{base_url}/data/bulk', timeout=10)
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f'Tipo de respuesta: {type(data)}')
            print(f'Contenido (preview): {json.dumps(data, indent=2)[:500]}...')
            
            # Si tiene datos, contar registros
            if isinstance(data, dict) and 'data' in data:
                print(f'📊 Registros en bulk: {len(data["data"])}')
            elif isinstance(data, list):
                print(f'📊 Registros en bulk: {len(data)}')
                
        except json.JSONDecodeError:
            print(f'Respuesta texto: {response.text[:300]}...')
    else:
        print(f'Error: {response.text[:200]}')
        
except Exception as e:
    print(f'Error: {e}')

# 2. Explorar /data/export
print('\n📤 2. ENDPOINT /data/export:')
try:
    response = requests.get(f'{base_url}/data/export', timeout=10)
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f'Tipo de respuesta: {type(data)}')
            print(f'Contenido (preview): {json.dumps(data, indent=2)[:500]}...')
            
            # Si tiene datos, contar registros
            if isinstance(data, dict) and 'data' in data:
                print(f'📊 Registros en export: {len(data["data"])}')
            elif isinstance(data, list):
                print(f'📊 Registros en export: {len(data)}')
                
        except json.JSONDecodeError:
            print(f'Respuesta texto: {response.text[:300]}...')
    else:
        print(f'Error: {response.text[:200]}')
        
except Exception as e:
    print(f'Error: {e}')

# 3. Probar diferentes parámetros con estos endpoints
print('\n🧪 3. PROBANDO PARÁMETROS CON ENDPOINTS BULK/EXPORT:')

bulk_params = [
    {'devices': 'esp32_wifi_001,arduino_eth_001'},
    {'device_ids': 'esp32_wifi_001,arduino_eth_001'},
    {'all': True},
    {'limit': 100},
    {'hours': 24},
    {'days': 1}
]

for endpoint in ['/data/bulk', '/data/export']:
    print(f'\n📋 Probando {endpoint}:')
    for params in bulk_params:
        try:
            response = requests.get(f'{base_url}{endpoint}', params=params, timeout=15)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and data.get('data'):
                        print(f'  ✅ {params}: {len(data["data"])} registros')
                    elif isinstance(data, list):
                        print(f'  ✅ {params}: {len(data)} registros')
                    else:
                        print(f'  ⚠️ {params}: Respuesta sin datos claros')
                except:
                    print(f'  📄 {params}: Respuesta no-JSON')
            else:
                print(f'  ❌ {params}: HTTP {response.status_code}')
        except Exception as e:
            print(f'  ❌ {params}: {str(e)[:40]}...')

# 4. Explorar endpoint /data general
print('\n📊 4. ENDPOINT /data GENERAL:')
general_params = [
    {},  # Sin parámetros
    {'limit': 100},
    {'hours': 1},
    {'all_devices': True},
    {'recent': True}
]

for params in general_params:
    try:
        response = requests.get(f'{base_url}/data', params=params, timeout=15)
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict) and data.get('data'):
                    print(f'  ✅ {params}: {len(data["data"])} registros')
                elif isinstance(data, list):
                    print(f'  ✅ {params}: {len(data)} registros')
                else:
                    print(f'  ⚠️ {params}: {data.get("message", "Sin datos")}')
            except:
                print(f'  📄 {params}: Respuesta no-JSON')
        else:
            print(f'  ❌ {params}: HTTP {response.status_code}')
    except Exception as e:
        print(f'  ❌ {params}: {str(e)[:40]}...')

print('\n💡 ESTRATEGIAS ALTERNATIVAS A INVESTIGAR:')
print('1. Paginación: Múltiples requests con limit=10 y offset')
print('2. Endpoints bulk/export con parámetros específicos')
print('3. Rangos de tiempo más pequeños pero múltiples')
print('4. Verificar si hay rate limiting que se puede sortear')