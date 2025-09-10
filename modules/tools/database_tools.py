"""
Herramientas de Base de Datos
============================

Herramientas que el agente puede usar para consultar la base de datos IoT.
"""

from typing import List, Dict, Any, Optional
from modules.database import DatabaseConnector, get_db
from modules.utils.logger import setup_logger

logger = setup_logger(__name__)


class DatabaseTools:
    """
    Herramientas para interactuar con la base de datos IoT.
    """
    
    def __init__(self):
        self.db = None
    
    async def _get_db(self) -> DatabaseConnector:
        """Obtiene la instancia de la base de datos"""
        if not self.db:
            self.db = await get_db()
        return self.db
    
    async def get_sensor_data_tool(self, device_id: Optional[str] = None, 
                                 limit: int = 100) -> List[Dict[str, Any]]:
        """
        Herramienta para obtener datos de sensores optimizada para IoT tiempo real.
        
        Args:
            device_id: ID del dispositivo (opcional)
            limit: Número máximo de resultados (aumentado a 100 para tiempo real)
            
        Returns:
            Lista de datos de sensores de los últimos 10 minutos
        """
        db = await self._get_db()
        try:
            # Consulta optimizada para datos en tiempo real (últimos 10 minutos)
            query = """
                SELECT 
                    id,
                    device_id,
                    sensor_type,
                    value,
                    unit,
                    timestamp,
                    created_at
                FROM sensor_data
                WHERE timestamp >= NOW() - INTERVAL '10 minutes'
            """
            params = []
            
            if device_id:
                query += " AND device_id = $1"
                params.append(device_id)
                query += " ORDER BY timestamp DESC LIMIT $2"
                params.append(limit)
            else:
                query += " ORDER BY timestamp DESC LIMIT $1"
                params.append(limit)
            
            data = await db.execute_query(query, *params)
            # Fallback: si inesperadamente llegan 0-1 registros y no se filtró por device, reintentar una vez
            if not device_id and len(data) <= 1:
                logger.warning("Resultado inusualmente pequeño (<=1). Reintentando consulta rápida fallback...")
                retry_query = """
                    SELECT id, device_id, sensor_type, value, unit, timestamp, created_at
                    FROM sensor_data
                    ORDER BY timestamp DESC
                    LIMIT $1
                """
                try:
                    retry_data = await db.execute_query(retry_query, limit)
                    if len(retry_data) > len(data):
                        logger.info(f"Fallback recuperó {len(retry_data)} registros (primera respuesta {len(data)})")
                        data = retry_data
                except Exception as inner:
                    logger.error(f"Error en fallback de sensor_data: {inner}")
            logger.info(f"Obtenidos {len(data)} registros de sensores (últimos 10 min)")
            return data
        except Exception as e:
            logger.error(f"Error obteniendo datos de sensores: {e}")
            return []
    
    async def get_recent_sensor_data_tool(self, minutes: int = 2, 
                                        limit: int = 50) -> List[Dict[str, Any]]:
        """
        Herramienta para obtener datos de sensores ultra-recientes.
        
        Args:
            minutes: Minutos hacia atrás (defecto: 2 min)
            limit: Número máximo de resultados
            
        Returns:
            Lista de datos de sensores ultra-recientes
        """
        db = await self._get_db()
        try:
            query = f"""
                SELECT 
                    id,
                    device_id,
                    sensor_type,
                    value,
                    unit,
                    timestamp,
                    created_at
                FROM sensor_data
                WHERE timestamp >= NOW() - INTERVAL '{minutes} minutes'
                ORDER BY timestamp DESC 
                LIMIT $1
            """
            
            data = await db.execute_query(query, limit)
            if len(data) == 0:
                # Fallback adicional: tomar últimos registros sin filtro temporal si nada llegó
                fallback = """
                    SELECT id, device_id, sensor_type, value, unit, timestamp, created_at
                    FROM sensor_data
                    ORDER BY timestamp DESC
                    LIMIT $1
                """
                try:
                    retry = await db.execute_query(fallback, limit)
                    if retry:
                        logger.info(f"Fallback ultra-reciente obtuvo {len(retry)} registros")
                        data = retry
                except Exception as inner:
                    logger.error(f"Error en fallback ultra-reciente: {inner}")
            logger.info(f"Obtenidos {len(data)} registros ultra-recientes (últimos {minutes} min)")
            return data
        except Exception as e:
            logger.error(f"Error obteniendo datos recientes: {e}")
            return []
    
    async def get_devices_tool(self) -> List[Dict[str, Any]]:
        """
        Herramienta para obtener lista de dispositivos activos.
        
        Returns:
            Lista de dispositivos activos
        """
        db = await self._get_db()
        try:
            devices = await db.get_active_devices()
            logger.info(f"Obtenidos {len(devices)} dispositivos activos")
            return devices
        except Exception as e:
            logger.error(f"Error obteniendo dispositivos: {e}")
            return []
    
    async def get_alerts_tool(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Herramienta para obtener alertas del sistema.
        
        Args:
            active_only: Si True, solo retorna alertas activas
            
        Returns:
            Lista de alertas
        """
        db = await self._get_db()
        try:
            alerts = await db.get_alerts(active_only)
            logger.info(f"Obtenidas {len(alerts)} alertas")
            return alerts
        except Exception as e:
            logger.error(f"Error obteniendo alertas: {e}")
            return []
    
    async def create_alert_tool(self, device_id: str, alert_type: str, 
                              message: str, severity: str = 'medium') -> bool:
        """
        Herramienta para crear una nueva alerta.
        
        Args:
            device_id: ID del dispositivo
            alert_type: Tipo de alerta
            message: Mensaje de la alerta
            severity: Severidad de la alerta
            
        Returns:
            True si se creó correctamente
        """
        db = await self._get_db()
        try:
            success = await db.create_alert(device_id, alert_type, message, severity)
            if success:
                logger.info(f"Alerta creada para dispositivo {device_id}")
            return success
        except Exception as e:
            logger.error(f"Error creando alerta: {e}")
            return False

    async def get_sensor_stats_tool(self) -> Dict[str, Any]:
        """Estadísticas globales de la tabla sensor_data para consultas avanzadas.
        Devuelve totales, rango temporal, número de dispositivos y conteo por dispositivo.
        """
        db = await self._get_db()
        try:
            total_q = "SELECT COUNT(*) AS total FROM sensor_data"
            range_q = "SELECT MIN(timestamp) AS first_ts, MAX(timestamp) AS last_ts FROM sensor_data"
            devs_q = "SELECT COUNT(DISTINCT device_id) AS devices FROM sensor_data"
            by_dev_q = (
                "SELECT device_id, COUNT(*) AS count "
                "FROM sensor_data GROUP BY device_id ORDER BY count DESC LIMIT 100"
            )

            total = await db.execute_query(total_q)
            trange = await db.execute_query(range_q)
            devs = await db.execute_query(devs_q)
            by_dev = await db.execute_query(by_dev_q)

            result = {
                "total_records": int(total[0]["total"]) if total else 0,
                "first_record_at": trange[0]["first_ts"] if trange else None,
                "last_record_at": trange[0]["last_ts"] if trange else None,
                "devices_count": int(devs[0]["devices"]) if devs else 0,
                "counts_by_device": by_dev,
            }
            logger.info(
                f"Stats: total={result['total_records']} devices={result['devices_count']}"
            )
            return result
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de sensores: {e}")
            return {
                "total_records": 0,
                "devices_count": 0,
                "counts_by_device": [],
                "error": str(e),
            }
