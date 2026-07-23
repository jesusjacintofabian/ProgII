"""
RBAC (Role-Based Access Control). Se usa como dependencia en cada endpoint
para que ningún desarrollador "se olvide" de proteger una ruta.

Uso:
    @router.post("/", dependencies=[Depends(requiere_rol("Administrador", "RRHH"))])
"""
from fastapi import Depends, HTTPException, status
from app.security.auth import get_current_user
from app import models


def requiere_rol(*roles_permitidos: str):
    def verificador(usuario: models.Usuario = Depends(get_current_user)):
        if usuario.rol.nombre not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción",
            )
        return usuario

    return verificador
