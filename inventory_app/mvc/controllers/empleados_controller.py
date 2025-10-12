# ==============================
# File: inventory_app/mvc/controllers/empleados_controller.py
# ==============================
from __future__ import annotations
from typing import List, Dict, Any, Optional

from .base_controller import BaseController


class EmpleadosController(BaseController):
    """Controlador para la gestión de empleados"""
    
    def get_data(self) -> List[Dict[str, Any]]:
        """Obtiene todos los empleados con información completa"""
        try:
            # Obtener empleados completos desde el servicio
            empleados = self.inventory_models.inventory_service.listar_empleados()
            empleados_data = []
            
            for empleado in empleados:
                # Obtener información del usuario desde user_models
                usuario = self.user_models.get_usuario_por_id(empleado.usuario_id)
                
                # Obtener información de la tienda
                tienda = self.inventory_models.inventory_service._rt.listar_tiendas()
                tienda_nombre = "N/A"
                for t in tienda:
                    if t.id == empleado.tienda_id:
                        tienda_nombre = t.nombre
                        break
                
                empleados_data.append({
                    'id': empleado.id,
                    'usuario_id': empleado.usuario_id,
                    'username': usuario.username if usuario else "N/A",
                    'nombres': empleado.nombres,
                    'apellidos': empleado.apellidos,
                    'dni': empleado.dni,
                    'jornada': empleado.jornada,
                    'tienda': tienda_nombre,
                    'rol': usuario.rol if usuario else "N/A",
                    'estado': "Activo" if usuario and usuario.activo else "Inactivo"
                })
            
            return empleados_data
            
        except Exception as e:
            print(f"Error al obtener empleados: {e}")
            # Fallback a solo usuarios si hay error
            usuarios = self.user_models.get_usuarios()
            return [
                {
                    'id': u.id,
                    'usuario_id': u.id,
                    'username': u.username,
                    'nombres': "N/A",
                    'apellidos': "N/A", 
                    'dni': "N/A",
                    'jornada': "N/A",
                    'tienda': "N/A",
                    'rol': u.rol,
                    'estado': "Activo" if u.activo else "Inactivo"
                }
                for u in usuarios
            ]
    
    def handle_action(self, action: str, data: Dict[str, Any]) -> bool:
        """Maneja las acciones de la vista de empleados"""
        try:
            if action == "create_empleado":
                return self._create_empleado(data)
            elif action == "create_empleado_completo":
                return self._create_empleado_completo(data)
            elif action == "edit_empleado":
                return self._edit_empleado(data)
            elif action == "edit_empleado_completo":
                return self._edit_empleado_completo(data)
            elif action == "delete_empleado":
                return self._delete_empleado(data)
            else:
                return False
        except Exception as e:
            raise Exception(f"Error en acción {action}: {str(e)}")
    
    def _create_empleado(self, data: Dict[str, Any]) -> bool:
        """Crea un nuevo empleado"""
        if not self.validate_user_permission("ADMIN"):
            raise PermissionError("Solo los administradores pueden crear empleados")
        
        username = data.get('username')
        password = data.get('password')
        rol = data.get('rol', 'OPERADOR')
        
        if not username or not password:
            raise ValueError("Usuario y contraseña son requeridos")
        
        self.user_models.create_usuario(username, password, rol)
        return True
    
    def _create_empleado_completo(self, data: Dict[str, Any]) -> bool:
        """Crea un empleado completo con información personal"""
        if not self.validate_user_permission("ADMIN"):
            raise PermissionError("Solo los administradores pueden crear empleados")
        
        username = data.get('username')
        password = data.get('password')
        rol = data.get('rol', 'OPERADOR')
        nombres = data.get('nombres')
        apellidos = data.get('apellidos')
        dni = data.get('dni')
        jornada = data.get('jornada')
        tienda_id = data.get('tienda_id')
        
        if not all([username, password, nombres, apellidos, dni, jornada, tienda_id]):
            raise ValueError("Todos los campos son requeridos")
        
        # Usar el servicio de inventario para crear empleado completo
        usuario, empleado = self.inventory_models.inventory_service.crear_empleado_completo(
            username, password, rol, nombres, apellidos, dni, jornada, tienda_id
        )
        
        return True
    
    def _edit_empleado_completo(self, data: Dict[str, Any]) -> bool:
        """Edita un empleado completo con información personal"""
        if not self.validate_user_permission("ADMIN"):
            raise PermissionError("Solo los administradores pueden editar empleados")
        
        print(f"DEBUG: Datos recibidos para editar empleado: {data}")
        
        empleado_id = data.get('empleado_id')
        usuario_id = data.get('usuario_id')
        username = data.get('username')
        password = data.get('password')  # Opcional
        rol = data.get('rol', 'OPERADOR')
        nombres = data.get('nombres')
        apellidos = data.get('apellidos')
        dni = data.get('dni')
        jornada = data.get('jornada')
        tienda_id = data.get('tienda_id')
        
        print(f"DEBUG: Campos extraídos:")
        print(f"  empleado_id: {empleado_id} (tipo: {type(empleado_id)})")
        print(f"  usuario_id: {usuario_id} (tipo: {type(usuario_id)})")
        print(f"  username: {username} (tipo: {type(username)})")
        print(f"  nombres: {nombres} (tipo: {type(nombres)})")
        print(f"  apellidos: {apellidos} (tipo: {type(apellidos)})")
        print(f"  dni: {dni} (tipo: {type(dni)})")
        print(f"  jornada: {jornada} (tipo: {type(jornada)})")
        print(f"  tienda_id: {tienda_id} (tipo: {type(tienda_id)})")
        
        # Validar campos requeridos (usuario_id es opcional, se puede obtener del empleado_id)
        campos_requeridos = {
            'empleado_id': empleado_id,
            'username': username,
            'nombres': nombres,
            'apellidos': apellidos,
            'dni': dni,
            'jornada': jornada,
            'tienda_id': tienda_id
        }
        
        campos_faltantes = []
        for campo, valor in campos_requeridos.items():
            if not valor or (isinstance(valor, str) and not valor.strip()):
                campos_faltantes.append(campo)
        
        if campos_faltantes:
            raise ValueError(f"Campos requeridos faltantes: {', '.join(campos_faltantes)}")
        
        # Si no se proporcionó usuario_id, obtenerlo del empleado
        if not usuario_id:
            try:
                empleado = self.inventory_models.inventory_service.obtener_empleado_por_id(empleado_id)
                if empleado:
                    usuario_id = empleado.usuario_id
                    print(f"DEBUG: usuario_id obtenido del empleado: {usuario_id}")
                else:
                    raise ValueError("No se pudo encontrar el empleado con el ID proporcionado")
            except Exception as e:
                print(f"Error al obtener usuario_id del empleado: {e}")
                raise ValueError("No se pudo obtener el usuario_id del empleado")
        
        try:
            # Actualizar usuario
            if password:
                # Si se proporcionó nueva contraseña, actualizar usuario con contraseña
                self.user_models.update_usuario(usuario_id, username, password, rol, True)
            else:
                # Si no hay nueva contraseña, actualizar solo username y rol
                self.user_models.update_usuario(usuario_id, username, None, rol, True)
            
            # Actualizar información del empleado
            success = self.inventory_models.inventory_service.actualizar_empleado(
                empleado_id, nombres, apellidos, dni, jornada, tienda_id
            )
            
            return success
            
        except Exception as e:
            print(f"Error al actualizar empleado completo: {e}")
            raise
    
    def _edit_empleado(self, data: Dict[str, Any]) -> bool:
        """Edita un empleado"""
        if not self.validate_user_permission("ADMIN"):
            raise PermissionError("Solo los administradores pueden editar empleados")
        
        user_id = data.get('id')
        username = data.get('username')
        password = data.get('password')
        rol = data.get('rol')
        activo = data.get('activo')
        
        if not user_id or not username:
            raise ValueError("ID y nombre de usuario son requeridos")
        
        self.user_models.update_usuario(user_id, username, password, rol, activo)
        return True
    
    def _delete_empleado(self, data: Dict[str, Any]) -> bool:
        """Elimina un empleado"""
        if not self.validate_user_permission("ADMIN"):
            raise PermissionError("Solo los administradores pueden eliminar empleados")
        
        user_id = data.get('id')
        if not user_id:
            raise ValueError("ID de usuario requerido")
        
        self.user_models.delete_usuario(user_id)
        return True
    
    def get_empleado_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un empleado por ID"""
        empleados = self.get_data()
        for empleado in empleados:
            if empleado['id'] == user_id:
                return empleado
        return None
