# ==============================
# File: main.py
# ==============================
"""
Aplicación principal del Sistema de Inventario Multitienda
Ahora usa la arquitectura MVC para mejor organización y mantenibilidad
"""

from inventory_app.infra.db import init_db
from inventory_app.infra.sqlite_repos import (
    SQLiteRepoUsuarios,
    SQLiteRepoTiendas,
    SQLiteRepoProductos,
    SQLiteRepoInventario,
    SQLiteRepoEmpleados,
)
from inventory_app.services.inventory_service import InventarioService
from inventory_app.mvc.models import InventoryModels, UserModels
from inventory_app.mvc.controllers import DashboardController
from inventory_app.mvc.views import DashboardView
from inventory_app.domain.models import Usuario
import tkinter as tk
from tkinter import ttk, messagebox


class MVCApp:
    """Aplicación principal usando arquitectura MVC"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.inventory_service = None
        self.inventory_models = None
        self.user_models = None
        self.dashboard_controller = None
        self.dashboard_view = None
        self.current_user = None
        
        self._initialize_services()
        self._build_login()
    
    def _initialize_services(self):
        """Inicializa los servicios y modelos"""
        # Inicializar base de datos
        init_db()
        
        # Crear servicios
        self.inventory_service = InventarioService(
            SQLiteRepoUsuarios(),
            SQLiteRepoTiendas(),
            SQLiteRepoProductos(),
            SQLiteRepoInventario(),
            SQLiteRepoEmpleados(),
        )
        
        # Crear modelos MVC
        self.inventory_models = InventoryModels(self.inventory_service)
        self.user_models = UserModels()
        
        # Cargar datos de demo
        self._bootstrap_demo_data()
    
    def _bootstrap_demo_data(self):
        """Carga datos de demostración"""
        # Crear demo si no hay tiendas
        if not self.inventory_service.listar_tiendas():
            # Crear tiendas de demo
            t1 = self.inventory_service.crear_tienda("Tienda Centro", "Av. Principal 123")
            t2 = self.inventory_service.crear_tienda("Tienda Norte", "Av. Norte 456")
            t3 = self.inventory_service.crear_tienda("Tienda Sur", "Av. Sur 789")
            
            # Crear almacenes
            a1 = self.inventory_service.crear_almacen(t1.id, "Almacén Principal")
            a2 = self.inventory_service.crear_almacen(t2.id, "Almacén Norte")
            a3 = self.inventory_service.crear_almacen(t3.id, "Almacén Sur")
            
            # Crear productos
            self.inventory_service.crear_producto("ARROZ01", "Arroz Costeño 1kg", "Arroz blanco de alta calidad", "un", 4.50, "Granos", "Costeño", 5, 1)
            self.inventory_service.crear_producto("AZUCAR1", "Azúcar Rubia 1kg", "Azúcar de caña natural", "un", 3.80, "Endulzantes", "Laredo", 3, 1)
            self.inventory_service.crear_producto("LECHE01", "Leche Gloria Lata", "Leche evaporada", "un", 4.20, "Lácteos", "Gloria", 2, 2)
            self.inventory_service.crear_producto("ACEITE1", "Aceite Primor 900ml", "Aceite vegetal para cocinar", "un", 8.50, "Aceites", "Primor", 3, 2)
            self.inventory_service.crear_producto("ATUN01", "Atún Primor 170g", "Atún en aceite", "un", 3.20, "Conservas", "Primor", 4, 1)
            
            # Crear usuarios de demo
            from inventory_app.infra.db import get_conn, _hash_pw
            with get_conn() as c:
                # Admin ya existe por defecto
                c.execute(
                    "INSERT OR IGNORE INTO usuarios(username, pw_hash, rol, activo) VALUES (?,?,?,?)",
                    ("operador1", _hash_pw("123"), "OPERADOR", 1)
                )
                c.execute(
                    "INSERT OR IGNORE INTO usuarios(username, pw_hash, rol, activo) VALUES (?,?,?,?)",
                    ("operador2", _hash_pw("123"), "OPERADOR", 1)
                )
            
            u = SQLiteRepoUsuarios().autenticar("admin", "admin")
            # Ingresos iniciales + mínimos
            for sku, cant, minv in [("ARROZ01", 30, 5), ("AZUCAR1", 10, 5), ("LECHE01", 0, 2), ("ACEITE1", 15, 3), ("ATUN01", 20, 4)]:
                p = SQLiteRepoProductos().buscar_por_sku(sku)
                if cant != 0:
                    SQLiteRepoInventario().ajustar_stock(a1.id, p.id, cant, u.id, nota="Carga inicial")
                    SQLiteRepoInventario().ajustar_stock(a2.id, p.id, cant//2, u.id, nota="Carga inicial")
                    SQLiteRepoInventario().ajustar_stock(a3.id, p.id, cant//3, u.id, nota="Carga inicial")
                SQLiteRepoInventario().set_minimo(a1.id, p.id, minv)
                SQLiteRepoInventario().set_minimo(a2.id, p.id, minv)
                SQLiteRepoInventario().set_minimo(a3.id, p.id, minv)
    
    def _build_login(self):
        """Construye la interfaz de login con estilo moderno"""
        # Configurar ventana principal
        self.root.title("Sistema de Inventario Multitienda")
        self.root.geometry("400x580")
        self.root.resizable(False, False)
        self.root.configure(bg='white')
        
        # Crear frame principal
        self.login_frame = tk.Frame(self.root, bg='white')
        self.login_frame.pack(expand=True, fill='both')
        
        # Crear barra de título
        self._create_title_bar()
        
        # Crear contenido principal
        self._create_login_content()
    
    def _create_title_bar(self):
        """Crea la barra de título azul"""
        title_frame = tk.Frame(self.login_frame, bg='#2E86C1', height=50)
        title_frame.pack(fill='x', side='top')
        title_frame.pack_propagate(False)
        
        # Título
        title_label = tk.Label(
            title_frame, 
            text="Sistema de Inventario Multitienda",
            bg='#2E86C1',
            fg='white',
            font=('Arial', 14, 'bold')
        )
        title_label.pack(expand=True)
                
    
    def _create_login_content(self):
        """Crea el contenido del formulario de login"""
        content_frame = tk.Frame(self.login_frame, bg='white')
        content_frame.pack(expand=True, fill='both', padx=50, pady=30)
        
        # Campo Usuario
        user_frame = tk.Frame(content_frame, bg='white')
        user_frame.pack(fill='x', pady=15)
        
        user_label = tk.Label(
            user_frame,
            text="Usuario",
            bg='white',
            fg='black',
            font=('Arial', 10),
            anchor='w'
        )
        user_label.pack(fill='x', pady=(0, 5))
        
        self.ent_user = tk.Entry(
            user_frame,
            font=('Arial', 10),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#2E86C1',
            highlightbackground='#D5D5D5'
        )
        self.ent_user.pack(fill='x', ipady=8)
        
        # Campo Contraseña
        password_frame = tk.Frame(content_frame, bg='white')
        password_frame.pack(fill='x', pady=15)
        
        password_label = tk.Label(
            password_frame,
            text="Contraseña",
            bg='white',
            fg='black',
            font=('Arial', 10),
            anchor='w'
        )
        password_label.pack(fill='x', pady=(0, 5))
        
        self.ent_pw = tk.Entry(
            password_frame,
            font=('Arial', 10),
            show="*",
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#2E86C1',
            highlightbackground='#D5D5D5'
        )
        self.ent_pw.pack(fill='x', ipady=8)
        
        # Campo Tienda
        store_frame = tk.Frame(content_frame, bg='white')
        store_frame.pack(fill='x', pady=15)
        
        store_label = tk.Label(
            store_frame,
            text="Tienda",
            bg='white',
            fg='black',
            font=('Arial', 10),
            anchor='w'
        )
        store_label.pack(fill='x', pady=(0, 5))
        
        # Obtener tiendas disponibles
        tiendas = self.inventory_service.listar_tiendas()
        store_options = [t.nombre for t in tiendas] if tiendas else ["Centro"]
        
        self.store_var = tk.StringVar(value=store_options[0] if store_options else "Centro")
        self.store_combo = ttk.Combobox(
            store_frame,
            textvariable=self.store_var,
            values=store_options,
            font=('Arial', 10),
            state='readonly'
        )
        self.store_combo.pack(fill='x', ipady=8)
        
        # Botón de login
        login_btn = tk.Button(
            content_frame,
            text="Iniciar sesión",
            bg='#2E86C1',
            fg='white',
            font=('Arial', 11, 'bold'),
            relief='flat',
            cursor='hand2',
            command=self._do_login,
            bd=0,
            padx=20,
            pady=12
        )
        login_btn.pack(fill='x', pady=(30, 0))
        
        # Efecto hover para el botón
        def on_enter(e):
            login_btn.config(bg='#3498DB')
        
        def on_leave(e):
            login_btn.config(bg='#2E86C1')
        
        login_btn.bind('<Enter>', on_enter)
        login_btn.bind('<Leave>', on_leave)
        
        # Información de usuario por defecto
        info_label = tk.Label(
            content_frame,
            text="Usuario por defecto: admin / admin",
            bg='white',
            fg='#7F8C8D',
            font=('Arial', 9)
        )
        info_label.pack(pady=(20, 0))
        
        # Permitir login con Enter
        self.root.bind('<Return>', lambda e: self._do_login())
    
    def _do_login(self):
        """Maneja el proceso de login"""
        username = self.ent_user.get().strip()
        password = self.ent_pw.get().strip()
        
        # Autenticar usuario
        user_model = self.user_models.authenticate_user(username, password)
        if not user_model:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos")
            return
        
        # Convertir a modelo de dominio
        self.current_user = Usuario(
            id=user_model.id,
            username=user_model.username,
            rol=user_model.rol,
            activo=user_model.activo
        )
        
        # Limpiar login y crear dashboard
        self.login_frame.destroy()
        self._create_dashboard()
    
    def _create_dashboard(self):
        """Crea el dashboard MVC"""
        # Crear controlador
        self.dashboard_controller = DashboardController(
            self.inventory_models,
            self.user_models,
            self.current_user
        )
        
        # Crear vista
        self.dashboard_view = DashboardView(
            self.root,
            self.dashboard_controller,
            self._handle_dashboard_action
        )
    
    def _handle_dashboard_action(self, action: str, data: dict) -> any:
        """Maneja las acciones del dashboard"""
        try:
            if action == "get_dashboard_data":
                return self.dashboard_controller.get_data()
            elif action == "get_user_info":
                return self.dashboard_controller.get_user_info()
            elif action == "get_tiendas_for_selector":
                return {"tiendas": self.dashboard_controller.get_data()['tiendas']}
            elif action == "get_view_data":
                return self.dashboard_controller._get_view_data(data)
            elif action == "get_alerts":
                alerts = self.dashboard_controller.reportes_controller.get_alerts()
                return {"alerts": alerts}
            elif action == "switch_view":
                return self.dashboard_controller._switch_view(data)
            elif action == "handle_view_action":
                return self.dashboard_controller._handle_view_action(data)
            else:
                return None
        except Exception as e:
            messagebox.showerror("Error", f"Error en acción {action}: {str(e)}")
            return None
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()


def main():
    """Función principal"""
    app = MVCApp()
    app.run()


if __name__ == "__main__":
    main()