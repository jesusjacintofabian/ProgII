import logging
import os
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app import models
from app.security.auth import registrar_auditoria

logger = logging.getLogger("secure_company_360")


def bloquear_ip(db: Session, direccion_ip: str, motivo: str = "Bloqueo automático por alerta de seguridad",
                usuario_id: Optional[int] = None) -> dict:
    existente = db.query(models.IPBloqueada).filter(
        models.IPBloqueada.direccion_ip == direccion_ip,
        models.IPBloqueada.activo == True,
    ).first()
    if existente:
        return {"exito": False, "mensaje": f"IP {direccion_ip} ya está bloqueada"}

    bloqueo = models.IPBloqueada(
        direccion_ip=direccion_ip,
        motivo=motivo[:255],
        bloqueado_por=usuario_id,
    )
    db.add(bloqueo)
    db.commit()
    registrar_auditoria(db, "BLOQUEO_IP", f"IP {direccion_ip} bloqueada: {motivo}", usuario_id=usuario_id)
    logger.warning(f"AUTO_RESPONSE | IP {direccion_ip} bloqueada: {motivo}")
    return {"exito": True, "mensaje": f"IP {direccion_ip} bloqueada exitosamente"}


def desbloquear_ip(db: Session, direccion_ip: str, usuario_id: Optional[int] = None) -> dict:
    bloqueo = db.query(models.IPBloqueada).filter(
        models.IPBloqueada.direccion_ip == direccion_ip,
        models.IPBloqueada.activo == True,
    ).first()
    if not bloqueo:
        return {"exito": False, "mensaje": f"IP {direccion_ip} no está bloqueada"}
    bloqueo.activo = False
    db.commit()
    registrar_auditoria(db, "DESBLOQUEO_IP", f"IP {direccion_ip} desbloqueada", usuario_id=usuario_id)
    logger.info(f"AUTO_RESPONSE | IP {direccion_ip} desbloqueada")
    return {"exito": True, "mensaje": f"IP {direccion_ip} desbloqueada exitosamente"}


def deshabilitar_usuario(db: Session, usuario_id: int, motivo: str = "Deshabilitado por seguridad",
                         admin_id: Optional[int] = None) -> dict:
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        return {"exito": False, "mensaje": f"Usuario ID {usuario_id} no encontrado"}
    if not usuario.activo:
        return {"exito": False, "mensaje": f"Usuario '{usuario.username}' ya está deshabilitado"}
    usuario.activo = False
    db.commit()
    registrar_auditoria(db, "DESHABILITAR_USUARIO",
                         f"Usuario '{usuario.username}' deshabilitado: {motivo}",
                         usuario_id=admin_id)
    logger.warning(f"AUTO_RESPONSE | Usuario '{usuario.username}' deshabilitado: {motivo}")
    return {"exito": True, "mensaje": f"Usuario '{usuario.username}' deshabilitado exitosamente"}


def habilitar_usuario(db: Session, usuario_id: int, admin_id: Optional[int] = None) -> dict:
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        return {"exito": False, "mensaje": f"Usuario ID {usuario_id} no encontrado"}
    if usuario.activo:
        return {"exito": False, "mensaje": f"Usuario '{usuario.username}' ya está habilitado"}
    usuario.activo = True
    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    db.commit()
    registrar_auditoria(db, "HABILITAR_USUARIO",
                         f"Usuario '{usuario.username}' habilitado nuevamente",
                         usuario_id=admin_id)
    return {"exito": True, "mensaje": f"Usuario '{usuario.username}' habilitado exitosamente"}


def enviar_correo(destinatario: str, asunto: str, cuerpo: str) -> dict:
    logger.info(f"AUTO_RESPONSE | CORREO SIMULADO Para: {destinatario} | Asunto: {asunto}")
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "correos_enviados")
    os.makedirs(logs_dir, exist_ok=True)
    filename = os.path.join(logs_dir, f"correo_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{destinatario.replace('@','_at_')}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Para: {destinatario}\n")
        f.write(f"Asunto: {asunto}\n")
        f.write(f"Fecha: {datetime.utcnow().isoformat()}\n")
        f.write(f"{'='*60}\n")
        f.write(f"{cuerpo}\n")
    return {"exito": True, "mensaje": f"Correo enviado a {destinatario} (simulado en {filename})"}


