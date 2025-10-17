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
        # Para usuarios no-ADMIN, filtrar automáticamente por su tienda asignada
        if self.current_user.rol != "ADMIN":
            user_info = self.get_user_info()
            self.tienda_filtro = user_info.get('tienda_id')
    
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
            elif action == "registrar_ingreso":
                return self._registrar_ingreso(data)
            elif action == "registrar_salida":
                return self._registrar_salida(data)
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
    
    def _registrar_ingreso(self, data: Dict[str, Any]) -> bool:
        """Registra un ingreso de producto"""
        if not self.has_any_role(["ADMIN", "ENCARGADO"]):
            raise PermissionError("Solo administradores y encargados pueden registrar ingresos")
        
        producto_id = data.get('producto_id')
        tienda_id = data.get('tienda_id')
        cantidad = data.get('cantidad')
        nota = data.get('nota')
        
        if not producto_id or not tienda_id or not cantidad:
            raise ValueError("Producto, tienda y cantidad son requeridos")
        
        try:
            cantidad_float = float(cantidad)
            if cantidad_float <= 0:
                raise ValueError("La cantidad debe ser mayor a 0")
        except (ValueError, TypeError):
            raise ValueError("Cantidad inválida")
        
        # Registrar el ingreso usando el servicio de inventario
        self.inventory_models.inventory_service.ingresar(tienda_id, producto_id, cantidad_float, self.current_user.id, nota)
        return True
    
    def _registrar_salida(self, data: Dict[str, Any]) -> bool:
        """Registra una salida de producto"""
        if not self.has_any_role(["ADMIN", "ENCARGADO", "VENDEDOR"]):
            raise PermissionError("No tiene permisos para registrar salidas")
        
        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad')
        nota = data.get('nota')
        
        if not producto_id or not cantidad:
            raise ValueError("Producto y cantidad son requeridos")
        
        try:
            cantidad_float = float(cantidad)
            if cantidad_float <= 0:
                raise ValueError("La cantidad debe ser mayor a 0")
        except (ValueError, TypeError):
            raise ValueError("Cantidad inválida")
        
        # Registrar la salida usando el servicio de inventario (simplificado para tiendas)
        self.inventory_models.registrar_salida_tienda(producto_id, cantidad_float, self.current_user.id, nota)
        return True
    
    def get_productos_for_selector(self) -> Dict[str, Any]:
        """Obtiene los productos disponibles para el selector"""
        productos = self.inventory_models.get_productos()
        return {
            'productos': [
                {
                    'id': p.id,
                    'display': f"{p.id} - {p.sku} - {p.nombre}"
                }
                for p in productos
            ]
        }
    
    def get_productos_con_stock(self, filtro: str = "") -> Dict[str, Any]:
        """Obtiene los productos con stock disponible para selección"""
        return self.inventory_models.get_productos_con_stock(filtro)
    
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
