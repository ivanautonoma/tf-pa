# ==============================
# File: inventory_app/domain/models.py
# ==============================
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Usuario:
    id: int
    username: str
    rol: str  # 'ADMIN' | 'OPERADOR'
    activo: bool


@dataclass
class Tienda:
    id: int
    nombre: str
    direccion: Optional[str]


@dataclass
class Producto:
    id: int
    sku: str
    nombre: str
    descripcion: Optional[str]
    unidad: str
    precio_unit: float
    categoria: Optional[str]
    proveedor: Optional[str]
    stock_minimo: int
    activo: bool
    tienda_id: int


@dataclass
class Empleado:
    id: int
    usuario_id: int
    nombres: str
    apellidos: str
    dni: str
    jornada: str  # 'COMPLETA' | 'MEDIA' | 'PARCIAL'
    tienda_id: int