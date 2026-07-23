from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Text, Float
)
from sqlalchemy.orm import relationship
from app.database import Base


class Rol(Base):
    __tablename__ = "rol"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(30), unique=True, nullable=False)

    usuarios = relationship("Usuario", back_populates="rol")


class Empleado(Base):
    __tablename__ = "empleado"
    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(120), nullable=False)
    cedula = Column(String(20), unique=True, nullable=False)
    cargo = Column(String(80))
    departamento = Column(String(80))
    fecha_ingreso = Column(Date, default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    usuario = relationship("Usuario", back_populates="empleado", uselist=False)
    activos_asignados = relationship("Activo", back_populates="empleado")


class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True, index=True)
    empleado_id = Column(Integer, ForeignKey("empleado.id"), nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    rol_id = Column(Integer, ForeignKey("rol.id"), nullable=False)
    intentos_fallidos = Column(Integer, default=0)
    bloqueado_hasta = Column(DateTime, nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    empleado = relationship("Empleado", back_populates="usuario")
    rol = relationship("Rol", back_populates="usuarios")
    tickets_reportados = relationship(
        "Ticket", back_populates="usuario", foreign_keys="Ticket.usuario_id"
    )


class Activo(Base):
    __tablename__ = "activo"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(30), nullable=False)  # Equipo, Software, Otro
    nombre = Column(String(120), nullable=False)
    numero_serie = Column(String(60), unique=True, nullable=True)
    estado = Column(String(30), default="Disponible")
    asignado_a = Column(Integer, ForeignKey("empleado.id"), nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    empleado = relationship("Empleado", back_populates="activos_asignados")
    software = relationship("Software", back_populates="activo")


class Software(Base):
    __tablename__ = "software"
    id = Column(Integer, primary_key=True, index=True)
    activo_id = Column(Integer, ForeignKey("activo.id"), nullable=False)
    licencia = Column(String(100))
    fecha_expiracion = Column(Date, nullable=True)

    activo = relationship("Activo", back_populates="software")


class Ticket(Base):
    __tablename__ = "ticket"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    titulo = Column(String(150), nullable=False)
    descripcion = Column(Text)
    categoria = Column(String(40), default="Soporte")
    prioridad = Column(String(20), default="Media")
    estado = Column(String(30), default="Abierto")
    asignado_a = Column(Integer, ForeignKey("usuario.id"), nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="tickets_reportados", foreign_keys=[usuario_id])


class LogAuditoria(Base):
    __tablename__ = "log_auditoria"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=True)
    accion = Column(String(100), nullable=False)
    detalle = Column(String(255), nullable=True)
    ip_origen = Column(String(45), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)


class IPBloqueada(Base):
    __tablename__ = "ip_bloqueada"
    id = Column(Integer, primary_key=True, index=True)
    direccion_ip = Column(String(45), unique=True, nullable=False, index=True)
    motivo = Column(String(255), nullable=True)
    bloqueado_por = Column(Integer, ForeignKey("usuario.id"), nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    bloqueador = relationship("Usuario", backref="ips_bloqueadas")


class ReglaAlerta(Base):
    __tablename__ = "regla_alerta"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(String(255), nullable=True)
    tipo_evento = Column(String(50), nullable=False)
    patron_deteccion = Column(String(255), nullable=True)
    umbral = Column(Integer, default=5)
    ventana_minutos = Column(Integer, default=10)
    nivel = Column(String(20), default="Alto")
    respuesta_automatica = Column(String(100), nullable=True)
    activa = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)


class AlertaSeguridad(Base):
    __tablename__ = "alerta_seguridad"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False, index=True)
    nivel = Column(String(20), nullable=False)
    mensaje = Column(String(500), nullable=False)
    ip_origen = Column(String(45), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=True)
    regla_id = Column(Integer, ForeignKey("regla_alerta.id"), nullable=True)
    leida = Column(Boolean, default=False)
    respondida_automaticamente = Column(Boolean, default=False)
    respuesta_ejecutada = Column(String(100), nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    regla = relationship("ReglaAlerta", backref="alertas_generadas")


class IncidenteSeguridad(Base):
    __tablename__ = "incidente_seguridad"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False, index=True)
    nivel = Column(String(20), nullable=False)
    descripcion = Column(Text, nullable=False)
    estado = Column(String(30), default="Abierto")
    ip_origen = Column(String(45), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=True)
    alerta_id = Column(Integer, ForeignKey("alerta_seguridad.id"), nullable=True)
    resuelto_por = Column(Integer, ForeignKey("usuario.id"), nullable=True)
    resuelto_en = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
