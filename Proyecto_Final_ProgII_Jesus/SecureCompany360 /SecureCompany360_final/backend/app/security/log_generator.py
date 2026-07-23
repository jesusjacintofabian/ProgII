import logging
import random
import string
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app import models
from app.security.auth import hash_password

logger = logging.getLogger("secure_company_360")

IPS_SIMULADAS = [
    "192.168.1.100", "10.0.0.45", "172.16.0.88",
    "203.0.113.50", "198.51.100.23", "185.220.101.42",
    "91.121.87.34", "45.33.32.156", "104.248.50.11",
    "167.99.89.47",
]

PAISES_IPS = {
    "192.168.1.100": "Panamá",
    "10.0.0.45": "Panamá",
    "172.16.0.88": "Panamá",
    "203.0.113.50": "Rusia",
    "198.51.100.23": "China",
    "185.220.101.42": "Alemania",
    "91.121.87.34": "Francia",
    "45.33.32.156": "EE.UU.",
    "104.248.50.11": "Nigeria",
    "167.99.89.47": "Brasil",
}

USUARIOS_PRUEBA = ["admin", "jperez", "mlopez", "rhernandez", "crodriguez"]


def _ip_aleatoria(externa: bool = False) -> str:
    if externa:
        return random.choice([ip for ip in IPS_SIMULADAS if PAISES_IPS.get(ip) != "Panamá"])
    return random.choice(IPS_SIMULADAS)


def generar_intento_login(
    db: Session,
    username: str,
    exito: bool,
    ip: Optional[str] = None,
    usuario_id: Optional[int] = None,
):
    if ip is None:
        ip = _ip_aleatoria(externa=not exito)
    accion = "LOGIN_OK" if exito else "LOGIN_FAIL"
    detalle = f"Login {'exitoso' if exito else 'fallido'} para {username}"
    log = models.LogAuditoria(
        usuario_id=usuario_id,
        accion=accion,
        detalle=detalle[:255],
        ip_origen=ip,
    )
    db.add(log)
    db.commit()
    nivel = "INFO" if exito else "WARNING"
    logger.log(getattr(logging, nivel), f"{accion} | {detalle} desde IP {ip}")


def generar_oleada_fuerza_bruta(db: Session, ip: str, cantidad: int = 10):
    for i in range(cantidad):
        username = random.choice(USUARIOS_PRUEBA)
        accion = "LOGIN_FAIL"
        detalle = f"Intento fallido #{i+1} para {username}"
        log = models.LogAuditoria(
            accion=accion,
            detalle=detalle[:255],
            ip_origen=ip,
        )
        db.add(log)
    db.commit()
    logger.warning(f"OLA_FB | {cantidad} intentos fallidos simulados desde IP {ip}")


def generar_inyeccion_sql(db: Session, ip: Optional[str] = None):
    if ip is None:
        ip = _ip_aleatoria(externa=True)
    payloads = [
        "admin' OR '1'='1",
        "'; DROP TABLE usuarios; --",
        "' UNION SELECT * FROM usuarios--",
        "admin'/*",
        "' OR 1=1--",
    ]
    for payload in payloads:
        log = models.LogAuditoria(
            accion="LOGIN_FAIL",
            detalle=f"Posible inyeccion SQL en username: {payload}",
            ip_origen=ip,
        )
        db.add(log)
    db.commit()
    logger.warning(f"SQLI_DETECTED | 5 intentos con patrones SQL desde IP {ip}")


def generar_actividad_fuera_horario(db: Session, cantidad: int = 8):
    for _ in range(cantidad):
        ip = _ip_aleatoria()
        username = random.choice(USUARIOS_PRUEBA)
        fecha = datetime.utcnow().replace(hour=random.choice([0, 1, 2, 3, 4, 23]))
        log = models.LogAuditoria(
            accion=random.choice(["LOGIN_OK", "CREATE_EMPLEADO", "CREATE_ACTIVO"]),
            detalle=f"Operacion fuera de horario por {username}",
            ip_origen=ip,
            fecha=fecha,
        )
        db.add(log)
    db.commit()
    logger.info(f"HORARIO_NOCTURNO | {cantidad} operaciones en horario no laboral generadas")


def generar_acceso_ip_sospechosa(db: Session):
    ip_externa = _ip_aleatoria(externa=True)
    usuario = db.query(models.Usuario).filter(models.Usuario.username == "admin").first()
    if usuario:
        log = models.LogAuditoria(
            usuario_id=usuario.id,
            accion="LOGIN_OK",
            detalle=f"Login exitoso desde IP extranjera ({PAISES_IPS.get(ip_externa, 'Desconocido')})",
            ip_origen=ip_externa,
        )
        db.add(log)
        db.commit()
        logger.warning(f"ACCESO_EXTERNO | Admin accedio desde IP extranjera {ip_externa}")


def generar_evento_completo(db: Session, escenario: str):
    if escenario == "fuerza_bruta":
        ip = _ip_aleatoria(externa=True)
        generar_oleada_fuerza_bruta(db, ip, cantidad=15)
        return {"escenario": "Fuerza Bruta", "ip": ip, "eventos": 15, "pais": PAISES_IPS.get(ip, "Desconocido")}

    elif escenario == "inyeccion_sql":
        ip = _ip_aleatoria(externa=True)
        generar_inyeccion_sql(db, ip)
        return {"escenario": "Inyección SQL", "ip": ip, "eventos": 5, "pais": PAISES_IPS.get(ip, "Desconocido")}

    elif escenario == "acceso_externo":
        generar_acceso_ip_sospechosa(db)
        return {"escenario": "Acceso desde IP Extranjera", "ip": "Variable", "eventos": 1}

    elif escenario == "actividad_nocturna":
        generar_actividad_fuera_horario(db)
        return {"escenario": "Actividad en Horario Nocturno", "eventos": 8}

    elif escenario == "completo":
        resultados = []
        resultados.append(generar_evento_completo(db, "fuerza_bruta"))
        resultados.append(generar_evento_completo(db, "inyeccion_sql"))
        resultados.append(generar_evento_completo(db, "acceso_externo"))
        resultados.append(generar_evento_completo(db, "actividad_nocturna"))
        return {"escenario": "Simulación Completa de Ataques", "eventos_generados": resultados}

    elif escenario == "normal":
        usuario = db.query(models.Usuario).first()
        uid = usuario.id if usuario else None
        for _ in range(5):
            generar_intento_login(db, random.choice(USUARIOS_PRUEBA), exito=True, usuario_id=uid)
        return {"escenario": "Tráfico Normal", "eventos": 5}

    return {"escenario": "Desconocido", "eventos": 0}
