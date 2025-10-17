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
        # Crear frame para filtros de estado
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
        
        # Separador
        separator = tk.Frame(self.action_frame, bg='#D5D5D5', width=2)
        separator.pack(side="left", fill="y", padx=15, pady=5)
        
        # Frame para búsqueda de productos
        search_frame = tk.Frame(self.action_frame, bg=self.white)
        search_frame.pack(side="left", padx=5)
        
        search_label = tk.Label(
            search_frame,
            text="Buscar producto:",
            bg=self.white,
            font=("Arial", 11, "bold")
        )
        search_label.pack(side="left", padx=(0, 10))
        
        # Variable y campo de búsqueda
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._on_search_change())
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 10),
            relief='solid',
            bd=1,
            width=25,
            highlightthickness=1,
            highlightcolor='#2E86C1',
            highlightbackground='#D5D5D5'
        )
        search_entry.pack(side="left", ipady=4)
        
        # Botón limpiar búsqueda
        btn_clear_search = tk.Button(
            search_frame,
            text="✕",
            command=self._clear_search,
            bg='#95A5A6',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            cursor='hand2',
            bd=0,
            padx=8,
            pady=4
        )
        btn_clear_search.pack(side="left", padx=(5, 0))
        
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
    
    def _on_search_change(self):
        """Maneja el cambio en el campo de búsqueda"""
        try:
            search_text = self.search_var.get().strip()
            success = self.on_action("handle_view_action", {
                "view_name": "reportes",
                "action": "set_search_filter",
                "action_data": {
                    "search_text": search_text
                }
            })
            
            if success:
                self.refresh_data()
        except Exception as e:
            self.show_error("Error", f"Error al buscar: {str(e)}")
    
    def _clear_search(self):
        """Limpia el campo de búsqueda"""
        self.search_var.set("")
    
