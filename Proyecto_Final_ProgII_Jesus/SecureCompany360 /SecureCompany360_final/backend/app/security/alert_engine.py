import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models
from app.security import auto_response

logger = logging.getLogger("secure_company_360")


def _crear_alerta(
    db: Session,
    tipo: str,
    nivel: str,
    mensaje: str,
    ip_origen: Optional[str] = None,
    usuario_id: Optional[int] = None,
    regla_id: Optional[int] = None,
) -> models.AlertaSeguridad:
    alerta = models.AlertaSeguridad(
        tipo=tipo,
        nivel=nivel,
        mensaje=mensaje[:500],
        ip_origen=ip_origen,
        usuario_id=usuario_id,
        regla_id=regla_id,
    )
    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    logger.warning(f"ALERTA [{nivel}] {tipo}: {mensaje}")

    # --- Respuesta Automática ---
    # Si la regla que disparó esta alerta tiene una respuesta_automatica configurada,
    # se ejecuta de inmediato (sin esperar a que un administrador la dispare a mano).
    if regla_id:
        regla = db.get(models.ReglaAlerta, regla_id)
        if regla and regla.respuesta_automatica:
            resultado = auto_response.ejecutar_respuesta(
                db,
                regla.respuesta_automatica,
                ip=ip_origen,
                usuario_id=usuario_id,
                admin_id=None,  # ejecutada por el sistema, no por un admin humano
            )
            if resultado.get("exito"):
                alerta.respondida_automaticamente = True
                alerta.respuesta_ejecutada = regla.respuesta_automatica
                db.commit()
                logger.warning(
                    f"RESPUESTA_AUTOMATICA | Regla '{regla.nombre}' ejecutó "
                    f"'{regla.respuesta_automatica}' por alerta #{alerta.id}: {resultado.get('mensaje')}"
                )

    return alerta


def _crear_incidente(
    db: Session,
    tipo: str,
    nivel: str,
    descripcion: str,
    ip_origen: Optional[str] = None,
    usuario_id: Optional[int] = None,
    alerta_id: Optional[int] = None,
) -> models.IncidenteSeguridad:
    incidente = models.IncidenteSeguridad(
        tipo=tipo,
        nivel=nivel,
        descripcion=descripcion,
        ip_origen=ip_origen,
        usuario_id=usuario_id,
        alerta_id=alerta_id,
    )
    db.add(incidente)
    db.commit()
    db.refresh(incidente)
    logger.error(f"INCIDENTE [{nivel}] {tipo}: {descripcion[:100]}")
    return incidente


def _contar_eventos(db: Session, accion: str, ip: str, minutos: int = 10) -> int:
    desde = datetime.utcnow() - timedelta(minutes=minutos)
    return db.query(models.LogAuditoria).filter(
        models.LogAuditoria.accion == accion,
        models.LogAuditoria.ip_origen == ip,
        models.LogAuditoria.fecha >= desde,
    ).count()


def _contar_eventos_usuario(db: Session, accion: str, usuario_id: int, minutos: int = 10) -> int:
    desde = datetime.utcnow() - timedelta(minutos=minutos)
    return db.query(models.LogAuditoria).filter(
        models.LogAuditoria.accion == accion,
        models.LogAuditoria.usuario_id == usuario_id,
        models.LogAuditoria.fecha >= desde,
    ).count()


def _ip_esta_bloqueada(db: Session, ip: str) -> bool:
    return db.query(models.IPBloqueada).filter(
        models.IPBloqueada.direccion_ip == ip,
        models.IPBloqueada.activo == True,
    ).first() is not None


def _obtener_reglas_activas(db: Session) -> List[models.ReglaAlerta]:
    return db.query(models.ReglaAlerta).filter(models.ReglaAlerta.activa == True).all()


