"""
Sistema de Seguimiento de Uso de API - Groq
==========================================

Controla y monitorea el uso diario de las APIs para evitar sobrepasar límites.
Incluye contadores de consultas, tokens y reseteo automático diario.
"""

import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import os

logger = logging.getLogger(__name__)

class UsageTracker:
    """Seguimiento de uso de APIs con límites diarios"""
    
    def __init__(self, data_file: str = "usage_data.json"):
        self.data_file = Path(data_file)
        self.usage_data = self._load_usage_data()
        
        # Límites diarios por modelo Groq (actualizados según documentación oficial)
        self.daily_limits = {
            "llama-3.1-8b-instant": {
                "requests": 30000,  # 30K requests por día
                "tokens": 1000000,  # 1M tokens por día
                "description": "Llama 3.1 8B Instant"
            },
            "llama-3.1-70b-versatile": {
                "requests": 6000,   # 6K requests por día
                "tokens": 1000000,  # 1M tokens por día
                "description": "Llama 3.1 70B Versatile"
            },
            "llama3-8b-8192": {
                "requests": 30000,  # 30K requests por día
                "tokens": 1000000,  # 1M tokens por día
                "description": "Llama 3 8B"
            },
            "llama3-70b-8192": {
                "requests": 6000,   # 6K requests por día
                "tokens": 1000000,  # 1M tokens por día
                "description": "Llama 3 70B"
            },
            "mixtral-8x7b-32768": {
                "requests": 5000,   # 5K requests por día
                "tokens": 1000000,  # 1M tokens por día
                "description": "Mixtral 8x7B"
            },
            "gemma-7b-it": {
                "requests": 15000,  # 15K requests por día
                "tokens": 1000000,  # 1M tokens por día
                "description": "Gemma 7B IT"
            }
        }
    
    def _load_usage_data(self) -> Dict[str, Any]:
        """Cargar datos de uso desde archivo"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Verificar si necesitamos resetear (nuevo día)
                last_date = data.get('last_reset_date')
                current_date = str(date.today())
                
                if last_date != current_date:
                    logger.info(f"🔄 Reseteando contadores diarios - Nuevo día: {current_date}")
                    return self._create_fresh_data()
                    
                return data
            else:
                return self._create_fresh_data()
                
        except Exception as e:
            logger.error(f"Error cargando datos de uso: {e}")
            return self._create_fresh_data()
    
    def _create_fresh_data(self) -> Dict[str, Any]:
        """Crear estructura de datos fresca para un nuevo día"""
        return {
            "last_reset_date": str(date.today()),
            "daily_usage": {},
            "total_lifetime": {
                "requests": 0,
                "tokens": 0,
                "days_active": 0
            }
        }
    
    def _save_usage_data(self):
        """Guardar datos de uso a archivo"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando datos de uso: {e}")
    
    def track_request(self, model: str, tokens_used: int = 0) -> Dict[str, Any]:
        """
        Registrar una consulta y retornar información de uso.
        
        Args:
            model: Nombre del modelo usado
            tokens_used: Número de tokens utilizados
            
        Returns:
            Diccionario con información de uso y límites
        """
        try:
            # Normalizar nombre del modelo
            model = model.lower().strip()
            
            # Inicializar datos del modelo si no existen
            if model not in self.usage_data["daily_usage"]:
                self.usage_data["daily_usage"][model] = {
                    "requests": 0,
                    "tokens": 0,
                    "last_request": None
                }
            
            # Incrementar contadores
            self.usage_data["daily_usage"][model]["requests"] += 1
            self.usage_data["daily_usage"][model]["tokens"] += tokens_used
            self.usage_data["daily_usage"][model]["last_request"] = datetime.now().isoformat()
            
            # Actualizar contadores totales
            self.usage_data["total_lifetime"]["requests"] += 1
            self.usage_data["total_lifetime"]["tokens"] += tokens_used
            
            # Guardar cambios
            self._save_usage_data()
            
            # Obtener información de uso
            usage_info = self.get_usage_info(model)
            
            logger.info(f"📊 Consulta registrada - {model}: {usage_info['requests_used']}/{usage_info['requests_limit']} requests, {usage_info['tokens_used']}/{usage_info['tokens_limit']} tokens")
            
            return usage_info
            
        except Exception as e:
            logger.error(f"Error registrando consulta: {e}")
            return self.get_usage_info(model)
    
    def get_usage_info(self, model: str) -> Dict[str, Any]:
        """
        Obtener información completa de uso para un modelo.
        
        Args:
            model: Nombre del modelo
            
        Returns:
            Información detallada de uso y límites
        """
        model = model.lower().strip()
        
        # Datos actuales del modelo
        current_usage = self.usage_data["daily_usage"].get(model, {
            "requests": 0,
            "tokens": 0,
            "last_request": None
        })
        
        # Límites del modelo
        limits = self.daily_limits.get(model, {
            "requests": 1000,
            "tokens": 100000,
            "description": "Modelo desconocido"
        })
        
        # Calcular porcentajes
        requests_percentage = (current_usage["requests"] / limits["requests"]) * 100
        tokens_percentage = (current_usage["tokens"] / limits["tokens"]) * 100
        
        # Determinar estado
        status = "normal"
        if requests_percentage >= 90 or tokens_percentage >= 90:
            status = "critical"
        elif requests_percentage >= 75 or tokens_percentage >= 75:
            status = "warning"
        
        return {
            "model": model,
            "model_description": limits["description"],
            "date": self.usage_data["last_reset_date"],
            
            # Requests
            "requests_used": current_usage["requests"],
            "requests_limit": limits["requests"],
            "requests_remaining": limits["requests"] - current_usage["requests"],
            "requests_percentage": round(requests_percentage, 1),
            
            # Tokens
            "tokens_used": current_usage["tokens"],
            "tokens_limit": limits["tokens"],
            "tokens_remaining": limits["tokens"] - current_usage["tokens"],
            "tokens_percentage": round(tokens_percentage, 1),
            
            # Estado
            "status": status,
            "can_make_request": current_usage["requests"] < limits["requests"],
            "last_request": current_usage["last_request"],
            
            # Estadísticas adicionales
            "lifetime_stats": self.usage_data["total_lifetime"]
        }
    
    def get_all_models_usage(self) -> Dict[str, Dict[str, Any]]:
        """Obtener uso de todos los modelos"""
        result = {}
        
        # Modelos con uso registrado
        for model in self.usage_data["daily_usage"].keys():
            result[model] = self.get_usage_info(model)
        
        # Agregar modelos disponibles sin uso
        for model in self.daily_limits.keys():
            if model not in result:
                result[model] = self.get_usage_info(model)
        
        return result
    
    def check_can_make_request(self, model: str) -> Tuple[bool, str]:
        """
        Verificar si se puede hacer una consulta sin sobrepasar límites.
        
        Args:
            model: Nombre del modelo
            
        Returns:
            Tupla (puede_hacer_consulta, mensaje)
        """
        usage_info = self.get_usage_info(model)
        
        if not usage_info["can_make_request"]:
            return False, f"⚠️ Límite diario alcanzado para {usage_info['model_description']} ({usage_info['requests_used']}/{usage_info['requests_limit']} requests)"
        
        if usage_info["status"] == "critical":
            return True, f"🚨 Uso crítico: {usage_info['requests_percentage']}% de requests utilizados"
        elif usage_info["status"] == "warning":
            return True, f"⚠️ Uso alto: {usage_info['requests_percentage']}% de requests utilizados"
        else:
            return True, f"✅ Uso normal: {usage_info['requests_remaining']} requests disponibles"
    
    def get_daily_summary(self) -> Dict[str, Any]:
        """Obtener resumen diario de uso"""
        total_requests = sum(
            model_data["requests"] 
            for model_data in self.usage_data["daily_usage"].values()
        )
        
        total_tokens = sum(
            model_data["tokens"] 
            for model_data in self.usage_data["daily_usage"].values()
        )
        
        models_used = len(self.usage_data["daily_usage"])
        
        return {
            "date": self.usage_data["last_reset_date"],
            "total_requests_today": total_requests,
            "total_tokens_today": total_tokens,
            "models_used_today": models_used,
            "active_models": list(self.usage_data["daily_usage"].keys()),
            "lifetime_stats": self.usage_data["total_lifetime"]
        }
    
    def force_reset(self):
        """Forzar reset de contadores (para testing)"""
        logger.info("🔄 Forzando reset de contadores de uso")
        self.usage_data = self._create_fresh_data()
        self._save_usage_data()

# Instancia global del tracker
usage_tracker = UsageTracker()