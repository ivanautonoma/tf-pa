# ==============================
# File: inventory_app/mvc/models/user_models.py
# ==============================
from __future__ import annotations
from typing import List, Optional
from dataclasses import dataclass

from ...domain.models import Usuario
from ...services.usuarios_service import UsuariosService


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
    
    def __init__(self, user_service: UsuariosService):
        self.user_service = user_service
    
    def get_usuarios(self) -> List[UsuarioModel]:
        """Obtiene todos los usuarios"""
        usuarios = self.user_service.listar_usuarios()
        return [UsuarioModel.from_domain(u) for u in usuarios]
    
    def create_usuario(self, username: str, password: str, rol: str = "VENDEDOR") -> UsuarioModel:
        """Crea un nuevo usuario"""
        usuario = self.user_service.crear_usuario(username, password, rol)
        return UsuarioModel.from_domain(usuario)
    
    def update_usuario(self, user_id: int, username: str, password: Optional[str] = None, 
                      rol: str = None, activo: bool = None) -> bool:
        """Actualiza un usuario - Nota: Requiere implementación en el servicio"""
        # TODO: Implementar método update en UsuariosService
        # Por ahora mantenemos funcionalidad básica
        return True
    
    def delete_usuario(self, user_id: int) -> bool:
        """Elimina un usuario - Nota: Requiere implementación en el servicio"""
        # TODO: Implementar método delete en UsuariosService con validación
        # Por ahora mantenemos funcionalidad básica
        return True
    
    def authenticate_user(self, username: str, password: str) -> Optional[UsuarioModel]:
        """Autentica un usuario"""
        usuario = self.user_service.autenticar(username, password)
        return UsuarioModel.from_domain(usuario) if usuario else None
    
    def get_usuario_por_id(self, usuario_id: int) -> Optional[UsuarioModel]:
        """Obtiene un usuario por su ID"""
        usuario = self.user_service.obtener_usuario_por_id(usuario_id)
        return UsuarioModel.from_domain(usuario) if usuario else None