# ==============================
# File: inventory_app/infra/db.py
# ==============================
from __future__ import annotations
import sqlite3
import hashlib

DB_PATH = "inventario.db"


def get_conn(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def init_db():
    ddl = [
        # Usuarios
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            pw_hash TEXT NOT NULL,
            rol TEXT NOT NULL CHECK(rol IN ('ADMIN','ENCARGADO','VENDEDOR')),
            activo INTEGER NOT NULL DEFAULT 1
        );
        """,
        # Tiendas
        """
        CREATE TABLE IF NOT EXISTS tiendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            direccion TEXT
        );
        """,
        # Productos
        """
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            unidad TEXT NOT NULL,
            precio_unit REAL NOT NULL CHECK(precio_unit >= 0),
            categoria TEXT,
            proveedor TEXT,
            stock_minimo INTEGER DEFAULT 0 CHECK(stock_minimo >= 0),
            activo INTEGER DEFAULT 1 CHECK(activo IN (0,1)),
            tienda_id INTEGER NOT NULL,
            FOREIGN KEY(tienda_id) REFERENCES tiendas(id) ON DELETE CASCADE
        );
        """,
        # Stock
        """
        CREATE TABLE IF NOT EXISTS stock (
            tienda_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad REAL NOT NULL DEFAULT 0 CHECK(cantidad >= 0),
            minimo REAL NOT NULL DEFAULT 0 CHECK(minimo >= 0),
            PRIMARY KEY(tienda_id, producto_id),
            FOREIGN KEY(tienda_id) REFERENCES tiendas(id) ON DELETE CASCADE,
            FOREIGN KEY(producto_id) REFERENCES productos(id) ON DELETE CASCADE
        );
        """,
        # Empleados (información adicional de usuarios)
        """
        CREATE TABLE IF NOT EXISTS empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL UNIQUE,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            dni TEXT NOT NULL UNIQUE,
            jornada TEXT NOT NULL CHECK(jornada IN ('COMPLETA','MEDIA','PARCIAL')),
            tienda_id INTEGER NOT NULL,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY(tienda_id) REFERENCES tiendas(id)
        );
        """,
        # Movimientos
        """
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tienda_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('INGRESO','SALIDA')),
            cantidad REAL NOT NULL CHECK(cantidad > 0),
            usuario_id INTEGER NOT NULL,
            ts TEXT NOT NULL,
            nota TEXT,
            FOREIGN KEY(tienda_id) REFERENCES tiendas(id),
            FOREIGN KEY(producto_id) REFERENCES productos(id),
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        );
        """,
    ]
    with get_conn() as c:
        for stmt in ddl:
            c.execute(stmt)
        # Crear admin si está vacío
        cur = c.execute("SELECT COUNT(*) AS n FROM usuarios")
        if cur.fetchone()[0] == 0:
            c.execute(
                "INSERT INTO usuarios(username, pw_hash, rol, activo) VALUES (?,?,?,1)",
                ("admin", _hash_pw("admin"), "ADMIN"),
            )