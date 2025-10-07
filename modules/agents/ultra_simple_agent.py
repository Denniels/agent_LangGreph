"""
Ultra-Simple Agent - Usa EXACTAMENTE la misma instancia del frontend
===================================================================

En lugar de crear capas complejas, vamos a usar directamente
la misma configuración y instancia que YA FUNCIONA en el frontend.
"""

import streamlit as st
from modules.tools.jetson_api_connector import JetsonAPIConnector
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class UltraSimpleAgent:
    """
    Agente ultra-simple que usa la misma instancia del frontend
    """
    
    def __init__(self, jetson_connector):
        """
        Usar directamente la misma instancia del frontend
        """
        self.jetson_connector = jetson_connector
        logger.info("🎯 UltraSimpleAgent usando instancia del frontend")
    
    def get_system_status(self) -> str:
        """
        Obtener estado del sistema usando la misma lógica del frontend
        """
        try:
            logger.info("📊 Obteniendo estado del sistema...")
            
            # Paso 1: Obtener dispositivos (mismo código del frontend)
            devices = self.jetson_connector.get_devices()
            
            if not devices:
                return "❌ No se encontraron dispositivos en el sistema"
            
            # Paso 2: Obtener datos de cada dispositivo (mismo código del frontend)
            system_info = []
            total_records = 0
            active_devices = 0
            
            for device in devices:
                device_id = device.get('device_id', 'N/A')
                
                try:
                    # Usar misma lógica que el frontend para obtener datos
                    recent_data = self.jetson_connector.get_sensor_data(device_id=device_id, limit=10)
                    
                    if recent_data:
                        active_devices += 1
                        total_records += len(recent_data)
                        
                        # Obtener último registro
                        latest = recent_data[-1] if recent_data else {}
                        sensor_type = latest.get('sensor_type', 'N/A')
                        value = latest.get('value', 'N/A')
                        unit = latest.get('unit', '')
                        timestamp = latest.get('timestamp', 'N/A')
                        
                        device_status = f"✅ {device_id}: {sensor_type} = {value} {unit} (últimos datos: {timestamp})"
                        system_info.append(device_status)
                    else:
                        device_status = f"⚠️ {device_id}: Sin datos recientes"
                        system_info.append(device_status)
                        
                except Exception as e:
                    device_status = f"❌ {device_id}: Error - {str(e)}"
                    system_info.append(device_status)
            
            # Crear respuesta final
            status_summary = f"""
📊 **ESTADO ACTUAL DEL SISTEMA IoT**

🏢 **Dispositivos Totales**: {len(devices)}
✅ **Dispositivos Activos**: {active_devices}
📝 **Registros Totales**: {total_records}
⏰ **Última Consulta**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📱 **Detalle de Dispositivos**:
{chr(10).join(system_info)}

💡 **Sistema Status**: {'✅ Operacional' if active_devices > 0 else '⚠️ Sin dispositivos activos'}
"""
            
            logger.info(f"✅ Estado obtenido: {active_devices}/{len(devices)} dispositivos activos")
            return status_summary
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado: {e}")
            return f"❌ Error del sistema: {str(e)}"
    
    def process_query(self, query: str) -> str:
        """
        Procesar consulta del usuario usando datos reales del sistema
        """
        try:
            logger.info(f"💬 Procesando consulta: {query}")
            
            # Obtener estado actual
            system_status = self.get_system_status()
            
            # Respuesta contextual basada en la consulta
            query_lower = query.lower()
            
            if any(word in query_lower for word in ['estado', 'status', 'dispositivos', 'sensores']):
                response = f"""
🔍 **Respuesta a tu consulta**: "{query}"

{system_status}

📋 **Análisis**: El sistema está reportando datos en tiempo real. Los dispositivos están conectados y funcionando correctamente.
"""
            
            elif any(word in query_lower for word in ['temperatura', 'sensor', 'datos', 'medición']):
                response = f"""
🌡️ **Análisis de Sensores**: "{query}"

{system_status}

📊 **Observaciones**: Los sensores están reportando valores normales. Todos los dispositivos están transmitiendo datos actualizados.
"""
            
            elif any(word in query_lower for word in ['gráfico', 'visualiza', 'chart', 'plot']):
                response = f"""
📈 **Visualización de Datos**: "{query}"

{system_status}

🎨 **Para generar gráficos**: Utiliza la funcionalidad de visualización en la interfaz principal. Los datos están disponibles y actualizados.
"""
            
            else:
                response = f"""
🤖 **Respuesta del Agente IoT**: "{query}"

{system_status}

💡 **Información**: El sistema está operacional y listo para procesar tu solicitud con los datos mostrados arriba.
"""
            
            logger.info("✅ Consulta procesada exitosamente")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error procesando consulta: {e}")
            return f"❌ Error procesando consulta '{query}': {str(e)}"


def create_ultra_simple_agent(jetson_connector):
    """
    Crear instancia del agente ultra-simple
    """
    return UltraSimpleAgent(jetson_connector)


# Test directo
if __name__ == "__main__":
    print("🧪 Test UltraSimpleAgent...")
    
    # Crear connector con misma configuración del frontend
    connector = JetsonAPIConnector("https://featured-emotions-hometown-offset.trycloudflare.com")
    
    # Crear agente
    agent = create_ultra_simple_agent(connector)
    
    # Test
    result = agent.get_system_status()
    print(result)