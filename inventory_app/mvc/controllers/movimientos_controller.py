# ==============================
# File: inventory_app/mvc/controllers/movimientos_controller.py
# ==============================
from __future__ import annotations
from typing import List, Dict, Any, Optional

from .base_controller import BaseController


class MovimientosController(BaseController):
    """Controlador para la gestión de movimientos"""
    
    def __init__(self, inventory_models, user_models, current_user):
        super().__init__(inventory_models, user_models, current_user)
        self.tienda_filtro = None
    
    def get_data(self) -> List[Dict[str, Any]]:
        """Obtiene los movimientos de inventario"""
        movimientos = self.inventory_models.get_movimientos(self.tienda_filtro)
        return [
            {
                'id': m.id,
                'producto': f"{m.producto_sku} - {m.producto_nombre}",
                'tipo': m.tipo,
                'cantidad': m.cantidad,
                'usuario': m.usuario_nombre,
                'tienda': m.tienda_nombre,
                'almacen': m.almacen_nombre,
                'fecha': m.fecha,
                'nota': m.nota or ""
            }
            for m in movimientos
        ]
    
    def handle_action(self, action: str, data: Dict[str, Any]) -> bool:
        """Maneja las acciones de la vista de movimientos"""
        try:
            if action == "set_tienda_filter":
                return self._set_tienda_filter(data)
            elif action == "clear_filters":
                return self._clear_filters()
            else:
                return False
        except Exception as e:
            raise Exception(f"Error en acción {action}: {str(e)}")
    
    def _set_tienda_filter(self, data: Dict[str, Any]) -> bool:
        """Establece el filtro de tienda"""
        tienda_id = data.get('tienda_id')
        self.tienda_filtro = tienda_id
        return True
    
    def _clear_filters(self) -> bool:
        """Limpia todos los filtros"""
        self.tienda_filtro = None
        return True
    
    def get_available_tiendas(self) -> List[Dict[str, Any]]:
        """Obtiene las tiendas disponibles para filtro"""
        tiendas = self.inventory_models.get_tiendas()
        return [
            {
                'id': t.id,
                'nombre': t.nombre
            }
            for t in tiendas
        ]
    
    def get_current_filter(self) -> Optional[int]:
        """Obtiene el filtro actual de tienda"""
        return self.tienda_filtro
