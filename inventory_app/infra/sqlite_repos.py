# ==============================
# File: inventory_app/infra/sqlite_repos.py
# ==============================
from __future__ import annotations
from typing import List, Optional, Tuple
from datetime import datetime
import sqlite3

from ..domain.models import Usuario, Tienda, Producto, Empleado
from ..domain.interfaces import RepoUsuarios, RepoTiendas, RepoProductos, RepoInventario, RepoEmpleados
from .db import get_conn, _hash_pw

        
class SQLiteRepoUsuarios(RepoUsuarios):
    def autenticar(self, username: str, password: str) -> Optional[Usuario]:
        with get_conn() as c:
            cur = c.execute("SELECT * FROM usuarios WHERE username=? AND activo=1", (username,))
            row = cur.fetchone()
            if not row or row["pw_hash"] != _hash_pw(password):
                return None
            return Usuario(id=row["id"], username=row["username"], rol=row["rol"], activo=bool(row["activo"]))

    def crear_usuario(self, username: str, password: str, rol: str) -> Usuario:
        with get_conn() as c:
            cur = c.execute(
                "INSERT INTO usuarios(username, pw_hash, rol, activo) VALUES (?,?,?,1)",
                (username, _hash_pw(password), rol)
            )
            return Usuario(
                id=cur.lastrowid,
                username=username,
                rol=rol,
                activo=True
            )

    def listar_usuarios(self) -> List[Usuario]:
        with get_conn() as c:
            cur = c.execute("SELECT * FROM usuarios ORDER BY username")
            return [
                Usuario(
                    id=row["id"],
                    username=row["username"],
                    rol=row["rol"],
                    activo=bool(row["activo"])
                )
                for row in cur.fetchall()
            ]

    def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Usuario]:
        with get_conn() as c:
            cur = c.execute("SELECT * FROM usuarios WHERE id=?", (usuario_id,))
            row = cur.fetchone()
            if not row:
                return None
            return Usuario(
                id=row["id"],
                username=row["username"],
                rol=row["rol"],
                activo=bool(row["activo"])
            )


class SQLiteRepoTiendas(RepoTiendas):
    def crear_tienda(self, nombre: str, direccion: Optional[str] = None, 
                     telefono: Optional[str] = None, email: Optional[str] = None,
                     responsable_id: Optional[int] = None) -> Tienda:
        with get_conn() as c:
            cur = c.execute(
                "INSERT INTO tiendas(nombre, direccion, telefono, email, responsable_id) VALUES (?,?,?,?,?)", 
                (nombre, direccion, telefono, email, responsable_id)
            )
            return Tienda(
                id=cur.lastrowid, 
                nombre=nombre, 
                direccion=direccion,
                telefono=telefono,
                email=email,
                responsable_id=responsable_id
            )

    def listar_tiendas(self) -> List[Tienda]:
        with get_conn() as c:
            cur = c.execute("SELECT * FROM tiendas ORDER BY nombre")
            return [Tienda(
                id=r["id"], 
                nombre=r["nombre"], 
                direccion=r["direccion"] if r["direccion"] else None,
                telefono=r["telefono"] if r["telefono"] else None,
                email=r["email"] if r["email"] else None,
                responsable_id=r["responsable_id"] if r["responsable_id"] else None
            ) for r in cur.fetchall()]
    
    def actualizar_tienda(self, tienda_id: int, nombre: str, direccion: Optional[str] = None,
                         telefono: Optional[str] = None, email: Optional[str] = None,
                         responsable_id: Optional[int] = None) -> bool:
        with get_conn() as c:
            cur = c.execute(
                "UPDATE tiendas SET nombre=?, direccion=?, telefono=?, email=?, responsable_id=? WHERE id=?",
                (nombre, direccion, telefono, email, responsable_id, tienda_id)
            )
            return cur.rowcount > 0
    
    def eliminar_tienda(self, tienda_id: int) -> bool:
        with get_conn() as c:
            cur = c.execute("DELETE FROM tiendas WHERE id=?", (tienda_id,))
            return cur.rowcount > 0



