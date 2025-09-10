"""
Agente IoT Principal con Ollama
==============================

Agente conversacional principal que maneja las interacciones con el sistema IoT usando Ollama.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from modules.tools.database_tools import DatabaseTools
from modules.tools.analysis_tools import AnalysisTools
from modules.agents.ollama_integration import OllamaLLMIntegration
from modules.utils.logger import logger


class IoTAgent:
    """
    Agente conversacional para el sistema IoT usando Ollama.
    """
    
    def __init__(self, model_name: str = "llama3.2:latest"):
        """
        Inicializa el agente IoT con integración de Ollama.
        
        Args:
            model_name (str): Nombre del modelo de Ollama a usar
        """
        self.llm = OllamaLLMIntegration(model_name)
        self.db_tools = DatabaseTools()
        self.analysis_tools = AnalysisTools()
        logger.info(f"Agente IoT inicializado con modelo: {model_name}")
    
    async def process_message(self, user_message: str) -> str:
        """
        Procesa un mensaje del usuario y genera una respuesta.
        
        Args:
            user_message (str): Mensaje del usuario
            
        Returns:
            str: Respuesta del agente
        """
        try:
            logger.info(f"Procesando mensaje del usuario: {user_message[:100]}...")
            
            # Determinar qué herramientas usar basado en el mensaje
            tools_to_use = self._determine_tools(user_message)
            
            # Recopilar datos de contexto
            context_data = await self._gather_context_data(tools_to_use)
            
            # Ejecutar herramientas según el análisis del mensaje
            tools_results = await self._execute_tools(user_message, tools_to_use)

            # Métricas precomputadas para orientar al LLM (sin JSON/código)
            pre_metrics = self._compose_technical_report(tools_results)
            if pre_metrics:
                tools_results["report_metrics"] = pre_metrics

            # Si el usuario pide gráfico/PDF, añade flags
            wants_viz = any(w in user_message.lower() for w in ["gráfico", "grafico", "visual", "chart"]) or "visualización" in user_message.lower()
            wants_pdf = "pdf" in user_message.lower() or "descargable" in user_message.lower() or "imprimible" in user_message.lower()
            if wants_viz or wants_pdf:
                tools_results["request_flags"] = {"wants_visualizations": wants_viz, "wants_pdf": wants_pdf}
            
            # Si una herramienta proporcionó respuesta directa (p. ej., total de registros), devuélvela sin pasar por LLM
            if isinstance(tools_results, dict) and 'direct_answer' in tools_results:
                logger.info("Respuesta directa generada por herramientas; omitiendo LLM")
                return tools_results['direct_answer']

            # Generar respuesta usando Ollama
            response = await self.llm.generate_response(
                user_message=user_message,
                context_data=context_data,
                tools_results=tools_results
            )
            
            logger.info("Mensaje procesado exitosamente")
            return response
            
        except Exception as e:
            logger.error(f"Error al procesar mensaje: {e}")
            return f"❌ Error al procesar tu consulta: {str(e)}"
    
    def _determine_tools(self, message: str) -> List[str]:
        """
        Determina qué herramientas usar basado en el mensaje del usuario.
        
        Args:
            message (str): Mensaje del usuario
            
        Returns:
            List[str]: Lista de herramientas a usar
        """
        message_lower = message.lower()
        tools: List[str] = []

        # Palabras clave para diferentes tipos de consultas
        if any(word in message_lower for word in ['temperatura', 'sensor', 'datos', 'lecturas', 'medición']):
            tools.append('sensor_data')

        if any(word in message_lower for word in ['dispositivo', 'device', 'estado', 'conectado', 'offline']):
            tools.append('devices')

        if any(word in message_lower for word in ['alerta', 'alert', 'problema', 'warning', 'error']):
            tools.append('alerts')

        if any(word in message_lower for word in ['análisis', 'tendencia', 'patrón', 'histórico', 'trend']):
            tools.append('analysis')

        if any(word in message_lower for word in ['anomalía', 'anómalo', 'unusual', 'extraño']):
            tools.append('anomalies')

        # Conteos/estadísticas totales
        if any(w in message_lower for w in ['total', 'conteo', 'cuenta', 'count', 'cuántos', 'cantidad']):
            tools.append('db_stats')

        # Si no se detecta nada específico, obtener datos generales
        if not tools:
            tools = ['sensor_data', 'devices', 'alerts']

        return tools
    
    async def _gather_context_data(self, tools_to_use: List[str]) -> Dict[str, Any]:
        """
        Recopila datos de contexto del sistema optimizado para IoT tiempo real.
        
        Args:
            tools_to_use (List[str]): Herramientas que se van a usar
            
        Returns:
            Dict[str, Any]: Datos de contexto con datos recientes
        """
        context = {
            "timestamp": datetime.now().isoformat(),
            "tools_requested": tools_to_use
        }
        
        try:
            # Obtener datos de tiempo real más completos
            recent_data = await self.db_tools.get_sensor_data_tool(limit=100)  # Aumentado a 100
            ultra_recent = await self.db_tools.get_recent_sensor_data_tool(minutes=2, limit=30)  # Nuevos datos ultra-recientes
            active_devices = await self.db_tools.get_devices_tool()
            alerts = await self.db_tools.get_alerts_tool(active_only=True)
            
            context.update({
                "recent_data": recent_data,
                "ultra_recent_data": ultra_recent,  # Datos de últimos 2 minutos
                "active_devices": active_devices,
                "alerts": alerts,
                "data_summary": {
                    "total_recent_records": len(recent_data),
                    "ultra_recent_records": len(ultra_recent),
                    "active_devices_count": len(active_devices),
                    "active_alerts_count": len(alerts)
                }
            })
            
        except Exception as e:
            logger.error(f"Error al recopilar datos de contexto: {e}")
            context["error"] = str(e)
            
        return context
    
    async def _execute_tools(self, message: str, tools_to_use: List[str]) -> Dict[str, Any]:
        """
        Ejecuta las herramientas determinadas.
        
        Args:
            message (str): Mensaje original del usuario
            tools_to_use (List[str]): Herramientas a ejecutar
            
        Returns:
            Dict[str, Any]: Resultados de las herramientas
        """
        results = {}
        
        try:
            # Ruta especial: si piden explícitamente el total, responde conciso sin informe
            msg = message.lower()
            wants_total = any(
                p in msg for p in [
                    'total de registros', 'total de lecturas', 'cantidad total', 'cuántos registros',
                    'cuantos registros', 'count(*)', 'conteo total', 'número total de registros'
                ]
            )
            if wants_total:
                stats = await self.db_tools.get_sensor_stats_tool()
                results['db_stats'] = stats
                # Construye respuesta breve y precisa; evita enviar a LLM para no desviar formato
                total = stats.get('total_records', 0)
                first_ts = stats.get('first_record_at')
                last_ts = stats.get('last_record_at')
                devices = stats.get('devices_count', 0)
                return {
                    'direct_answer': f"Total de registros en sensor_data: {total}. Dispositivos con lecturas: {devices}. Rango temporal: {first_ts} → {last_ts}.",
                    'db_stats': stats
                }

            if 'sensor_data' in tools_to_use:
                # Usar un límite mayor para brindar suficiente contexto
                results['sensor_data'] = await self.db_tools.get_sensor_data_tool(limit=100)
                
            if 'devices' in tools_to_use:
                results['devices'] = await self.db_tools.get_devices_tool()
                
            if 'alerts' in tools_to_use:
                results['alerts'] = await self.db_tools.get_alerts_tool()
                
            if 'analysis' in tools_to_use:
                # Obtener más datos para análisis
                sensor_data = await self.db_tools.get_sensor_data_tool(limit=150)
                if sensor_data:
                    results['trends'] = self.analysis_tools.analyze_sensor_trends(sensor_data)
                    
            if 'anomalies' in tools_to_use:
                sensor_data = await self.db_tools.get_sensor_data_tool(limit=120)
                if sensor_data:
                    results['anomalies'] = self.analysis_tools.detect_anomalies(sensor_data)

            if 'db_stats' in tools_to_use and 'db_stats' not in results:
                results['db_stats'] = await self.db_tools.get_sensor_stats_tool()
                    
        except Exception as e:
            logger.error(f"Error al ejecutar herramientas: {e}")
            results['error'] = str(e)
            
        return results

    def _compose_technical_report(self, tools_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas agregadas para ayudar al LLM a redactar un informe técnico.
        No retorna texto final; sólo cifras para orientar la respuesta.
        """
        report = {}
        try:
            data = tools_results.get("sensor_data", [])
            if isinstance(data, list) and data:
                # Agregados básicos por tipo de sensor
                from statistics import mean, pstdev
                by_type = {}
                for row in data:
                    t = row.get("sensor_type")
                    by_type.setdefault(t, []).append(float(row.get("value", 0)))
                metrics = {}
                for t, vals in by_type.items():
                    if not vals:
                        continue
                    metrics[t] = {
                        "count": len(vals),
                        "avg": float(mean(vals)),
                        "min": float(min(vals)),
                        "max": float(max(vals)),
                        "std": float(pstdev(vals)) if len(vals) > 1 else 0.0,
                    }
                report["metrics_by_sensor_type"] = metrics
                report["total_readings"] = sum(m["count"] for m in metrics.values())
        except Exception as e:
            logger.warning(f"No se pudieron calcular métricas previas: {e}")
        return report
    
    async def create_alert_from_message(self, device_id: str, message: str, severity: str = "medium") -> Dict[str, Any]:
        """
        Crea una alerta basada en un mensaje.
        
        Args:
            device_id (str): ID del dispositivo
            message (str): Mensaje de la alerta
            severity (str): Severidad de la alerta
            
        Returns:
            Dict[str, Any]: Resultado de la creación de alerta
        """
        try:
            result = await self.db_tools.create_alert_tool(
                device_id=device_id,
                alert_type="user_generated",
                message=message,
                severity=severity
            )
            
            logger.info(f"Alerta creada para dispositivo {device_id}")
            return {"success": True, "alert_id": result}
            
        except Exception as e:
            logger.error(f"Error al crear alerta: {e}")
            return {"success": False, "error": str(e)}
    
    def clear_conversation_history(self):
        """Limpia el historial de conversación."""
        self.llm.clear_conversation_history()
        logger.info("Historial de conversación limpiado")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del estado del agente.
        
        Returns:
            Dict[str, Any]: Resumen del estado
        """
        llm_summary = self.llm.get_conversation_summary()
        
        return {
            "agent_status": "active",
            "model_info": llm_summary,
            "tools_available": [
                "database_tools",
                "analysis_tools",
                "ollama_integration"
            ],
            "last_update": datetime.now().isoformat()
        }
    
    async def test_system_health(self) -> Dict[str, Any]:
        """
        Prueba la salud del sistema completo.
        
        Returns:
            Dict[str, Any]: Estado de salud del sistema
        """
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        try:
            # Probar conexión Ollama
            ollama_status = await self.llm.test_connection()
            health_report["components"]["ollama"] = {
                "status": "healthy" if ollama_status else "error",
                "model": self.llm.model_name
            }
            
            # Probar herramientas de base de datos
            try:
                db_test = await self.db_tools.get_sensor_data_tool(limit=1)
                health_report["components"]["database"] = {
                    "status": "healthy",
                    "last_data": db_test[0] if db_test else None
                }
            except Exception as e:
                health_report["components"]["database"] = {
                    "status": "error",
                    "error": str(e)
                }
            
            # Probar herramientas de análisis
            try:
                test_data = [{"value": 25.0, "timestamp": datetime.now()}]
                trends_test = self.analysis_tools.analyze_sensor_trends(test_data)
                health_report["components"]["analysis"] = {
                    "status": "healthy"
                }
            except Exception as e:
                health_report["components"]["analysis"] = {
                    "status": "error",
                    "error": str(e)
                }
            
            # Determinar estado general
            all_healthy = all(
                comp["status"] == "healthy" 
                for comp in health_report["components"].values()
            )
            
            health_report["overall_status"] = "healthy" if all_healthy else "degraded"
            
        except Exception as e:
            logger.error(f"Error en prueba de salud del sistema: {e}")
            health_report["overall_status"] = "error"
            health_report["error"] = str(e)
            
        return health_report
