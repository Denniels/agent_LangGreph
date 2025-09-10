"""
Modelos de Datos para IoT
========================

Modelos de datos que representan las entidades principales del sistema IoT.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class SensorData:
    """Modelo para datos de sensores"""
    device_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime
    location: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a diccionario"""
        return {
            'device_id': self.device_id,
            'sensor_type': self.sensor_type,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'location': self.location
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SensorData':
        """Crea una instancia desde un diccionario"""
        return cls(
            device_id=data['device_id'],
            sensor_type=data['sensor_type'],
            value=float(data['value']),
            unit=data['unit'],
            timestamp=data['timestamp'] if isinstance(data['timestamp'], datetime) 
                     else datetime.fromisoformat(data['timestamp']),
            location=data.get('location')
        )


@dataclass
class Device:
    """Modelo para dispositivos IoT"""
    device_id: str
    device_name: str
    device_type: str
    location: str
    status: str
    last_seen: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a diccionario"""
        return {
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'location': self.location,
            'status': self.status,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Device':
        """Crea una instancia desde un diccionario"""
        return cls(
            device_id=data['device_id'],
            device_name=data['device_name'],
            device_type=data['device_type'],
            location=data['location'],
            status=data['status'],
            last_seen=data['last_seen'] if isinstance(data.get('last_seen'), datetime)
                     else datetime.fromisoformat(data['last_seen']) if data.get('last_seen') else None
        )


@dataclass
class Alert:
    """Modelo para alertas del sistema"""
    alert_id: Optional[str]
    device_id: str
    alert_type: str
    message: str
    severity: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    status: str = 'active'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a diccionario"""
        return {
            'alert_id': self.alert_id,
            'device_id': self.device_id,
            'alert_type': self.alert_type,
            'message': self.message,
            'severity': self.severity,
            'created_at': self.created_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Alert':
        """Crea una instancia desde un diccionario"""
        return cls(
            alert_id=data.get('alert_id'),
            device_id=data['device_id'],
            alert_type=data['alert_type'],
            message=data['message'],
            severity=data['severity'],
            created_at=data['created_at'] if isinstance(data['created_at'], datetime)
                      else datetime.fromisoformat(data['created_at']),
            resolved_at=data['resolved_at'] if isinstance(data.get('resolved_at'), datetime)
                       else datetime.fromisoformat(data['resolved_at']) if data.get('resolved_at') else None,
            status=data.get('status', 'active')
        )
