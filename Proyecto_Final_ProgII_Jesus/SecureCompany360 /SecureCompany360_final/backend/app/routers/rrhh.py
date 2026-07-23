from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security.auth import get_current_user, hash_password, registrar_auditoria
from app.security.permissions import requiere_rol

router = APIRouter(prefix="/rrhh", tags=["RRHH - Grupo 1"])


# ---------- Empleados ----------

@router.post("/empleados", response_model=schemas.EmpleadoOut,
             dependencies=[Depends(requiere_rol("Administrador", "RRHH"))])
def crear_empleado(datos: schemas.EmpleadoCreate, request: Request,
                    db: Session = Depends(get_db),
                    usuario=Depends(get_current_user)):
    if db.query(models.Empleado).filter(models.Empleado.cedula == datos.cedula).first():
        raise HTTPException(status_code=409, detail="Ya existe un empleado con esa cédula")

    empleado = models.Empleado(**datos.model_dump())
    db.add(empleado)
    db.commit()
    db.refresh(empleado)

    registrar_auditoria(db, "CREATE_EMPLEADO", f"Empleado {empleado.id} creado",
                         usuario_id=usuario.id, ip=request.client.host)
    return empleado


@router.get("/empleados", response_model=list[schemas.EmpleadoOut],
            dependencies=[Depends(requiere_rol("Administrador", "RRHH", "Analista"))])
def listar_empleados(db: Session = Depends(get_db)):
    return db.query(models.Empleado).filter(models.Empleado.activo == True).all()  # noqa: E712


@router.get("/empleados/{empleado_id}", response_model=schemas.EmpleadoOut,
            dependencies=[Depends(requiere_rol("Administrador", "RRHH", "Analista"))])
def obtener_empleado(empleado_id: int, db: Session = Depends(get_db)):
    empleado = db.get(models.Empleado, empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


# ---------- Usuarios / cuentas de acceso ----------

@router.post("/usuarios", response_model=schemas.UsuarioOut,
             dependencies=[Depends(requiere_rol("Administrador", "RRHH"))])
def crear_usuario(datos: schemas.UsuarioCreate, request: Request,
                   db: Session = Depends(get_db),
                   admin=Depends(get_current_user)):
    empleado = db.get(models.Empleado, datos.empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no existe")

    if db.query(models.Usuario).filter(models.Usuario.username == datos.username).first():
        raise HTTPException(status_code=409, detail="Ese nombre de usuario ya existe")

    rol = db.query(models.Rol).filter(models.Rol.nombre == datos.rol_nombre).first()
    if not rol:
        raise HTTPException(status_code=400, detail="Rol inválido")

    nuevo_usuario = models.Usuario(
        empleado_id=empleado.id,
        username=datos.username,
        password_hash=hash_password(datos.password),
        rol_id=rol.id,
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    registrar_auditoria(db, "CREATE_USUARIO", f"Usuario {nuevo_usuario.username} creado",
                         usuario_id=admin.id, ip=request.client.host)

    return schemas.UsuarioOut(id=nuevo_usuario.id, username=nuevo_usuario.username,
                               rol=rol.nombre, activo=nuevo_usuario.activo)


@router.get("/usuarios", response_model=list[schemas.UsuarioOut],
            dependencies=[Depends(requiere_rol("Administrador", "RRHH"))])
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()
    return [
        schemas.UsuarioOut(id=u.id, username=u.username, rol=u.rol.nombre, activo=u.activo)
        for u in usuarios
    ]
