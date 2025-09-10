"""
Conector de Base de Datos PostgreSQL
===================================

Este módulo maneja todas las conexiones y operaciones con la base de datos PostgreSQL.
Utiliza variables de entorno para las credenciales de conexión.
"""

import os
import asyncio
import asyncpg
from typing import Optional, List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from modules.utils.logger import setup_logger

# Cargar variables de entorno
load_dotenv()

logger = setup_logger(__name__)


class DatabaseConnector:
    """
    Conector para base de datos PostgreSQL con soporte asíncrono.
    """
    
    def __init__(self):
        """Inicializa el conector con las credenciales del archivo .env"""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 5432))
        self.database = os.getenv('DB_NAME', 'iot_db')
        self.user = os.getenv('DB_USER', 'iot_user')
        self.password = os.getenv('DB_PASSWORD')
        self.pool: Optional[asyncpg.Pool] = None
        
        if not self.password:
            raise ValueError("DB_PASSWORD debe estar definido en el archivo .env")
    
    async def connect(self) -> None:
        """
        Establece la conexión con la base de datos usando un pool de conexiones.
        """
        try:
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info(f"Conexión establecida con la base de datos {self.database}")
        except Exception as e:
            logger.error(f"Error al conectar con la base de datos: {e}")
            raise
    
    async def disconnect(self) -> None:
        """
        Cierra el pool de conexiones.
        """
        if self.pool:
            await self.pool.close()
            logger.info("Conexión con la base de datos cerrada")
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SELECT y retorna los resultados.
        
        Args:
            query (str): Consulta SQL a ejecutar
            *args: Parámetros para la consulta
            
        Returns:
            List[Dict[str, Any]]: Lista de resultados como diccionarios
        """
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as connection:
                rows = await connection.fetch(query, *args)
                # Convertir a lista de diccionarios
                result = [dict(row) for row in rows]
                logger.debug(f"Consulta ejecutada: {query[:100]}... | Resultados: {len(result)}")
                return result
        except Exception as e:
            logger.error(f"Error ejecutando consulta: {e}")
            raise
    
    async def execute_command(self, command: str, *args) -> str:
        """
        Ejecuta un comando INSERT, UPDATE o DELETE.
        
        Args:
            command (str): Comando SQL a ejecutar
            *args: Parámetros para el comando
            
        Returns:
            str: Resultado del comando
        """
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as connection:
                result = await connection.execute(command, *args)
                logger.debug(f"Comando ejecutado: {command[:100]}... | Resultado: {result}")
                return result
        except Exception as e:
            logger.error(f"Error ejecutando comando: {e}")
            raise
    
    async def get_sensor_data(self, device_id: Optional[str] = None, 
                            limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene datos de sensores de la base de datos.
        
        Args:
            device_id (Optional[str]): ID del dispositivo específico
            limit (int): Límite de resultados
            
        Returns:
            List[Dict[str, Any]]: Lista de datos de sensores
        """
        base_query = """
            SELECT 
                id,
                device_id,
                sensor_type,
                value,
                unit,
                timestamp,
                created_at
            FROM sensor_data
        """
        
        if device_id:
            query = base_query + " WHERE device_id = $1 ORDER BY timestamp DESC LIMIT $2"
            return await self.execute_query(query, device_id, limit)
        else:
            query = base_query + " ORDER BY timestamp DESC LIMIT $1"
            return await self.execute_query(query, limit)
    
    async def get_active_devices(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de dispositivos activos.
        
        Returns:
            List[Dict[str, Any]]: Lista de dispositivos activos
        """
        query = """
            SELECT 
                device_id,
                device_type,
                name,
                status,
                last_seen,
                ip_address,
                port,
                created_at,
                updated_at
            FROM devices 
            WHERE status = 'online'
            ORDER BY last_seen DESC
        """
        return await self.execute_query(query)
    
    async def get_alerts(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Obtiene eventos del sistema (usando system_events como alertas).
        
        Args:
            active_only (bool): Si True, solo eventos recientes (últimas 24 horas)
            
        Returns:
            List[Dict[str, Any]]: Lista de eventos/alertas
        """
        base_query = """
            SELECT 
                id,
                event_type,
                device_id,
                message,
                metadata,
                timestamp
            FROM system_events
        """
        
        if active_only:
            # Eventos de las últimas 24 horas
            query = base_query + " WHERE timestamp >= NOW() - INTERVAL '24 hours' ORDER BY timestamp DESC LIMIT 100"
        else:
            query = base_query + " ORDER BY timestamp DESC LIMIT 100"
        
        return await self.execute_query(query)
    
    async def create_alert(self, device_id: str, event_type: str, 
                          message: str, metadata: Optional[Dict] = None) -> bool:
        """
        Crea un nuevo evento/alerta en el sistema.
        
        Args:
            device_id (str): ID del dispositivo
            event_type (str): Tipo de evento
            message (str): Mensaje del evento
            metadata (Optional[Dict]): Metadatos adicionales
            
        Returns:
            bool: True si se creó correctamente
        """
        command = """
            INSERT INTO system_events (event_type, device_id, message, metadata, timestamp)
            VALUES ($1, $2, $3, $4, NOW())
        """
        
        try:
            import json
            metadata_json = json.dumps(metadata) if metadata else None
            await self.execute_command(
                command, 
                event_type, 
                device_id, 
                message, 
                metadata_json
            )
            logger.info(f"Evento creado para dispositivo {device_id}: {message}")
            return True
        except Exception as e:
            logger.error(f"Error creando evento: {e}")
            return False
    
    async def health_check(self) -> bool:
        """
        Verifica el estado de la conexión con la base de datos.
        
        Returns:
            bool: True si la conexión está funcionando
        """
        try:
            result = await self.execute_query("SELECT 1 as health_check")
            return len(result) == 1 and result[0]['health_check'] == 1
        except Exception as e:
            logger.error(f"Health check falló: {e}")
            return False


# Instancia global del conector
db_connector = DatabaseConnector()


async def get_db() -> DatabaseConnector:
    """
    Función helper para obtener la instancia del conector de base de datos.
    
    Returns:
        DatabaseConnector: Instancia del conector
    """
    if not db_connector.pool:
        await db_connector.connect()
    return db_connector
