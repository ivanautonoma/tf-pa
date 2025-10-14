# ==============================
# File: inventory_app/mvc/views/empleados_view.py
# ==============================
from __future__ import annotations
from typing import List, Dict, Any
from .base_view import BaseView


class EmpleadosView(BaseView):
    """Vista para la gestión de empleados"""
    
    def _setup_view(self):
        """Configura la vista de empleados"""
        # Botones de acción
        btn_nuevo = self.create_button("Nuevo Empleado", self._crear_empleado)
        btn_nuevo.pack(side="left", padx=5)
        
        btn_editar = self.create_button("Editar Empleado", self._editar_empleado, self.light_blue)
        btn_editar.pack(side="left", padx=5)
        
        btn_eliminar = self.create_button("Eliminar Empleado", self._eliminar_empleado, self.red_color)
        btn_eliminar.pack(side="left", padx=5)
        
        # Configurar tabla
        columns = ["ID", "Usuario", "Nombres", "Apellidos", "DNI", "Jornada", "Tienda", "Rol", "Estado"]
        widths = [60, 120, 120, 120, 100, 80, 120, 80, 80]
        self.setup_table_columns(columns, widths)
        
        # Cargar datos iniciales
        self.refresh_data()
    
    def get_view_name(self) -> str:
        """Retorna el nombre de la vista"""
        return "empleados"
    
    def _crear_empleado(self):
        """Crea un nuevo empleado con formulario unificado"""
        try:
            print("DEBUG: Intentando abrir formulario de empleado...")
            self._mostrar_formulario_empleado()
            print("DEBUG: Formulario creado exitosamente")
        except Exception as e:
            print(f"DEBUG: Error al crear formulario: {str(e)}")
            self.show_error("Error", f"No se pudo abrir el formulario: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _editar_empleado(self):
        """Edita un empleado seleccionado con formulario unificado"""
        selected = self.get_selected_item()
        if not selected:
            self.show_info("Info", "Seleccione un empleado para editar")
            return
        
        data = selected['data']
        self._mostrar_formulario_editar_empleado(data)
    
    def _eliminar_empleado(self):
        """Elimina un empleado seleccionado"""
        selected = self.get_selected_item()
        if not selected:
            self.show_info("Info", "Seleccione un empleado para eliminar")
            return
        
        data = selected['data']
        user_id = data.get('id')
        username = data.get('usuario')
        
        if self.ask_yes_no("Confirmar", f"¿Eliminar el empleado '{username}'?"):
            try:
                success = self.on_action("handle_view_action", {
                    "view_name": "empleados",
                    "action": "delete_empleado",
                    "action_data": {
                        "id": int(user_id)
                    }
                })
                
                if success:
                    self.refresh_data()
                    self.show_info("Éxito", "Empleado eliminado correctamente")
            except Exception as e:
                self.show_error("Error", f"Error al eliminar empleado: {str(e)}")
    
    def _mostrar_formulario_empleado(self):
        """Muestra formulario unificado para crear empleado"""
        try:
            import tkinter as tk
            from tkinter import ttk
            
            # Crear ventana de formulario
            form_window = tk.Toplevel(self.parent_frame.winfo_toplevel())
            form_window.title("Nuevo Empleado")
            form_window.geometry("450x600")
            form_window.resizable(True, True)
            form_window.configure(bg='white')
            form_window.minsize(400, 500)
            
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
                text="Registrar Nuevo Empleado",
                bg='white',
                fg='#2E86C1',
                font=('Arial', 16, 'bold')
            )
            title_label.pack(pady=(0, 20))
            
            # Variables para los campos
            username_var = tk.StringVar()
            password_var = tk.StringVar()
            rol_var = tk.StringVar(value="OPERADOR")
            nombres_var = tk.StringVar()
            apellidos_var = tk.StringVar()
            dni_var = tk.StringVar()
            jornada_var = tk.StringVar(value="COMPLETA")
            tienda_var = tk.StringVar()
            
            # Obtener tiendas disponibles
            try:
                # Obtener las tiendas a través del controlador
                tiendas_data = self.controller.inventory_models.get_tiendas()
                tienda_options = [f"{t.id} - {t.nombre}" for t in tiendas_data]
            except Exception as e:
                print(f"Error al cargar tiendas: {e}")
                tienda_options = ["1 - Centro"]  # Fallback si no se pueden cargar las tiendas
            
            # Crear campos del formulario
            campos = [
                ("Usuario", username_var, "entry"),
                ("Contraseña", password_var, "password"),
                ("Rol", rol_var, "combo", ["ADMIN", "OPERADOR"]),
                ("Nombres", nombres_var, "entry"),
                ("Apellidos", apellidos_var, "entry"),
                ("DNI", dni_var, "entry"),
                ("Jornada", jornada_var, "combo", ["COMPLETA", "MEDIA", "PARCIAL"]),
                ("Tienda", tienda_var, "combo", tienda_options)
            ]
            
            # Crear campos
            for i, (label_text, var, field_type, *options) in enumerate(campos):
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
                    
                elif field_type == "password":
                    entry = tk.Entry(
                        field_frame,
                        textvariable=var,
                        font=('Arial', 10),
                        show="*",
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
                        values=options[0],
                        font=('Arial', 10),
                        state='readonly'
                    )
                    combo.pack(fill='x', ipady=6)
            
            # Botones
            button_frame = tk.Frame(main_frame, bg='white')
            button_frame.pack(fill='x', pady=(20, 0))
            
            def guardar_empleado():
                """Guarda el empleado con todos los datos"""
                # Validar campos requeridos
                if not all([username_var.get(), password_var.get(), nombres_var.get(), 
                           apellidos_var.get(), dni_var.get(), tienda_var.get()]):
                    self.show_error("Error", "Por favor complete todos los campos requeridos")
                    return
                
                # Obtener ID de tienda seleccionada
                tienda_seleccionada = tienda_var.get()
                if not tienda_seleccionada:
                    self.show_error("Error", "Seleccione una tienda")
                    return
                
                tienda_id = int(tienda_seleccionada.split(' - ')[0])
                
                try:
                    # Crear empleado completo
                    success = self.on_action("handle_view_action", {
                        "view_name": "empleados",
                        "action": "create_empleado_completo",
                        "action_data": {
                            "username": username_var.get().strip(),
                            "password": password_var.get().strip(),
                            "rol": rol_var.get(),
                            "nombres": nombres_var.get().strip(),
                            "apellidos": apellidos_var.get().strip(),
                            "dni": dni_var.get().strip(),
                            "jornada": jornada_var.get(),
                            "tienda_id": tienda_id
                        }
                    })
                    
                    if success:
                        form_window.destroy()
                        self.refresh_data()
                        self.show_info("Éxito", "Empleado creado correctamente")
                    else:
                        self.show_error("Error", "No se pudo crear el empleado")
                        
                except Exception as e:
                    self.show_error("Error", f"Error al crear empleado: {str(e)}")
            
            def cancelar():
                """Cierra el formulario sin guardar"""
                form_window.destroy()
            
            # Botón Guardar
            btn_guardar = tk.Button(
                button_frame,
                text="Guardar Empleado",
                bg='#2E86C1',
                fg='white',
                font=('Arial', 11, 'bold'),
                relief='flat',
                cursor='hand2',
                command=guardar_empleado,
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
    
    def _mostrar_formulario_editar_empleado(self, empleado_data):
        """Muestra formulario unificado para editar empleado"""
        try:
            import tkinter as tk
            from tkinter import ttk
            
            # Crear ventana de formulario
            form_window = tk.Toplevel(self.parent_frame.winfo_toplevel())
            form_window.title("Editar Empleado")
            form_window.geometry("450x600")
            form_window.resizable(True, True)
            form_window.configure(bg='white')
            form_window.minsize(400, 500)
            
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
                text="Editar Empleado",
                bg='white',
                fg='#2E86C1',
                font=('Arial', 16, 'bold')
            )
            title_label.pack(pady=(0, 20))
            
            # Variables para los campos con datos existentes
            username_var = tk.StringVar(value=empleado_data.get('username', ''))
            password_var = tk.StringVar()  # Vacío para nueva contraseña
            rol_var = tk.StringVar(value=empleado_data.get('rol', 'OPERADOR'))
            nombres_var = tk.StringVar(value=empleado_data.get('nombres', ''))
            apellidos_var = tk.StringVar(value=empleado_data.get('apellidos', ''))
            dni_var = tk.StringVar(value=empleado_data.get('dni', ''))
            jornada_var = tk.StringVar(value=empleado_data.get('jornada', 'COMPLETA'))
            tienda_var = tk.StringVar()
            
            # Obtener tiendas disponibles
            try:
                # Obtener las tiendas a través del controlador
                tiendas_data = self.controller.inventory_models.get_tiendas()
                tienda_options = [f"{t.id} - {t.nombre}" for t in tiendas_data]
                
                # Seleccionar la tienda actual
                tienda_actual = empleado_data.get('tienda', '')
                for i, option in enumerate(tienda_options):
                    if tienda_actual in option:
                        tienda_var.set(option)
                        break
                else:
                    tienda_var.set(tienda_options[0] if tienda_options else "1 - Centro")
                    
            except Exception as e:
                print(f"Error al cargar tiendas: {e}")
                tienda_options = ["1 - Centro"]
                tienda_var.set("1 - Centro")
            
            # Crear campos del formulario
            campos = [
                ("Usuario", username_var, "entry"),
                ("Nueva Contraseña (opcional)", password_var, "password"),
                ("Rol", rol_var, "combo", ["ADMIN", "OPERADOR"]),
                ("Nombres", nombres_var, "entry"),
                ("Apellidos", apellidos_var, "entry"),
                ("DNI", dni_var, "entry"),
                ("Jornada", jornada_var, "combo", ["COMPLETA", "MEDIA", "PARCIAL"]),
                ("Tienda", tienda_var, "combo", tienda_options)
            ]
            
            # Crear campos
            for i, (label_text, var, field_type, *options) in enumerate(campos):
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
                    
                elif field_type == "password":
                    entry = tk.Entry(
                        field_frame,
                        textvariable=var,
                        font=('Arial', 10),
                        show="*",
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
                        values=options[0],
                        font=('Arial', 10),
                        state='readonly'
                    )
                    combo.pack(fill='x', ipady=6)
            
            # Botones
            button_frame = tk.Frame(main_frame, bg='white')
            button_frame.pack(fill='x', pady=(20, 0))
            
            def actualizar_empleado():
                """Actualiza el empleado con los datos modificados"""
                # Validar campos requeridos
                if not all([username_var.get(), nombres_var.get(), 
                           apellidos_var.get(), dni_var.get(), tienda_var.get()]):
                    self.show_error("Error", "Por favor complete todos los campos requeridos")
                    return
                
                # Obtener ID de tienda seleccionada
                tienda_seleccionada = tienda_var.get()
                if not tienda_seleccionada:
                    self.show_error("Error", "Seleccione una tienda")
                    return
                
                tienda_id = int(tienda_seleccionada.split(' - ')[0])
                
                try:
                    # Preparar datos para actualizar
                    action_data = {
                        "empleado_id": empleado_data.get('id'),
                        "username": username_var.get().strip(),
                        "rol": rol_var.get(),
                        "nombres": nombres_var.get().strip(),
                        "apellidos": apellidos_var.get().strip(),
                        "dni": dni_var.get().strip(),
                        "jornada": jornada_var.get(),
                        "tienda_id": tienda_id
                    }
                    
                    # Solo incluir contraseña si se proporcionó una nueva
                    nueva_password = password_var.get().strip()
                    if nueva_password:
                        action_data["password"] = nueva_password
                    
                    # Actualizar empleado completo
                    success = self.on_action("handle_view_action", {
                        "view_name": "empleados",
                        "action": "edit_empleado_completo",
                        "action_data": action_data
                    })
                    
                    if success:
                        form_window.destroy()
                        self.refresh_data()
                        self.show_info("Éxito", "Empleado actualizado correctamente")
                    else:
                        self.show_error("Error", "No se pudo actualizar el empleado")
                        
                except Exception as e:
                    self.show_error("Error", f"Error al actualizar empleado: {str(e)}")
            
            def cancelar():
                """Cierra el formulario sin guardar"""
                form_window.destroy()
            
            # Botón Actualizar
            btn_actualizar = tk.Button(
                button_frame,
                text="Actualizar Empleado",
                bg='#2E86C1',
                fg='white',
                font=('Arial', 11, 'bold'),
                relief='flat',
                cursor='hand2',
                command=actualizar_empleado,
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
