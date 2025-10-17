# ==============================
# File: inventory_app/mvc/models/inventory_models.py
# ==============================
from __future__ import annotations
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from ...domain.models import Tienda, Producto
from ...services.inventory_service import InventarioService


@dataclass
class TiendaModel:
    """Modelo de datos para tiendas"""
    id: int
    nombre: str
    direccion: Optional[str]
    telefono: Optional[str] = None
    email: Optional[str] = None
    responsable_id: Optional[int] = None
    
    @classmethod
    def from_domain(cls, tienda: Tienda) -> 'TiendaModel':
        return cls(
            id=tienda.id,
            nombre=tienda.nombre,
            direccion=tienda.direccion,
            telefono=tienda.telefono,
            email=tienda.email,
            responsable_id=tienda.responsable_id
        )


@dataclass
class ProductoModel:
    """Modelo de datos para productos"""
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
    
    @classmethod
    def from_domain(cls, producto: Producto) -> 'ProductoModel':
        return cls(
            id=producto.id,
            sku=producto.sku,
            nombre=producto.nombre,
            descripcion=producto.descripcion,
            unidad=producto.unidad,
            precio_unit=producto.precio_unit,
            categoria=producto.categoria,
            proveedor=producto.proveedor,
            stock_minimo=producto.stock_minimo,
            activo=producto.activo,
            tienda_id=producto.tienda_id
        )


@dataclass
class MovimientoModel:
    """Modelo de datos para movimientos de inventario"""
    id: int
    producto_id: int
    producto_sku: str
    producto_nombre: str
    tipo: str  # INGRESO o SALIDA
    cantidad: float
    usuario_id: int
    usuario_nombre: str
    tienda_nombre: str
    fecha: str
    nota: Optional[str]


@dataclass
class StockModel:
    """Modelo de datos para stock"""
    tienda: str
    producto_sku: str
    producto_nombre: str
    cantidad: float
    minimo: float
    estado: str  # OK, BAJO MINIMO, SIN STOCK


