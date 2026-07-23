from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security.auth import (
    verify_password, crear_access_token, crear_refresh_token,
    registrar_intento_fallido, resetear_intentos, esta_bloqueado,
    registrar_auditoria, decodificar_token,
)
from app.security.rate_limit import limiter
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=schemas.TokenResponse)
@limiter.limit(settings.LOGIN_RATE_LIMIT)
def login(request: Request, datos: schemas.LoginRequest, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else None

    usuario = db.query(models.Usuario).filter(
        models.Usuario.username == datos.username
    ).first()

    # Mensaje genérico SIEMPRE (no revelar si el usuario existe o no)
    error_generico = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuario o contraseña incorrectos",
    )

    if usuario is None:
        registrar_auditoria(db, "LOGIN_FAIL", f"Usuario inexistente: {datos.username}", ip=ip)
        raise error_generico

    if esta_bloqueado(usuario):
        registrar_auditoria(db, "LOGIN_BLOQUEADO", "Cuenta bloqueada temporalmente",
                             usuario_id=usuario.id, ip=ip)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Cuenta bloqueada temporalmente por intentos fallidos. Intenta más tarde.",
        )

    if not usuario.activo or not verify_password(datos.password, usuario.password_hash):
        registrar_intento_fallido(usuario, db)
        registrar_auditoria(db, "LOGIN_FAIL", "Contraseña incorrecta",
                             usuario_id=usuario.id, ip=ip)
        raise error_generico

    resetear_intentos(usuario, db)
    registrar_auditoria(db, "LOGIN_OK", "Login exitoso", usuario_id=usuario.id, ip=ip)

    access_token = crear_access_token({"sub": usuario.username, "rol": usuario.rol.nombre})
    refresh_token = crear_refresh_token({"sub": usuario.username})

    return schemas.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        rol=usuario.rol.nombre,
    )


@router.post("/refresh", response_model=schemas.TokenResponse)
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    payload = decodificar_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token de refresco inválido")

    usuario = db.query(models.Usuario).filter(
        models.Usuario.username == payload.get("sub")
    ).first()
    if usuario is None or not usuario.activo:
        raise HTTPException(status_code=401, detail="Usuario no válido")

    access_token = crear_access_token({"sub": usuario.username, "rol": usuario.rol.nombre})
    new_refresh = crear_refresh_token({"sub": usuario.username})
    return schemas.TokenResponse(
        access_token=access_token, refresh_token=new_refresh, rol=usuario.rol.nombre
    )
