# ==============================
# File: inventory_app/services/inventory_service.py
# ==============================
from __future__ import annotations
from typing import List, Optional
import sqlite3

from ..domain.models import Usuario, Tienda, Producto, Empleado
from ..domain.interfaces import RepoUsuarios, RepoTiendas, RepoProductos, RepoInventario, RepoEmpleados, Reporte
from .reports import ReporteTablaTexto


class InventarioService:
    def __init__(self, ru: RepoUsuarios, rt: RepoTiendas, rp: RepoProductos, ri: RepoInventario, re: RepoEmpleados):
        self._ru = ru
        self._rt = rt
        self._rp = rp
        self._ri = ri
        self._re = re

    # Auth
    def login(self, username: str, password: str) -> Optional[Usuario]:
        return self._ru.autenticar(username, password)

    # Tiendas / Almacenes
    def crear_tienda(self, nombre: str, direccion: Optional[str] = None,
                     telefono: Optional[str] = None, email: Optional[str] = None,
                     responsable_id: Optional[int] = None) -> Tienda:
        return self._rt.crear_tienda(nombre, direccion, telefono, email, responsable_id)

    def listar_tiendas(self) -> List[Tienda]:
        return self._rt.listar_tiendas()
    
    def actualizar_tienda(self, tienda_id: int, nombre: str, direccion: Optional[str] = None,
                         telefono: Optional[str] = None, email: Optional[str] = None,
                         responsable_id: Optional[int] = None) -> bool:
        """Actualiza una tienda"""
        return self._rt.actualizar_tienda(tienda_id, nombre, direccion, telefono, email, responsable_id)
    
    def eliminar_tienda(self, tienda_id: int) -> bool:
        """Elimina una tienda"""
        # Validaciones de negocio
        tiendas = self._rt.listar_tiendas()
        if len(tiendas) <= 1:
            raise ValueError("No se puede eliminar la única tienda")
        return self._rt.eliminar_tienda(tienda_id)


    # Productos
    def crear_producto(self, sku: str, nombre: str, descripcion: Optional[str], unidad: str, precio: float, 
                      categoria: Optional[str], proveedor: Optional[str], stock_minimo: int = 0, tienda_id: int = 1) -> Producto:
        # Crear el producto
        producto = self._rp.crear_producto(sku, nombre, descripcion, unidad, precio, categoria, proveedor, stock_minimo, tienda_id)
        
        # Inicializar stock en la tienda
        self._inicializar_stock_producto(producto.id, tienda_id, stock_minimo)
        
        return producto
    
    def _inicializar_stock_producto(self, producto_id: int, tienda_id: int, stock_inicial: int = 0):
        """Inicializa el stock de un producto en la tienda"""
        try:
            # Inicializar stock directamente en la tienda
            self._ri.set_minimo(tienda_id, producto_id, stock_inicial)
            if stock_inicial > 0:
                # Si hay stock inicial, registrarlo como ingreso
                self._ri.ajustar_stock(tienda_id, producto_id, stock_inicial, 1, "Stock inicial")
                
        except Exception as e:
            print(f"Error al inicializar stock del producto {producto_id}: {e}")

    def listar_productos(self, q: str = "") -> List[Producto]:
        return self._rp.listar_productos(q)
    
    def buscar_productos_con_stock(self, filtro: str = "", stock_mayor_a: float = 0):
        """Busca productos que tengan stock disponible"""
        return self._rp.buscar_con_stock(filtro, stock_mayor_a)
    
    def actualizar_producto(self, producto_id: int, sku: str, nombre: str, descripcion: Optional[str], 
                           unidad: str, precio: float, categoria: Optional[str], proveedor: Optional[str], 
                           stock_minimo: int = 0, activo: bool = True, tienda_id: int = 1) -> bool:
        return self._rp.actualizar_producto(producto_id, sku, nombre, descripcion, unidad, precio, categoria, proveedor, stock_minimo, activo, tienda_id)
    
    def eliminar_producto(self, producto_id: int) -> bool:
        return self._rp.eliminar_producto(producto_id)

    # Stock & movimientos
    def set_minimo(self, tienda_id: int, producto_id: int, minimo: float) -> None:
        self._ri.set_minimo(tienda_id, producto_id, minimo)

    def ingresar(self, tienda_id: int, producto_id: int, cantidad: float, usuario_id: int, nota: str | None = None) -> None:
        self._ri.ajustar_stock(tienda_id, producto_id, abs(cantidad), usuario_id, nota)

    def egresar(self, tienda_id: int, producto_id: int, cantidad: float, usuario_id: int, nota: str | None = None) -> None:
        self._ri.ajustar_stock(tienda_id, producto_id, -abs(cantidad), usuario_id, nota)

    def reporte_stock(self, tienda_id: int, renderer: Reporte | None = None) -> str:
        filas = self._ri.reporte_stock(tienda_id)
        renderer = renderer or ReporteTablaTexto()
        return renderer.render(filas)

    def items_bajo_minimo(self, tienda_id: int):
        filas = self._ri.reporte_stock(tienda_id)
        return [r for r in filas if r["estado"] in ("SIN STOCK", "BAJO MINIMO")]
    
    def obtener_movimientos(self, tienda_id: Optional[int] = None, limit: int = 200):
        """Obtiene movimientos con información completa"""
        return self._ri.obtener_movimientos(tienda_id, limit)

    # Empleados
    def crear_empleado(self, usuario_id: int, nombres: str, apellidos: str, dni: str, jornada: str, tienda_id: int) -> Empleado:
        return self._re.crear_empleado(usuario_id, nombres, apellidos, dni, jornada, tienda_id)

    def listar_empleados(self) -> List[Empleado]:
        return self._re.listar_empleados()

    def obtener_empleado_por_usuario(self, usuario_id: int) -> Optional[Empleado]:
        return self._re.obtener_empleado_por_usuario(usuario_id)

    def actualizar_empleado(self, empleado_id: int, nombres: str, apellidos: str, dni: str, jornada: str, tienda_id: int) -> bool:
        return self._re.actualizar_empleado(empleado_id, nombres, apellidos, dni, jornada, tienda_id)

    def eliminar_empleado(self, empleado_id: int) -> bool:
        return self._re.eliminar_empleado(empleado_id)

    # Método para crear empleado completo (usuario + empleado)
    def crear_empleado_completo(self, username: str, password: str, rol: str, 
                               nombres: str, apellidos: str, dni: str, 
                               jornada: str, tienda_id: int) -> tuple[Usuario, Empleado]:
        """Crea un usuario y su información de empleado en una sola operación"""
        # 1. Crear usuario
        usuario = self._ru.crear_usuario(username, password, rol)
        
        # 2. Crear empleado con la información adicional
        empleado = self._re.crear_empleado(
            usuario.id, nombres, apellidos, dni, jornada, tienda_id
        )
        
        return usuario, empleado
    
    def obtener_empleado_por_id(self, empleado_id: int) -> Optional[Empleado]:
        """Obtiene un empleado por su ID"""
        return self._re.obtener_empleado_por_id(empleado_id)