class InventoryModels:
    """Clase que maneja todos los modelos de inventario"""
    
    def __init__(self, inventory_service: InventarioService):
        self.inventory_service = inventory_service
    
    # Tiendas
    def get_tiendas(self) -> List[TiendaModel]:
        """Obtiene todas las tiendas"""
        tiendas = self.inventory_service.listar_tiendas()
        return [TiendaModel.from_domain(t) for t in tiendas]
    
    def create_tienda(self, nombre: str, direccion: Optional[str] = None,
                      telefono: Optional[str] = None, email: Optional[str] = None,
                      responsable_id: Optional[int] = None) -> TiendaModel:
        """Crea una nueva tienda"""
        tienda = self.inventory_service.crear_tienda(nombre, direccion, telefono, email, responsable_id)
        return TiendaModel.from_domain(tienda)
    
    def update_tienda(self, tienda_id: int, nombre: str, direccion: Optional[str] = None,
                      telefono: Optional[str] = None, email: Optional[str] = None,
                      responsable_id: Optional[int] = None) -> bool:
        """Actualiza una tienda"""
        return self.inventory_service.actualizar_tienda(tienda_id, nombre, direccion, telefono, email, responsable_id)
    
    def delete_tienda(self, tienda_id: int) -> bool:
        """Elimina una tienda"""
        return self.inventory_service.eliminar_tienda(tienda_id)
    
    # Productos
    def get_productos(self) -> List[ProductoModel]:
        """Obtiene todos los productos"""
        productos = self.inventory_service.listar_productos()
        return [ProductoModel.from_domain(p) for p in productos]
    
    def create_producto(self, sku: str, nombre: str, descripcion: Optional[str], unidad: str, precio: float, 
                       categoria: Optional[str], proveedor: Optional[str], stock_minimo: int = 0, tienda_id: int = 1) -> ProductoModel:
        """Crea un nuevo producto"""
        producto = self.inventory_service.crear_producto(sku, nombre, descripcion, unidad, precio, categoria, proveedor, stock_minimo, tienda_id)
        return ProductoModel.from_domain(producto)
    
    def update_producto(self, producto_id: int, sku: str, nombre: str, descripcion: Optional[str], unidad: str, precio: float, 
                       categoria: Optional[str], proveedor: Optional[str], stock_minimo: int = 0, activo: bool = True, tienda_id: int = 1) -> bool:
        """Actualiza un producto"""
        return self.inventory_service.actualizar_producto(producto_id, sku, nombre, descripcion, unidad, precio, categoria, proveedor, stock_minimo, activo, tienda_id)
    
    def delete_producto(self, producto_id: int) -> bool:
        """Elimina un producto"""
        return self.inventory_service.eliminar_producto(producto_id)
    
    # Movimientos
    def get_movimientos(self, tienda_id: Optional[int] = None, limit: int = 200) -> List[MovimientoModel]:
        """Obtiene los movimientos de inventario"""
        # Usar Service Layer
        movimientos_dict = self.inventory_service.obtener_movimientos(tienda_id, limit)
        
        # Convertir a MovimientoModel
        return [MovimientoModel(
            id=m['id'],
            producto_id=m['producto_id'],
            producto_sku=m['sku'],
            producto_nombre=m['producto_nombre'],
            tipo=m['tipo'],
            cantidad=m['cantidad'],
            usuario_id=m['usuario_id'],
            usuario_nombre=m['username'],
            tienda_nombre=m['tienda_nombre'],
            fecha=m['ts'][:16],  # Solo fecha y hora
            nota=m['nota']
        ) for m in movimientos_dict]
    
    def registrar_salida(self, producto_id: int, tienda_id: int, cantidad: float, usuario_id: int, nota: Optional[str] = None) -> bool:
        """Registra una salida de producto"""
        try:
            # Usar el servicio de inventario para ajustar el stock (cantidad negativa = salida)
            self.inventory_service.egresar(tienda_id, producto_id, cantidad, usuario_id, nota)
            return True
        except Exception as e:
            print(f"Error al registrar salida: {e}")
            return False
    
    def registrar_salida_tienda(self, producto_id: int, cantidad: float, usuario_id: int, nota: Optional[str] = None) -> bool:
        """Registra una salida de producto directamente en la tienda"""
        try:
            # Obtener el producto completo a través del servicio
            productos = self.inventory_service.listar_productos()
            producto = next((p for p in productos if p.id == producto_id), None)
            
            if not producto:
                raise ValueError("Producto no encontrado")
            
            # Usar el servicio de inventario para registrar la salida
            self.inventory_service.egresar(producto.tienda_id, producto_id, cantidad, usuario_id, nota)
            return True
                
        except Exception as e:
            print(f"Error al registrar salida: {e}")
            raise e
    
    def get_productos_con_stock(self, filtro: str = "") -> Dict[str, Any]:
        """Obtiene productos con stock disponible"""
        try:
            # Usar Service Layer
            productos = self.inventory_service.buscar_productos_con_stock(filtro, stock_mayor_a=0)
            
            return {
                'productos': [
                    {
                        'id': p['id'],
                        'sku': p['sku'],
                        'nombre': p['nombre'],
                        'precio': p['precio_unit'],
                        'categoria': p['categoria'],
                        'tienda': p['tienda_nombre'],
                        'stock': p['stock']
                    }
                    for p in productos
                ]
            }
                
        except Exception as e:
            print(f"Error obteniendo productos con stock: {e}")
            return {'productos': []}
    
    # Stock y Reportes
    def get_stock_report(self, tienda_id: Optional[int] = None) -> List[StockModel]:
        """Obtiene el reporte de stock"""
        if tienda_id:
            # Usar Service Layer para una tienda específica
            reporte_dict = self.inventory_service.items_bajo_minimo(tienda_id) if False else []
            # Para obtener todos los items de una tienda, usar el reporte completo
            tienda = next((t for t in self.inventory_service.listar_tiendas() if t.id == tienda_id), None)
            tienda_nombre = tienda.nombre if tienda else f"Tienda {tienda_id}"
            
            filas = self.inventory_service._ri.reporte_stock(tienda_id)
            return [StockModel(
                tienda=tienda_nombre,
                producto_sku=r['sku'],
                producto_nombre=r['nombre'],
                cantidad=r['cantidad'],
                minimo=r['minimo'],
                estado=r['estado']
            ) for r in filas]
        else:
            # Obtener para todas las tiendas
            result = []
            for tienda in self.inventory_service.listar_tiendas():
                filas = self.inventory_service._ri.reporte_stock(tienda.id)
                for r in filas:
                    result.append(StockModel(
                        tienda=tienda.nombre,
                        producto_sku=r['sku'],
                        producto_nombre=r['nombre'],
                        cantidad=r['cantidad'],
                        minimo=r['minimo'],
                        estado=r['estado']
                    ))
            return result
    
    def get_alerts(self) -> List[StockModel]:
        """Obtiene las alertas de stock"""
        # Obtener alertas para todas las tiendas usando Service Layer
        result = []
        for tienda in self.inventory_service.listar_tiendas():
            alertas = self.inventory_service.items_bajo_minimo(tienda.id)
            for a in alertas:
                result.append(StockModel(
                    tienda=tienda.nombre,
                    producto_sku=a['sku'],
                    producto_nombre=a['nombre'],
                    cantidad=a['cantidad'],
                    minimo=a['minimo'],
                    estado=a['estado']
                ))
        return result
    
    def get_empleado_by_user_id(self, user_id: int):
        """Obtiene un empleado por su ID de usuario"""
        return self.inventory_service.obtener_empleado_por_usuario(user_id)
