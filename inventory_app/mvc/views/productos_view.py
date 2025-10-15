# ==============================
# File: inventory_app/mvc/views/productos_view.py
# ==============================
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any
from .base_view import BaseView


class ProductosView(BaseView):
    """Vista para la gestión de productos"""
    
    def _setup_view(self):
        """Configura la vista de productos"""
        # Obtener información del usuario para mostrar botones según rol
        user_info = self.on_action("get_user_info", {})
        user_rol = user_info.get('rol') if user_info else None
        
        # Botones de acción - Solo ADMIN puede crear, editar y eliminar productos
        if user_rol == "ADMIN":
            btn_nuevo = self.create_button("Nuevo Producto", self._crear_producto)
            btn_nuevo.pack(side="left", padx=5)
            
            btn_editar = self.create_button("Editar Producto", self._editar_producto, self.light_blue)
            btn_editar.pack(side="left", padx=5)
            
            btn_eliminar = self.create_button("Eliminar Producto", self._eliminar_producto, self.red_color)
            btn_eliminar.pack(side="left", padx=5)
        
        # Configurar tabla
        columns = ["ID", "SKU", "Nombre", "Descripción", "Categoría", "Proveedor", "Unidad", "Precio", "Stock Mín.", "Tienda", "Estado"]
        widths = [60, 100, 150, 200, 100, 120, 80, 80, 80, 100, 80]
        self.setup_table_columns(columns, widths)
        
        # Cargar datos iniciales
        self.refresh_data()
    
    def get_view_name(self) -> str:
        """Retorna el nombre de la vista"""
        return "productos"
    
    def _crear_producto(self):
        """Crea un nuevo producto con formulario unificado"""
        self._mostrar_formulario_producto()
    
    def _editar_producto(self):
        """Edita un producto seleccionado con formulario unificado"""
        selected = self.get_selected_item()
        if not selected:
            self.show_info("Info", "Seleccione un producto para editar")
            return
        
        data = selected['data']
        self._mostrar_formulario_editar_producto(data)
    
    def _eliminar_producto(self):
        """Elimina un producto seleccionado"""
        selected = self.get_selected_item()
        if not selected:
            self.show_info("Info", "Seleccione un producto para eliminar")
            return
        
        data = selected['data']
        producto_id = data.get('id')
        sku = data.get('sku')
        nombre = data.get('nombre')
        
        if self.ask_yes_no("Confirmar", f"¿Eliminar el producto '{sku} - {nombre}'?"):
            try:
                success = self.on_action("handle_view_action", {
                    "view_name": "productos",
                    "action": "delete_producto",
                    "action_data": {
                        "id": int(producto_id)
                    }
                })
                
                if success:
                    self.refresh_data()
                    self.show_info("Éxito", "Producto eliminado correctamente")
            except Exception as e:
                self.show_error("Error", f"Error al eliminar producto: {str(e)}")
    
    def _mostrar_formulario_producto(self):
        """Muestra formulario unificado para crear producto"""
        try:
            import tkinter as tk
            from tkinter import ttk
            
            # Crear ventana de formulario
            form_window = tk.Toplevel(self.parent_frame.winfo_toplevel())
            form_window.title("Nuevo Producto")
            form_window.geometry("450x650")
            form_window.resizable(True, True)
            form_window.configure(bg='white')
            form_window.minsize(400, 550)
            
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
                text="Registrar Nuevo Producto",
                bg='white',
                fg='#2E86C1',
                font=('Arial', 16, 'bold')
            )
            title_label.pack(pady=(0, 20))
            
            # Variables para los campos
            sku_var = tk.StringVar()
            nombre_var = tk.StringVar()
            descripcion_var = tk.StringVar()
            categoria_var = tk.StringVar()
            proveedor_var = tk.StringVar()
            unidad_var = tk.StringVar(value="un")
            precio_var = tk.StringVar()
            stock_minimo_var = tk.StringVar(value="0")
            tienda_var = tk.StringVar()
            
            # Crear campos del formulario
            campos = [
                ("SKU *", sku_var, "entry"),
                ("Nombre *", nombre_var, "entry"),
                ("Descripción", descripcion_var, "entry"),
                ("Categoría", categoria_var, "entry"),
                ("Proveedor", proveedor_var, "entry"),
                ("Unidad", unidad_var, "entry"),
                ("Precio Unitario *", precio_var, "entry"),
                ("Stock Mínimo", stock_minimo_var, "entry")
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
            
            # Separador
            separator = tk.Frame(main_frame, height=2, bg='#E0E0E0')
            separator.pack(fill='x', pady=20)
            
            # Sección de asignación a tienda
            section_label = tk.Label(
                main_frame,
                text="Asignación a Tienda",
                bg='white',
                fg='#E67E22',
                font=('Arial', 12, 'bold')
            )
            section_label.pack(pady=(0, 15))
            
            # Tienda
            tienda_frame = tk.Frame(main_frame, bg='white')
            tienda_frame.pack(fill='x', pady=8)
            
            tk.Label(
                tienda_frame,
                text="Tienda *",
                bg='white',
                fg='black',
                font=('Arial', 10),
                anchor='w'
            ).pack(fill='x', pady=(0, 3))
            
            tienda_combo = ttk.Combobox(
                tienda_frame,
                textvariable=tienda_var,
                state="readonly",
                font=('Arial', 10)
            )
            tienda_combo.pack(fill='x', ipady=6)
            
            # Cargar tiendas
            try:
                dashboard_data = self.on_action("get_dashboard_data", {})
                tiendas_data = dashboard_data.get('tiendas', [])
                tienda_options = [t['display'] for t in tiendas_data]
                tienda_combo['values'] = tienda_options
            except Exception as e:
                print(f"Error cargando tiendas: {e}")
                tiendas_data = []
            
            # Botones
            button_frame = tk.Frame(main_frame, bg='white')
            button_frame.pack(fill='x', pady=(20, 0))
            
            def guardar_producto():
                """Guarda el producto con todos los datos"""
                # Validar campos requeridos
                if not all([sku_var.get(), nombre_var.get(), precio_var.get(), tienda_var.get()]):
                    self.show_error("Error", "SKU, nombre, precio y tienda son campos requeridos")
                    return
                
                try:
                    precio_float = float(precio_var.get().strip())
                    stock_minimo_int = int(stock_minimo_var.get().strip() or "0")
                except ValueError:
                    self.show_error("Error", "Precio y stock mínimo deben ser números válidos")
                    return
                
                try:
                    # Extraer ID de tienda
                    tienda_id = int(tienda_var.get().split(' - ')[0])
                    
                    # Crear producto
                    success = self.on_action("handle_view_action", {
                        "view_name": "productos",
                        "action": "create_producto",
                        "action_data": {
                            "sku": sku_var.get().strip(),
                            "nombre": nombre_var.get().strip(),
                            "descripcion": descripcion_var.get().strip() or None,
                            "categoria": categoria_var.get().strip() or None,
                            "proveedor": proveedor_var.get().strip() or None,
                            "unidad": unidad_var.get().strip() or "un",
                            "precio": precio_float,
                            "stock_minimo": stock_minimo_int,
                            "tienda_id": tienda_id
                        }
                    })
                    
                    if success:
                        form_window.destroy()
                        self.refresh_data()
                        self.show_info("Éxito", "Producto creado correctamente")
                    else:
                        self.show_error("Error", "No se pudo crear el producto")
                        
                except Exception as e:
                    self.show_error("Error", f"Error al crear producto: {str(e)}")
            
            def cancelar():
                """Cierra el formulario sin guardar"""
                form_window.destroy()
            
            # Botón Guardar
            btn_guardar = tk.Button(
                button_frame,
                text="Guardar Producto",
                bg='#2E86C1',
                fg='white',
                font=('Arial', 11, 'bold'),
                relief='flat',
                cursor='hand2',
                command=guardar_producto,
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
    
    def _mostrar_formulario_editar_producto(self, producto_data):
        """Muestra formulario unificado para editar producto"""
        try:
            import tkinter as tk
            from tkinter import ttk
            
            # Crear ventana de formulario
            form_window = tk.Toplevel(self.parent_frame.winfo_toplevel())
            form_window.title("Editar Producto")
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
                text="Editar Producto",
                bg='white',
                fg='#2E86C1',
                font=('Arial', 16, 'bold')
            )
            title_label.pack(pady=(0, 20))
            
            # Variables para los campos con datos existentes
            sku_var = tk.StringVar(value=producto_data.get('sku', ''))
            nombre_var = tk.StringVar(value=producto_data.get('nombre', ''))
            descripcion_var = tk.StringVar(value=producto_data.get('descripcion', ''))
            categoria_var = tk.StringVar(value=producto_data.get('categoria', ''))
            proveedor_var = tk.StringVar(value=producto_data.get('proveedor', ''))
            unidad_var = tk.StringVar(value=producto_data.get('unidad', 'un'))
            precio_var = tk.StringVar(value=producto_data.get('precio', ''))
            stock_minimo_var = tk.StringVar(value=producto_data.get('stock_minimo', '0'))
            activo_var = tk.BooleanVar(value=producto_data.get('estado', 'Activo') == 'Activo')
            
            # Crear campos del formulario
            campos = [
                ("SKU", sku_var, "entry"),
                ("Nombre", nombre_var, "entry"),
                ("Descripción", descripcion_var, "entry"),
                ("Categoría", categoria_var, "entry"),
                ("Proveedor", proveedor_var, "entry"),
                ("Unidad", unidad_var, "entry"),
                ("Precio Unitario", precio_var, "entry"),
                ("Stock Mínimo", stock_minimo_var, "entry")
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
            
            # Checkbox para activo
            activo_frame = tk.Frame(main_frame, bg='white')
            activo_frame.pack(fill='x', pady=8)
            
            activo_checkbox = tk.Checkbutton(
                activo_frame,
                text="Producto Activo",
                variable=activo_var,
                bg='white',
                font=('Arial', 10)
            )
            activo_checkbox.pack(anchor='w')
            
            # Botones
            button_frame = tk.Frame(main_frame, bg='white')
            button_frame.pack(fill='x', pady=(20, 0))
            
            def actualizar_producto():
                """Actualiza el producto con los datos modificados"""
                # Validar campos requeridos
                if not all([sku_var.get(), nombre_var.get(), precio_var.get()]):
                    self.show_error("Error", "SKU, nombre y precio son campos requeridos")
                    return
                
                try:
                    precio_float = float(precio_var.get().strip())
                    stock_minimo_int = int(stock_minimo_var.get().strip() or "0")
                except ValueError:
                    self.show_error("Error", "Precio y stock mínimo deben ser números válidos")
                    return
                
                try:
                    # Preparar datos para actualizar
                    action_data = {
                        "id": producto_data.get('id'),
                        "sku": sku_var.get().strip(),
                        "nombre": nombre_var.get().strip(),
                        "descripcion": descripcion_var.get().strip() or None,
                        "categoria": categoria_var.get().strip() or None,
                        "proveedor": proveedor_var.get().strip() or None,
                        "unidad": unidad_var.get().strip() or "un",
                        "precio": precio_float,
                        "stock_minimo": stock_minimo_int,
                        "activo": activo_var.get()
                    }
                    
                    # Actualizar producto
                    success = self.on_action("handle_view_action", {
                        "view_name": "productos",
                        "action": "edit_producto",
                        "action_data": action_data
                    })
                    
                    if success:
                        form_window.destroy()
                        self.refresh_data()
                        self.show_info("Éxito", "Producto actualizado correctamente")
                    else:
                        self.show_error("Error", "No se pudo actualizar el producto")
                        
                except Exception as e:
                    self.show_error("Error", f"Error al actualizar producto: {str(e)}")
            
            def cancelar():
                """Cierra el formulario sin guardar"""
                form_window.destroy()
            
            # Botón Actualizar
            btn_actualizar = tk.Button(
                button_frame,
                text="Actualizar Producto",
                bg='#2E86C1',
                fg='white',
                font=('Arial', 11, 'bold'),
                relief='flat',
                cursor='hand2',
                command=actualizar_producto,
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
