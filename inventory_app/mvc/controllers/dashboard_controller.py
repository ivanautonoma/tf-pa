# ==============================
# File: inventory_app/mvc/controllers/dashboard_controller.py
# ==============================
from __future__ import annotations
from typing import Dict, Any, List, Optional

from .base_controller import BaseController
from .tiendas_controller import TiendasController
from .empleados_controller import EmpleadosController
from .productos_controller import ProductosController
from .movimientos_controller import MovimientosController
from .reportes_controller import ReportesController


class DashboardController(BaseController):
    """Controlador principal del dashboard"""
    
    def __init__(self, inventory_models, user_models, current_user):
        super().__init__(inventory_models, user_models, current_user)
        
        # Inicializar controladores específicos
        self.tiendas_controller = TiendasController(inventory_models, user_models, current_user)
        self.empleados_controller = EmpleadosController(inventory_models, user_models, current_user)
        self.productos_controller = ProductosController(inventory_models, user_models, current_user)
        self.movimientos_controller = MovimientosController(inventory_models, user_models, current_user)
        self.reportes_controller = ReportesController(inventory_models, user_models, current_user)
        
        # Configuración del dashboard
        self.current_view = "tiendas"
        self.allowed_views = self._get_allowed_views()
    
    def get_data(self) -> Dict[str, Any]:
        """Obtiene los datos del dashboard"""
        return {
            'user_info': self.get_user_info(),
            'allowed_views': self.allowed_views,
            'current_view': self.current_view,
            'tiendas': self._get_tiendas_for_selector()
        }
    
    def handle_action(self, action: str, data: Dict[str, Any]) -> bool:
        """Maneja las acciones del dashboard"""
        try:
            if action == "switch_view":
                return self._switch_view(data)
            elif action == "get_view_data":
                return self._get_view_data(data)
            elif action == "handle_view_action":
                return self._handle_view_action(data)
            else:
                return False
        except Exception as e:
            raise Exception(f"Error en acción {action}: {str(e)}")
    
    def _get_allowed_views(self) -> List[str]:
        """Obtiene las vistas permitidas según el rol del usuario"""
        if self.current_user.rol == "ADMIN":
            return ["tiendas", "empleados", "productos", "movimientos", "reportes"]
        elif self.current_user.rol == "OPERADOR":
            return ["productos", "movimientos", "reportes"]
        else:
            return []
    
    def _get_tiendas_for_selector(self) -> List[Dict[str, Any]]:
        """Obtiene las tiendas para el selector"""
        tiendas = self.inventory_models.get_tiendas()
        return [
            {
                'id': t.id,
                'nombre': t.nombre,
                'display': f"{t.id} - {t.nombre}"
            }
            for t in tiendas
        ]
    
    def _switch_view(self, data: Dict[str, Any]) -> bool:
        """Cambia la vista actual"""
        view_name = data.get('view_name')
        if view_name in self.allowed_views:
            self.current_view = view_name
            return True
        return False
    
    def _get_view_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene los datos de una vista específica"""
        view_name = data.get('view_name', self.current_view)
        
        if view_name == "tiendas":
            return {'data': self.tiendas_controller.get_data()}
        elif view_name == "empleados":
            return {'data': self.empleados_controller.get_data()}
        elif view_name == "productos":
            return {'data': self.productos_controller.get_data()}
        elif view_name == "movimientos":
            return {'data': self.movimientos_controller.get_data()}
        elif view_name == "reportes":
            return {'data': self.reportes_controller.get_data()}
        else:
            return {'data': []}
    
    def _handle_view_action(self, data: Dict[str, Any]) -> bool:
        """Maneja una acción de una vista específica"""
        view_name = data.get('view_name', self.current_view)
        action = data.get('action')
        action_data = data.get('action_data', {})
        
        if view_name == "tiendas":
            return self.tiendas_controller.handle_action(action, action_data)
        elif view_name == "empleados":
            return self.empleados_controller.handle_action(action, action_data)
        elif view_name == "productos":
            return self.productos_controller.handle_action(action, action_data)
        elif view_name == "movimientos":
            return self.movimientos_controller.handle_action(action, action_data)
        elif view_name == "reportes":
            return self.reportes_controller.handle_action(action, action_data)
        else:
            return False
    
    def get_controller_for_view(self, view_name: str):
        """Obtiene el controlador para una vista específica"""
        if view_name == "tiendas":
            return self.tiendas_controller
        elif view_name == "empleados":
            return self.empleados_controller
        elif view_name == "productos":
            return self.productos_controller
        elif view_name == "movimientos":
            return self.movimientos_controller
        elif view_name == "reportes":
            return self.reportes_controller
        else:
            return None
    
    def refresh_current_view(self) -> Dict[str, Any]:
        """Actualiza la vista actual"""
        return self._get_view_data({'view_name': self.current_view})
