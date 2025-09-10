"""
Sistema de Logging
==================

Configuración del sistema de logging para toda la aplicación.
"""

import sys
from loguru import logger
from typing import Optional


def setup_logger(name: Optional[str] = None, level: str = "INFO") -> object:
    """
    Configura el sistema de logging con loguru.
    
    Args:
        name (Optional[str]): Nombre del logger
        level (str): Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        object: Logger configurado
    """
    # Remover configuración por defecto
    logger.remove()
    
    # Configurar formato
    format_string = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    # Agregar handler para consola
    logger.add(
        sys.stderr,
        format=format_string,
        level=level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # Agregar handler para archivo
    logger.add(
        "logs/app.log",
        format=format_string,
        level=level,
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    if name:
        return logger.bind(name=name)
    
    return logger
