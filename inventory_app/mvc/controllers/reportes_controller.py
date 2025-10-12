# ==============================
# File: inventory_app/mvc/controllers/reportes_controller.py
# ==============================
from __future__ import annotations
from typing import List, Dict, Any, Optional

from .base_controller import BaseController


class ReportesController(BaseController):
    """Controlador para reportes y alertas"""
    
    def __init__(self, inventory_models, user_models, current_user):
        super().__init__(inventory_models, user_models, current_user)
        self.tienda_filtro = None
    
    def get_data(self) -> List[Dict[str, Any]]:
        """Obtiene el reporte de stock"""
        stock_report = self.inventory_models.get_stock_report(self.tienda_filtro)
        return [
            {
                'tienda': s.tienda,
                'almacen': s.almacen,
                'producto': f"{s.producto_sku} - {s.producto_nombre}",
                'stock': s.cantidad,
                'minimo': s.minimo,
                'estado': s.estado
            }
            for s in stock_report
        ]
    
    def handle_action(self, action: str, data: Dict[str, Any]) -> bool:
        """Maneja las acciones de la vista de reportes"""
        try:
            if action == "set_tienda_filter":
                return self._set_tienda_filter(data)
            elif action == "clear_filters":
                return self._clear_filters()
            elif action == "export_csv":
                return self._export_csv(data)
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
    
    def _export_csv(self, data: Dict[str, Any]) -> bool:
        """Exporta el reporte a CSV"""
        if not self.validate_user_permission("ADMIN"):
            raise PermissionError("Solo los administradores pueden exportar reportes")
        
        filename = data.get('filename')
        if not filename:
            raise ValueError("Nombre de archivo requerido")
        
        # La lógica de exportación se manejará en la vista
        return True
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Obtiene las alertas de stock"""
        alerts = self.inventory_models.get_alerts()
        return [
            {
                'tienda': a.tienda,
                'almacen': a.almacen,
                'producto': f"{a.producto_sku} - {a.producto_nombre}",
                'stock': a.cantidad,
                'minimo': a.minimo,
                'estado': a.estado
            }
            for a in alerts
        ]
    
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
