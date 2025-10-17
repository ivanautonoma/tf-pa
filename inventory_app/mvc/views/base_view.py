# ==============================
# File: inventory_app/mvc/views/base_view.py
# ==============================
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, List, Dict, Any, Callable
from abc import ABC, abstractmethod


class BaseView(ABC):
    """Vista base para todas las vistas del dashboard"""
    
    def __init__(self, parent_frame: tk.Frame, controller, on_action: Callable):
        self.parent_frame = parent_frame
        self.controller = controller
        self.on_action = on_action  # Callback para comunicarse con el controlador
        
        # Colores del tema
        self.blue_color = "#1e3a8a"
        self.light_blue = "#3b82f6"
        self.white = "#ffffff"
        self.light_gray = "#f3f4f6"
        self.red_color = "#dc2626"
        self.orange_color = "#f59e0b"
        
        # Frame principal de la vista
        self.main_frame = tk.Frame(parent_frame, bg=self.white)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Frame para botones de acción
        self.action_frame = tk.Frame(self.main_frame, bg=self.white)
        self.action_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        # Frame para la tabla de datos
        self.data_frame = tk.Frame(self.main_frame, bg=self.white)
        self.data_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.data_frame.columnconfigure(0, weight=1)
        self.data_frame.rowconfigure(0, weight=1)
        
        # Crear tabla
        self._create_table()
        
        # Inicializar la vista específica
        self._setup_view()
    
    def _create_table(self):
        """Crea la tabla con scrollbar"""
        # Frame para la tabla con borde
        table_container = tk.Frame(self.data_frame, bg="#e5e7eb", relief="solid", bd=1)
        table_container.grid(row=0, column=0, sticky="nsew")
        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(0, weight=1)
        
        # Treeview
        self.tree = ttk.Treeview(table_container, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
    
    def create_button(self, text: str, command, bg_color: str = None, **kwargs) -> tk.Button:
        """Crea un botón con el estilo estándar"""
        bg_color = bg_color or self.blue_color
        return tk.Button(
            self.action_frame,
            text=text,
            command=command,
            bg=bg_color,
            fg=self.white,
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            cursor="hand2",
            **kwargs
        )
    
    def setup_table_columns(self, columns: List[str], widths: List[int] = None):
        """Configura las columnas de la tabla"""
        if widths is None:
            widths = [150] * len(columns)
        
        self.tree["columns"] = columns
        self.tree["show"] = "headings"
        
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
    
    def clear_table(self):
        """Limpia todos los elementos de la tabla"""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def populate_table(self, data: List[Dict[str, Any]]):
        """Pobla la tabla con datos"""
        self.clear_table()
        for row_data in data:
            values = []
            for col in self.tree["columns"]:
                # Mapear nombres de columnas a claves de datos
                if col.lower() == "id":
                    values.append(str(row_data.get('id', "")))
                elif col.lower() == "usuario":
                    values.append(str(row_data.get('username', "")))
                elif col.lower() == "nombre":
                    values.append(str(row_data.get('nombre', "")))
                elif col.lower() == "dirección" or col.lower() == "direccion":
                    values.append(str(row_data.get('direccion', "")))
                elif col.lower() == "teléfono" or col.lower() == "telefono":
                    values.append(str(row_data.get('telefono', "")))
                elif col.lower() == "email":
                    values.append(str(row_data.get('email', "")))
                elif col.lower() == "responsable":
                    values.append(str(row_data.get('responsable', "")))
                elif col.lower() == "nombres":
                    values.append(str(row_data.get('nombres', "")))
                elif col.lower() == "apellidos":
                    values.append(str(row_data.get('apellidos', "")))
                elif col.lower() == "dni":
                    values.append(str(row_data.get('dni', "")))
                elif col.lower() == "jornada":
                    values.append(str(row_data.get('jornada', "")))
                elif col.lower() == "tienda":
                    values.append(str(row_data.get('tienda', "")))
                elif col.lower() == "rol":
                    values.append(str(row_data.get('rol', "")))
                elif col.lower() == "estado":
                    values.append(str(row_data.get('estado', "")))
                elif col.lower() == "sku":
                    values.append(str(row_data.get('sku', "")))
                elif col.lower() == "descripción":
                    values.append(str(row_data.get('descripcion', "")))
                elif col.lower() == "categoría":
                    values.append(str(row_data.get('categoria', "")))
                elif col.lower() == "proveedor":
                    values.append(str(row_data.get('proveedor', "")))
                elif col.lower() == "unidad":
                    values.append(str(row_data.get('unidad', "")))
                elif col.lower() == "precio":
                    values.append(str(row_data.get('precio', "")))
                elif col.lower() == "stock mín.":
                    values.append(str(row_data.get('stock_minimo', "")))
                elif col.lower() == "stock actual":
                    values.append(str(row_data.get('stock_actual', "")))
                elif col.lower() == "precio unit.":
                    values.append(str(row_data.get('precio_unit', "")))
                elif col.lower() == "producto":
                    values.append(str(row_data.get('producto', "")))
                elif col.lower() == "stock":
                    values.append(str(row_data.get('stock', "")))
                elif col.lower() == "almacén":
                    values.append(str(row_data.get('almacen', "")))
                elif col.lower() == "mínimo":
                    values.append(str(row_data.get('minimo', "")))
                elif col.lower() == "estado":
                    values.append(str(row_data.get('estado', "")))
                else:
                    values.append(str(row_data.get(col.lower(), "")))
            self.tree.insert("", "end", values=values)
    
    def get_selected_item(self) -> Optional[Dict[str, Any]]:
        """Obtiene el elemento seleccionado en la tabla"""
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = self.tree.item(selection[0])
        columns = self.tree["columns"]
        values = item['values']
        
        return {
            'values': values,
            'item_id': selection[0],
            'data': dict(zip([col.lower() for col in columns], values))
        }
    
    def show_info(self, title: str, message: str):
        """Muestra un mensaje de información"""
        messagebox.showinfo(title, message)
    
    def show_error(self, title: str, message: str):
        """Muestra un mensaje de error"""
        messagebox.showerror(title, message)
    
    def show_warning(self, title: str, message: str):
        """Muestra un mensaje de advertencia"""
        messagebox.showwarning(title, message)
    
    def ask_yes_no(self, title: str, message: str) -> bool:
        """Pregunta sí/no al usuario"""
        return messagebox.askyesno(title, message)
    
    def ask_string(self, title: str, prompt: str, initial_value: str = "") -> Optional[str]:
        """Pide un string al usuario"""
        return simpledialog.askstring(title, prompt, initialvalue=initial_value)
    
    def ask_float(self, title: str, prompt: str, initial_value: str = "") -> Optional[float]:
        """Pide un float al usuario"""
        try:
            value = simpledialog.askstring(title, prompt, initialvalue=initial_value)
            return float(value) if value else None
        except (TypeError, ValueError):
            return None
    
    def pack(self):
        """Muestra la vista"""
        self.main_frame.pack(fill="both", expand=True)
    
    def destroy(self):
        """Destruye la vista"""
        self.main_frame.destroy()
    
    def refresh_data(self):
        """Actualiza los datos de la vista"""
        try:
            data = self.on_action("get_view_data", {"view_name": self.get_view_name()})
            if data and 'data' in data:
                self.populate_table(data['data'])
        except Exception as e:
            self.show_error("Error", f"Error al actualizar datos: {str(e)}")
    
    @abstractmethod
    def _setup_view(self):
        """Configura la vista específica. Debe ser implementado por las subclases"""
        pass
    
    @abstractmethod
    def get_view_name(self) -> str:
        """Retorna el nombre de la vista. Debe ser implementado por las subclases"""
        pass
