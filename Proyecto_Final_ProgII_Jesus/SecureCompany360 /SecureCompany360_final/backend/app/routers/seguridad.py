from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security.auth import get_current_user, registrar_auditoria
from app.security.permissions import requiere_rol

router = APIRouter(prefix="/admin", tags=["Centro de Seguridad - Grupo 3"])


# ========================
# GENERADOR DE LOGS
# ========================

from app.security import log_generator

@router.post("/logs/generar", dependencies=[Depends(requiere_rol("Administrador"))])
def generar_logs(datos: schemas.LogGenerarRequest, request: Request,
                 db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    resultado = log_generator.generar_evento_completo(db, datos.escenario)
    registrar_auditoria(db, "GENERAR_LOGS",
                         f"Logs generados: {datos.escenario}",
                         usuario_id=usuario.id, ip=request.client.host)
    return resultado


# ========================
# MOTOR DE ALERTAS
# ========================

from app.security import alert_engine

@router.get("/alertas", response_model=list[schemas.AlertaSeguridadOut],
            dependencies=[Depends(requiere_rol("Administrador"))])
def listar_alertas(no_leidas: bool = Query(False), db: Session = Depends(get_db)):
    return alert_engine.obtener_alertas_recientes(db, no_leidas=no_leidas)


@router.post("/alertas/evaluar", dependencies=[Depends(requiere_rol("Administrador"))])
def evaluar_alertas(request: Request, db: Session = Depends(get_db),
                    usuario=Depends(get_current_user)):
    generadas = alert_engine.evaluar_alertas(db)
    total = len(generadas)
    registrar_auditoria(db, "EVALUAR_ALERTAS",
                         f"Evaluación completada: {total} alerta(s) generada(s)",
                         usuario_id=usuario.id, ip=request.client.host)
    return {"alertas_generadas": total, "detalle": [{"id": a.id, "tipo": a.tipo, "nivel": a.nivel} for a in generadas]}


@router.patch("/alertas/{alerta_id}/leer", dependencies=[Depends(requiere_rol("Administrador"))])
def marcar_alerta_leida(alerta_id: int, db: Session = Depends(get_db)):
    alerta = db.get(models.AlertaSeguridad, alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    alerta.leida = True
    db.commit()
    return {"exito": True, "mensaje": "Alerta marcada como leída"}


@router.get("/incidentes", response_model=list[schemas.IncidenteSeguridadOut],
            dependencies=[Depends(requiere_rol("Administrador"))])
def listar_incidentes(db: Session = Depends(get_db)):
    return alert_engine.obtener_incidentes(db)


@router.patch("/incidentes/{incidente_id}", dependencies=[Depends(requiere_rol("Administrador"))])
def actualizar_incidente(incidente_id: int, estado: str = Query(..., pattern=r"^(Abierto|En_Investigacion|Resuelto|Cerrado)$"),
                         db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    incidente = db.get(models.IncidenteSeguridad, incidente_id)
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    incidente.estado = estado
    if estado in ("Resuelto", "Cerrado"):
        incidente.resuelto_por = usuario.id
        incidente.resuelto_en = datetime.utcnow()
    db.commit()
    return {"exito": True, "mensaje": f"Incidente {incidente_id} actualizado a '{estado}'"}


# ========================
# RESPUESTAS AUTOMATIZADAS
# ========================

from app.security import auto_response

@router.post("/respuestas/bloquear-ip", response_model=schemas.RespuestaAccionOut,
             dependencies=[Depends(requiere_rol("Administrador"))])
def bloquear_ip(datos: schemas.IPBloquearRequest, request: Request,
                db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    resultado = auto_response.bloquear_ip(db, datos.direccion_ip, datos.motivo, usuario_id=usuario.id)
    if not resultado["exito"]:
        raise HTTPException(status_code=409, detail=resultado["mensaje"])
    return resultado


@router.post("/respuestas/desbloquear-ip", response_model=schemas.RespuestaAccionOut,
             dependencies=[Depends(requiere_rol("Administrador"))])
def desbloquear_ip(datos: schemas.IPBloquearRequest, request: Request,
                   db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return auto_response.desbloquear_ip(db, datos.direccion_ip, usuario_id=usuario.id)


@router.get("/ips-bloqueadas", response_model=list[schemas.IPBloqueadaOut],
            dependencies=[Depends(requiere_rol("Administrador"))])
def listar_ips_bloqueadas(db: Session = Depends(get_db)):
    ips = db.query(models.IPBloqueada).filter(
        models.IPBloqueada.activo == True
    ).order_by(models.IPBloqueada.creado_en.desc()).all()
    return [
        {
            "id": ip.id, "direccion_ip": ip.direccion_ip,
            "motivo": ip.motivo, "activo": ip.activo,
            "creado_en": ip.creado_en.isoformat(),
        }
        for ip in ips
    ]


@router.delete("/ips-bloqueadas/{ip_id}", response_model=schemas.RespuestaAccionOut,
               dependencies=[Depends(requiere_rol("Administrador"))])
def eliminar_ip_bloqueada(ip_id: int, request: Request,
                          db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    ip = db.get(models.IPBloqueada, ip_id)
    if not ip:
        raise HTTPException(status_code=404, detail="IP bloqueada no encontrada")
    ip.activo = False
    db.commit()
    registrar_auditoria(db, "ELIMINAR_IP_BLOQUEADA", f"IP {ip.direccion_ip} eliminada de bloqueos",
                         usuario_id=usuario.id, ip=request.client.host)
    return {"exito": True, "mensaje": f"IP {ip.direccion_ip} eliminada de la lista de bloqueo"}


@router.post("/respuestas/deshabilitar-usuario", response_model=schemas.RespuestaAccionOut,
             dependencies=[Depends(requiere_rol("Administrador"))])
def deshabilitar_usuario_endpoint(datos: schemas.DeshabilitarUsuarioRequest, request: Request,
                                  db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    resultado = auto_response.deshabilitar_usuario(db, datos.usuario_id, datos.motivo, admin_id=usuario.id)
    if not resultado["exito"]:
        raise HTTPException(status_code=409, detail=resultado["mensaje"])
    return resultado


@router.post("/respuestas/habilitar-usuario", response_model=schemas.RespuestaAccionOut,
             dependencies=[Depends(requiere_rol("Administrador"))])
def habilitar_usuario_endpoint(datos: schemas.DeshabilitarUsuarioRequest, request: Request,
                               db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return auto_response.habilitar_usuario(db, datos.usuario_id, admin_id=usuario.id)


@router.post("/respuestas/enviar-correo", response_model=schemas.RespuestaAccionOut,
             dependencies=[Depends(requiere_rol("Administrador"))])
def enviar_correo_endpoint(datos: schemas.CorreoRequest, request: Request,
                           usuario=Depends(get_current_user)):
    resultado = auto_response.enviar_correo(datos.destinatario, datos.asunto, datos.cuerpo)
    return resultado


@router.post("/respuestas/generar-reporte", response_model=schemas.RespuestaAccionOut,
             dependencies=[Depends(requiere_rol("Administrador"))])
def generar_reporte_endpoint(tipo: str = Query("completo"), request: Request = None,
                             db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    resultado = auto_response.generar_reporte(tipo, db)
    registrar_auditoria(db, "GENERAR_REPORTE",
                         f"Reporte {tipo} generado: {resultado.get('archivo', 'N/A')}",
                         usuario_id=usuario.id, ip=request.client.host if request else None)
    return resultado


# ========================
# DASHBOARD DE SEGURIDAD
# ========================

@router.get("/seguridad/dashboard", response_model=schemas.DashboardSeguridadOut,
            dependencies=[Depends(requiere_rol("Administrador"))])
def dashboard_seguridad(db: Session = Depends(get_db)):
    hace_24h = datetime.utcnow() - timedelta(hours=24)
    hace_1h = datetime.utcnow() - timedelta(hours=1)

    alertas_no_leidas = db.query(models.AlertaSeguridad).filter(
        models.AlertaSeguridad.leida == False).count()
    incidentes_abiertos = db.query(models.IncidenteSeguridad).filter(
        models.IncidenteSeguridad.estado.in_(["Abierto", "En_Investigacion"])).count()
    ips_bloqueadas = db.query(models.IPBloqueada).filter(
        models.IPBloqueada.activo == True).count()
    usuarios_deshabilitados = db.query(models.Usuario).filter(
        models.Usuario.activo == False).count()
    intentos_fallidos_24h = db.query(models.LogAuditoria).filter(
        models.LogAuditoria.accion == "LOGIN_FAIL",
        models.LogAuditoria.fecha >= hace_24h).count()
    alertas_ultima_hora = db.query(models.AlertaSeguridad).filter(
        models.AlertaSeguridad.creado_en >= hace_1h).count()

    if alertas_ultima_hora > 0 or incidentes_abiertos > 0:
        nivel_riesgo = "Alto" if incidentes_abiertos > 2 else "Medio"
    else:
        nivel_riesgo = "Bajo"

    return schemas.DashboardSeguridadOut(
        alertas_no_leidas=alertas_no_leidas,
        incidentes_abiertos=incidentes_abiertos,
        ips_bloqueadas=ips_bloqueadas,
        usuarios_deshabilitados=usuarios_deshabilitados,
        intentos_fallidos_24h=intentos_fallidos_24h,
        alertas_ultima_hora=alertas_ultima_hora,
        nivel_riesgo_actual=nivel_riesgo,
    )
