# ==============================
# File: inventory_app/mvc/controllers/productos_controller.py
# ==============================
from __future__ import annotations
from typing import List, Dict, Any, Optional

from .base_controller import BaseController


class ProductosController(BaseController):
    """Controlador para la gestión de productos"""
    
    def __init__(self, inventory_models, user_models, current_user):
        super().__init__(inventory_models, user_models, current_user)
        self.tienda_filtro = None
    
    def get_data(self) -> List[Dict[str, Any]]:
        """Obtiene todos los productos con información completa"""
        productos = self.inventory_models.get_productos()
        
        # Aplicar filtro de tienda si está activo
        if self.tienda_filtro is not None:
            productos = [p for p in productos if p.tienda_id == self.tienda_filtro]
        
        return [
            {
                'id': p.id,
                'sku': p.sku,
                'nombre': p.nombre,
                'descripcion': p.descripcion or "",
                'categoria': p.categoria or "",
                'proveedor': p.proveedor or "",
                'unidad': p.unidad,
                'precio': f"{p.precio_unit:.2f}",
                'stock_minimo': str(p.stock_minimo),
                'tienda': self._get_tienda_name(p.tienda_id),
                'estado': "Activo" if p.activo else "Inactivo"
            }
            for p in productos
        ]
    
    def _get_tienda_name(self, tienda_id: int) -> str:
        """Obtiene el nombre de la tienda por su ID"""
        try:
            tiendas = self.inventory_models.get_tiendas()
            for tienda in tiendas:
                if tienda.id == tienda_id:
                    return tienda.nombre
            return f"Tienda {tienda_id}"
        except Exception as e:
            print(f"Error obteniendo nombre de tienda: {e}")
            return f"Tienda {tienda_id}"
    
    def handle_action(self, action: str, data: Dict[str, Any]) -> bool:
        """Maneja las acciones de la vista de productos"""
        try:
            if action == "create_producto":
                return self._create_producto(data)
            elif action == "edit_producto":
                return self._edit_producto(data)
            elif action == "delete_producto":
                return self._delete_producto(data)
            elif action == "set_tienda_filter":
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
    
    def _create_producto(self, data: Dict[str, Any]) -> bool:
        """Crea un nuevo producto"""
        if not self.validate_user_permission("ADMIN"):
            raise PermissionError("Solo los administradores pueden crear productos")
        
        sku = data.get('sku')
        nombre = data.get('nombre')
        descripcion = data.get('descripcion')
        unidad = data.get('unidad', 'un')
        precio = data.get('precio')
        categoria = data.get('categoria')
        proveedor = data.get('proveedor')
        stock_minimo = data.get('stock_minimo', 0)
        tienda_id = data.get('tienda_id', 1)
        
        if not sku or not nombre or not precio:
            raise ValueError("SKU, nombre y precio son requeridos")
        
        try:
            precio_float = float(precio)
            stock_minimo_int = int(stock_minimo) if stock_minimo else 0
            tienda_id_int = int(tienda_id)
        except (ValueError, TypeError):
            raise ValueError("Precio, stock mínimo o tienda inválido")
        
        self.inventory_models.create_producto(sku, nombre, descripcion, unidad, precio_float, categoria, proveedor, stock_minimo_int, tienda_id_int)
        return True
    
    def _edit_producto(self, data: Dict[str, Any]) -> bool:
        """Edita un producto"""
        if not self.validate_user_permission("ADMIN"):
            raise PermissionError("Solo los administradores pueden editar productos")
        
        producto_id = data.get('id')
        sku = data.get('sku')
        nombre = data.get('nombre')
        descripcion = data.get('descripcion')
        unidad = data.get('unidad')
        precio = data.get('precio')
        categoria = data.get('categoria')
        proveedor = data.get('proveedor')
        stock_minimo = data.get('stock_minimo', 0)
        activo = data.get('activo', True)
        
        if not producto_id or not sku or not nombre or not precio:
            raise ValueError("ID, SKU, nombre y precio son requeridos")
        
        try:
            precio_float = float(precio)
            stock_minimo_int = int(stock_minimo) if stock_minimo else 0
            activo_bool = bool(activo)
        except (ValueError, TypeError):
            raise ValueError("Precio, stock mínimo o estado inválido")
        
        self.inventory_models.update_producto(producto_id, sku, nombre, descripcion, unidad, precio_float, categoria, proveedor, stock_minimo_int, activo_bool)
        return True
    
    def _delete_producto(self, data: Dict[str, Any]) -> bool:
        """Elimina un producto"""
        if not self.validate_user_permission("ADMIN"):
            raise PermissionError("Solo los administradores pueden eliminar productos")
        
        producto_id = data.get('id')
        if not producto_id:
            raise ValueError("ID de producto requerido")
        
        self.inventory_models.delete_producto(producto_id)
        return True
    
    def get_producto_by_id(self, producto_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por ID"""
        productos = self.get_data()
        for producto in productos:
            if producto['id'] == producto_id:
                return producto
        return None
    
    def get_producto_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por SKU"""
        productos = self.get_data()
        for producto in productos:
            if producto['sku'] == sku:
                return producto
        return None
