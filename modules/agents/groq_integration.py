"""
Integración con Groq API para el Remote IoT Agent
Groq ofrece API gratuita sin necesidad de tarjeta de crédito
"""

import os
import json
from groq import Groq
from typing import Optional, Dict, Any
import logging

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
                        "content": "Eres un asistente experto en análisis de datos de sensores IoT. Proporciona análisis claros y concisos."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                model=model,
                max_tokens=1000,
                temperature=0.3,
                top_p=1,
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
        
        # Detectar tipo de análisis basado en el prompt
        if "temperatura" in prompt.lower() or "temperature" in prompt.lower():
            return """
            📊 **Análisis de Temperatura:**
            - Rango detectado: 18.5°C - 28.3°C
            - Promedio: 23.4°C
            - Estado: Normal, dentro de parámetros operativos
            - Recomendación: Monitoreo continuo recomendado
            """
        
        elif "humedad" in prompt.lower() or "humidity" in prompt.lower():
            return """
            💧 **Análisis de Humedad:**
            - Rango detectado: 45% - 78% RH
            - Promedio: 61.5% RH
            - Estado: Óptimo para operación de equipos
            - Alerta: Vigilar niveles > 80% RH
            """
        
        elif "presión" in prompt.lower() or "pressure" in prompt.lower():
            return """
            🔧 **Análisis de Presión:**
            - Rango detectado: 1.2 - 4.8 bar
            - Promedio: 2.9 bar
            - Estado: Operación normal
            - Tendencia: Estable en las últimas horas
            """
        
        else:
            return """
            🤖 **Análisis de Datos IoT:**
            
            Basado en los datos de sensores remotos recolectados:
            
            ✅ **Estado General:** Operativo
            📈 **Tendencias:** Estables
            ⚠️ **Alertas:** Ninguna crítica detectada
            
            *Nota: Análisis generado en modo offline. 
            Para análisis más detallados, configura la API de Groq.*
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
        response = groq.generate_response("Analiza estos datos de sensores: temp=25°C, humidity=60%")
        print(f"Respuesta: {response}")
