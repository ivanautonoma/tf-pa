# ==============================
# File: inventory_app/mvc/models/user_models.py
# ==============================
from __future__ import annotations
from typing import List, Optional
from dataclasses import dataclass

from ...domain.models import Usuario


@dataclass
class UsuarioModel:
    """Modelo de datos para usuarios"""
    id: int
    username: str
    rol: str
    activo: bool
    
    @classmethod
    def from_domain(cls, usuario: Usuario) -> 'UsuarioModel':
        return cls(
            id=usuario.id,
            username=usuario.username,
            rol=usuario.rol,
            activo=usuario.activo
        )


class UserModels:
    """Clase que maneja todos los modelos de usuarios"""
    
    def __init__(self):
        pass
    
    def get_usuarios(self) -> List[UsuarioModel]:
        """Obtiene todos los usuarios"""
        from ...infra.db import get_conn
        with get_conn() as c:
            usuarios = c.execute("SELECT * FROM usuarios ORDER BY username").fetchall()
            return [UsuarioModel(
                id=u['id'],
                username=u['username'],
                rol=u['rol'],
                activo=bool(u['activo'])
            ) for u in usuarios]
    
    def create_usuario(self, username: str, password: str, rol: str = "OPERADOR") -> UsuarioModel:
        """Crea un nuevo usuario"""
        from ...infra.db import get_conn, _hash_pw
        with get_conn() as c:
            cursor = c.execute(
                "INSERT INTO usuarios(username, pw_hash, rol, activo) VALUES (?,?,?,?)",
                (username, _hash_pw(password), rol, 1)
            )
            return UsuarioModel(
                id=cursor.lastrowid,
                username=username,
                rol=rol,
                activo=True
            )
    
    def update_usuario(self, user_id: int, username: str, password: Optional[str] = None, 
                      rol: str = None, activo: bool = None) -> bool:
        """Actualiza un usuario"""
        from ...infra.db import get_conn, _hash_pw
        with get_conn() as c:
            if password:
                c.execute(
                    "UPDATE usuarios SET username=?, pw_hash=?, rol=?, activo=? WHERE id=?",
                    (username, _hash_pw(password), rol, int(activo), user_id)
                )
            else:
                c.execute(
                    "UPDATE usuarios SET username=?, rol=?, activo=? WHERE id=?",
                    (username, rol, int(activo), user_id)
                )
            return True
    
    def delete_usuario(self, user_id: int) -> bool:
        """Elimina un usuario"""
        from ...infra.db import get_conn
        with get_conn() as c:
            # Verificar que no sea el admin principal
            usuario = c.execute("SELECT username FROM usuarios WHERE id=?", (user_id,)).fetchone()
            if usuario and usuario['username'] == 'admin':
                raise ValueError("No se puede eliminar el administrador principal")
            
            c.execute("DELETE FROM usuarios WHERE id=?", (user_id,))
            return True
    
    def authenticate_user(self, username: str, password: str) -> Optional[UsuarioModel]:
        """Autentica un usuario"""
        from ...infra.db import get_conn, _hash_pw
        with get_conn() as c:
            cur = c.execute("SELECT * FROM usuarios WHERE username=? AND activo=1", (username,))
            row = cur.fetchone()
            if not row or row["pw_hash"] != _hash_pw(password):
                return None
            return UsuarioModel(
                id=row["id"],
                username=row["username"],
                rol=row["rol"],
                activo=bool(row["activo"])
            )
    
    def get_usuario_por_id(self, usuario_id: int) -> Optional[UsuarioModel]:
        """Obtiene un usuario por su ID"""
        from ...infra.db import get_conn
        with get_conn() as c:
            cur = c.execute("SELECT * FROM usuarios WHERE id=?", (usuario_id,))
            row = cur.fetchone()
            if not row:
                return None
            return UsuarioModel(
                id=row["id"],
                username=row["username"],
                rol=row["rol"],
                activo=bool(row["activo"])
            )