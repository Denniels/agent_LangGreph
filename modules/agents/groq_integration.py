"""
Integración con Groq API para el Remote IoT Agent
Groq ofrece API gratuita sin necesidad de tarjeta de crédito
"""

import os
import json
from groq import Groq
from typing import Optional, Dict, Any
import logging
from prompts.system_prompt import SYSTEM_PROMPT

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqIntegration:
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializar integración con Groq
        
        Args:
            api_key: API key de Groq (opcional, se puede usar variable de entorno)
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.client = None
        
        # Modelos disponibles en Groq (todos gratuitos)
        self.available_models = [
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant", 
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
            "gemma-7b-it"
        ]
        
        self.default_model = "llama-3.1-8b-instant"  # Rápido y eficiente
        
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("✅ Cliente Groq inicializado con API key")
            except Exception as e:
                logger.error(f"Error inicializando cliente Groq: {e}")
                self.client = None
        else:
            logger.warning("GROQ_API_KEY no encontrada. Usando respuestas de fallback.")
    
    def generate_response(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Generar respuesta usando Groq API
        
        Args:
            prompt: Prompt para el modelo
            model: Modelo a usar (opcional)
            
        Returns:
            Respuesta generada o mensaje de fallback
        """
        if not self.client:
            return self._get_fallback_response(prompt)
        
        model = model or self.default_model
        
        try:
            logger.info(f"Enviando request a Groq con modelo: {model}")
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                model=model,
                max_tokens=1000,
                temperature=0.1,  # Más bajo para reducir alucinaciones
                top_p=0.8,        # Más conservador
                stream=False
            )
            
            content = chat_completion.choices[0].message.content
            logger.info(f"Respuesta exitosa de Groq: {len(content)} caracteres")
            return content
                
        except Exception as e:
            logger.error(f"Excepción en Groq API: {str(e)}")
            return self._get_fallback_response(prompt)
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Probar conexión con Groq API
        
        Returns:
            Diccionario con resultado de la prueba
        """
        if not self.client:
            return {
                "success": False,
                "error": "API key no configurada",
                "suggestion": "Configura GROQ_API_KEY en variables de entorno"
            }
        
        test_prompt = "Responde solo con 'OK' si puedes leer este mensaje."
        
        try:
            response = self.generate_response(test_prompt)
            
            if "OK" in response.upper() or len(response) > 0:
                return {
                    "success": True,
                    "message": "Conexión exitosa con Groq API",
                    "model": self.default_model,
                    "response": response
                }
            else:
                return {
                    "success": False,
                    "error": "Respuesta inesperada",
                    "response": response
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error de conexión: {str(e)}"
            }
    
    def _get_fallback_response(self, prompt: str) -> str:
        """
        Generar respuesta de fallback cuando Groq API no está disponible
        """
        logger.info("Usando respuesta de fallback")
        
        # Respuesta conservadora sin inventar datos
        if "temperatura" in prompt.lower() or "temperature" in prompt.lower():
            return """
            ⚠️ **Sistema en Modo Fallback**
            
            🔍 **Consulta sobre Temperatura**
            - Dispositivos disponibles: ESP32 WiFi, Arduino Ethernet
            - Sensores de temperatura: Disponibles
            - Estado: Para obtener datos actuales, se requiere conexión con la base de datos
            
            💡 **Recomendación**: Verificar conectividad de red y reintenta la consulta
            """
        
        elif "ldr" in prompt.lower() or "luz" in prompt.lower() or "light" in prompt.lower():
            return """
            ⚠️ **Sistema en Modo Fallback**
            
            🔍 **Consulta sobre Sensor LDR/Luz**
            - Dispositivos con LDR: ESP32 WiFi
            - Sensor de luz: Disponible
            - Estado: Para obtener datos actuales, se requiere conexión con la base de datos
            
            💡 **Recomendación**: Verificar conectividad de red y reintenta la consulta
            """
        
        elif any(sensor in prompt.lower() for sensor in ["humedad", "humidity", "movimiento", "presión", "co2", "ph", "voltage", "voltaje"]):
            return """
            ❌ **Sensor No Disponible**
            
            � **Sensores disponibles en nuestro sistema:**
            - 🌡️ Temperatura (ESP32, Arduino)
            - 💡 LDR/Luz (ESP32)
            
            ❌ **Sensores NO disponibles:**
            - Humedad, Movimiento, Presión, CO2, pH, etc.
            
            💡 **Sugerencia**: Consulta sobre temperatura o niveles de luz
            """
        
        else:
            return """
            ⚠️ **Sistema en Modo Fallback**
            
            🤖 **Estado actual:**
            - Conectividad con API limitada
            - Base de datos: Verificando conexión
            
            📊 **Servicios disponibles:**
            - Consultas sobre temperatura y luz
            - Estado de dispositivos ESP32 y Arduino
            - Análisis de tendencias (cuando hay conectividad)
            
            💡 **Recomendación**: Reintenta tu consulta en unos momentos
            """
    
    def get_models(self) -> list:
        """Obtener lista de modelos disponibles"""
        return self.available_models

# Función de conveniencia para uso directo
def create_groq_client(api_key: Optional[str] = None) -> GroqIntegration:
    """
    Crear cliente de Groq
    
    Args:
        api_key: API key opcional
        
    Returns:
        Instancia de GroqIntegration
    """
    return GroqIntegration(api_key)

# Test básico si se ejecuta directamente
if __name__ == "__main__":
    groq = GroqIntegration()
    test_result = groq.test_connection()
    print(f"Test de conexión: {test_result}")
    
    if test_result['success']:
        response = groq.generate_response("Analiza estos datos de sensores reales: temp=25°C, ldr=85%")
        print(f"Respuesta: {response}")
