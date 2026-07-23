from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security.permissions import requiere_rol

router = APIRouter(prefix="/admin", tags=["Administrador General - Grupo 2"])


@router.get("/dashboard", response_model=schemas.DashboardMetrics,
            dependencies=[Depends(requiere_rol("Administrador"))])
def dashboard(db: Session = Depends(get_db)):
    hace_24h = datetime.utcnow() - timedelta(hours=24)

    return schemas.DashboardMetrics(
        total_usuarios_activos=db.query(models.Usuario).filter(
            models.Usuario.activo == True).count(),
        total_empleados=db.query(models.Empleado).filter(
            models.Empleado.activo == True).count(),
        tickets_abiertos=db.query(models.Ticket).filter(
            models.Ticket.estado.in_(["Abierto", "En Progreso"])).count(),
        tickets_criticos=db.query(models.Ticket).filter(
            models.Ticket.prioridad == "Critica",
            models.Ticket.estado != "Cerrado").count(),
        activos_disponibles=db.query(models.Activo).filter(
            models.Activo.estado == "Disponible").count(),
        activos_asignados=db.query(models.Activo).filter(
            models.Activo.estado == "Asignado").count(),
        intentos_login_fallidos_24h=db.query(models.LogAuditoria).filter(
            models.LogAuditoria.accion == "LOGIN_FAIL",
            models.LogAuditoria.fecha >= hace_24h).count(),
    )


@router.get("/auditoria", dependencies=[Depends(requiere_rol("Administrador"))])
def ver_auditoria(db: Session = Depends(get_db), limite: int = 100):
    logs = db.query(models.LogAuditoria).order_by(
        models.LogAuditoria.fecha.desc()
    ).limit(min(limite, 500)).all()
    return [
        {
            "id": l.id, "usuario_id": l.usuario_id, "accion": l.accion,
            "detalle": l.detalle, "ip_origen": l.ip_origen,
            "fecha": l.fecha.isoformat(),
        }
        for l in logs
    ]


from app.security import log_analyzer

@router.get(
    "/analisis-logs",
    response_model=schemas.LogAnalysisOut,
    tags=["Centro de Seguridad - Grupo 3"],
    summary="Análisis integral de logs de ciberseguridad y sistema",
    description="""
Analiza los registros de auditoría almacenados en la base de datos y los logs técnicos
en disco (`secure_company_360.log`), buscando patrones de ataque, errores de sistema
y eventos de comportamiento anómalo.

**Patrones y Ataques detectados:**
- Fuerza bruta por IP (≥ 5 intentos fallidos desde la misma dirección IP).
- Fuerza bruta por cuenta de usuario (≥ 5 intentos fallidos sobre la misma firma).
- Inyección SQL en payloads de login (detecta `OR 1=1`, `UNION SELECT`, `--`, `/*`, etc.).

**Errores detectados:**
- Excepciones técnicas no controladas registradas en `secure_company_360.log`.
- Bloqueos temporales de cuentas por superar el umbral de intentos fallidos.

**Eventos anómalos detectados:**
- Actividad en horario nocturno no habitual (11 PM – 5 AM).

**Niveles de riesgo:**
- `Bajo` — Sin anomalías significativas.
- `Medio` — Bloqueos, errores moderados o actividad nocturna inusual.
- `Alto` — Fuerza bruta activa o posibles inyecciones SQL detectadas.

Requiere privilegios de **Administrador**.
    """,
    dependencies=[Depends(requiere_rol("Administrador"))],
)
def analizar_logs(db: Session = Depends(get_db)):
    """Ejecuta el escaneo inteligente de registros de auditoría y archivos de logs."""
    return log_analyzer.generar_analisis_completo(db)
