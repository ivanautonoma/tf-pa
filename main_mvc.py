# ==============================
# File: main_mvc.py
# ==============================
from inventory_app.infra.db import init_db
from inventory_app.infra.sqlite_repos import (
    SQLiteRepoUsuarios,
    SQLiteRepoTiendas,
    SQLiteRepoProductos,
    SQLiteRepoInventario,
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
            self.inventory_service.crear_producto("ARROZ01", "Arroz Costeño 1kg", "un", 4.50)
            self.inventory_service.crear_producto("AZUCAR1", "Azúcar Rubia 1kg", "un", 3.80)
            self.inventory_service.crear_producto("LECHE01", "Leche Gloria Lata", "un", 4.20)
            self.inventory_service.crear_producto("ACEITE1", "Aceite Primor 900ml", "un", 8.50)
            self.inventory_service.crear_producto("ATUN01", "Atún Primor 170g", "un", 3.20)
            
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
        """Construye la interfaz de login"""
        self.login_frame = ttk.Frame(self.root)
        self.login_frame.pack(expand=True)
        
        ttk.Label(self.login_frame, text="Usuario").grid(row=0, column=0, pady=5, padx=5, sticky="e")
        ttk.Label(self.login_frame, text="Contraseña").grid(row=1, column=0, pady=5, padx=5, sticky="e")
        
        self.ent_user = ttk.Entry(self.login_frame)
        self.ent_pw = ttk.Entry(self.login_frame, show="*")
        self.ent_user.grid(row=0, column=1, pady=5)
        self.ent_pw.grid(row=1, column=1, pady=5)
        
        ttk.Button(self.login_frame, text="Ingresar", command=self._do_login).grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Label(self.login_frame, text="Usuario por defecto: admin / admin").grid(row=3, column=0, columnspan=2, pady=5)
    
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