def _inicializar_reglas(db: Session):
    if db.query(models.ReglaAlerta).count() > 0:
        return

    reglas = [
        models.ReglaAlerta(
            nombre="Fuerza Bruta por IP",
            descripcion="Detecta múltiples intentos de login fallidos desde una misma IP",
            tipo_evento="FUERZA_BRUTA_IP",
            umbral=5,
            ventana_minutos=10,
            nivel="Alto",
            respuesta_automatica="bloquear_ip",
        ),
        models.ReglaAlerta(
            nombre="Fuerza Bruta por Usuario",
            descripcion="Detecta múltiples intentos de login fallidos sobre un mismo usuario",
            tipo_evento="FUERZA_BRUTA_USUARIO",
            umbral=5,
            ventana_minutos=10,
            nivel="Alto",
            respuesta_automatica="deshabilitar_usuario",
        ),
        models.ReglaAlerta(
            nombre="Posible Inyección SQL",
            descripcion="Detecta patrones de SQL injection en intentos de login",
            tipo_evento="INYECCION_SQL",
            umbral=1,
            ventana_minutos=30,
            nivel="Critico",
            respuesta_automatica="bloquear_ip",
        ),
        models.ReglaAlerta(
            nombre="Actividad Fuera de Horario",
            descripcion="Detecta operaciones en horario no laboral (11PM-5AM)",
            tipo_evento="ACTIVIDAD_FUERA_HORARIO",
            umbral=5,
            ventana_minutos=60,
            nivel="Medio",
        ),
        models.ReglaAlerta(
            nombre="Acceso desde IP Extranjera",
            descripcion="Detecta accesos exitosos desde IPs de países de alto riesgo",
            tipo_evento="ACCESO_EXTRANJERO",
            umbral=1,
            ventana_minutos=1440,
            nivel="Medio",
        ),
    ]
    for r in reglas:
        db.add(r)
    db.commit()


