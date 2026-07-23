from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security.auth import get_current_user, registrar_auditoria
from app.security.permissions import requiere_rol

router = APIRouter(prefix="/inventario", tags=["Inventario - Grupo 1"])


@router.post("/activos", response_model=schemas.ActivoOut,
             dependencies=[Depends(requiere_rol("Administrador", "RRHH"))])
def registrar_activo(datos: schemas.ActivoCreate, request: Request,
                      db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    if datos.numero_serie:
        existente = db.query(models.Activo).filter(
            models.Activo.numero_serie == datos.numero_serie
        ).first()
        if existente:
            raise HTTPException(status_code=409, detail="Número de serie ya registrado")

    activo = models.Activo(**datos.model_dump())
    db.add(activo)
    db.commit()
    db.refresh(activo)

    registrar_auditoria(db, "CREATE_ACTIVO", f"Activo {activo.id} registrado",
                         usuario_id=usuario.id, ip=request.client.host)
    return activo


@router.get("/activos", response_model=list[schemas.ActivoOut])
def listar_activos(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return db.query(models.Activo).all()


@router.post("/activos/solicitar", response_model=schemas.ActivoOut)
def solicitar_activo(datos: schemas.ActivoSolicitud, request: Request,
                      db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    """Cualquier usuario autenticado puede solicitar un activo disponible.
    Un usuario normal solo puede solicitar para sí mismo (su propio empleado_id)."""
    if usuario.rol.nombre == "Usuario" and datos.empleado_id != usuario.empleado_id:
        raise HTTPException(status_code=403, detail="Solo puedes solicitar activos para ti mismo")

    activo = db.get(models.Activo, datos.activo_id)
    if not activo:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    if activo.estado != "Disponible":
        raise HTTPException(status_code=409, detail="El activo no está disponible")

    empleado = db.get(models.Empleado, datos.empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    activo.estado = "Solicitado"
    activo.asignado_a = empleado.id
    db.commit()
    db.refresh(activo)

    registrar_auditoria(db, "SOLICITUD_ACTIVO", f"Activo {activo.id} solicitado por empleado {empleado.id}",
                         usuario_id=usuario.id, ip=request.client.host)
    return activo


@router.patch("/activos/{activo_id}/aprobar", response_model=schemas.ActivoOut,
              dependencies=[Depends(requiere_rol("Administrador", "RRHH"))])
def aprobar_activo(activo_id: int, request: Request, db: Session = Depends(get_db),
                    usuario=Depends(get_current_user)):
    activo = db.get(models.Activo, activo_id)
    if not activo:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    activo.estado = "Asignado"
    db.commit()
    db.refresh(activo)

    registrar_auditoria(db, "APROBAR_ACTIVO", f"Activo {activo.id} asignado",
                         usuario_id=usuario.id, ip=request.client.host)
    return activo
