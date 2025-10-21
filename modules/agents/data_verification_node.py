"""
Nodo de Verificación de Datos - Prevención de Alucinaciones LLM
==============================================================

Este módulo implementa un sistema de verificación para asegurar que
el agente solo hable de sensores y datos que realmente existen.
"""

import asyncio
from typing import Dict, List, Any, Set
from datetime import datetime
from modules.utils.logger import logger
from modules.database.db_connector import DatabaseConnector


class DataVerificationNode:
    """
    Nodo especializado en verificar la veracidad de los datos
    antes de generar respuestas finales.
    """
    
    def __init__(self):
        """Inicializa el nodo de verificación"""
        self.db_connector = DatabaseConnector()
        self.valid_sensor_types: Set[str] = set()
        self.valid_devices: Set[str] = set()
        self.last_refresh = None
        self.cache_duration = 300  # 5 minutos
        
    async def refresh_valid_data_cache(self) -> None:
        """
        Actualiza la caché de datos válidos desde la base de datos
        """
        try:
            await self.db_connector.connect()
            
            # Obtener tipos de sensores válidos
            sensor_query = "SELECT DISTINCT sensor_type FROM sensor_data WHERE timestamp >= NOW() - INTERVAL '24 hours';"
            sensor_results = await self.db_connector.execute_query(sensor_query)
            
            self.valid_sensor_types.clear()
            if sensor_results:
                for row in sensor_results:
                    if isinstance(row, dict):
                        sensor_type = row.get('sensor_type', '').lower().strip()
                    else:
                        sensor_type = str(row[0]).lower().strip() if row else ""
                    
                    if sensor_type:
                        self.valid_sensor_types.add(sensor_type)
            
            # Obtener dispositivos válidos
            device_query = "SELECT device_id FROM devices WHERE status = 'active';"
            device_results = await self.db_connector.execute_query(device_query)
            
            self.valid_devices.clear()
            if device_results:
                for row in device_results:
                    if isinstance(row, dict):
                        device_id = row.get('device_id', '').strip()
                    else:
                        device_id = str(row[0]).strip() if row else ""
                    
                    if device_id:
                        self.valid_devices.add(device_id)
            
            self.last_refresh = datetime.now()
            
            logger.info(f"✅ Caché actualizada: {len(self.valid_sensor_types)} tipos de sensores, {len(self.valid_devices)} dispositivos")
            logger.info(f"📊 Sensores válidos: {sorted(self.valid_sensor_types)}")
            
        except Exception as e:
            logger.error(f"❌ Error actualizando caché de verificación: {e}")
            
    async def ensure_fresh_cache(self) -> None:
        """Asegura que la caché esté actualizada"""
        if (not self.last_refresh or 
            (datetime.now() - self.last_refresh).total_seconds() > self.cache_duration):
            await self.refresh_valid_data_cache()
    
    def get_sensor_classification(self) -> Dict[str, List[str]]:
        """
        Clasifica los sensores válidos por categorías
        """
        classification = {
            "temperatura": [],
            "luz": [],
            "otros": []
        }
        
        for sensor in self.valid_sensor_types:
            sensor_lower = sensor.lower()
            if any(temp_keyword in sensor_lower for temp_keyword in 
                   ['temp', 'ntc', 't1', 't2', 't3']):
                classification["temperatura"].append(sensor)
            elif any(light_keyword in sensor_lower for light_keyword in 
                     ['ldr', 'light', 'luz']):
                classification["luz"].append(sensor)
            else:
                classification["otros"].append(sensor)
                
        return classification
    
    def identify_hallucinations(self, response_text: str) -> List[Dict[str, str]]:
        """
        Identifica posibles alucinaciones en el texto de respuesta
        """
        hallucinations = []
        response_lower = response_text.lower()
        
        # Palabras clave que indican sensores inexistentes en nuestro hardware
        # HARDWARE REAL: Solo tenemos sensores de temperatura (NTC/thermistores) y LDR (luminosidad)
        forbidden_keywords = {
            'humedad': ['humedad', 'humidity', 'hum_', '%rh'],
            'presion': ['presión', 'pressure', 'hpa', 'bar', 'atm'],
            'movimiento': ['movimiento', 'motion', 'pir'],
            'sonido': ['sonido', 'sound', 'ruido', 'db', 'decibel'],
            'co2': ['co2', 'dióxido', 'carbono'],
            'ph': ['ph', 'acidez', 'alcalinidad'],  
            'flujo': ['flujo', 'flow', 'caudal'],
            'voltaje': ['voltage', 'voltaje', 'volt', 'v']
        }
        
        for category, keywords in forbidden_keywords.items():
            for keyword in keywords:
                if keyword in response_lower:
                    # Verificar que no sea parte de otra palabra
                    import re
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    if re.search(pattern, response_lower):
                        hallucinations.append({
                            'type': 'sensor_inexistente',
                            'category': category,
                            'keyword': keyword,
                            'message': f"Mención de '{keyword}' pero no tenemos sensores de {category}"
                        })
        
        return hallucinations
    
    def generate_correction_prompt(self, hallucinations: List[Dict[str, str]]) -> str:
        """
        Genera un prompt de corrección basado en las alucinaciones detectadas
        """
        if not hallucinations:
            return ""
        
        classification = self.get_sensor_classification()
        
        correction = "\n\n⚠️ CORRECCIÓN NECESARIA:\n"
        correction += "Se detectaron menciones de sensores que NO existen en nuestro sistema:\n\n"
        
        for hall in hallucinations:
            correction += f"❌ {hall['message']}\n"
        
        correction += f"\n✅ SENSORES REALES DISPONIBLES:\n"
        correction += f"🌡️ Temperatura: {', '.join(classification['temperatura'])}\n"
        correction += f"💡 Luz: {', '.join(classification['luz'])}\n"
        if classification['otros']:
            correction += f"🔧 Otros: {', '.join(classification['otros'])}\n"
        
        correction += "\n📝 Por favor, reescribe la respuesta usando ÚNICAMENTE los sensores reales disponibles."
        
        return correction
    
    async def verify_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Nodo principal de verificación que valida la respuesta antes de enviarla
        """
        try:
            logger.info("🔍 Iniciando verificación de datos...")
            
            # Asegurar caché actualizada
            await self.ensure_fresh_cache()
            
            # Obtener la respuesta generada
            response = state.get("final_response", "")
            
            if not response:
                logger.warning("⚠️ No hay respuesta para verificar")
                return state
            
            # Identificar alucinaciones
            hallucinations = self.identify_hallucinations(response)
            
            # Agregar metadata de verificación
            state["verification_metadata"] = {
                "timestamp": datetime.now(),
                "hallucinations_detected": len(hallucinations),
                "hallucinations": hallucinations,
                "valid_sensor_types": list(self.valid_sensor_types),
                "sensor_classification": self.get_sensor_classification()
            }
            
            if hallucinations:
                logger.warning(f"⚠️ Se detectaron {len(hallucinations)} posibles alucinaciones")
                
                # Generar corrección
                correction_prompt = self.generate_correction_prompt(hallucinations)
                
                # Marcar para corrección
                state["needs_correction"] = True
                state["correction_prompt"] = correction_prompt
                state["original_response"] = response
                
                # Reemplazar respuesta con versión corregida temporalmente
                state["final_response"] = (
                    f"🔍 **Verificación de Datos**\n\n"
                    f"He detectado algunas inconsistencias en mi respuesta anterior. "
                    f"Permíteme corregir la información basándome únicamente en los sensores reales disponibles:\n\n"
                    f"**Sensores disponibles en nuestro sistema:**\n"
                    f"🌡️ **Temperatura**: {', '.join(self.get_sensor_classification()['temperatura'])}\n"
                    f"💡 **Luz/LDR**: {', '.join(self.get_sensor_classification()['luz'])}\n\n"
                    f"❌ **Nota importante**: No tenemos sensores de humedad, presión, movimiento u otros tipos no listados.\n\n"
                    f"¿Te gustaría que reformule mi respuesta basándome únicamente en los datos reales disponibles?"
                )
                
                logger.info("✅ Respuesta marcada para corrección")
            else:
                logger.info("✅ Verificación exitosa - no se detectaron alucinaciones")
                state["needs_correction"] = False
            
            # Agregar nodo a la lista de ejecutados
            if "execution_metadata" in state:
                state["execution_metadata"]["nodes_executed"].append("data_verification")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en verificación de datos: {e}")
            state["verification_error"] = str(e)
            return state
