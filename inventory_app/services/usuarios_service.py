# ==============================
# File: inventory_app/services/usuarios_service.py
# ==============================
from __future__ import annotations
from typing import List, Optional

from ..domain.models import Usuario
from ..domain.interfaces import RepoUsuarios


class UsuariosService:
    """Servicio de lógica de negocio para gestión de usuarios"""
    
    def __init__(self, repo_usuarios: RepoUsuarios):
        self._ru = repo_usuarios
    
    def autenticar(self, username: str, password: str) -> Optional[Usuario]:
        """Autentica un usuario con username y password"""
        return self._ru.autenticar(username, password)
    
    def crear_usuario(self, username: str, password: str, rol: str) -> Usuario:
        """Crea un nuevo usuario"""
        # Aquí se pueden agregar validaciones de negocio
        # Por ejemplo: validar que el username no esté vacío,
        # que el rol sea válido, etc.
        if not username or not password:
            raise ValueError("Username y password son requeridos")
        
        if rol not in ("ADMIN", "ENCARGADO", "VENDEDOR"):
            raise ValueError(f"Rol inválido: {rol}")
        
        return self._ru.crear_usuario(username, password, rol)
    
    def listar_usuarios(self) -> List[Usuario]:
        """Lista todos los usuarios"""
        return self._ru.listar_usuarios()
    
    def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Usuario]:
        """Obtiene un usuario por su ID"""
        return self._ru.obtener_usuario_por_id(usuario_id)

