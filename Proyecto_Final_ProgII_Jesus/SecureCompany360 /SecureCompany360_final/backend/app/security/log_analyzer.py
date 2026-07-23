import os
import re
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models

# Ruta por defecto para el archivo de logs
LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "secure_company_360.log")

def analizar_archivo_logs() -> Dict[str, Any]:
    """
    Analiza el archivo secure_company_360.log en búsqueda de errores y logs técnicos.
    """
    stats = {
        "total_lineas": 0,
        "total_errores": 0,
        "total_info": 0,
        "errores_recientes": []
    }
    
    if not os.path.exists(LOG_FILE_PATH):
        return stats

    # Expresión regular para parsear: 2026-07-20 20:54:10,123 | INFO | Mensaje
    log_pattern = re.compile(r"^([\d\-\s:,]+) \| ([A-Z]+) \| (.*)$")

    try:
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                stats["total_lineas"] += 1
                match = log_pattern.match(line.strip())
                if match:
                    timestamp, level, message = match.groups()
                    if level == "ERROR":
                        stats["total_errores"] += 1
                        stats["errores_recientes"].append({
                            "timestamp": timestamp,
                            "mensaje": message
                        })
                    elif level == "INFO":
                        stats["total_info"] += 1
        
        # Mantener solo los últimos 15 errores
        stats["errores_recientes"] = stats["errores_recientes"][-15:]
    except Exception:
        # Silenciar problemas de lectura
        pass

    return stats


def analizar_base_auditoria(db: Session) -> Dict[str, Any]:
    """
    Analiza la tabla de LogAuditoria en la base de datos para identificar fallos repetidos,
    acciones frecuentes y posibles ataques.
    """
    # Intentos fallidos por IP
    ips_fallidas = (
        db.query(models.LogAuditoria.ip_origen, func.count(models.LogAuditoria.id).label("total"))
        .filter(models.LogAuditoria.accion == "LOGIN_FAIL")
        .group_by(models.LogAuditoria.ip_origen)
        .order_by(func.count(models.LogAuditoria.id).desc())
        .limit(10)
        .all()
    )

    # Intentos fallidos por detalle (que incluye el nombre de usuario inexistente o el id del usuario)
    usuarios_fallidos = (
        db.query(models.LogAuditoria.detalle, func.count(models.LogAuditoria.id).label("total"))
        .filter(models.LogAuditoria.accion == "LOGIN_FAIL")
        .group_by(models.LogAuditoria.detalle)
        .order_by(func.count(models.LogAuditoria.id).desc())
        .limit(10)
        .all()
    )

    # Total de bloqueos
    total_bloqueos = db.query(models.LogAuditoria).filter(models.LogAuditoria.accion == "LOGIN_BLOQUEADO").count()
    total_fallidos = db.query(models.LogAuditoria).filter(models.LogAuditoria.accion == "LOGIN_FAIL").count()
    total_auditoria = db.query(models.LogAuditoria).count()

    # Usuarios más activos
    usuarios_activos = (
        db.query(models.Usuario.username, func.count(models.LogAuditoria.id).label("total"))
        .join(models.LogAuditoria, models.LogAuditoria.usuario_id == models.Usuario.id)
        .group_by(models.Usuario.username)
        .order_by(func.count(models.LogAuditoria.id).desc())
        .limit(5)
        .all()
    )

    return {
        "total_auditoria": total_auditoria,
        "total_bloqueos": total_bloqueos,
        "total_fallidos": total_fallidos,
        "ips_fallidas": [{"ip": ip or "Desconocido", "cantidad": cant} for ip, cant in ips_fallidas],
        "usuarios_fallidos": [{"usuario": det or "Desconocido", "cantidad": cant} for det, cant in usuarios_fallidos],
        "usuarios_activos": [{"usuario": u, "acciones": cant} for u, cant in usuarios_activos]
    }


