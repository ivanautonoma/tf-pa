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
from inventory_app.services.usuarios_service import UsuariosService
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
        
        self.user_service = UsuariosService(SQLiteRepoUsuarios())
        
        # Crear modelos MVC
        self.inventory_models = InventoryModels(self.inventory_service)
        self.user_models = UserModels(self.user_service)
        
        # Cargar datos de demo
        self._bootstrap_demo_data()
    
    def _bootstrap_demo_data(self):
        """Carga datos de demostración con nuevo sistema de roles"""
        # Crear demo si no hay tiendas
        if not self.inventory_service.listar_tiendas():
            from inventory_app.infra.db import get_conn, _hash_pw
            
            # 1. Crear tiendas (sin responsable aún, se asignará después)
            t1 = self.inventory_service.crear_tienda("Tienda Centro", "Av. Principal 123, Lima", "01-234-5678", "centro@tienda.com")
            t2 = self.inventory_service.crear_tienda("Tienda Norte", "Av. Túpac Amaru 456, Lima", "01-345-6789", "norte@tienda.com")
            t3 = self.inventory_service.crear_tienda("Tienda Sur", "Av. Aviación 789, Lima", "01-456-7890", "sur@tienda.com")
            
            # 2. Crear usuarios con nuevos roles
            with get_conn() as c:
                # Encargados
                c.execute(
                    "INSERT OR IGNORE INTO usuarios(username, pw_hash, rol, activo) VALUES (?,?,?,?)",
                    ("carlos", _hash_pw("123"), "ENCARGADO", 1)
                )
                c.execute(
                    "INSERT OR IGNORE INTO usuarios(username, pw_hash, rol, activo) VALUES (?,?,?,?)",
                    ("maria", _hash_pw("123"), "ENCARGADO", 1)
                )
                # Vendedores
                c.execute(
                    "INSERT OR IGNORE INTO usuarios(username, pw_hash, rol, activo) VALUES (?,?,?,?)",
                    ("juan", _hash_pw("123"), "VENDEDOR", 1)
                )
                c.execute(
                    "INSERT OR IGNORE INTO usuarios(username, pw_hash, rol, activo) VALUES (?,?,?,?)",
                    ("ana", _hash_pw("123"), "VENDEDOR", 1)
                )
            
            # 3. Crear empleados
            u_carlos = SQLiteRepoUsuarios().autenticar("carlos", "123")
            u_maria = SQLiteRepoUsuarios().autenticar("maria", "123")
            u_juan = SQLiteRepoUsuarios().autenticar("juan", "123")
            u_ana = SQLiteRepoUsuarios().autenticar("ana", "123")
            
            e_carlos = self.inventory_service.crear_empleado(u_carlos.id, "Carlos", "Rodríguez", "12345678", "COMPLETA", t1.id)
            e_maria = self.inventory_service.crear_empleado(u_maria.id, "María", "González", "87654321", "COMPLETA", t2.id)
            e_juan = self.inventory_service.crear_empleado(u_juan.id, "Juan", "Pérez", "11223344", "COMPLETA", t3.id)
            e_ana = self.inventory_service.crear_empleado(u_ana.id, "Ana", "Torres", "55667788", "MEDIA", t1.id)
            
            # Asignar responsables a las tiendas (Carlos y María son ENCARGADOS)
            with get_conn() as c:
                c.execute("UPDATE tiendas SET responsable_id=? WHERE id=?", (e_carlos.id, t1.id))
                c.execute("UPDATE tiendas SET responsable_id=? WHERE id=?", (e_maria.id, t2.id))
                # t3 (Tienda Sur) queda sin responsable por ahora (Juan es VENDEDOR)
            
            # 4. Crear productos
            # Tienda Centro
            p1 = self.inventory_service.crear_producto("ARR001", "Arroz Costeño 1kg", "Arroz blanco de primera", "kg", 4.50, "Granos", "Costeño", 10, t1.id)
            p2 = self.inventory_service.crear_producto("AZU001", "Azúcar Rubia 1kg", "Azúcar de caña", "kg", 3.80, "Endulzantes", "Laredo", 8, t1.id)
            p3 = self.inventory_service.crear_producto("ACE001", "Aceite Primor 1L", "Aceite vegetal", "L", 9.50, "Aceites", "Primor", 5, t1.id)
            # Tienda Norte
            p4 = self.inventory_service.crear_producto("LEC001", "Leche Gloria Lata", "Leche evaporada", "lata", 4.20, "Lácteos", "Gloria", 12, t2.id)
            p5 = self.inventory_service.crear_producto("ATU001", "Atún Florida 170g", "Atún en aceite", "lata", 3.50, "Conservas", "Florida", 15, t2.id)
            p6 = self.inventory_service.crear_producto("FID001", "Fideos Don Vittorio 1kg", "Fideos tallarin", "kg", 3.20, "Pastas", "Don Vittorio", 10, t2.id)
            # Tienda Sur
            p7 = self.inventory_service.crear_producto("GAL001", "Galletas Soda 6pack", "Galletas saladas", "pack", 5.80, "Galletas", "Field", 8, t3.id)
            p8 = self.inventory_service.crear_producto("JAB001", "Jabón Bolívar 3pack", "Jabón de tocador", "pack", 4.50, "Limpieza", "Bolívar", 6, t3.id)
            
            # 5. Registrar stock inicial (simulando que lo hacen los encargados)
            self.inventory_service.ingresar(t1.id, p1.id, 50, u_carlos.id, "Recepción de mercancía")
            self.inventory_service.ingresar(t1.id, p2.id, 30, u_carlos.id, "Recepción de mercancía")
            self.inventory_service.ingresar(t1.id, p3.id, 25, u_carlos.id, "Recepción de mercancía")
            
            self.inventory_service.ingresar(t2.id, p4.id, 40, u_maria.id, "Recepción de mercancía")
            self.inventory_service.ingresar(t2.id, p5.id, 8, u_maria.id, "Recepción de mercancía")
            self.inventory_service.ingresar(t2.id, p6.id, 25, u_maria.id, "Recepción de mercancía")
            
            # Admin registra para Tienda Sur
            u_admin = SQLiteRepoUsuarios().autenticar("admin", "admin")
            self.inventory_service.ingresar(t3.id, p7.id, 15, u_admin.id, "Recepción de mercancía")
            # p8 sin stock inicial (ejemplo de SIN STOCK)
            
            # 6. Registrar algunas ventas (simulando vendedores)
            self.inventory_service.egresar(t1.id, p1.id, 5, u_ana.id, "Venta a cliente")
            self.inventory_service.egresar(t1.id, p2.id, 3, u_ana.id, "Venta a cliente")
            self.inventory_service.egresar(t3.id, p7.id, 4, u_juan.id, "Venta a cliente")
    
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
            elif action == "get_productos_con_stock":
                return self.dashboard_controller.movimientos_controller.get_productos_con_stock(data.get('filtro', ''))
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