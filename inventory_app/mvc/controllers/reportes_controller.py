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
        self.status_filtro = "todos"
        self.search_filtro = ""
        # Para usuarios no-ADMIN, filtrar automáticamente por su tienda asignada
        if self.current_user.rol != "ADMIN":
            user_info = self.get_user_info()
            self.tienda_filtro = user_info.get('tienda_id')
    
    def get_data(self) -> List[Dict[str, Any]]:
        """Obtiene el reporte de stock"""
        stock_report = self.inventory_models.get_stock_report(self.tienda_filtro)
        
        # Filtrar por estado si es necesario
        filtered_report = []
        for s in stock_report:
            # Aplicar filtro de estado
            estado_match = False
            if self.status_filtro == "todos":
                estado_match = True
            elif self.status_filtro == "ok" and s.estado == "OK":
                estado_match = True
            elif self.status_filtro == "bajo_stock" and s.estado == "BAJO MINIMO":
                estado_match = True
            elif self.status_filtro == "sin_stock" and s.estado == "SIN STOCK":
                estado_match = True
            
            # Aplicar filtro de búsqueda de producto
            search_match = True
            if self.search_filtro:
                search_lower = self.search_filtro.lower()
                sku_match = search_lower in s.producto_sku.lower()
                nombre_match = search_lower in s.producto_nombre.lower()
                search_match = sku_match or nombre_match
            
            # Solo agregar si pasa ambos filtros
            if estado_match and search_match:
                filtered_report.append(s)
        
        return [
            {
                'id': s.producto_sku,  # Usar SKU como ID
                'producto': s.producto_nombre,
                'tienda': s.tienda,
                'estado': s.estado,
                'stock': s.cantidad
            }
            for s in filtered_report
        ]
    
    def handle_action(self, action: str, data: Dict[str, Any]) -> bool:
        """Maneja las acciones de la vista de reportes"""
        try:
            if action == "set_tienda_filter":
                return self._set_tienda_filter(data)
            elif action == "set_status_filter":
                return self._set_status_filter(data)
            elif action == "set_search_filter":
                return self._set_search_filter(data)
            elif action == "clear_tienda_filter":
                return self._clear_tienda_filter()
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
    
    def _set_status_filter(self, data: Dict[str, Any]) -> bool:
        """Establece el filtro de estado"""
        status_filter = data.get('status_filter')
        if status_filter in ["todos", "ok", "bajo_stock", "sin_stock"]:
            self.status_filtro = status_filter
            return True
        return False
    
    def _set_search_filter(self, data: Dict[str, Any]) -> bool:
        """Establece el filtro de búsqueda de productos"""
        search_text = data.get('search_text', '')
        self.search_filtro = search_text
        return True
    
    def _clear_tienda_filter(self) -> bool:
        """Limpia solo el filtro de tienda (mantiene el filtro de estado)"""
        self.tienda_filtro = None
        return True
    
    def _clear_filters(self) -> bool:
        """Limpia todos los filtros"""
        self.tienda_filtro = None
        self.status_filtro = "todos"
        self.search_filtro = ""
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
