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
        
        btn_editar = self.create_button("Editar Tienda", self._editar_tienda, self.light_blue)
        btn_editar.pack(side="left", padx=5)
        
        btn_quitar = self.create_button("Quitar tienda", self._eliminar_tienda, self.red_color)
        btn_quitar.pack(side="left", padx=5)
        
        # Configurar tabla
        columns = ["ID", "Nombre", "Dirección", "Teléfono", "Email", "Responsable"]
        widths = [60, 180, 200, 100, 150, 150]
        self.setup_table_columns(columns, widths)
        
        # Cargar datos iniciales
        self.refresh_data()
    
    def get_view_name(self) -> str:
        """Retorna el nombre de la vista"""
        return "tiendas"
    
    def _crear_tienda(self):
        """Crea una nueva tienda con formulario completo"""
        self._mostrar_formulario_tienda()
    
    def _editar_tienda(self):
        """Edita una tienda seleccionada"""
        selected = self.get_selected_item()
        if not selected:
            self.show_info("Info", "Seleccione una tienda para editar")
            return
        
        data = selected['data']
        self._mostrar_formulario_editar_tienda(data)
    
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
            
            # Obtener solo empleados con rol ENCARGADO
            try:
                empleados = self.controller.inventory_models.inventory_service.listar_empleados()
                usuarios_data = [self.controller.user_models.get_usuario_por_id(e.usuario_id) for e in empleados]
                
                # Filtrar solo ENCARGADOS
                encargados = [(e, u) for e, u in zip(empleados, usuarios_data) if u and u.rol == "ENCARGADO"]
                responsable_options = ["Sin asignar"] + [f"{e.id} - {e.nombres} {e.apellidos}" for e, u in encargados]
            except Exception as e:
                print(f"Error al cargar encargados: {e}")
                responsable_options = ["Sin asignar"]
            
            # Crear campos del formulario
            campos = [
                ("Nombre de la Tienda *", nombre_var, "entry"),
                ("Dirección", direccion_var, "entry"),
                ("Teléfono", telefono_var, "entry"),
                ("Email", email_var, "entry"),
                ("Responsable (Encargado)", responsable_var, "combo", responsable_options)
            ]
            
            # Crear campos
            for i, campo_info in enumerate(campos):
                label_text = campo_info[0]
                var = campo_info[1]
                field_type = campo_info[2]
                options = campo_info[3] if len(campo_info) > 3 else None
                
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
                elif field_type == "combo":
                    combo = ttk.Combobox(
                        field_frame,
                        textvariable=var,
                        values=options,
                        font=('Arial', 10),
                        state='readonly'
                    )
                    combo.pack(fill='x', ipady=6)
                    if options:
                        combo.current(0)
            
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
                    # Extraer responsable_id
                    responsable_id = None
                    responsable_seleccionado = responsable_var.get()
                    if responsable_seleccionado and responsable_seleccionado != "Sin asignar":
                        responsable_id = int(responsable_seleccionado.split(' - ')[0])
                    
                    # Crear tienda
                    success = self.on_action("handle_view_action", {
                        "view_name": "tiendas",
                        "action": "create_tienda",
                        "action_data": {
                            "nombre": nombre_var.get().strip(),
                            "direccion": direccion_var.get().strip() or None,
                            "telefono": telefono_var.get().strip() or None,
                            "email": email_var.get().strip() or None,
                            "responsable_id": responsable_id
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
    
    def _mostrar_formulario_editar_tienda(self, tienda_data):
        """Muestra formulario para editar tienda"""
        try:
            import tkinter as tk
            from tkinter import ttk
            
            # Crear ventana de formulario
            form_window = tk.Toplevel(self.parent_frame.winfo_toplevel())
            form_window.title("Editar Tienda")
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
                text="Editar Tienda",
                bg='white',
                fg='#2E86C1',
                font=('Arial', 16, 'bold')
            )
            title_label.pack(pady=(0, 20))
            
            # Variables para los campos con datos existentes
            nombre_var = tk.StringVar(value=tienda_data.get('nombre', ''))
            direccion_var = tk.StringVar(value=tienda_data.get('direccion', ''))
            telefono_var = tk.StringVar(value=tienda_data.get('telefono', ''))
            email_var = tk.StringVar(value=tienda_data.get('email', ''))
            responsable_var = tk.StringVar()
            
            # Obtener solo empleados con rol ENCARGADO
            try:
                empleados = self.controller.inventory_models.inventory_service.listar_empleados()
                usuarios_data = [self.controller.user_models.get_usuario_por_id(e.usuario_id) for e in empleados]
                
                # Filtrar solo ENCARGADOS
                encargados = [(e, u) for e, u in zip(empleados, usuarios_data) if u and u.rol == "ENCARGADO"]
                responsable_options = ["Sin asignar"] + [f"{e.id} - {e.nombres} {e.apellidos}" for e, u in encargados]
                
                # Seleccionar responsable actual si existe
                responsable_actual = tienda_data.get('responsable', '')
                if responsable_actual and responsable_actual != "Sin asignar":
                    # Buscar el responsable en los encargados
                    for e, u in encargados:
                        if f"{e.nombres} {e.apellidos}" == responsable_actual:
                            responsable_var.set(f"{e.id} - {e.nombres} {e.apellidos}")
                            break
                    else:
                        responsable_var.set("Sin asignar")
                else:
                    responsable_var.set("Sin asignar")
                    
            except Exception as e:
                print(f"Error al cargar encargados: {e}")
                responsable_options = ["Sin asignar"]
                responsable_var.set("Sin asignar")
            
            # Crear campos del formulario
            campos = [
                ("Nombre de la Tienda *", nombre_var, "entry"),
                ("Dirección", direccion_var, "entry"),
                ("Teléfono", telefono_var, "entry"),
                ("Email", email_var, "entry"),
                ("Responsable (Encargado)", responsable_var, "combo", responsable_options)
            ]
            
            # Crear campos
            for i, campo_info in enumerate(campos):
                label_text = campo_info[0]
                var = campo_info[1]
                field_type = campo_info[2]
                options = campo_info[3] if len(campo_info) > 3 else None
                
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
                elif field_type == "combo":
                    combo = ttk.Combobox(
                        field_frame,
                        textvariable=var,
                        values=options,
                        font=('Arial', 10),
                        state='readonly'
                    )
                    combo.pack(fill='x', ipady=6)
            
            # Botones
            button_frame = tk.Frame(main_frame, bg='white')
            button_frame.pack(fill='x', pady=(20, 0))
            
            def actualizar_tienda():
                """Actualiza la tienda con todos los datos"""
                # Validar campos requeridos
                if not nombre_var.get().strip():
                    self.show_error("Error", "El nombre de la tienda es requerido")
                    return
                
                try:
                    # Extraer responsable_id
                    responsable_id = None
                    responsable_seleccionado = responsable_var.get()
                    if responsable_seleccionado and responsable_seleccionado != "Sin asignar":
                        responsable_id = int(responsable_seleccionado.split(' - ')[0])
                    
                    # Actualizar tienda
                    success = self.on_action("handle_view_action", {
                        "view_name": "tiendas",
                        "action": "edit_tienda",
                        "action_data": {
                            "tienda_id": int(tienda_data.get('id')),
                            "nombre": nombre_var.get().strip(),
                            "direccion": direccion_var.get().strip() or None,
                            "telefono": telefono_var.get().strip() or None,
                            "email": email_var.get().strip() or None,
                            "responsable_id": responsable_id
                        }
                    })
                    
                    if success:
                        form_window.destroy()
                        self.refresh_data()
                        self.show_info("Éxito", "Tienda actualizada correctamente")
                    else:
                        self.show_error("Error", "No se pudo actualizar la tienda")
                        
                except Exception as e:
                    self.show_error("Error", f"Error al actualizar tienda: {str(e)}")
            
            def cancelar():
                """Cierra el formulario sin guardar"""
                form_window.destroy()
            
            # Botón Actualizar
            btn_actualizar = tk.Button(
                button_frame,
                text="Actualizar Tienda",
                bg='#2E86C1',
                fg='white',
                font=('Arial', 11, 'bold'),
                relief='flat',
                cursor='hand2',
                command=actualizar_tienda,
                bd=0,
                padx=20,
                pady=10
            )
            btn_actualizar.pack(side='left', padx=(0, 10))
            
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
            def on_enter_actualizar(e):
                btn_actualizar.config(bg='#3498DB')
            def on_leave_actualizar(e):
                btn_actualizar.config(bg='#2E86C1')
            
            def on_enter_cancelar(e):
                btn_cancelar.config(bg='#7F8C8D')
            def on_leave_cancelar(e):
                btn_cancelar.config(bg='#95A5A6')
            
            btn_actualizar.bind('<Enter>', on_enter_actualizar)
            btn_actualizar.bind('<Leave>', on_leave_actualizar)
            btn_cancelar.bind('<Enter>', on_enter_cancelar)
            btn_cancelar.bind('<Leave>', on_leave_cancelar)
            
        except Exception as e:
            self.show_error("Error", f"Error al crear formulario de edición: {str(e)}")
            import traceback
            traceback.print_exc()
