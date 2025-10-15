# ==============================
# File: inventory_app/mvc/views/reportes_view.py
# ==============================
from __future__ import annotations
from typing import List, Dict, Any
import tkinter as tk
from .base_view import BaseView


class ReportesView(BaseView):
    """Vista para reportes y alertas del sistema"""
    
    def _setup_view(self):
        """Configura la vista de reportes"""
        # Crear frame para filtros
        filter_frame = tk.Frame(self.action_frame, bg=self.white)
        filter_frame.pack(side="left", padx=5)
        
        # Label para filtros
        filter_label = tk.Label(
            filter_frame, 
            text="Estado:", 
            bg=self.white, 
            font=("Arial", 11, "bold")
        )
        filter_label.pack(side="left", padx=(0, 10))
        
        # Variable para radio buttons
        self.status_filter_var = tk.StringVar(value="todos")
        
        # Radio buttons para filtros de estado
        radio_todos = tk.Radiobutton(
            filter_frame,
            text="Todos",
            variable=self.status_filter_var,
            value="todos",
            command=self._on_status_filter_change,
            bg=self.white,
            font=("Arial", 10)
        )
        radio_todos.pack(side="left", padx=5)
        
        radio_ok = tk.Radiobutton(
            filter_frame,
            text="OK",
            variable=self.status_filter_var,
            value="ok",
            command=self._on_status_filter_change,
            bg=self.white,
            font=("Arial", 10)
        )
        radio_ok.pack(side="left", padx=5)
        
        radio_bajo = tk.Radiobutton(
            filter_frame,
            text="Bajo mínimo",
            variable=self.status_filter_var,
            value="bajo_stock",
            command=self._on_status_filter_change,
            bg=self.white,
            font=("Arial", 10)
        )
        radio_bajo.pack(side="left", padx=5)
        
        radio_sin = tk.Radiobutton(
            filter_frame,
            text="Sin stock",
            variable=self.status_filter_var,
            value="sin_stock",
            command=self._on_status_filter_change,
            bg=self.white,
            font=("Arial", 10)
        )
        radio_sin.pack(side="left", padx=5)
        
        # Configurar tabla
        columns = ["ID", "Producto", "Tienda", "Estado", "Stock"]
        widths = [80, 200, 120, 100, 80]
        self.setup_table_columns(columns, widths)
        
        # Cargar datos iniciales
        self.refresh_data()
    
    def get_view_name(self) -> str:
        """Retorna el nombre de la vista"""
        return "reportes"
    
    def _on_status_filter_change(self):
        """Maneja el cambio en el filtro de estado"""
        try:
            status_filter = self.status_filter_var.get()
            success = self.on_action("handle_view_action", {
                "view_name": "reportes",
                "action": "set_status_filter",
                "action_data": {
                    "status_filter": status_filter
                }
            })
            
            if success:
                self.refresh_data()
        except Exception as e:
            self.show_error("Error", f"Error al cambiar filtro: {str(e)}")
    
