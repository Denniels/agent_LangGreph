import requests

base_url = 'https://respect-craps-lit-aged.trycloudflare.com'
device_id = 'esp32_wifi_001'

print('🔍 Probando diferentes límites para encontrar el máximo:')

for limit in [10, 15, 20, 25, 30, 35, 40, 45, 50, 100]:
    try:
        response = requests.get(f'{base_url}/data/{device_id}', params={'limit': limit})
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                print(f'✅ limit={limit}: {len(data["data"])} registros')
            else:
                print(f'❌ limit={limit}: {data.get("message", "Sin datos")}')
                break  # Si falla aquí, límites mayores también fallarán
        else:
            print(f'❌ limit={limit}: Status {response.status_code}')
            break
    except Exception as e:
        print(f'❌ limit={limit}: Error {str(e)[:30]}...')
        break

print('\n🔍 Probando también arduino_eth_001:')
device_id = 'arduino_eth_001'

for limit in [10, 15, 20, 25, 30]:
    try:
        response = requests.get(f'{base_url}/data/{device_id}', params={'limit': limit})
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                print(f'✅ limit={limit}: {len(data["data"])} registros')
            else:
                print(f'❌ limit={limit}: {data.get("message", "Sin datos")}')
                break
        else:
            print(f'❌ limit={limit}: Status {response.status_code}')
            break
    except Exception as e:
        print(f'❌ limit={limit}: Error {str(e)[:30]}...')
        break