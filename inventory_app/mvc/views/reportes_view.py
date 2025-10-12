# ==============================
# File: inventory_app/mvc/views/reportes_view.py
# ==============================
from __future__ import annotations
from typing import List, Dict, Any
from .base_view import BaseView


class ReportesView(BaseView):
    """Vista para reportes y alertas del sistema"""
    
    def _setup_view(self):
        """Configura la vista de reportes"""
        # Botones de acción
        btn_stock = self.create_button("Reporte de Stock", self._generar_reporte_stock)
        btn_stock.pack(side="left", padx=5)
        
        btn_alertas = self.create_button("Ver Alertas", self._ver_alertas, self.orange_color)
        btn_alertas.pack(side="left", padx=5)
        
        btn_exportar = self.create_button("Exportar CSV", self._exportar_csv, self.light_blue)
        btn_exportar.pack(side="left", padx=5)
        
        btn_filtrar = self.create_button("Filtrar por Tienda", self._filtrar_por_tienda, self.light_blue)
        btn_filtrar.pack(side="left", padx=5)
        
        # Configurar tabla
        columns = ["Tienda", "Almacén", "Producto", "Stock", "Mínimo", "Estado"]
        widths = [120, 120, 200, 80, 80, 100]
        self.setup_table_columns(columns, widths)
        
        # Cargar datos iniciales
        self.refresh_data()
    
    def get_view_name(self) -> str:
        """Retorna el nombre de la vista"""
        return "reportes"
    
    def _generar_reporte_stock(self):
        """Genera y muestra el reporte de stock"""
        self.refresh_data()
        self.show_info("Reporte", "Reporte de stock actualizado")
    
    def _ver_alertas(self):
        """Muestra las alertas de stock"""
        try:
            alerts_data = self.on_action("get_alerts", {"view_name": "reportes"})
            if not alerts_data or 'alerts' not in alerts_data:
                self.show_info("Alertas", "No hay alertas. Todo está en orden.")
                return
            
            alerts = alerts_data['alerts']
            if not alerts:
                self.show_info("Alertas", "No hay alertas. Todo está en orden.")
                return
            
            alertas_text = "🚨 ALERTAS DE STOCK:\n\n"
            for alert in alerts:
                emoji = "🔴" if alert['estado'] == 'SIN STOCK' else "🟡"
                alertas_text += f"{emoji} {alert['tienda']} - {alert['almacen']}: {alert['producto']}\n"
                alertas_text += f"   Stock: {alert['stock']}, Mínimo: {alert['minimo']}, Estado: {alert['estado']}\n\n"
            
            self.show_warning("Alertas de Stock", alertas_text)
        except Exception as e:
            self.show_error("Error", f"Error al obtener alertas: {str(e)}")
    
    def _exportar_csv(self):
        """Exporta el reporte actual a CSV"""
        try:
            from tkinter import filedialog
            import csv
            
            # Solicitar archivo de destino
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Guardar reporte como CSV"
            )
            
            if not filename:
                return
            
            # Obtener datos de la tabla
            data = self.on_action("get_view_data", {"view_name": "reportes"})
            if not data or 'data' not in data:
                self.show_error("Error", "No hay datos para exportar")
                return
            
            # Escribir CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Escribir encabezados
                writer.writerow(["Tienda", "Almacén", "Producto", "Stock", "Mínimo", "Estado"])
                # Escribir datos
                for row in data['data']:
                    writer.writerow([
                        row.get('tienda', ''),
                        row.get('almacen', ''),
                        row.get('producto', ''),
                        row.get('stock', ''),
                        row.get('minimo', ''),
                        row.get('estado', '')
                    ])
            
            self.show_info("Exportar", f"Reporte exportado correctamente a:\n{filename}")
            
        except Exception as e:
            self.show_error("Error", f"Error al exportar: {str(e)}")
    
    def _filtrar_por_tienda(self):
        """Filtra el reporte por tienda"""
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
                "view_name": "reportes",
                "action": "set_tienda_filter",
                "action_data": {
                    "tienda_id": tienda_id
                }
            })
            
            if success:
                self.refresh_data()
        except Exception as e:
            self.show_error("Error", f"Error al establecer filtro: {str(e)}")
    
    def _clear_filters(self):
        """Limpia todos los filtros"""
        try:
            success = self.on_action("handle_view_action", {
                "view_name": "reportes",
                "action": "clear_filters",
                "action_data": {}
            })
            
            if success:
                self.refresh_data()
        except Exception as e:
            self.show_error("Error", f"Error al limpiar filtros: {str(e)}")