def evaluar_alertas(db: Session) -> List[Dict[str, Any]]:
    _inicializar_reglas(db)
    reglas = _obtener_reglas_activas(db)
    alertas_generadas = []

    logins_recientes = (
        db.query(models.LogAuditoria)
        .filter(models.LogAuditoria.fecha >= datetime.utcnow() - timedelta(hours=1))
        .order_by(models.LogAuditoria.fecha.desc())
        .all()
    )

    for regla in reglas:
        if regla.tipo_evento == "FUERZA_BRUTA_IP":
            ips_contador = {}
            for log in logins_recientes:
                if log.accion == "LOGIN_FAIL" and log.ip_origen:
                    ips_contador[log.ip_origen] = ips_contador.get(log.ip_origen, 0) + 1

            for ip, cantidad in ips_contador.items():
                if cantidad >= regla.umbral and not _ip_esta_bloqueada(db, ip):
                    alerta = _crear_alerta(
                        db, "FUERZA_BRUTA_IP", regla.nivel,
                        f"IP {ip} registra {cantidad} intentos de login fallidos en los últimos {regla.ventana_minutos} min.",
                        ip_origen=ip, regla_id=regla.id,
                    )
                    alertas_generadas.append(alerta)

                    if cantidad >= regla.umbral * 2:
                        _crear_incidente(
                            db, "FUERZA_BRUTA_IP", "Critico",
                            f"Ataque de fuerza bruta sostenido desde IP {ip} ({cantidad} intentos). Se requiere acción inmediata.",
                            ip_origen=ip, alerta_id=alerta.id,
                        )

        elif regla.tipo_evento == "FUERZA_BRUTA_USUARIO":
              usuarios_contador = {}
              for log in logins_recientes:
                  if log.accion == "LOGIN_FAIL" and log.usuario_id:
                      usuarios_contador[log.usuario_id] = usuarios_contador.get(log.usuario_id, 0) + 1

              for uid, cantidad in usuarios_contador.items():
                  if cantidad >= regla.umbral:
                      usuario = db.query(models.Usuario).filter(models.Usuario.id == uid).first()
                      nombre_u = usuario.username if usuario else f"ID {uid}"
                      alerta = _crear_alerta(
                          db, "FUERZA_BRUTA_USUARIO", regla.nivel,
                          f"Usuario '{nombre_u}' recibió {cantidad} intentos fallidos en {regla.ventana_minutos} min.",
                          usuario_id=uid, regla_id=regla.id,
                      )
                      alertas_generadas.append(alerta)

        elif regla.tipo_evento == "INYECCION_SQL":
            patrones = [r"'", r"\bunion\b", r"\bselect\b", r"--", r"/\*", r"\bor\s+1=1\b"]
            for log in logins_recientes:
                if log.detalle:
                    for pat in patrones:
                        if re.search(pat, log.detalle.lower()):
                            existe = db.query(models.AlertaSeguridad).filter(
                                models.AlertaSeguridad.tipo == "INYECCION_SQL",
                                models.AlertaSeguridad.ip_origen == log.ip_origen,
                                models.AlertaSeguridad.creado_en >= datetime.utcnow() - timedelta(minutes=30),
                            ).first()
                            if not existe:
                                alerta = _crear_alerta(
                                    db, "INYECCION_SQL", regla.nivel,
                                    f"Posible inyección SQL detectada desde IP {log.ip_origen}: '{log.detalle[:100]}'",
                                    ip_origen=log.ip_origen, regla_id=regla.id,
                                )
                                alertas_generadas.append(alerta)
                                _crear_incidente(
                                    db, "INYECCION_SQL", "Critico",
                                    f"Intento de inyección SQL detectado desde {log.ip_origen}. Payload: {log.detalle[:200]}",
                                    ip_origen=log.ip_origen, alerta_id=alerta.id,
                                )
                            break

        elif regla.tipo_evento == "ACTIVIDAD_FUERA_HORARIO":
            nocturnos = [l for l in logins_recientes if l.fecha.hour >= 23 or l.fecha.hour < 5]
            if len(nocturnos) >= regla.umbral:
                existe = db.query(models.AlertaSeguridad).filter(
                    models.AlertaSeguridad.tipo == "ACTIVIDAD_FUERA_HORARIO",
                    models.AlertaSeguridad.creado_en >= datetime.utcnow() - timedelta(hours=1),
                ).first()
                if not existe:
                    ips = set(l.ip_origen for l in nocturnos if l.ip_origen)
                    alerta = _crear_alerta(
                        db, "ACTIVIDAD_FUERA_HORARIO", regla.nivel,
                        f"{len(nocturnos)} operaciones en horario nocturno (11PM-5AM) desde {len(ips)} IP(s) distintas.",
                        regla_id=regla.id,
                    )
                    alertas_generadas.append(alerta)

        elif regla.tipo_evento == "ACCESO_EXTRANJERO":
            for log in logins_recientes:
                if log.accion == "LOGIN_OK" and log.ip_origen:
                    if not log.ip_origen.startswith(("192.168.", "10.", "172.16.")):
                        existe = db.query(models.AlertaSeguridad).filter(
                            models.AlertaSeguridad.tipo == "ACCESO_EXTRANJERO",
                            models.AlertaSeguridad.ip_origen == log.ip_origen,
                            models.AlertaSeguridad.creado_en >= datetime.utcnow() - timedelta(hours=24),
                        ).first()
                        if not existe:
                            alerta = _crear_alerta(
                                db, "ACCESO_EXTRANJERO", regla.nivel,
                                f"Acceso exitoso desde IP externa {log.ip_origen} (usuario ID {log.usuario_id or 'N/A'})",
                                ip_origen=log.ip_origen, usuario_id=log.usuario_id, regla_id=regla.id,
                            )
                            alertas_generadas.append(alerta)

    return alertas_generadas


def obtener_alertas_recientes(db: Session, no_leidas: bool = False, limite: int = 50) -> List[Dict]:
    query = db.query(models.AlertaSeguridad).order_by(models.AlertaSeguridad.creado_en.desc())
    if no_leidas:
        query = query.filter(models.AlertaSeguridad.leida == False)
    alertas = query.limit(limite).all()
    return [
        {
            "id": a.id,
            "tipo": a.tipo,
            "nivel": a.nivel,
            "mensaje": a.mensaje,
            "ip_origen": a.ip_origen,
            "leida": a.leida,
            "respuesta_ejecutada": a.respuesta_ejecutada,
            "creado_en": a.creado_en.isoformat(),
        }
        for a in alertas
    ]


def obtener_incidentes(db: Session, limite: int = 30) -> List[Dict]:
    incidentes = db.query(models.IncidenteSeguridad).order_by(
        models.IncidenteSeguridad.creado_en.desc()
    ).limit(limite).all()
    return [
        {
            "id": i.id,
            "tipo": i.tipo,
            "nivel": i.nivel,
            "descripcion": i.descripcion,
            "estado": i.estado,
            "ip_origen": i.ip_origen,
            "alerta_id": i.alerta_id,
            "creado_en": i.creado_en.isoformat(),
        }
        for i in incidentes
    ]
