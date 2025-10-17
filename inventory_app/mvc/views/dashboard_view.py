# ==============================
# File: inventory_app/mvc/views/dashboard_view.py
# ==============================
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional

from .base_view import BaseView
from .tiendas_view import TiendasView
from .empleados_view import EmpleadosView
from .productos_view import ProductosView
from .movimientos_view import MovimientosView
from .reportes_view import ReportesView


class DashboardView:
    """Vista principal del dashboard que coordina todas las vistas"""
    
    def __init__(self, parent_window, controller, on_action):
        self.parent_window = parent_window
        self.controller = controller
        self.on_action = on_action
        
        # Configurar colores
        self.blue_color = "#1e3a8a"
        self.light_blue = "#3b82f6"
        self.white = "#ffffff"
        self.light_gray = "#f3f4f6"
        
        # Vista actual
        self.current_view = None
        self.views = {}
        
        # Configurar la ventana principal
        self._setup_window()
        self._build_dashboard()
    
    def _setup_window(self):
        """Configura la ventana principal"""
        self.parent_window.title("Sistema de Inventario Multitienda")
        self.parent_window.geometry("1200x800")
        
        # Configurar grid
        self.parent_window.columnconfigure(0, weight=1)
        self.parent_window.rowconfigure(1, weight=1)
    
    def _build_dashboard(self):
        """Construye el dashboard completo"""
        # Header azul
        self._build_header()
        
        # Contenido principal
        self._build_main_content()
    
    def _build_header(self):
        """Construye el header azul"""
        # Frame del header azul
        self.header_frame = tk.Frame(self.parent_window, bg=self.blue_color, height=60)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_propagate(False)
        
        # Usuario en la izquierda
        user_info = self.on_action("get_user_info", {})
        user_label = tk.Label(
            self.header_frame, 
            text=f"{user_info.get('username', '').upper()}", 
            bg=self.blue_color, 
            fg=self.white, 
            font=("Arial", 14, "bold")
        )
        user_label.pack(side="left", padx=20, pady=15)
        
        # Título centrado
        title_label = tk.Label(
            self.header_frame, 
            text="Sistema de Inventario Multitienda", 
            bg=self.blue_color, 
            fg=self.white, 
            font=("Arial", 16, "bold")
        )
        title_label.pack(expand=True, pady=15)
    
    def _build_main_content(self):
        """Construye el contenido principal"""
        # Frame principal
        self.main_frame = tk.Frame(self.parent_window, bg=self.light_gray)
        self.main_frame.grid(row=1, column=0, sticky="nsew")
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Contenido de las tabs (debe ir antes de navegación)
        self._build_content_area()
        
        # Navegación con tabs
        self._build_navigation()
    
    def _build_navigation(self):
        """Construye la navegación con tabs"""
        # Frame de navegación
        nav_frame = tk.Frame(self.main_frame, bg=self.white, height=50)
        nav_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        nav_frame.grid_propagate(False)
        nav_frame.columnconfigure(0, weight=1)
        
        # Tabs de navegación
        self.tabs_frame = tk.Frame(nav_frame, bg=self.white)
        self.tabs_frame.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        # Obtener vistas permitidas
        dashboard_data = self.on_action("get_dashboard_data", {})
        allowed_views = dashboard_data.get('allowed_views', [])
        
        # Crear botones de navegación solo para las vistas permitidas
        self.tab_buttons = {}
        tab_names = {
            "empleados": "Empleados",
            "tiendas": "Tiendas", 
            "productos": "Productos",
            "movimientos": "Movimientos",
            "reportes": "Reportes"
        }
        
        for i, view_id in enumerate(allowed_views):
            if view_id in tab_names:
                btn = tk.Button(
                    self.tabs_frame,
                    text=tab_names[view_id],
                    command=lambda v=view_id: self._switch_tab(v),
                    bg=self.white,
                    fg="#374151",
                    font=("Arial", 11),
                    relief="flat",
                    padx=20,
                    pady=8,
                    cursor="hand2"
                )
                btn.grid(row=0, column=i, padx=5)
                self.tab_buttons[view_id] = btn
        
        # Selector de tienda
        store_frame = tk.Frame(nav_frame, bg=self.white)
        store_frame.grid(row=0, column=1, sticky="e", padx=20, pady=10)
        
        tk.Label(store_frame, text="Tienda:", bg=self.white, font=("Arial", 11)).pack(side="left")
        self.store_combo = ttk.Combobox(store_frame, state="readonly", width=20)
        self.store_combo.pack(side="left", padx=5)
        self.store_combo.bind("<<ComboboxSelected>>", lambda e: self._on_store_change())
        
        # Cargar tiendas
        self._load_stores()
        
        # Activar tab inicial
        if allowed_views:
            self._switch_tab(allowed_views[0])
    
    def _build_content_area(self):
        """Construye el área de contenido"""
        # Frame de contenido
        self.content_frame = tk.Frame(self.main_frame, bg=self.white)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
    
    def _switch_tab(self, tab_id: str):
        """Cambia la vista activa"""
        # Actualizar botones de navegación
        for tid, btn in self.tab_buttons.items():
            if tid == tab_id:
                btn.config(bg=self.light_blue, fg=self.white)
                btn.config(relief="solid", bd=0)
            else:
                btn.config(bg=self.white, fg="#374151", relief="flat")
        
        # Cambiar vista en el controlador
        self.on_action("switch_view", {"view_name": tab_id})
        
        # Destruir vista actual si existe
        if self.current_view:
            self.current_view.destroy()
        
        # Crear nueva vista
        self._create_view(tab_id)
    
    def _create_view(self, view_name: str):
        """Crea una vista específica"""
        if view_name == "tiendas":
            self.current_view = TiendasView(self.content_frame, self.controller, self.on_action)
        elif view_name == "empleados":
            self.current_view = EmpleadosView(self.content_frame, self.controller, self.on_action)
        elif view_name == "productos":
            self.current_view = ProductosView(self.content_frame, self.controller, self.on_action)
        elif view_name == "movimientos":
            self.current_view = MovimientosView(self.content_frame, self.controller, self.on_action)
        elif view_name == "reportes":
            self.current_view = ReportesView(self.content_frame, self.controller, self.on_action)
        
        if self.current_view:
            self.current_view.pack()
    
    def _load_stores(self):
        """Carga las tiendas en el selector"""
        try:
            dashboard_data = self.on_action("get_dashboard_data", {})
            tiendas = dashboard_data.get('tiendas', [])
            user_info = self.on_action("get_user_info", {})
            user_rol = user_info.get('rol')
            
            store_values = ["Todos"] + [t['display'] for t in tiendas]
            self.store_combo['values'] = store_values
            
            # Configurar según el rol del usuario
            if user_rol == "ADMIN":
                # ADMIN puede ver todas las tiendas, seleccionar "Todos" por defecto
                self.store_combo.current(0)
                self.store_combo.config(state="readonly")
            else:
                # VENDEDOR y ENCARGADO ven solo su tienda asignada
                user_tienda_id = user_info.get('tienda_id')
                if user_tienda_id:
                    # Buscar la tienda del usuario en la lista
                    for i, tienda in enumerate(tiendas):
                        if tienda['id'] == user_tienda_id:
                            # Seleccionar la tienda del usuario (índice + 1 porque "Todos" está en 0)
                            self.store_combo.current(i + 1)
                            break
                    else:
                        # Si no se encuentra la tienda, seleccionar "Todos"
                        self.store_combo.current(0)
                else:
                    # Si no tiene tienda asignada, seleccionar "Todos"
                    self.store_combo.current(0)
                
                # Deshabilitar el selector para usuarios no-ADMIN
                self.store_combo.config(state="disabled")
                
        except Exception as e:
            print(f"Error al cargar tiendas: {e}")
    
    def _on_store_change(self):
        """Maneja el cambio de tienda seleccionada"""
        try:
            selected_store = self.store_combo.get()
            
            # Si estamos en la vista de movimientos, aplicar filtro
            if hasattr(self, 'current_view') and self.current_view and self.current_view.get_view_name() == "movimientos":
                if selected_store == "Todos":
                    # Limpiar filtro
                    self.on_action("handle_view_action", {
                        "view_name": "movimientos",
                        "action": "clear_filters",
                        "action_data": {}
                    })
                else:
                    # Aplicar filtro por tienda
                    # Extraer ID de la tienda del formato "ID - Nombre"
                    tienda_id = int(selected_store.split(' - ')[0])
                    self.on_action("handle_view_action", {
                        "view_name": "movimientos",
                        "action": "set_tienda_filter",
                        "action_data": {
                            "tienda_id": tienda_id
                        }
                    })
            
            # Si estamos en la vista de reportes, aplicar filtro
            elif hasattr(self, 'current_view') and self.current_view and self.current_view.get_view_name() == "reportes":
                if selected_store == "Todos":
                    # Limpiar filtro de tienda (mantener filtro de estado)
                    self.on_action("handle_view_action", {
                        "view_name": "reportes",
                        "action": "clear_tienda_filter",
                        "action_data": {}
                    })
                else:
                    # Aplicar filtro por tienda
                    # Extraer ID de la tienda del formato "ID - Nombre"
                    tienda_id = int(selected_store.split(' - ')[0])
                    self.on_action("handle_view_action", {
                        "view_name": "reportes",
                        "action": "set_tienda_filter",
                        "action_data": {
                            "tienda_id": tienda_id
                        }
                    })
            
            # Si estamos en la vista de empleados, aplicar filtro
            elif hasattr(self, 'current_view') and self.current_view and self.current_view.get_view_name() == "empleados":
                if selected_store == "Todos":
                    # Limpiar filtro
                    self.on_action("handle_view_action", {
                        "view_name": "empleados",
                        "action": "clear_filters",
                        "action_data": {}
                    })
                else:
                    # Aplicar filtro por tienda
                    # Extraer ID de la tienda del formato "ID - Nombre"
                    tienda_id = int(selected_store.split(' - ')[0])
                    self.on_action("handle_view_action", {
                        "view_name": "empleados",
                        "action": "set_tienda_filter",
                        "action_data": {
                            "tienda_id": tienda_id
                        }
                    })
            
            # Si estamos en la vista de productos, aplicar filtro
            elif hasattr(self, 'current_view') and self.current_view and self.current_view.get_view_name() == "productos":
                if selected_store == "Todos":
                    # Limpiar filtro
                    self.on_action("handle_view_action", {
                        "view_name": "productos",
                        "action": "clear_filters",
                        "action_data": {}
                    })
                else:
                    # Aplicar filtro por tienda
                    # Extraer ID de la tienda del formato "ID - Nombre"
                    tienda_id = int(selected_store.split(' - ')[0])
                    self.on_action("handle_view_action", {
                        "view_name": "productos",
                        "action": "set_tienda_filter",
                        "action_data": {
                            "tienda_id": tienda_id
                        }
                    })
            
            # Actualizar datos de la vista actual
            if self.current_view and hasattr(self.current_view, 'refresh_data'):
                self.current_view.refresh_data()
                
        except Exception as e:
            print(f"Error al cambiar tienda: {e}")
    
    def refresh_current_view(self):
        """Actualiza la vista actual"""
        if self.current_view and hasattr(self.current_view, 'refresh_data'):
            self.current_view.refresh_data()
    
    def destroy(self):
        """Destruye el dashboard"""
        if self.current_view:
            self.current_view.destroy()
        self.main_frame.destroy()
        self.header_frame.destroy()
