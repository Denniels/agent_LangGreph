"""
Configuración de la Aplicación
==============================

Manejo centralizado de la configuración usando variables de entorno.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class Config:
    """
    Clase para manejar la configuración de la aplicación.
    """
    
    # Base de datos
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '5432'))
    DB_NAME: str = os.getenv('DB_NAME', 'iot_db')
    DB_USER: str = os.getenv('DB_USER', 'iot_user')
    DB_PASSWORD: Optional[str] = os.getenv('DB_PASSWORD')
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # Aplicación
    APP_NAME: str = os.getenv('APP_NAME', 'Agente IoT')
    APP_VERSION: str = os.getenv('APP_VERSION', '1.0.0')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Streamlit
    STREAMLIT_PORT: int = int(os.getenv('STREAMLIT_PORT', '8501'))
    STREAMLIT_HOST: str = os.getenv('STREAMLIT_HOST', 'localhost')
    
    @classmethod
    def validate(cls) -> bool:
        """
        Valida que las configuraciones requeridas estén presentes.
        
        Returns:
            bool: True si todas las configuraciones requeridas están presentes
        """
        required_vars = [
            'DB_PASSWORD',
            'OPENAI_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Variables de entorno faltantes: {', '.join(missing_vars)}")
            return False
        
        return True
    
    @classmethod
    def get_db_url(cls) -> str:
        """
        Construye la URL de conexión a la base de datos.
        
        Returns:
            str: URL de conexión PostgreSQL
        """
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def get_async_db_url(cls) -> str:
        """
        Construye la URL de conexión asíncrona a la base de datos.
        
        Returns:
            str: URL de conexión PostgreSQL asíncrona
        """
        return f"postgresql+asyncpg://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
