"""
Esquemas Pydantic: esta es la primera línea de defensa contra payloads maliciosos.
Todo lo que entra por la API pasa por aquí antes de tocar la base de datos.
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import re

# ---------------- AUTH ----------------

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    rol: str


# ---------------- EMPLEADO / RRHH (Grupo 1) ----------------

class EmpleadoCreate(BaseModel):
    nombre_completo: str = Field(..., min_length=3, max_length=120)
    cedula: str = Field(..., min_length=5, max_length=20)
    cargo: Optional[str] = Field(None, max_length=80)
    departamento: Optional[str] = Field(None, max_length=80)

    @field_validator("cedula")
    @classmethod
    def validar_cedula(cls, v):
        if not re.match(r"^[A-Za-z0-9\-]+$", v):
            raise ValueError("Cédula con formato inválido")
        return v


class EmpleadoOut(BaseModel):
    id: int
    nombre_completo: str
    cedula: str
    cargo: Optional[str]
    departamento: Optional[str]
    fecha_ingreso: date
    activo: bool

    class Config:
        from_attributes = True


class UsuarioCreate(BaseModel):
    empleado_id: int
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.]+$")
    password: str = Field(..., min_length=8, max_length=72)
    rol_nombre: str = Field(..., max_length=30)

    @field_validator("password")
    @classmethod
    def password_segura(cls, v):
        if not re.search(r"[A-Z]", v) or not re.search(r"[0-9]", v):
            raise ValueError(
                "La contraseña debe tener al menos una mayúscula y un número"
            )
        return v


class UsuarioOut(BaseModel):
    id: int
    username: str
    rol: str
    activo: bool

    class Config:
        from_attributes = True


# ---------------- INVENTARIO (Grupo 1) ----------------

class ActivoCreate(BaseModel):
    tipo: str = Field(..., pattern=r"^(Equipo|Software|Otro)$")
    nombre: str = Field(..., min_length=2, max_length=120)
    numero_serie: Optional[str] = Field(None, max_length=60)


class ActivoOut(BaseModel):
    id: int
    tipo: str
    nombre: str
    numero_serie: Optional[str]
    estado: str
    asignado_a: Optional[int]
    fecha_registro: datetime

    class Config:
        from_attributes = True


class ActivoSolicitud(BaseModel):
    activo_id: int
    empleado_id: int


# ---------------- MESA DE AYUDA (Grupo 2) ----------------

class TicketCreate(BaseModel):
    titulo: str = Field(..., min_length=5, max_length=150)
    descripcion: str = Field(..., max_length=4000)
    categoria: str = Field(..., pattern=r"^(Incidencia|Solicitud|Soporte)$")
    prioridad: str = Field("Media", pattern=r"^(Baja|Media|Alta|Critica)$")


class TicketUpdate(BaseModel):
    estado: Optional[str] = Field(None, pattern=r"^(Abierto|En Progreso|Resuelto|Cerrado)$")
    asignado_a: Optional[int] = None
    prioridad: Optional[str] = Field(None, pattern=r"^(Baja|Media|Alta|Critica)$")


class TicketOut(BaseModel):
    id: int
    titulo: str
    descripcion: Optional[str]
    categoria: str
    prioridad: str
    estado: str
    usuario_id: int
    asignado_a: Optional[int]
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True


# ---------------- ADMIN / DASHBOARD (Grupo 2) ----------------

class DashboardMetrics(BaseModel):
    total_usuarios_activos: int
    total_empleados: int
    tickets_abiertos: int
    tickets_criticos: int
    activos_disponibles: int
    activos_asignados: int
    intentos_login_fallidos_24h: int


# ---------------- ANALIZADOR DE LOGS ----------------

class LogResumen(BaseModel):
    total_log_archivo: int
    total_log_auditoria: int
    total_errores: int
    total_bloqueos: int
    total_fallidos: int


class LogAlerta(BaseModel):
    nivel: str
    tipo: str
    mensaje: str


class IPFallida(BaseModel):
    ip: str
    cantidad: int


class UsuarioActivo(BaseModel):
    usuario: str
    acciones: int


class ErrorReciente(BaseModel):
    timestamp: str
    mensaje: str


class LogAnalysisOut(BaseModel):
    nivel_riesgo: str
    resumen: LogResumen
    alertas: List[LogAlerta]
    ips_fallidas: List[IPFallida]
    usuarios_activos: List[UsuarioActivo]
    errores_recientes: List[ErrorReciente]
    recomendaciones: List[str]


# ---------------- SEGURIDAD / ALERTAS (Nuevo) ----------------


class AlertaSeguridadOut(BaseModel):
    id: int
    tipo: str
    nivel: str
    mensaje: str
    ip_origen: Optional[str] = None
    leida: bool
    respuesta_ejecutada: Optional[str] = None
    creado_en: str


class IncidenteSeguridadOut(BaseModel):
    id: int
    tipo: str
    nivel: str
    descripcion: str
    estado: str
    ip_origen: Optional[str] = None
    alerta_id: Optional[int] = None
    creado_en: str


class IPBloqueadaOut(BaseModel):
    id: int
    direccion_ip: str
    motivo: Optional[str] = None
    activo: bool
    creado_en: str


class IPBloquearRequest(BaseModel):
    direccion_ip: str = Field(..., max_length=45)
    motivo: str = Field("Bloqueo manual por administrador", max_length=255)


class DeshabilitarUsuarioRequest(BaseModel):
    usuario_id: int
    motivo: str = Field("Deshabilitado por administrador", max_length=255)


class CorreoRequest(BaseModel):
    destinatario: str = Field(..., max_length=255)
    asunto: str = Field(..., max_length=255)
    cuerpo: str = Field(..., max_length=4000)


class RespuestaAccionOut(BaseModel):
    exito: bool
    mensaje: str
    archivo: Optional[str] = None


class LogGenerarRequest(BaseModel):
    escenario: str = Field("completo", pattern=r"^(fuerza_bruta|inyeccion_sql|acceso_externo|actividad_nocturna|completo|normal)$")


class DashboardSeguridadOut(BaseModel):
    alertas_no_leidas: int
    incidentes_abiertos: int
    ips_bloqueadas: int
    usuarios_deshabilitados: int
    intentos_fallidos_24h: int
    alertas_ultima_hora: int
    nivel_riesgo_actual: str

