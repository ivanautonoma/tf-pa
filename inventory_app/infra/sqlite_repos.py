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

def ajustar_stock(self, almacen_id: int, producto_id: int, delta: float, usuario_id: int, nota: Optional[str] = None) -> None:
    # No registrar ni tocar stock si el delta es cero
    if delta == 0:
        return
    with get_conn() as c:
        ...
        
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
    def crear_tienda(self, nombre: str, direccion: Optional[str]) -> Tienda:
        with get_conn() as c:
            cur = c.execute("INSERT INTO tiendas(nombre, direccion) VALUES (?,?)", (nombre, direccion))
            return Tienda(id=cur.lastrowid, nombre=nombre, direccion=direccion)

    def listar_tiendas(self) -> List[Tienda]:
        with get_conn() as c:
            cur = c.execute("SELECT * FROM tiendas ORDER BY nombre")
            return [Tienda(id=r["id"], nombre=r["nombre"], direccion=r["direccion"]) for r in cur.fetchall()]



class SQLiteRepoProductos(RepoProductos):
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
            r = cur.fetchone()
            if not r:
                return None
            return Producto(
                id=r["id"], 
                sku=r["sku"], 
                nombre=r["nombre"], 
                descripcion=r["descripcion"] if r["descripcion"] else None,
                unidad=r["unidad"], 
                precio_unit=r["precio_unit"],
                categoria=r["categoria"] if r["categoria"] else None,
                proveedor=r["proveedor"] if r["proveedor"] else None,
                stock_minimo=r["stock_minimo"] if r["stock_minimo"] is not None else 0,
                activo=bool(r["activo"] if r["activo"] is not None else 1),
                tienda_id=r["tienda_id"]
            )

    def listar_productos(self, q: str = "") -> List[Producto]:
        q_like = f"%{q}%"
        with get_conn() as c:
            cur = c.execute(
                "SELECT * FROM productos WHERE sku LIKE ? OR nombre LIKE ? ORDER BY nombre",
                (q_like, q_like),
            )
            return [
                        Producto(
                            id=r["id"], 
                            sku=r["sku"], 
                            nombre=r["nombre"], 
                            descripcion=r["descripcion"] if r["descripcion"] else None,
                            unidad=r["unidad"], 
                            precio_unit=r["precio_unit"],
                            categoria=r["categoria"] if r["categoria"] else None,
                            proveedor=r["proveedor"] if r["proveedor"] else None,
                            stock_minimo=r["stock_minimo"] if r["stock_minimo"] is not None else 0,
                            activo=bool(r["activo"] if r["activo"] is not None else 1),
                            tienda_id=r["tienda_id"]
                        ) for r in cur.fetchall()
            ]
    
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
            return list(c.execute(sql, (tienda_id,)))


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