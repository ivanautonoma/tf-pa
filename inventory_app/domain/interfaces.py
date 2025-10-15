# ==============================
# File: inventory_app/domain/interfaces.py
# ==============================
from __future__ import annotations
from typing import List, Optional, Iterable, Protocol, Tuple
from abc import ABC, abstractmethod
import sqlite3

from .models import Usuario, Tienda, Producto, Empleado


class RepoUsuarios(ABC):
    @abstractmethod
    def autenticar(self, username: str, password: str) -> Optional[Usuario]: ...
    
    @abstractmethod
    def crear_usuario(self, username: str, password: str, rol: str) -> Usuario: ...
    
    @abstractmethod
    def listar_usuarios(self) -> List[Usuario]: ...
    
    @abstractmethod
    def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Usuario]: ...


class RepoEmpleados(ABC):
    @abstractmethod
    def crear_empleado(self, usuario_id: int, nombres: str, apellidos: str, dni: str, jornada: str, tienda_id: int) -> Empleado: ...
    
    @abstractmethod
    def listar_empleados(self) -> List[Empleado]: ...
    
    @abstractmethod
    def obtener_empleado_por_usuario(self, usuario_id: int) -> Optional[Empleado]: ...
    
    @abstractmethod
    def actualizar_empleado(self, empleado_id: int, nombres: str, apellidos: str, dni: str, jornada: str, tienda_id: int) -> bool: ...
    
    @abstractmethod
    def eliminar_empleado(self, empleado_id: int) -> bool: ...


class RepoTiendas(ABC):
    @abstractmethod
    def crear_tienda(self, nombre: str, direccion: Optional[str]) -> Tienda: ...

    @abstractmethod
    def listar_tiendas(self) -> List[Tienda]: ...


class RepoProductos(ABC):
    @abstractmethod
    def crear_producto(self, sku: str, nombre: str, descripcion: Optional[str], unidad: str, precio: float, 
                      categoria: Optional[str], proveedor: Optional[str], stock_minimo: int = 0, tienda_id: int = 1) -> Producto: ...

    @abstractmethod
    def buscar_por_sku(self, sku: str) -> Optional[Producto]: ...

    @abstractmethod
    def listar_productos(self, q: str = "") -> List[Producto]: ...
    
    @abstractmethod
    def actualizar_producto(self, producto_id: int, sku: str, nombre: str, descripcion: Optional[str], 
                           unidad: str, precio: float, categoria: Optional[str], proveedor: Optional[str], 
                           stock_minimo: int = 0, activo: bool = True, tienda_id: int = 1) -> bool: ...
    
    @abstractmethod
    def eliminar_producto(self, producto_id: int) -> bool: ...


class RepoInventario(ABC):
    @abstractmethod
    def set_minimo(self, tienda_id: int, producto_id: int, minimo: float) -> None: ...

    @abstractmethod
    def ajustar_stock(self, tienda_id: int, producto_id: int, delta: float, usuario_id: int, nota: Optional[str] = None) -> None: ...

    @abstractmethod
    def obtener_stock(self, tienda_id: int, producto_id: int) -> Tuple[float, float]: ...

    @abstractmethod
    def reporte_stock(self, tienda_id: int) -> List[sqlite3.Row]: ...


class Reporte(Protocol):
    def render(self, filas: Iterable[sqlite3.Row]) -> str: ...