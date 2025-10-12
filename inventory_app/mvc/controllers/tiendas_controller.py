# ==============================
# File: inventory_app/mvc/controllers/tiendas_controller.py
# ==============================
from __future__ import annotations
from typing import List, Dict, Any, Optional

from .base_controller import BaseController


class TiendasController(BaseController):
    """Controlador para la gestión de tiendas"""
    
    def get_data(self) -> List[Dict[str, Any]]:
        """Obtiene todas las tiendas"""
        tiendas = self.inventory_models.get_tiendas()
        return [
            {
                'id': t.id,
                'nombre': t.nombre,
                'direccion': t.direccion or ''
            }
            for t in tiendas
        ]
    
    def handle_action(self, action: str, data: Dict[str, Any]) -> bool:
        """Maneja las acciones de la vista de tiendas"""
        try:
            if action == "create_tienda":
                return self._create_tienda(data)
            elif action == "delete_tienda":
                return self._delete_tienda(data)
            else:
                return False
        except Exception as e:
            raise Exception(f"Error en acción {action}: {str(e)}")
    
    def _create_tienda(self, data: Dict[str, Any]) -> bool:
        """Crea una nueva tienda"""
        if not self.validate_user_permission("ADMIN"):
            raise PermissionError("Solo los administradores pueden crear tiendas")
        
        nombre = data.get('nombre')
        if not nombre:
            raise ValueError("El nombre de la tienda es requerido")
        
        direccion = data.get('direccion', '')
        self.inventory_models.create_tienda(nombre, direccion)
        return True
    
    def _delete_tienda(self, data: Dict[str, Any]) -> bool:
        """Elimina una tienda"""
        if not self.validate_user_permission("ADMIN"):
            raise PermissionError("Solo los administradores pueden eliminar tiendas")
        
        tienda_id = data.get('id')
        if not tienda_id:
            raise ValueError("ID de tienda requerido")
        
        self.inventory_models.delete_tienda(tienda_id)
        return True
    
    def get_tienda_by_id(self, tienda_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una tienda por ID"""
        tiendas = self.get_data()
        for tienda in tiendas:
            if tienda['id'] == tienda_id:
                return tienda
        return None
