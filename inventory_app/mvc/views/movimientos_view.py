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
        # Obtener información del usuario para mostrar botones según rol
        user_info = self.on_action("get_user_info", {})
        user_rol = user_info.get('rol') if user_info else None
        
        # Botones de acción según rol
        # Solo ADMIN y ENCARGADO pueden registrar ingresos
        if user_rol in ["ADMIN", "ENCARGADO"]:
            btn_registrar_ingreso = self.create_button("Registrar Ingreso", self._registrar_ingreso, "#10b981")
            btn_registrar_ingreso.pack(side="left", padx=5)
        
        # ADMIN, ENCARGADO y VENDEDOR pueden registrar salidas
        if user_rol in ["ADMIN", "ENCARGADO", "VENDEDOR"]:
            btn_registrar_salida = self.create_button("Registrar Salida", self._registrar_salida, self.red_color)
            btn_registrar_salida.pack(side="left", padx=5)
        
        btn_refrescar = self.create_button("Refrescar", self.refresh_data)
        btn_refrescar.pack(side="left", padx=5)
        
        # Configurar tabla
        columns = ["ID", "Producto", "Tipo", "Cantidad", "Usuario", "Tienda", "Fecha", "Nota"]
        widths = [60, 200, 80, 80, 100, 120, 120, 150]
        self.setup_table_columns(columns, widths)
        
        # Cargar datos iniciales
        self.refresh_data()
    
    def get_view_name(self) -> str:
        """Retorna el nombre de la vista"""
        return "movimientos"
    
    def _registrar_ingreso(self):
        """Muestra formulario para registrar ingreso de producto"""
        self._mostrar_formulario_ingreso()
    
    def _registrar_salida(self):
        """Muestra formulario para registrar salida de producto"""
        self._mostrar_formulario_salida()
    
    def _mostrar_formulario_ingreso(self):
        """Muestra ventana de selección de productos para registrar ingreso"""
        self._mostrar_selector_productos_ingreso()
    
    def _mostrar_formulario_salida(self):
        """Muestra ventana de selección de productos para registrar salida"""
        self._mostrar_selector_productos()
    
    def _mostrar_selector_productos(self):
        """Muestra ventana de selección de productos con búsqueda"""
        import tkinter as tk
        from tkinter import ttk
        
        # Crear ventana de selección
        selector_window = tk.Toplevel(self.parent_frame.winfo_toplevel())
        selector_window.title("Seleccionar Producto para Salida")
        selector_window.geometry("800x600")
        selector_window.resizable(True, True)
        selector_window.configure(bg='white')
        selector_window.minsize(700, 500)
        
        # Centrar ventana
        selector_window.transient(self.parent_frame.winfo_toplevel())
        selector_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(selector_window, bg='white')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Seleccionar Producto para Registrar Salida",
            bg='white',
            fg='#E74C3C',
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Frame de búsqueda
        search_frame = tk.Frame(main_frame, bg='white')
        search_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            search_frame,
            text="Buscar producto:",
            bg='white',
            fg='black',
            font=('Arial', 10, 'bold')
        ).pack(side='left', padx=(0, 10))
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=search_var,
            font=('Arial', 10),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#E74C3C',
            highlightbackground='#D5D5D5'
        )
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        # Frame para tabla de productos
        table_frame = tk.Frame(main_frame, bg='white')
        table_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Crear Treeview para tabla de productos
        columns = ("SKU", "Nombre", "Stock", "Precio", "Categoría", "Tienda")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        tree.heading("SKU", text="SKU")
        tree.heading("Nombre", text="Nombre")
        tree.heading("Stock", text="Stock")
        tree.heading("Precio", text="Precio")
        tree.heading("Categoría", text="Categoría")
        tree.heading("Tienda", text="Tienda")
        
        tree.column("SKU", width=100)
        tree.column("Nombre", width=200)
        tree.column("Stock", width=80)
        tree.column("Precio", width=80)
        tree.column("Categoría", width=120)
        tree.column("Tienda", width=120)
        
        # Scrollbar para tabla
        scrollbar_tree = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar_tree.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar_tree.pack(side="right", fill="y")
        
        # Frame de botones
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x')
        
        # Variables para producto seleccionado
        selected_product = {'id': None, 'data': None}
        
        def cargar_productos():
            """Carga todos los productos en la tabla"""
            # Limpiar tabla
            for item in tree.get_children():
                tree.delete(item)
            
            # Obtener productos con stock
            productos_data = self.on_action("get_productos_con_stock", {})
            if productos_data and 'productos' in productos_data:
                for producto in productos_data['productos']:
                    tree.insert("", "end", values=(
                        producto['sku'],
                        producto['nombre'],
                        f"{producto['stock']:.1f}",
                        f"${producto['precio']:.2f}",
                        producto['categoria'] or "Sin categoría",
                        producto['tienda']
                    ), tags=(producto['id'],))
        
        def filtrar_productos():
            """Filtra productos según el texto de búsqueda"""
            search_text = search_var.get().lower()
            
            # Limpiar tabla
            for item in tree.get_children():
                tree.delete(item)
            
            # Obtener productos filtrados
            productos_data = self.on_action("get_productos_con_stock", {"filtro": search_text})
            if productos_data and 'productos' in productos_data:
                for producto in productos_data['productos']:
                    tree.insert("", "end", values=(
                        producto['sku'],
                        producto['nombre'],
                        f"{producto['stock']:.1f}",
                        f"${producto['precio']:.2f}",
                        producto['categoria'] or "Sin categoría",
                        producto['tienda']
                    ), tags=(producto['id'],))
        
        def on_product_select(event):
            """Maneja la selección de un producto"""
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                product_id = item['tags'][0]
                product_data = {
                    'id': product_id,
                    'sku': item['values'][0],
                    'nombre': item['values'][1],
                    'stock': float(item['values'][2]),
                    'precio': item['values'][3],
                    'categoria': item['values'][4],
                    'tienda': item['values'][5]
                }
                selected_product['id'] = product_id
                selected_product['data'] = product_data
                
                # Habilitar botón seleccionar
                btn_seleccionar.config(state='normal')
        
        def seleccionar_producto():
            """Abre el formulario de salida con el producto seleccionado"""
            if selected_product['id']:
                selector_window.destroy()
                self._mostrar_formulario_salida_producto(selected_product['data'])
        
        def cancelar():
            """Cierra la ventana sin seleccionar"""
            selector_window.destroy()
        
        # Configurar eventos
        tree.bind("<<TreeviewSelect>>", on_product_select)
        search_var.trace("w", lambda *args: filtrar_productos())
        
        # Botones
        btn_seleccionar = tk.Button(
            button_frame,
            text="Seleccionar Producto",
            bg='#E74C3C',
            fg='white',
            font=('Arial', 11, 'bold'),
            relief='flat',
            cursor='hand2',
            command=seleccionar_producto,
            bd=0,
            padx=20,
            pady=10,
            state='disabled'
        )
        btn_seleccionar.pack(side='left', padx=(0, 10))
        
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
        def on_enter_seleccionar(e):
            if btn_seleccionar['state'] == 'normal':
                btn_seleccionar.config(bg='#C0392B')
        def on_leave_seleccionar(e):
            if btn_seleccionar['state'] == 'normal':
                btn_seleccionar.config(bg='#E74C3C')
        
        def on_enter_cancelar(e):
            btn_cancelar.config(bg='#7F8C8D')
        def on_leave_cancelar(e):
            btn_cancelar.config(bg='#95A5A6')
        
        btn_seleccionar.bind('<Enter>', on_enter_seleccionar)
        btn_seleccionar.bind('<Leave>', on_leave_seleccionar)
        btn_cancelar.bind('<Enter>', on_enter_cancelar)
        btn_cancelar.bind('<Leave>', on_leave_cancelar)
        
        # Cargar productos iniciales
        cargar_productos()
    
    def _mostrar_selector_productos_ingreso(self):
        """Muestra ventana de selección de productos para registrar ingreso"""
        import tkinter as tk
        from tkinter import ttk
        
        # Crear ventana de selección
        selector_window = tk.Toplevel(self.parent_frame.winfo_toplevel())
        selector_window.title("Seleccionar Producto para Ingreso")
        selector_window.geometry("800x600")
        selector_window.resizable(True, True)
        selector_window.configure(bg='white')
        selector_window.minsize(700, 500)
        
        # Centrar ventana
        selector_window.transient(self.parent_frame.winfo_toplevel())
        selector_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(selector_window, bg='white')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Seleccionar Producto para Registrar Ingreso",
            bg='white',
            fg='#10b981',
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Frame de búsqueda
        search_frame = tk.Frame(main_frame, bg='white')
        search_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            search_frame,
            text="Buscar producto:",
            bg='white',
            fg='black',
            font=('Arial', 10, 'bold')
        ).pack(side='left', padx=(0, 10))
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=search_var,
            font=('Arial', 10),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#10b981',
            highlightbackground='#D5D5D5'
        )
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        # Frame para tabla de productos
        table_frame = tk.Frame(main_frame, bg='white')
        table_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Crear Treeview para tabla de productos
        columns = ("SKU", "Nombre", "Categoría", "Proveedor", "Tienda", "Precio")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        tree.heading("SKU", text="SKU")
        tree.heading("Nombre", text="Nombre")
        tree.heading("Categoría", text="Categoría")
        tree.heading("Proveedor", text="Proveedor")
        tree.heading("Tienda", text="Tienda")
        tree.heading("Precio", text="Precio")
        
        tree.column("SKU", width=100)
        tree.column("Nombre", width=200)
        tree.column("Categoría", width=120)
        tree.column("Proveedor", width=120)
        tree.column("Tienda", width=120)
        tree.column("Precio", width=80)
        
        # Scrollbar para tabla
        scrollbar_tree = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar_tree.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar_tree.pack(side="right", fill="y")
        
        # Frame de botones
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x')
        
        # Variables para producto seleccionado
        selected_product = {'id': None, 'data': None}
        
        def cargar_productos():
            """Carga todos los productos en la tabla"""
            # Limpiar tabla
            for item in tree.get_children():
                tree.delete(item)
            
            # Obtener TODOS los productos (no solo los con stock)
            productos_data = self.on_action("get_view_data", {"view_name": "productos"})
            if productos_data and 'data' in productos_data:
                for producto in productos_data['data']:
                    tree.insert("", "end", values=(
                        producto['sku'],
                        producto['nombre'],
                        producto.get('categoria', 'Sin categoría'),
                        producto.get('proveedor', 'Sin proveedor'),
                        producto.get('tienda', 'N/A'),
                        f"${float(producto['precio']):.2f}"
                    ), tags=(producto['id'],))
        
        def filtrar_productos():
            """Filtra productos según el texto de búsqueda"""
            search_text = search_var.get().lower()
            
            # Limpiar tabla
            for item in tree.get_children():
                tree.delete(item)
            
            # Obtener todos los productos
            productos_data = self.on_action("get_view_data", {"view_name": "productos"})
            if productos_data and 'data' in productos_data:
                for producto in productos_data['data']:
                    # Filtrar por SKU, nombre o categoría
                    sku = producto['sku'].lower()
                    nombre = producto['nombre'].lower()
                    categoria = producto.get('categoria', '').lower()
                    
                    if search_text in sku or search_text in nombre or search_text in categoria:
                        tree.insert("", "end", values=(
                            producto['sku'],
                            producto['nombre'],
                            producto.get('categoria', 'Sin categoría'),
                            producto.get('proveedor', 'Sin proveedor'),
                            producto.get('tienda', 'N/A'),
                            f"${float(producto['precio']):.2f}"
                        ), tags=(producto['id'],))
        
        def on_product_select(event):
            """Maneja la selección de un producto"""
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                product_id = item['tags'][0]
                product_data = {
                    'id': product_id,
                    'sku': item['values'][0],
                    'nombre': item['values'][1],
                    'categoria': item['values'][2],
                    'proveedor': item['values'][3],
                    'tienda': item['values'][4],
                    'precio': item['values'][5]
                }
                selected_product['id'] = product_id
                selected_product['data'] = product_data
                
                # Habilitar botón seleccionar
                btn_seleccionar.config(state='normal')
        
        def seleccionar_producto():
            """Abre el formulario de ingreso con el producto seleccionado"""
            if selected_product['id']:
                selector_window.destroy()
                self._mostrar_formulario_ingreso_producto(selected_product['data'])
        
        def cancelar():
            """Cierra la ventana sin seleccionar"""
            selector_window.destroy()
        
        # Configurar eventos
        tree.bind("<<TreeviewSelect>>", on_product_select)
        search_var.trace("w", lambda *args: filtrar_productos())
        
        # Botones
        btn_seleccionar = tk.Button(
            button_frame,
            text="Seleccionar Producto",
            bg='#10b981',
            fg='white',
            font=('Arial', 11, 'bold'),
            relief='flat',
            cursor='hand2',
            command=seleccionar_producto,
            bd=0,
            padx=20,
            pady=10,
            state='disabled'
        )
        btn_seleccionar.pack(side='left', padx=(0, 10))
        
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
        def on_enter_seleccionar(e):
            if btn_seleccionar['state'] == 'normal':
                btn_seleccionar.config(bg='#059669')
        def on_leave_seleccionar(e):
            if btn_seleccionar['state'] == 'normal':
                btn_seleccionar.config(bg='#10b981')
        
        def on_enter_cancelar(e):
            btn_cancelar.config(bg='#7F8C8D')
        def on_leave_cancelar(e):
            btn_cancelar.config(bg='#95A5A6')
        
        btn_seleccionar.bind('<Enter>', on_enter_seleccionar)
        btn_seleccionar.bind('<Leave>', on_leave_seleccionar)
        btn_cancelar.bind('<Enter>', on_enter_cancelar)
        btn_cancelar.bind('<Leave>', on_leave_cancelar)
        
        # Cargar productos iniciales
        cargar_productos()
    
    def _mostrar_formulario_ingreso_producto(self, producto_data):
        """Muestra formulario de ingreso con producto pre-seleccionado"""
        import tkinter as tk
        from tkinter import ttk
        
        # Crear ventana de formulario con scroll
        form_window = tk.Toplevel(self.parent_frame.winfo_toplevel())
        form_window.title("Registrar Ingreso de Producto")
        form_window.geometry("500x550")
        form_window.resizable(True, True)
        form_window.configure(bg='white')
        form_window.minsize(450, 500)
        
        # Centrar ventana
        form_window.transient(self.parent_frame.winfo_toplevel())
        form_window.grab_set()
        
        # Canvas y Scrollbar para hacer scrollable
        canvas = tk.Canvas(form_window, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(form_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=20)
        scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=20)
        
        # Frame principal dentro del scrollable
        main_frame = tk.Frame(scrollable_frame, bg='white')
        main_frame.pack(expand=True, fill='both', padx=10)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Registrar Ingreso de Mercancía",
            bg='white',
            fg='#10b981',
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Información del producto seleccionado
        producto_info_frame = tk.Frame(main_frame, bg='#F0FDF4', relief='solid', bd=1)
        producto_info_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            producto_info_frame,
            text="Producto Seleccionado:",
            bg='#F0FDF4',
            fg='black',
            font=('Arial', 10, 'bold')
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        tk.Label(
            producto_info_frame,
            text=f"SKU: {producto_data['sku']}",
            bg='#F0FDF4',
            fg='black',
            font=('Arial', 10)
        ).pack(anchor='w', padx=10, pady=2)
        
        tk.Label(
            producto_info_frame,
            text=f"Nombre: {producto_data['nombre']}",
            bg='#F0FDF4',
            fg='black',
            font=('Arial', 10)
        ).pack(anchor='w', padx=10, pady=2)
        
        tk.Label(
            producto_info_frame,
            text=f"Categoría: {producto_data.get('categoria', 'Sin categoría')}",
            bg='#F0FDF4',
            fg='black',
            font=('Arial', 10)
        ).pack(anchor='w', padx=10, pady=(2, 10))
        
        # Variables para los campos
        tienda_var = tk.StringVar()
        cantidad_var = tk.StringVar()
        nota_var = tk.StringVar()
        
        # Selector de Tienda
        tienda_frame = tk.Frame(main_frame, bg='white')
        tienda_frame.pack(fill='x', pady=8)
        
        tk.Label(
            tienda_frame,
            text="Tienda Destino *",
            bg='white',
            fg='black',
            font=('Arial', 10, 'bold'),
            anchor='w'
        ).pack(fill='x', pady=(0, 3))
        
        # Obtener tiendas
        tiendas_data = self.on_action("get_tiendas_for_selector", {})
        tiendas = tiendas_data.get('tiendas', []) if tiendas_data else []
        tienda_options = [t['display'] for t in tiendas]
        
        tienda_combo = ttk.Combobox(
            tienda_frame,
            textvariable=tienda_var,
            values=tienda_options,
            state='readonly',
            font=('Arial', 10)
        )
        tienda_combo.pack(fill='x', ipady=6)
        if tienda_options:
            tienda_combo.current(0)
        
        # Cantidad
        cantidad_frame = tk.Frame(main_frame, bg='white')
        cantidad_frame.pack(fill='x', pady=8)
        
        tk.Label(
            cantidad_frame,
            text="Cantidad a Ingresar *",
            bg='white',
            fg='black',
            font=('Arial', 10, 'bold'),
            anchor='w'
        ).pack(fill='x', pady=(0, 3))
        
        cantidad_entry = tk.Entry(
            cantidad_frame,
            textvariable=cantidad_var,
            font=('Arial', 10),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#10b981',
            highlightbackground='#D5D5D5'
        )
        cantidad_entry.pack(fill='x', ipady=6)
        
        # Nota
        nota_frame = tk.Frame(main_frame, bg='white')
        nota_frame.pack(fill='x', pady=8)
        
        tk.Label(
            nota_frame,
            text="Nota (opcional)",
            bg='white',
            fg='black',
            font=('Arial', 10, 'bold'),
            anchor='w'
        ).pack(fill='x', pady=(0, 3))
        
        nota_entry = tk.Entry(
            nota_frame,
            textvariable=nota_var,
            font=('Arial', 10),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#10b981',
            highlightbackground='#D5D5D5'
        )
        nota_entry.pack(fill='x', ipady=6)
        
        # Botones
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x', pady=(20, 0))
        
        def registrar_ingreso():
            """Registra el ingreso del producto"""
            # Validar tienda
            if not tienda_var.get().strip():
                self.show_error("Error", "Debe seleccionar una tienda")
                return
            
            # Validar cantidad
            if not cantidad_var.get().strip():
                self.show_error("Error", "La cantidad es requerida")
                return
            
            try:
                cantidad_float = float(cantidad_var.get().strip())
                if cantidad_float <= 0:
                    self.show_error("Error", "La cantidad debe ser mayor a 0")
                    return
                
            except ValueError:
                self.show_error("Error", "La cantidad debe ser un número válido")
                    return
                
            # Obtener ID de tienda
            tienda_id = int(tienda_var.get().split(' - ')[0])
                
            # Registrar ingreso
                success = self.on_action("handle_view_action", {
                    "view_name": "movimientos",
                    "action": "registrar_ingreso",
                    "action_data": {
                    "producto_id": int(producto_data['id']),
                        "tienda_id": tienda_id,
                    "cantidad": cantidad_float,
                    "nota": nota_var.get().strip() or None
                    }
                })
                
                if success:
                form_window.destroy()
                self.refresh_data()
                    self.show_info("Éxito", "Ingreso registrado correctamente")
            else:
                self.show_error("Error", "No se pudo registrar el ingreso")
                    
        def cancelar():
            """Cierra el formulario sin guardar"""
            form_window.destroy()
        
        # Botón Registrar
        btn_registrar = tk.Button(
            button_frame,
            text="Registrar Ingreso",
            bg='#10b981',
            fg='white',
            font=('Arial', 11, 'bold'),
            relief='flat',
            cursor='hand2',
            command=registrar_ingreso,
            bd=0,
            padx=20,
            pady=10
        )
        btn_registrar.pack(side='left', padx=(0, 10))
        
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
        def on_enter_registrar(e):
            btn_registrar.config(bg='#059669')
        def on_leave_registrar(e):
            btn_registrar.config(bg='#10b981')
        
        def on_enter_cancelar(e):
            btn_cancelar.config(bg='#7F8C8D')
        def on_leave_cancelar(e):
            btn_cancelar.config(bg='#95A5A6')
        
        btn_registrar.bind('<Enter>', on_enter_registrar)
        btn_registrar.bind('<Leave>', on_leave_registrar)
        btn_cancelar.bind('<Enter>', on_enter_cancelar)
        btn_cancelar.bind('<Leave>', on_leave_cancelar)
        
        # Bind mousewheel para scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Unbind al cerrar ventana
        def on_closing():
            canvas.unbind_all("<MouseWheel>")
            form_window.destroy()
        
        form_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Bind mousewheel para scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Unbind al cerrar ventana
        def on_closing():
            canvas.unbind_all("<MouseWheel>")
            form_window.destroy()
        
        form_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    def _mostrar_formulario_salida_producto(self, producto_data):
        """Muestra formulario de salida con producto pre-seleccionado"""
        import tkinter as tk
        from tkinter import ttk
        
        # Crear ventana de formulario con scroll
        form_window = tk.Toplevel(self.parent_frame.winfo_toplevel())
        form_window.title("Registrar Salida de Producto")
        form_window.geometry("500x500")
        form_window.resizable(True, True)
        form_window.configure(bg='white')
        form_window.minsize(450, 450)
        
        # Centrar ventana
        form_window.transient(self.parent_frame.winfo_toplevel())
        form_window.grab_set()
        
        # Canvas y Scrollbar para hacer scrollable
        canvas = tk.Canvas(form_window, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(form_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=20)
        scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=20)
        
        # Frame principal dentro del scrollable
        main_frame = tk.Frame(scrollable_frame, bg='white')
        main_frame.pack(expand=True, fill='both', padx=10)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Registrar Salida de Producto",
            bg='white',
            fg='#E74C3C',
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Información del producto seleccionado
        producto_info_frame = tk.Frame(main_frame, bg='#F8F9FA', relief='solid', bd=1)
        producto_info_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            producto_info_frame,
            text="Producto Seleccionado:",
            bg='#F8F9FA',
            fg='black',
            font=('Arial', 10, 'bold')
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        tk.Label(
            producto_info_frame,
            text=f"SKU: {producto_data['sku']}",
            bg='#F8F9FA',
            fg='black',
            font=('Arial', 10)
        ).pack(anchor='w', padx=10, pady=2)
        
        tk.Label(
            producto_info_frame,
            text=f"Nombre: {producto_data['nombre']}",
            bg='#F8F9FA',
            fg='black',
            font=('Arial', 10)
        ).pack(anchor='w', padx=10, pady=2)
        
        tk.Label(
            producto_info_frame,
            text=f"Stock Disponible: {producto_data['stock']:.1f} unidades",
            bg='#F8F9FA',
            fg='#27AE60',
            font=('Arial', 10, 'bold')
        ).pack(anchor='w', padx=10, pady=(2, 10))
        
        # Variables para los campos
        cantidad_var = tk.StringVar()
        nota_var = tk.StringVar()
        
        # Cantidad
        cantidad_frame = tk.Frame(main_frame, bg='white')
        cantidad_frame.pack(fill='x', pady=8)
        
        tk.Label(
            cantidad_frame,
            text="Cantidad a Retirar *",
            bg='white',
            fg='black',
            font=('Arial', 10, 'bold'),
            anchor='w'
        ).pack(fill='x', pady=(0, 3))
        
        cantidad_entry = tk.Entry(
            cantidad_frame,
            textvariable=cantidad_var,
            font=('Arial', 10),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#E74C3C',
            highlightbackground='#D5D5D5'
        )
        cantidad_entry.pack(fill='x', ipady=6)
        
        # Nota
        nota_frame = tk.Frame(main_frame, bg='white')
        nota_frame.pack(fill='x', pady=8)
        
        tk.Label(
            nota_frame,
            text="Nota (opcional)",
            bg='white',
            fg='black',
            font=('Arial', 10, 'bold'),
            anchor='w'
        ).pack(fill='x', pady=(0, 3))
        
        nota_entry = tk.Entry(
            nota_frame,
            textvariable=nota_var,
            font=('Arial', 10),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#E74C3C',
            highlightbackground='#D5D5D5'
        )
        nota_entry.pack(fill='x', ipady=6)
        
        # Botones
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x', pady=(20, 0))
        
        def registrar_salida():
            """Registra la salida del producto"""
            # Validar cantidad
            if not cantidad_var.get().strip():
                self.show_error("Error", "La cantidad es requerida")
                return
            
            try:
                cantidad_float = float(cantidad_var.get().strip())
                if cantidad_float <= 0:
                    self.show_error("Error", "La cantidad debe ser mayor a 0")
                    return
                
                if cantidad_float > producto_data['stock']:
                    self.show_error("Error", f"Stock insuficiente. Disponible: {producto_data['stock']:.1f}")
                    return
                    
            except ValueError:
                self.show_error("Error", "La cantidad debe ser un número válido")
                return
            
            # Registrar salida
            success = self.on_action("handle_view_action", {
                "view_name": "movimientos",
                "action": "registrar_salida",
                "action_data": {
                    "producto_id": int(producto_data['id']),
                    "cantidad": cantidad_float,
                    "nota": nota_var.get().strip() or None
                }
            })
            
            if success:
                form_window.destroy()
                self.refresh_data()
                self.show_info("Éxito", "Salida registrada correctamente")
            else:
                self.show_error("Error", "No se pudo registrar la salida")
        
        def cancelar():
            """Cierra el formulario sin guardar"""
            form_window.destroy()
        
        # Botón Registrar
        btn_registrar = tk.Button(
            button_frame,
            text="Registrar Salida",
            bg='#E74C3C',
            fg='white',
            font=('Arial', 11, 'bold'),
            relief='flat',
            cursor='hand2',
            command=registrar_salida,
            bd=0,
            padx=20,
            pady=10
        )
        btn_registrar.pack(side='left', padx=(0, 10))
        
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
        def on_enter_registrar(e):
            btn_registrar.config(bg='#C0392B')
        def on_leave_registrar(e):
            btn_registrar.config(bg='#E74C3C')
        
        def on_enter_cancelar(e):
            btn_cancelar.config(bg='#7F8C8D')
        def on_leave_cancelar(e):
            btn_cancelar.config(bg='#95A5A6')
        
        btn_registrar.bind('<Enter>', on_enter_registrar)
        btn_registrar.bind('<Leave>', on_leave_registrar)
        btn_cancelar.bind('<Enter>', on_enter_cancelar)
        btn_cancelar.bind('<Leave>', on_leave_cancelar)
        
        # Bind mousewheel para scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Unbind al cerrar ventana
        def on_closing():
            canvas.unbind_all("<MouseWheel>")
            form_window.destroy()
        
        form_window.protocol("WM_DELETE_WINDOW", on_closing)