class SQLiteRepoProductos(RepoProductos):
    def _row_to_producto(self, row) -> Optional[Producto]:
        """Convierte una fila de BD a modelo Producto"""
        if not row:
            return None
        
        return Producto(
            id=row["id"],
            sku=row["sku"],
            nombre=row["nombre"],
            descripcion=row["descripcion"] if row["descripcion"] else None,
            unidad=row["unidad"],
            precio_unit=row["precio_unit"],
            categoria=row["categoria"] if row["categoria"] else None,
            proveedor=row["proveedor"] if row["proveedor"] else None,
            stock_minimo=row["stock_minimo"] if row["stock_minimo"] is not None else 0,
            activo=bool(row["activo"] if row["activo"] is not None else 1),
            tienda_id=row["tienda_id"]
        )
    
    def crear_producto(self, sku: str, nombre: str, descripcion: Optional[str], unidad: str, precio: float, 
                      categoria: Optional[str], proveedor: Optional[str], stock_minimo: int = 0, tienda_id: int = 1) -> Producto:
        with get_conn() as c:
            cur = c.execute(
                "INSERT INTO productos(sku, nombre, descripcion, unidad, precio_unit, categoria, proveedor, stock_minimo, tienda_id) VALUES (?,?,?,?,?,?,?,?,?)",
                (sku, nombre, descripcion, unidad, precio, categoria, proveedor, stock_minimo, tienda_id),
            )
            return Producto(
                id=cur.lastrowid, 
                sku=sku, 
                nombre=nombre, 
                descripcion=descripcion,
                unidad=unidad, 
                precio_unit=precio,
                categoria=categoria,
                proveedor=proveedor,
                stock_minimo=stock_minimo,
                activo=True,
                tienda_id=tienda_id
            )

    def buscar_por_sku(self, sku: str) -> Optional[Producto]:
        with get_conn() as c:
            cur = c.execute("SELECT * FROM productos WHERE sku=?", (sku,))
            return self._row_to_producto(cur.fetchone())

    def listar_productos(self, q: str = "") -> List[Producto]:
        q_like = f"%{q}%"
        with get_conn() as c:
            cur = c.execute(
                "SELECT * FROM productos WHERE sku LIKE ? OR nombre LIKE ? ORDER BY nombre",
                (q_like, q_like),
            )
            return [self._row_to_producto(r) for r in cur.fetchall()]
    
    def actualizar_producto(self, producto_id: int, sku: str, nombre: str, descripcion: Optional[str], 
                           unidad: str, precio: float, categoria: Optional[str], proveedor: Optional[str], 
                           stock_minimo: int = 0, activo: bool = True, tienda_id: int = 1) -> bool:
        with get_conn() as c:
            cur = c.execute("""
                UPDATE productos 
                SET sku=?, nombre=?, descripcion=?, unidad=?, precio_unit=?, categoria=?, proveedor=?, stock_minimo=?, activo=?, tienda_id=?
                WHERE id=?
            """, (sku, nombre, descripcion, unidad, precio, categoria, proveedor, stock_minimo, int(activo), tienda_id, producto_id))
            return cur.rowcount > 0
    
    def eliminar_producto(self, producto_id: int) -> bool:
        with get_conn() as c:
            cur = c.execute("DELETE FROM productos WHERE id=?", (producto_id,))
            return cur.rowcount > 0
    
    def buscar_con_stock(self, filtro: str = "", stock_mayor_a: float = 0):
        with get_conn() as c:
            base_query = """
                SELECT p.id, p.sku, p.nombre, p.precio_unit, p.categoria, 
                       t.nombre as tienda_nombre, COALESCE(s.cantidad, 0) as stock
                FROM productos p
                JOIN tiendas t ON p.tienda_id = t.id
                LEFT JOIN stock s ON p.id = s.producto_id AND s.tienda_id = t.id
                WHERE p.activo = 1 AND COALESCE(s.cantidad, 0) > ?
            """
            
            params = [stock_mayor_a]
            
            # Agregar filtro si se proporciona
            if filtro:
                base_query += " AND (LOWER(p.sku) LIKE ? OR LOWER(p.nombre) LIKE ? OR LOWER(p.categoria) LIKE ?)"
                filtro_param = f"%{filtro.lower()}%"
                params.extend([filtro_param, filtro_param, filtro_param])
            
            base_query += " ORDER BY p.sku"
            
            productos = c.execute(base_query, params).fetchall()
            return [dict(row) for row in productos]


