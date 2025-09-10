-- Datos de Ejemplo para el Sistema IoT
-- =====================================

-- Insertar dispositivos de ejemplo
INSERT INTO devices (device_id, device_name, device_type, location, status, last_seen) VALUES
('TEMP_001', 'Sensor Temperatura Oficina', 'temperature_sensor', 'Oficina Principal', 'active', CURRENT_TIMESTAMP),
('HUM_001', 'Sensor Humedad Oficina', 'humidity_sensor', 'Oficina Principal', 'active', CURRENT_TIMESTAMP),
('TEMP_002', 'Sensor Temperatura Almacén', 'temperature_sensor', 'Almacén', 'active', CURRENT_TIMESTAMP - INTERVAL '5 minutes'),
('PRESS_001', 'Sensor Presión Lab', 'pressure_sensor', 'Laboratorio', 'active', CURRENT_TIMESTAMP - INTERVAL '2 minutes'),
('LIGHT_001', 'Sensor Luz Sala', 'light_sensor', 'Sala de Conferencias', 'active', CURRENT_TIMESTAMP),
('MOTION_001', 'Detector Movimiento', 'motion_sensor', 'Entrada Principal', 'active', CURRENT_TIMESTAMP - INTERVAL '1 minute'),
('TEMP_003', 'Sensor Temperatura Exterior', 'temperature_sensor', 'Exterior', 'maintenance', CURRENT_TIMESTAMP - INTERVAL '2 hours')
ON CONFLICT (device_id) DO NOTHING;

-- Insertar configuración de sensores
INSERT INTO sensor_config (device_id, sensor_type, min_threshold, max_threshold, alert_enabled) VALUES
('TEMP_001', 'temperature', 18.0, 25.0, true),
('TEMP_002', 'temperature', 15.0, 30.0, true),
('TEMP_003', 'temperature', -10.0, 40.0, true),
('HUM_001', 'humidity', 30.0, 70.0, true),
('PRESS_001', 'pressure', 980.0, 1020.0, true),
('LIGHT_001', 'light', 100.0, 1000.0, true)
ON CONFLICT DO NOTHING;

-- Función para generar datos de sensores aleatorios
CREATE OR REPLACE FUNCTION generate_sample_sensor_data(
    device_id_param VARCHAR(50),
    sensor_type_param VARCHAR(50),
    base_value DECIMAL(10,4),
    variance DECIMAL(10,4),
    unit_param VARCHAR(20),
    location_param VARCHAR(100),
    hours_back INTEGER DEFAULT 24,
    readings_per_hour INTEGER DEFAULT 4
) RETURNS VOID AS $$
DECLARE
    i INTEGER;
    current_time TIMESTAMP;
    random_value DECIMAL(10,4);
BEGIN
    FOR i IN 0..(hours_back * readings_per_hour - 1) LOOP
        current_time := CURRENT_TIMESTAMP - (i * INTERVAL '15 minutes');
        random_value := base_value + (RANDOM() - 0.5) * variance * 2;
        
        INSERT INTO sensor_data (device_id, sensor_type, value, unit, timestamp, location)
        VALUES (device_id_param, sensor_type_param, random_value, unit_param, current_time, location_param);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Generar datos de ejemplo para las últimas 24 horas
SELECT generate_sample_sensor_data('TEMP_001', 'temperature', 22.0, 3.0, '°C', 'Oficina Principal', 24, 4);
SELECT generate_sample_sensor_data('TEMP_002', 'temperature', 20.0, 5.0, '°C', 'Almacén', 24, 4);
SELECT generate_sample_sensor_data('TEMP_003', 'temperature', 15.0, 8.0, '°C', 'Exterior', 24, 4);
SELECT generate_sample_sensor_data('HUM_001', 'humidity', 45.0, 15.0, '%', 'Oficina Principal', 24, 4);
SELECT generate_sample_sensor_data('PRESS_001', 'pressure', 1013.25, 10.0, 'hPa', 'Laboratorio', 24, 4);
SELECT generate_sample_sensor_data('LIGHT_001', 'light', 400.0, 200.0, 'lux', 'Sala de Conferencias', 24, 4);

-- Insertar algunas alertas de ejemplo
INSERT INTO alerts (device_id, alert_type, message, severity, status, created_at) VALUES
('TEMP_002', 'high_temperature', 'Temperatura alta detectada en el almacén: 31.2°C', 'high', 'active', CURRENT_TIMESTAMP - INTERVAL '2 hours'),
('TEMP_003', 'device_offline', 'Dispositivo no responde desde hace 2 horas', 'medium', 'active', CURRENT_TIMESTAMP - INTERVAL '2 hours'),
('HUM_001', 'high_humidity', 'Humedad elevada en oficina principal: 75%', 'medium', 'active', CURRENT_TIMESTAMP - INTERVAL '30 minutes'),
('PRESS_001', 'low_pressure', 'Presión baja detectada en laboratorio: 978 hPa', 'low', 'resolved', CURRENT_TIMESTAMP - INTERVAL '4 hours', CURRENT_TIMESTAMP - INTERVAL '3 hours', 'system'),
('MOTION_001', 'no_motion', 'No se detecta movimiento en entrada principal por más de 1 hora', 'low', 'active', CURRENT_TIMESTAMP - INTERVAL '1 hour')
ON CONFLICT DO NOTHING;

-- Crear algunas lecturas más recientes con valores anómalos para testing
INSERT INTO sensor_data (device_id, sensor_type, value, unit, timestamp, location) VALUES
-- Temperatura anormalmente alta
('TEMP_001', 'temperature', 35.5, '°C', CURRENT_TIMESTAMP - INTERVAL '5 minutes', 'Oficina Principal'),
-- Humedad muy baja
('HUM_001', 'humidity', 15.2, '%', CURRENT_TIMESTAMP - INTERVAL '3 minutes', 'Oficina Principal'),
-- Presión anormalmente alta
('PRESS_001', 'pressure', 1045.8, 'hPa', CURRENT_TIMESTAMP - INTERVAL '1 minute', 'Laboratorio'),
-- Lecturas normales recientes
('TEMP_001', 'temperature', 23.1, '°C', CURRENT_TIMESTAMP, 'Oficina Principal'),
('HUM_001', 'humidity', 48.3, '%', CURRENT_TIMESTAMP, 'Oficina Principal'),
('LIGHT_001', 'light', 420.7, 'lux', CURRENT_TIMESTAMP, 'Sala de Conferencias')
ON CONFLICT DO NOTHING;
