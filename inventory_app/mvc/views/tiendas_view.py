# ==============================
# File: inventory_app/mvc/views/tiendas_view.py
# ==============================
from __future__ import annotations
from typing import List, Dict, Any
from .base_view import BaseView


class TiendasView(BaseView):
    """Vista para la gestión de tiendas"""
    
    def _setup_view(self):
        """Configura la vista de tiendas"""
        # Botones de acción
        btn_nueva = self.create_button("Nueva Tienda", self._crear_tienda)
        btn_nueva.pack(side="left", padx=5)
        
        btn_quitar = self.create_button("Quitar tienda", self._eliminar_tienda, self.red_color)
        btn_quitar.pack(side="left", padx=5)
        
        # Configurar tabla
        columns = ["ID", "Nombre", "Direccion"]
        widths = [80, 200, 300]
        self.setup_table_columns(columns, widths)
        
        # Cargar datos iniciales
        self.refresh_data()
    
    def get_view_name(self) -> str:
        """Retorna el nombre de la vista"""
        return "tiendas"
    
    def _crear_tienda(self):
        """Crea una nueva tienda"""
        nombre = self.ask_string("Nueva Tienda", "Nombre de la tienda:")
        if not nombre:
            return
        
        direccion = self.ask_string("Nueva Tienda", "Dirección (opcional):")
        
        try:
            success = self.on_action("handle_view_action", {
                "view_name": "tiendas",
                "action": "create_tienda",
                "action_data": {
                    "nombre": nombre,
                    "direccion": direccion
                }
            })
            
            if success:
                self.refresh_data()
                self.show_info("Éxito", "Tienda creada correctamente")
        except Exception as e:
            self.show_error("Error", f"Error al crear tienda: {str(e)}")
    
    def _eliminar_tienda(self):
        """Elimina una tienda seleccionada"""
        selected = self.get_selected_item()
        if not selected:
            self.show_info("Info", "Seleccione una tienda para eliminar")
            return
        
        tienda_id = selected['data']['id']
        tienda_nombre = selected['data']['nombre']
        
        if self.ask_yes_no("Confirmar", f"¿Eliminar la tienda '{tienda_nombre}'?"):
            try:
                success = self.on_action("handle_view_action", {
                    "view_name": "tiendas",
                    "action": "delete_tienda",
                    "action_data": {
                        "id": int(tienda_id)
                    }
                })
                
                if success:
                    self.refresh_data()
                    self.show_info("Éxito", "Tienda eliminada correctamente")
            except Exception as e:
                self.show_error("Error", f"Error al eliminar tienda: {str(e)}")
