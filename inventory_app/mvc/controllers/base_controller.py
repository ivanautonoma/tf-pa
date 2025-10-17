# ==============================
# File: inventory_app/mvc/controllers/base_controller.py
# ==============================
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from ..models import InventoryModels, UserModels
from ...domain.models import Usuario


class BaseController(ABC):
    """Controlador base para todos los controladores MVC"""
    
    def __init__(self, inventory_models: InventoryModels, user_models: UserModels, current_user: Usuario):
        self.inventory_models = inventory_models
        self.user_models = user_models
        self.current_user = current_user
    
    @abstractmethod
    def get_data(self) -> List[Dict[str, Any]]:
        """Obtiene los datos para la vista"""
        pass
    
    @abstractmethod
    def handle_action(self, action: str, data: Dict[str, Any]) -> bool:
        """Maneja las acciones de la vista"""
        pass
    
    def refresh_data(self) -> List[Dict[str, Any]]:
        """Actualiza los datos"""
        return self.get_data()
    
    def validate_user_permission(self, required_role: str) -> bool:
        """Valida si el usuario tiene el rol requerido"""
        return self.current_user.rol == required_role
    
    def has_any_role(self, roles: List[str]) -> bool:
        """Valida si el usuario tiene alguno de los roles especificados"""
        return self.current_user.rol in roles
    
    def get_user_info(self) -> Dict[str, Any]:
        """Obtiene información del usuario actual"""
        # Obtener información del empleado asociado al usuario
        empleado = self.inventory_models.get_empleado_by_user_id(self.current_user.id)
        tienda_id = empleado.tienda_id if empleado else None
        
        return {
            'id': self.current_user.id,
            'username': self.current_user.username,
            'rol': self.current_user.rol,
            'activo': self.current_user.activo,
            'tienda_id': tienda_id
        }
