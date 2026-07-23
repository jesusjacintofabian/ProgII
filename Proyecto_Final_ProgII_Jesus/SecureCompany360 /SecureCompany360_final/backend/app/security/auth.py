"""
Núcleo de "Protección" del sistema: hashing de contraseñas, JWT, y control
de fuerza bruta. Compartido por Grupo 1 (RRHH/login) y usado por Grupo 2
(cualquier endpoint protegido).
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ---------- Contraseñas ----------
# Usamos bcrypt directamente (sin passlib, que está sin mantenimiento y rompe
# con versiones nuevas de bcrypt). bcrypt trunca/rechaza >72 bytes por diseño,
# por eso los schemas limitan la contraseña a 72 caracteres.

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


# ---------- JWT ----------

def crear_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def crear_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------- Control de fuerza bruta ----------

def registrar_intento_fallido(usuario: models.Usuario, db: Session) -> None:
    usuario.intentos_fallidos += 1
    if usuario.intentos_fallidos >= settings.MAX_INTENTOS_FALLIDOS:
        usuario.bloqueado_hasta = datetime.utcnow() + timedelta(
            minutes=settings.BLOQUEO_MINUTOS
        )
    db.commit()


def resetear_intentos(usuario: models.Usuario, db: Session) -> None:
    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    db.commit()


def esta_bloqueado(usuario: models.Usuario) -> bool:
    if usuario.bloqueado_hasta and usuario.bloqueado_hasta > datetime.utcnow():
        return True
    return False


# ---------- Dependencia: usuario actual a partir del token ----------

def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.Usuario:
    payload = decodificar_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Tipo de token inválido")
    username: Optional[str] = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Token sin sujeto")

    usuario = db.query(models.Usuario).filter(models.Usuario.username == username).first()
    if usuario is None or not usuario.activo:
        raise HTTPException(status_code=401, detail="Usuario no válido")
    return usuario


def registrar_auditoria(
    db: Session, accion: str, detalle: str = "", usuario_id: Optional[int] = None,
    ip: Optional[str] = None,
) -> None:
    log = models.LogAuditoria(
        usuario_id=usuario_id, accion=accion, detalle=detalle[:255], ip_origen=ip
    )
    db.add(log)
    db.commit()