class SQLiteRepoInventario(RepoInventario):
    def set_minimo(self, tienda_id: int, producto_id: int, minimo: float) -> None:
        with get_conn() as c:
            c.execute(
                "INSERT INTO stock(tienda_id, producto_id, minimo, cantidad) VALUES (?,?,?,0) "
                "ON CONFLICT(tienda_id, producto_id) DO UPDATE SET minimo=excluded.minimo",
                (tienda_id, producto_id, minimo),
            )

    def ajustar_stock(self, tienda_id: int, producto_id: int, delta: float, usuario_id: int, nota: Optional[str] = None) -> None:
        with get_conn() as c:
            cur = c.execute("SELECT cantidad FROM stock WHERE tienda_id=? AND producto_id=?", (tienda_id, producto_id))
            row = cur.fetchone()
            if row is None:
                if delta < 0:
                    raise ValueError("No se puede egresar stock inexistente")
                c.execute("INSERT INTO stock(tienda_id, producto_id, cantidad, minimo) VALUES (?,?,?,0)", (tienda_id, producto_id, delta))
            else:
                nueva = row["cantidad"] + delta
                if nueva < 0:
                    raise ValueError("Stock insuficiente para la operación")
                c.execute("UPDATE stock SET cantidad=? WHERE tienda_id=? AND producto_id=?", (nueva, tienda_id, producto_id))
            c.execute(
                "INSERT INTO movimientos(tienda_id, producto_id, tipo, cantidad, usuario_id, ts, nota) VALUES (?,?,?,?,?,?,datetime('now'))",
                (tienda_id, producto_id, "INGRESO" if delta > 0 else "SALIDA", abs(delta), usuario_id, nota),
            )

    def obtener_stock(self, tienda_id: int, producto_id: int) -> Tuple[float, float]:
        with get_conn() as c:
            cur = c.execute("SELECT cantidad, minimo FROM stock WHERE tienda_id=? AND producto_id=?", (tienda_id, producto_id))
            r = cur.fetchone()
            if not r:
                return 0.0, 0.0
            return float(r["cantidad"]), float(r["minimo"])

    def reporte_stock(self, tienda_id: int):
        sql = """
        SELECT p.sku, p.nombre, p.unidad, IFNULL(s.cantidad,0) AS cantidad, IFNULL(s.minimo,0) AS minimo,
               CASE WHEN IFNULL(s.cantidad,0) = 0 THEN 'SIN STOCK'
                    WHEN IFNULL(s.cantidad,0) <= IFNULL(s.minimo,0) THEN 'BAJO MINIMO'
                    ELSE 'OK' END AS estado
        FROM productos p
        LEFT JOIN stock s ON s.producto_id = p.id AND s.tienda_id = ?
        ORDER BY p.nombre
        """
        with get_conn() as c:
            return [dict(row) for row in c.execute(sql, (tienda_id,))]
    
    def obtener_movimientos(self, tienda_id: Optional[int] = None, limit: int = 200):
        with get_conn() as c:
            if tienda_id:
                query = """
                    SELECT m.id, m.producto_id, p.sku, p.nombre as producto_nombre, 
                           m.tipo, m.cantidad, m.usuario_id, u.username, 
                           t.nombre as tienda_nombre, m.ts, m.nota
                    FROM movimientos m
                    JOIN productos p ON m.producto_id = p.id
                    JOIN usuarios u ON m.usuario_id = u.id
                    JOIN tiendas t ON m.tienda_id = t.id
                    WHERE t.id = ?
                    ORDER BY m.ts DESC LIMIT ?
                """
                params = (tienda_id, limit)
            else:
                query = """
                    SELECT m.id, m.producto_id, p.sku, p.nombre as producto_nombre, 
                           m.tipo, m.cantidad, m.usuario_id, u.username, 
                           t.nombre as tienda_nombre, m.ts, m.nota
                    FROM movimientos m
                    JOIN productos p ON m.producto_id = p.id
                    JOIN usuarios u ON m.usuario_id = u.id
                    JOIN tiendas t ON m.tienda_id = t.id
                    ORDER BY m.ts DESC LIMIT ?
                """
                params = (limit,)
            
            movimientos = c.execute(query, params).fetchall()
            return [dict(m) for m in movimientos]


