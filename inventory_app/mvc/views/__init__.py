# ==============================
# File: inventory_app/mvc/views/__init__.py
# ==============================
from .base_view import BaseView
from .tiendas_view import TiendasView
from .empleados_view import EmpleadosView
from .productos_view import ProductosView
from .movimientos_view import MovimientosView
from .reportes_view import ReportesView
from .dashboard_view import DashboardView

__all__ = [
    'BaseView',
    'TiendasView', 
    'EmpleadosView',
    'ProductosView',
    'MovimientosView',
    'ReportesView',
    'DashboardView'
]
