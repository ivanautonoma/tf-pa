# ==============================
# File: inventory_app/mvc/views/movimientos_view.py
# ==============================
from __future__ import annotations
from typing import List, Dict, Any
from .base_view import BaseView


class MovimientosView(BaseView):
    """Vista para mostrar los movimientos de inventario"""
    
    def _setup_view(self):
        """Configura la vista de movimientos"""
        # Botones de acción
        btn_refrescar = self.create_button("Refrescar", self.refresh_data)
        btn_refrescar.pack(side="left", padx=5)
        
        btn_filtrar = self.create_button("Filtrar por Tienda", self._filtrar_por_tienda, self.light_blue)
        btn_filtrar.pack(side="left", padx=5)
        
        btn_limpiar = self.create_button("Limpiar Filtros", self._limpiar_filtros, self.orange_color)
        btn_limpiar.pack(side="left", padx=5)
        
        # Configurar tabla
        columns = ["ID", "Producto", "Tipo", "Cantidad", "Usuario", "Tienda", "Almacén", "Fecha", "Nota"]
        widths = [60, 200, 80, 80, 100, 120, 120, 120, 150]
        self.setup_table_columns(columns, widths)
        
        # Cargar datos iniciales
        self.refresh_data()
    
    def get_view_name(self) -> str:
        """Retorna el nombre de la vista"""
        return "movimientos"
    
    def _filtrar_por_tienda(self):
        """Filtra los movimientos por tienda"""
        try:
            # Obtener tiendas disponibles
            tiendas_data = self.on_action("get_tiendas_for_selector", {})
            if not tiendas_data or 'tiendas' not in tiendas_data:
                self.show_info("Info", "No hay tiendas disponibles")
                return
            
            tiendas = tiendas_data['tiendas']
            
            # Crear diálogo de selección
            from tkinter import messagebox
            result = messagebox.askyesnocancel(
                "Filtrar por Tienda", 
                "¿Desea filtrar por una tienda específica?\n\nSí: Seleccionar tienda\nNo: Mostrar todas\nCancelar: Mantener filtro actual"
            )
            
            if result is True:  # Sí - seleccionar tienda
                self._show_tienda_selection_dialog(tiendas)
            elif result is False:  # No - mostrar todas
                self._clear_filters()
        except Exception as e:
            self.show_error("Error", f"Error al filtrar: {str(e)}")
    
    def _show_tienda_selection_dialog(self, tiendas: List[Dict[str, Any]]):
        """Muestra el diálogo de selección de tienda"""
        import tkinter as tk
        
        dialog = tk.Toplevel()
        dialog.title("Seleccionar Tienda")
        dialog.geometry("300x200")
        dialog.transient(self.parent_frame)
        dialog.grab_set()
        
        tk.Label(dialog, text="Seleccione una tienda:").pack(pady=10)
        
        listbox = tk.Listbox(dialog)
        listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Agregar opción "Todas las tiendas"
        listbox.insert(tk.END, "Todas las tiendas")
        for tienda in tiendas:
            listbox.insert(tk.END, tienda['display'])
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                selected_text = listbox.get(selection[0])
                if selected_text == "Todas las tiendas":
                    self._clear_filters()
                else:
                    # Extraer ID de la tienda
                    tienda_id = int(selected_text.split(" - ")[0])
                    self._set_tienda_filter(tienda_id)
                dialog.destroy()
        
        tk.Button(dialog, text="Seleccionar", command=on_select).pack(pady=5)
    
    def _set_tienda_filter(self, tienda_id: int):
        """Establece el filtro de tienda"""
        try:
            success = self.on_action("handle_view_action", {
                "view_name": "movimientos",
                "action": "set_tienda_filter",
                "action_data": {
                    "tienda_id": tienda_id
                }
            })
            
            if success:
                self.refresh_data()
        except Exception as e:
            self.show_error("Error", f"Error al establecer filtro: {str(e)}")
    
    def _limpiar_filtros(self):
        """Limpia todos los filtros"""
        try:
            success = self.on_action("handle_view_action", {
                "view_name": "movimientos",
                "action": "clear_filters",
                "action_data": {}
            })
            
            if success:
                self.refresh_data()
                self.show_info("Filtros", "Filtros limpiados")
        except Exception as e:
            self.show_error("Error", f"Error al limpiar filtros: {str(e)}")