def generar_reporte(tipo: str = "completo", db: Optional[Session] = None) -> dict:
    reportes_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reportes")
    os.makedirs(reportes_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(reportes_dir, f"reporte_{tipo}_{timestamp}.md")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Reporte de Seguridad - Secure Company 360\n")
        f.write(f"**Tipo:** {tipo.upper()}\n")
        f.write(f"**Generado:** {datetime.utcnow().isoformat()}\n\n")

        if db:

            f.write("## Métricas Generales\n\n")
            total_usuarios = db.query(models.Usuario).count()
            activos_empleados = db.query(models.Empleado).filter(models.Empleado.activo == True).count()
            tickets_abiertos = db.query(models.Ticket).filter(
                models.Ticket.estado.in_(["Abierto", "En Progreso"])).count()
            f.write(f"- Usuarios registrados: {total_usuarios}\n")
            f.write(f"- Empleados activos: {activos_empleados}\n")
            f.write(f"- Tickets abiertos: {tickets_abiertos}\n\n")

            f.write("## Eventos de Auditoría\n\n")
            total_aud = db.query(models.LogAuditoria).count()
            fallidos = db.query(models.LogAuditoria).filter(
                models.LogAuditoria.accion == "LOGIN_FAIL").count()
            bloqueos = db.query(models.LogAuditoria).filter(
                models.LogAuditoria.accion == "LOGIN_BLOQUEADO").count()
            f.write(f"- Total eventos de auditoría: {total_aud}\n")
            f.write(f"- Intentos fallidos: {fallidos}\n")
            f.write(f"- Cuentas bloqueadas: {bloqueos}\n\n")

            f.write("## Alertas de Seguridad\n\n")
            alertas = db.query(models.AlertaSeguridad).order_by(
                models.AlertaSeguridad.creado_en.desc()).limit(20).all()
            if not alertas:
                f.write("No hay alertas registradas.\n")
            for a in alertas:
                f.write(f"- [{a.nivel}] {a.tipo}: {a.mensaje[:100]}\n")

            f.write("\n## Incidentes de Seguridad\n\n")
            incidentes = db.query(models.IncidenteSeguridad).order_by(
                models.IncidenteSeguridad.creado_en.desc()).limit(10).all()
            if not incidentes:
                f.write("No hay incidentes registrados.\n")
            for i in incidentes:
                f.write(f"- [{i.nivel}] {i.tipo} ({i.estado}): {i.descripcion[:100]}\n")

            f.write("\n## IPs Bloqueadas\n\n")
            ips = db.query(models.IPBloqueada).filter(
                models.IPBloqueada.activo == True).all()
            if not ips:
                f.write("No hay IPs bloqueadas.\n")
            for ip in ips:
                f.write(f"- {ip.direccion_ip} (motivo: {ip.motivo})\n")

        f.write(f"\n---\n*Generado automáticamente por Secure Company 360*\n")

    logger.info(f"AUTO_RESPONSE | Reporte generado: {filename}")
    return {"exito": True, "mensaje": f"Reporte generado exitosamente", "archivo": filename}


def ejecutar_respuesta(db: Session, tipo_respuesta: str, ip: Optional[str] = None,
                       usuario_id: Optional[int] = None, admin_id: Optional[int] = None) -> dict:
    if tipo_respuesta == "bloquear_ip" and ip:
        resultado = bloquear_ip(db, ip, usuario_id=admin_id)
        if resultado["exito"]:
            enviar_correo(
                "admin@securecompany360.local",
                f"Alerta: IP {ip} bloqueada automáticamente",
                f"La IP {ip} ha sido bloqueada por el sistema de seguridad.\nMotivo: Superó el umbral de intentos fallidos.\nAcción: Bloqueo automático ejecutado.",
            )
        return resultado

    elif tipo_respuesta == "deshabilitar_usuario" and usuario_id:
        resultado = deshabilitar_usuario(db, usuario_id, admin_id=admin_id)
        if resultado["exito"]:
            enviar_correo(
                "admin@securecompany360.local",
                f"Alerta: Usuario deshabilitado automáticamente",
                f"Un usuario ha sido deshabilitado por el sistema de seguridad.\nMotivo: Actividad sospechosa detectada.\nAcción: Deshabilitación automática ejecutada.",
            )
        return resultado

    elif tipo_respuesta == "enviar_correo":
        return enviar_correo(
            "admin@securecompany360.local",
            "Notificación del Sistema de Seguridad - Secure Company 360",
            "Se ha generado una alerta de seguridad que requiere atención.\n\nPor favor revise el dashboard de seguridad para más detalles."
        )

    elif tipo_respuesta == "generar_reporte":
        return generar_reporte("alerta", db)

    return {"exito": False, "mensaje": f"Tipo de respuesta '{tipo_respuesta}' no reconocido"}