def generar_analisis_completo(db: Session) -> Dict[str, Any]:
    """
    Consolida la información del archivo de logs y la base de datos de auditoría,
    creando alertas, determinando el nivel de riesgo global y redactando recomendaciones.
    """
    archivo_stats = analizar_archivo_logs()
    auditoria_stats = analizar_base_auditoria(db)

    alertas = []
    recomendaciones = []
    nivel_riesgo = "Bajo"

    # --- 1. PATRONES Y ATAQUES ---

    # Fuerza bruta por IP (>= 5 intentos fallidos)
    for item in auditoria_stats["ips_fallidas"]:
        if item["cantidad"] >= 5 and item["ip"] != "Desconocido":
            alertas.append({
                "nivel": "Alto",
                "tipo": "FUERZA_BRUTA_IP",
                "mensaje": f"IP {item['ip']} registra {item['cantidad']} intentos de inicio de sesión fallidos."
            })
            recomendaciones.append(f"Considerar bloquear la dirección IP {item['ip']} mediante firewall o regla de red.")

    # Fuerza bruta por usuario/detalle (>= 5 intentos fallidos)
    for item in auditoria_stats["usuarios_fallidos"]:
        if item["cantidad"] >= 5:
            alertas.append({
                "nivel": "Alto",
                "tipo": "FUERZA_BRUTA_USUARIO",
                "mensaje": f"Múltiples accesos fallidos ({item['cantidad']}) registrados bajo la firma: '{item['usuario']}'."
            })
            recomendaciones.append("Revisar si la cuenta del usuario está siendo atacada y sugerir cambio de contraseña.")

    # Escaneo de SQL Injections (Ataques web)
    sql_patterns = [r"'", r"\bunion\b", r"\bselect\b", r"--", r"/\*", r"\bor\s+1=1\b", r"\bor\s+'1'='1'"]
    sql_detectado = False
    
    # Traer logs recientes para examinar inyecciones
    logs_recientes = db.query(models.LogAuditoria).order_by(models.LogAuditoria.fecha.desc()).limit(200).all()
    for log in logs_recientes:
        if log.detalle:
            det_lower = log.detalle.lower()
            for pat in sql_patterns:
                if re.search(pat, det_lower):
                    alertas.append({
                        "nivel": "Alto",
                        "tipo": "INYECCION_SQL_DETECTADA",
                        "mensaje": f"Posible inyección SQL detectada en el payload de login: '{log.detalle}' desde IP {log.ip_origen or 'Desconocida'}."
                    })
                    sql_detectado = True
                    break
            if sql_detectado:
                break
    if sql_detectado:
        recomendaciones.append("Auditar las queries del backend y verificar la sanitización estricta de parámetros en Pydantic.")

    # --- 2. ERRORES ---
    
    # Excepciones técnicas
    if archivo_stats["total_errores"] > 0:
        nivel_err = "Medio" if archivo_stats["total_errores"] < 10 else "Alto"
        alertas.append({
            "nivel": nivel_err,
            "tipo": "ERRORES_SISTEMA",
            "mensaje": f"Se encontraron {archivo_stats["total_errores"]} excepciones técnicas no controladas en secure_company_360.log."
        })
        recomendaciones.append("Revisar los últimos errores del archivo de logs técnicos para parchar fallos de programación.")

    # Cuentas bloqueadas temporales (Eventos de error de seguridad)
    if auditoria_stats["total_bloqueos"] > 0:
        alertas.append({
            "nivel": "Medio",
            "tipo": "CUENTAS_BLOQUEADAS",
            "mensaje": f"Se registraron {auditoria_stats['total_bloqueos']} bloqueos temporales de cuentas por intentos fallidos."
        })
        recomendaciones.append("Monitorear el estado de las cuentas bloqueadas y confirmar con los empleados si fueron ellos.")

    # --- 3. EVENTOS (Comportamiento anómalo en horarios / operaciones críticas) ---

    # Detección de operaciones en horarios nocturnos (Anomalía horaria de 11 PM a 5 AM)
    nocturnos_count = 0
    for log in logs_recientes:
        # Extraer hora
        hora = log.fecha.hour
        if hora >= 23 or hora < 5:
            nocturnos_count += 1
            
    if nocturnos_count >= 5:
        alertas.append({
            "nivel": "Medio",
            "tipo": "ACTIVIDAD_FUERA_HORARIO",
            "mensaje": f"Se registran {nocturnos_count} operaciones en horario nocturno no habitual (11 PM - 5 AM)."
        })
        recomendaciones.append("Validar si el personal autorizado tiene tareas de mantenimiento programadas en horario nocturno.")

    # --- DETERMINAR NIVEL DE RIESGO ---
    if any(a["nivel"] == "Alto" for a in alertas):
        nivel_riesgo = "Alto"
    elif any(a["nivel"] == "Medio" for a in alertas):
        nivel_riesgo = "Medio"

    # Recomendación por defecto si no hay amenazas graves
    if not alertas:
        recomendaciones.append("El sistema se encuentra funcionando de manera óptima. Continúe con el monitoreo rutinario.")

    return {
        "nivel_riesgo": nivel_riesgo,
        "resumen": {
            "total_log_archivo": archivo_stats["total_lineas"],
            "total_log_auditoria": auditoria_stats["total_auditoria"],
            "total_errores": archivo_stats["total_errores"],
            "total_bloqueos": auditoria_stats["total_bloqueos"],
            "total_fallidos": auditoria_stats["total_fallidos"]
        },
        "alertas": alertas,
        "ips_fallidas": auditoria_stats["ips_fallidas"],
        "usuarios_activos": auditoria_stats["usuarios_activos"],
        "errores_recientes": archivo_stats["errores_recientes"],
        "recomendaciones": recomendaciones
    }