class SQLiteRepoEmpleados(RepoEmpleados):
    def crear_empleado(self, usuario_id: int, nombres: str, apellidos: str, dni: str, jornada: str, tienda_id: int) -> Empleado:
        with get_conn() as c:
            cur = c.execute(
                "INSERT INTO empleados(usuario_id, nombres, apellidos, dni, jornada, tienda_id) VALUES (?,?,?,?,?,?)",
                (usuario_id, nombres, apellidos, dni, jornada, tienda_id)
            )
            return Empleado(
                id=cur.lastrowid,
                usuario_id=usuario_id,
                nombres=nombres,
                apellidos=apellidos,
                dni=dni,
                jornada=jornada,
                tienda_id=tienda_id
            )

    def listar_empleados(self) -> List[Empleado]:
        with get_conn() as c:
            cur = c.execute("""
                SELECT e.*, u.username, u.rol, u.activo, t.nombre as tienda_nombre
                FROM empleados e
                JOIN usuarios u ON e.usuario_id = u.id
                JOIN tiendas t ON e.tienda_id = t.id
                ORDER BY e.apellidos, e.nombres
            """)
            return [
                Empleado(
                    id=row["id"],
                    usuario_id=row["usuario_id"],
                    nombres=row["nombres"],
                    apellidos=row["apellidos"],
                    dni=row["dni"],
                    jornada=row["jornada"],
                    tienda_id=row["tienda_id"]
                )
                for row in cur.fetchall()
            ]

    def obtener_empleado_por_usuario(self, usuario_id: int) -> Optional[Empleado]:
        with get_conn() as c:
            cur = c.execute("SELECT * FROM empleados WHERE usuario_id=?", (usuario_id,))
            row = cur.fetchone()
            if not row:
                return None
            return Empleado(
                id=row["id"],
                usuario_id=row["usuario_id"],
                nombres=row["nombres"],
                apellidos=row["apellidos"],
                dni=row["dni"],
                jornada=row["jornada"],
                tienda_id=row["tienda_id"]
            )
    
    def obtener_empleado_por_id(self, empleado_id: int) -> Optional[Empleado]:
        with get_conn() as c:
            cur = c.execute("SELECT * FROM empleados WHERE id=?", (empleado_id,))
            row = cur.fetchone()
            if not row:
                return None
            return Empleado(
                id=row["id"],
                usuario_id=row["usuario_id"],
                nombres=row["nombres"],
                apellidos=row["apellidos"],
                dni=row["dni"],
                jornada=row["jornada"],
                tienda_id=row["tienda_id"]
            )

    def actualizar_empleado(self, empleado_id: int, nombres: str, apellidos: str, dni: str, jornada: str, tienda_id: int) -> bool:
        with get_conn() as c:
            cur = c.execute("""
                UPDATE empleados 
                SET nombres=?, apellidos=?, dni=?, jornada=?, tienda_id=?
                WHERE id=?
            """, (nombres, apellidos, dni, jornada, tienda_id, empleado_id))
            return cur.rowcount > 0

    def eliminar_empleado(self, empleado_id: int) -> bool:
        with get_conn() as c:
            cur = c.execute("DELETE FROM empleados WHERE id=?", (empleado_id,))
            return cur.rowcount > 0