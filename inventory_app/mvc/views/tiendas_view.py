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
        """Crea una nueva tienda con formulario completo"""
        self._mostrar_formulario_tienda()
    
    def _mostrar_formulario_tienda(self):
        """Muestra formulario para crear tienda"""
        try:
            import tkinter as tk
            from tkinter import ttk
            
            # Crear ventana de formulario
            form_window = tk.Toplevel(self.parent_frame.winfo_toplevel())
            form_window.title("Nueva Tienda")
            form_window.geometry("450x500")
            form_window.resizable(True, True)
            form_window.configure(bg='white')
            form_window.minsize(400, 400)
            
            # Centrar ventana
            form_window.transient(self.parent_frame.winfo_toplevel())
            form_window.grab_set()
            
            # Crear canvas y scrollbar para scroll
            canvas = tk.Canvas(form_window, bg='white')
            scrollbar = ttk.Scrollbar(form_window, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='white')
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Frame principal dentro del scrollable_frame
            main_frame = tk.Frame(scrollable_frame, bg='white')
            main_frame.pack(expand=True, fill='both', padx=30, pady=20)
            
            # Pack canvas y scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Configurar scroll con mouse wheel
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            def _unbind_mousewheel(event):
                canvas.unbind_all("<MouseWheel>")
            form_window.bind("<Destroy>", _unbind_mousewheel)
            
            # Título
            title_label = tk.Label(
                main_frame,
                text="Registrar Nueva Tienda",
                bg='white',
                fg='#2E86C1',
                font=('Arial', 16, 'bold')
            )
            title_label.pack(pady=(0, 20))
            
            # Variables para los campos
            nombre_var = tk.StringVar()
            direccion_var = tk.StringVar()
            telefono_var = tk.StringVar()
            email_var = tk.StringVar()
            responsable_var = tk.StringVar()
            
            # Crear campos del formulario
            campos = [
                ("Nombre de la Tienda *", nombre_var, "entry"),
                ("Dirección", direccion_var, "entry"),
                ("Teléfono", telefono_var, "entry"),
                ("Email", email_var, "entry"),
                ("Responsable", responsable_var, "entry")
            ]
            
            # Crear campos
            for i, (label_text, var, field_type) in enumerate(campos):
                # Frame para cada campo
                field_frame = tk.Frame(main_frame, bg='white')
                field_frame.pack(fill='x', pady=8)
                
                # Label
                label = tk.Label(
                    field_frame,
                    text=label_text,
                    bg='white',
                    fg='black',
                    font=('Arial', 10),
                    anchor='w'
                )
                label.pack(fill='x', pady=(0, 3))
                
                # Campo de entrada
                if field_type == "entry":
                    entry = tk.Entry(
                        field_frame,
                        textvariable=var,
                        font=('Arial', 10),
                        relief='solid',
                        bd=1,
                        highlightthickness=1,
                        highlightcolor='#2E86C1',
                        highlightbackground='#D5D5D5'
                    )
                    entry.pack(fill='x', ipady=6)
            
            # Botones
            button_frame = tk.Frame(main_frame, bg='white')
            button_frame.pack(fill='x', pady=(20, 0))
            
            def guardar_tienda():
                """Guarda la tienda con todos los datos"""
                # Validar campos requeridos
                if not nombre_var.get().strip():
                    self.show_error("Error", "El nombre de la tienda es requerido")
                    return
                
                try:
                    # Crear tienda
                    success = self.on_action("handle_view_action", {
                        "view_name": "tiendas",
                        "action": "create_tienda",
                        "action_data": {
                            "nombre": nombre_var.get().strip(),
                            "direccion": direccion_var.get().strip() or None,
                            "telefono": telefono_var.get().strip() or None,
                            "email": email_var.get().strip() or None,
                            "responsable": responsable_var.get().strip() or None
                        }
                    })
                    
                    if success:
                        form_window.destroy()
                        self.refresh_data()
                        self.show_info("Éxito", "Tienda creada correctamente")
                    else:
                        self.show_error("Error", "No se pudo crear la tienda")
                        
                except Exception as e:
                    self.show_error("Error", f"Error al crear tienda: {str(e)}")
            
            def cancelar():
                """Cierra el formulario sin guardar"""
                form_window.destroy()
            
            # Botón Guardar
            btn_guardar = tk.Button(
                button_frame,
                text="Guardar Tienda",
                bg='#2E86C1',
                fg='white',
                font=('Arial', 11, 'bold'),
                relief='flat',
                cursor='hand2',
                command=guardar_tienda,
                bd=0,
                padx=20,
                pady=10
            )
            btn_guardar.pack(side='left', padx=(0, 10))
            
            # Botón Cancelar
            btn_cancelar = tk.Button(
                button_frame,
                text="Cancelar",
                bg='#95A5A6',
                fg='white',
                font=('Arial', 11),
                relief='flat',
                cursor='hand2',
                command=cancelar,
                bd=0,
                padx=20,
                pady=10
            )
            btn_cancelar.pack(side='left')
            
            # Efectos hover para botones
            def on_enter_guardar(e):
                btn_guardar.config(bg='#3498DB')
            def on_leave_guardar(e):
                btn_guardar.config(bg='#2E86C1')
            
            def on_enter_cancelar(e):
                btn_cancelar.config(bg='#7F8C8D')
            def on_leave_cancelar(e):
                btn_cancelar.config(bg='#95A5A6')
            
            btn_guardar.bind('<Enter>', on_enter_guardar)
            btn_guardar.bind('<Leave>', on_leave_guardar)
            btn_cancelar.bind('<Enter>', on_enter_cancelar)
            btn_cancelar.bind('<Leave>', on_leave_cancelar)
            
        except Exception as e:
            self.show_error("Error", f"Error al crear formulario: {str(e)}")
            import traceback
            traceback.print_exc()
    
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
