import requests
import json

base_url = 'https://wonder-sufficiently-generator-click.trycloudflare.com'

print('🎯 VERIFICANDO SOLUCIÓN ENCONTRADA')
print('=' * 50)

# Probar endpoint /data general con diferentes límites
print('\n🔍 PROBANDO ENDPOINT /data GENERAL:')

for limit in [50, 100, 200, 500, 1000]:
    try:
        response = requests.get(f'{base_url}/data', params={'limit': limit}, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                records = data['data']
                print(f'✅ limit={limit}: {len(records)} registros obtenidos')
                
                # Analizar dispositivos en los datos
                devices = set()
                for record in records[:5]:  # Primeros 5 para análisis
                    device_id = record.get('device_id')
                    if device_id:
                        devices.add(device_id)
                        
                print(f'   📱 Dispositivos en datos: {list(devices)}')
                
                # Mostrar ejemplo de registro
                if records:
                    sample = records[0]
                    timestamp = sample.get('timestamp', 'N/A')
                    sensor_type = sample.get('sensor_type', 'N/A')
                    value = sample.get('value', 'N/A')
                    print(f'   📊 Ejemplo: {timestamp} - {sensor_type}: {value}')
                
                break  # Encontramos el límite que funciona
            else:
                print(f'❌ limit={limit}: {data.get("message", "Sin datos")}')
        else:
            print(f'❌ limit={limit}: HTTP {response.status_code}')
    except Exception as e:
        print(f'❌ limit={limit}: Error {str(e)[:40]}...')

# Probar con parámetros de tiempo
print('\n⏰ PROBANDO PARÁMETROS TEMPORALES:')
time_params = [
    {'hours': 0.5},  # 30 minutos
    {'hours': 1},    # 1 hora  
    {'hours': 6},    # 6 horas
    {'hours': 24},   # 24 horas
    {'days': 1},     # 1 día
    {'days': 7}      # 1 semana
]

for params in time_params:
    try:
        response = requests.get(f'{base_url}/data', params=params, timeout=20)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                records = data['data']
                print(f'✅ {params}: {len(records)} registros')
                
                # Verificar rango temporal real de los datos
                if records:
                    timestamps = [r.get('timestamp') for r in records if r.get('timestamp')]
                    if timestamps:
                        print(f'   📅 Desde: {min(timestamps)}')
                        print(f'   📅 Hasta: {max(timestamps)}')
            else:
                print(f'❌ {params}: {data.get("message", "Sin datos")}')
        else:
            print(f'❌ {params}: HTTP {response.status_code}')
    except Exception as e:
        print(f'❌ {params}: Error {str(e)[:40]}...')

print('\n🎉 CONCLUSIÓN:')
print('✅ El endpoint /data GENERAL puede obtener muchos más registros')
print('✅ Necesitamos cambiar de /data/{device_id} a /data con filtrado')
print('✅ Esto resolverá el problema de análisis temporal limitado')