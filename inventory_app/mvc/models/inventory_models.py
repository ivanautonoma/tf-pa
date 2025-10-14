# ==============================
# File: inventory_app/mvc/models/inventory_models.py
# ==============================
from __future__ import annotations
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from ...domain.models import Tienda, Almacen, Producto
from ...services.inventory_service import InventarioService


@dataclass
class TiendaModel:
    """Modelo de datos para tiendas"""
    id: int
    nombre: str
    direccion: Optional[str]
    
    @classmethod
    def from_domain(cls, tienda: Tienda) -> 'TiendaModel':
        return cls(
            id=tienda.id,
            nombre=tienda.nombre,
            direccion=tienda.direccion
        )


@dataclass
class AlmacenModel:
    """Modelo de datos para almacenes"""
    id: int
    tienda_id: int
    nombre: str
    
    @classmethod
    def from_domain(cls, almacen: Almacen) -> 'AlmacenModel':
        return cls(
            id=almacen.id,
            tienda_id=almacen.tienda_id,
            nombre=almacen.nombre
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
    almacen_id: int
    almacen_nombre: str
    tienda_nombre: str
    fecha: str
    nota: Optional[str]


@dataclass
class StockModel:
    """Modelo de datos para stock"""
    tienda: str
    almacen: str
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
    
    def create_tienda(self, nombre: str, direccion: Optional[str] = None) -> TiendaModel:
        """Crea una nueva tienda"""
        tienda = self.inventory_service.crear_tienda(nombre, direccion)
        return TiendaModel.from_domain(tienda)
    
    def delete_tienda(self, tienda_id: int) -> bool:
        """Elimina una tienda"""
        from ...infra.db import get_conn
        with get_conn() as c:
            # Verificar si hay almacenes
            almacenes = c.execute(
                "SELECT COUNT(*) as count FROM almacenes WHERE tienda_id=?", 
                (tienda_id,)
            ).fetchone()
            
            if almacenes['count'] > 0:
                raise ValueError("No se puede eliminar una tienda que tiene almacenes asociados")
            
            c.execute("DELETE FROM tiendas WHERE id=?", (tienda_id,))
            return True
    
    # Almacenes
    def get_almacenes(self, tienda_id: int) -> List[AlmacenModel]:
        """Obtiene todos los almacenes de una tienda"""
        almacenes = self.inventory_service.listar_almacenes(tienda_id)
        return [AlmacenModel.from_domain(a) for a in almacenes]
    
    def create_almacen(self, tienda_id: int, nombre: str) -> AlmacenModel:
        """Crea un nuevo almacén"""
        almacen = self.inventory_service.crear_almacen(tienda_id, nombre)
        return AlmacenModel.from_domain(almacen)
    
    # Productos
    def get_productos(self) -> List[ProductoModel]:
        """Obtiene todos los productos"""
        from ...infra.db import get_conn
        with get_conn() as c:
            productos = c.execute("SELECT * FROM productos ORDER BY nombre").fetchall()
            return [ProductoModel(
                id=p['id'],
                sku=p['sku'],
                nombre=p['nombre'],
                descripcion=p['descripcion'] if p['descripcion'] else None,
                unidad=p['unidad'],
                precio_unit=p['precio_unit'],
                categoria=p['categoria'] if p['categoria'] else None,
                proveedor=p['proveedor'] if p['proveedor'] else None,
                stock_minimo=p['stock_minimo'] if p['stock_minimo'] is not None else 0,
                activo=bool(p['activo'] if p['activo'] is not None else 1),
                tienda_id=p['tienda_id']
            ) for p in productos]
    
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
        from ...infra.db import get_conn
        with get_conn() as c:
            if tienda_id:
                query = """
                    SELECT m.*, p.sku, p.nombre as producto_nombre, u.username, 
                           a.nombre as almacen_nombre, t.nombre as tienda_nombre
                    FROM movimientos m
                    JOIN productos p ON m.producto_id = p.id
                    JOIN usuarios u ON m.usuario_id = u.id
                    JOIN almacenes a ON m.almacen_id = a.id
                    JOIN tiendas t ON a.tienda_id = t.id
                    WHERE t.id = ?
                    ORDER BY m.ts DESC
                    LIMIT ?
                """
                params = (tienda_id, limit)
            else:
                query = """
                    SELECT m.*, p.sku, p.nombre as producto_nombre, u.username, 
                           a.nombre as almacen_nombre, t.nombre as tienda_nombre
                    FROM movimientos m
                    JOIN productos p ON m.producto_id = p.id
                    JOIN usuarios u ON m.usuario_id = u.id
                    JOIN almacenes a ON m.almacen_id = a.id
                    JOIN tiendas t ON a.tienda_id = t.id
                    ORDER BY m.ts DESC
                    LIMIT ?
                """
                params = (limit,)
            
            movimientos = c.execute(query, params).fetchall()
            return [MovimientoModel(
                id=m['id'],
                producto_id=m['producto_id'],
                producto_sku=m['sku'],
                producto_nombre=m['producto_nombre'],
                tipo=m['tipo'],
                cantidad=m['cantidad'],
                usuario_id=m['usuario_id'],
                usuario_nombre=m['username'],
                almacen_id=m['almacen_id'],
                almacen_nombre=m['almacen_nombre'],
                tienda_nombre=m['tienda_nombre'],
                fecha=m['ts'][:16],  # Solo fecha y hora
                nota=m['nota']
            ) for m in movimientos]
    
    def registrar_salida(self, producto_id: int, almacen_id: int, cantidad: float, usuario_id: int, nota: Optional[str] = None) -> bool:
        """Registra una salida de producto"""
        try:
            # Usar el servicio de inventario para ajustar el stock (cantidad negativa = salida)
            self.inventory_service.ajustar_stock(almacen_id, producto_id, -cantidad, usuario_id, nota)
            return True
        except Exception as e:
            print(f"Error al registrar salida: {e}")
            return False
    
    def registrar_salida_tienda(self, producto_id: int, cantidad: float, usuario_id: int, nota: Optional[str] = None) -> bool:
        """Registra una salida de producto directamente en la tienda (sin almacenes)"""
        try:
            from ...infra.db import get_conn
            from datetime import datetime
            
            with get_conn() as c:
                # Obtener la tienda del producto
                cur = c.execute("SELECT tienda_id FROM productos WHERE id = ?", (producto_id,))
                producto_row = cur.fetchone()
                if not producto_row:
                    raise ValueError("Producto no encontrado")
                
                tienda_id = producto_row['tienda_id']
                
                # Obtener el almacén principal de la tienda (asumimos que existe)
                cur = c.execute("SELECT id FROM almacenes WHERE tienda_id = ? LIMIT 1", (tienda_id,))
                almacen_row = cur.fetchone()
                if not almacen_row:
                    # Si no existe almacén, crear uno por defecto
                    c.execute("INSERT INTO almacenes (tienda_id, nombre) VALUES (?, ?)", 
                             (tienda_id, f"Almacén Principal - Tienda {tienda_id}"))
                    almacen_id = c.lastrowid
                else:
                    almacen_id = almacen_row['id']
                
                # Verificar stock disponible
                cur = c.execute("SELECT cantidad FROM stock WHERE almacen_id = ? AND producto_id = ?", 
                               (almacen_id, producto_id))
                stock_row = cur.fetchone()
                
                if stock_row:
                    stock_actual = stock_row['cantidad']
                    if stock_actual < cantidad:
                        raise ValueError(f"Stock insuficiente. Disponible: {stock_actual}, Solicitado: {cantidad}")
                    
                    # Actualizar stock
                    nuevo_stock = stock_actual - cantidad
                    c.execute("UPDATE stock SET cantidad = ? WHERE almacen_id = ? AND producto_id = ?",
                             (nuevo_stock, almacen_id, producto_id))
                else:
                    raise ValueError("El producto no tiene stock registrado")
                
                # Registrar el movimiento
                c.execute("""
                    INSERT INTO movimientos (almacen_id, producto_id, tipo, cantidad, usuario_id, ts, nota)
                    VALUES (?, ?, 'SALIDA', ?, ?, datetime('now'), ?)
                """, (almacen_id, producto_id, cantidad, usuario_id, nota))
                
                return True
                
        except Exception as e:
            print(f"Error al registrar salida: {e}")
            raise e
    
    def get_productos_con_stock(self, filtro: str = "") -> Dict[str, Any]:
        """Obtiene los productos con stock disponible para selección"""
        try:
            from ...infra.db import get_conn
            
            with get_conn() as c:
                # Query base para obtener productos con stock
                base_query = """
                    SELECT p.id, p.sku, p.nombre, p.precio_unit, p.categoria, 
                           t.nombre as tienda_nombre, COALESCE(s.cantidad, 0) as stock
                    FROM productos p
                    JOIN tiendas t ON p.tienda_id = t.id
                    LEFT JOIN stock s ON p.id = s.producto_id
                    WHERE p.activo = 1 AND COALESCE(s.cantidad, 0) > 0
                """
                
                params = []
                
                # Agregar filtro si se proporciona
                if filtro:
                    base_query += " AND (LOWER(p.sku) LIKE ? OR LOWER(p.nombre) LIKE ? OR LOWER(p.categoria) LIKE ?)"
                    filtro_param = f"%{filtro.lower()}%"
                    params.extend([filtro_param, filtro_param, filtro_param])
                
                base_query += " ORDER BY p.sku"
                
                productos = c.execute(base_query, params).fetchall()
                
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
        from ...infra.db import get_conn
        with get_conn() as c:
            if tienda_id:
                query = """
                    SELECT t.nombre as tienda, a.nombre as almacen, p.sku, p.nombre as producto,
                           IFNULL(s.cantidad,0) as cantidad, IFNULL(s.minimo,0) as minimo,
                           CASE WHEN IFNULL(s.cantidad,0) = 0 THEN 'SIN STOCK'
                                WHEN IFNULL(s.cantidad,0) <= IFNULL(s.minimo,0) THEN 'BAJO MINIMO'
                                ELSE 'OK' END AS estado
                    FROM tiendas t
                    JOIN almacenes a ON t.id = a.tienda_id
                    CROSS JOIN productos p
                    LEFT JOIN stock s ON s.producto_id = p.id AND s.almacen_id = a.id
                    WHERE t.id = ?
                    ORDER BY t.nombre, a.nombre, p.nombre
                """
                params = (tienda_id,)
            else:
                query = """
                    SELECT t.nombre as tienda, a.nombre as almacen, p.sku, p.nombre as producto,
                           IFNULL(s.cantidad,0) as cantidad, IFNULL(s.minimo,0) as minimo,
                           CASE WHEN IFNULL(s.cantidad,0) = 0 THEN 'SIN STOCK'
                                WHEN IFNULL(s.cantidad,0) <= IFNULL(s.minimo,0) THEN 'BAJO MINIMO'
                                ELSE 'OK' END AS estado
                    FROM tiendas t
                    JOIN almacenes a ON t.id = a.tienda_id
                    CROSS JOIN productos p
                    LEFT JOIN stock s ON s.producto_id = p.id AND s.almacen_id = a.id
                    ORDER BY t.nombre, a.nombre, p.nombre
                """
                params = ()
            
            reporte = c.execute(query, params).fetchall()
            return [StockModel(
                tienda=r['tienda'],
                almacen=r['almacen'],
                producto_sku=r['sku'],
                producto_nombre=r['producto'],
                cantidad=r['cantidad'],
                minimo=r['minimo'],
                estado=r['estado']
            ) for r in reporte]
    
    def get_alerts(self) -> List[StockModel]:
        """Obtiene las alertas de stock"""
        from ...infra.db import get_conn
        with get_conn() as c:
            alertas = c.execute("""
                SELECT t.nombre as tienda, a.nombre as almacen, p.sku, p.nombre as producto,
                       IFNULL(s.cantidad,0) as cantidad, IFNULL(s.minimo,0) as minimo,
                       CASE WHEN IFNULL(s.cantidad,0) = 0 THEN 'SIN STOCK'
                            WHEN IFNULL(s.cantidad,0) <= IFNULL(s.minimo,0) THEN 'BAJO MINIMO'
                            ELSE 'OK' END AS estado
                FROM tiendas t
                JOIN almacenes a ON t.id = a.tienda_id
                CROSS JOIN productos p
                LEFT JOIN stock s ON s.producto_id = p.id AND s.almacen_id = a.id
                WHERE IFNULL(s.cantidad,0) = 0 OR IFNULL(s.cantidad,0) <= IFNULL(s.minimo,0)
                ORDER BY t.nombre, a.nombre, p.nombre
            """).fetchall()
            
            return [StockModel(
                tienda=a['tienda'],
                almacen=a['almacen'],
                producto_sku=a['sku'],
                producto_nombre=a['producto'],
                cantidad=a['cantidad'],
                minimo=a['minimo'],
                estado=a['estado']
            ) for a in alertas]
