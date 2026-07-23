-- =========================================================
-- Secure Company 360 - Esquema de Base de Datos (SQL Server)
-- Grupo 1 (RRHH + Inventario) y Grupo 2 (Mesa de Ayuda + Admin)
-- =========================================================

IF DB_ID('SecureCompany360') IS NULL
BEGIN
    CREATE DATABASE SecureCompany360;
END
GO

USE SecureCompany360;
GO

-- ---------- ROLES ----------
IF OBJECT_ID('dbo.Rol', 'U') IS NOT NULL DROP TABLE dbo.Rol;
CREATE TABLE dbo.Rol (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE
);

INSERT INTO dbo.Rol (nombre) VALUES
    ('Administrador'), ('RRHH'), ('Soporte'), ('Analista'), ('Usuario');

-- ---------- EMPLEADOS ----------
IF OBJECT_ID('dbo.Empleado', 'U') IS NOT NULL DROP TABLE dbo.Empleado;
CREATE TABLE dbo.Empleado (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre_completo VARCHAR(120) NOT NULL,
    cedula VARCHAR(20) NOT NULL UNIQUE,
    cargo VARCHAR(80) NULL,
    departamento VARCHAR(80) NULL,
    fecha_ingreso DATE NOT NULL DEFAULT GETDATE(),
    activo BIT NOT NULL DEFAULT 1
);

-- ---------- USUARIOS (login) ----------
IF OBJECT_ID('dbo.Usuario', 'U') IS NOT NULL DROP TABLE dbo.Usuario;
CREATE TABLE dbo.Usuario (
    id INT IDENTITY(1,1) PRIMARY KEY,
    empleado_id INT NOT NULL FOREIGN KEY REFERENCES dbo.Empleado(id),
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol_id INT NOT NULL FOREIGN KEY REFERENCES dbo.Rol(id),
    intentos_fallidos INT NOT NULL DEFAULT 0,
    bloqueado_hasta DATETIME NULL,
    activo BIT NOT NULL DEFAULT 1,
    creado_en DATETIME NOT NULL DEFAULT GETDATE()
);

-- ---------- ACTIVOS (inventario) ----------
IF OBJECT_ID('dbo.Activo', 'U') IS NOT NULL DROP TABLE dbo.Activo;
CREATE TABLE dbo.Activo (
    id INT IDENTITY(1,1) PRIMARY KEY,
    tipo VARCHAR(30) NOT NULL CHECK (tipo IN ('Equipo','Software','Otro')),
    nombre VARCHAR(120) NOT NULL,
    numero_serie VARCHAR(60) NULL UNIQUE,
    estado VARCHAR(30) NOT NULL DEFAULT 'Disponible'
        CHECK (estado IN ('Disponible','Asignado','Solicitado','Baja')),
    asignado_a INT NULL FOREIGN KEY REFERENCES dbo.Empleado(id),
    fecha_registro DATETIME NOT NULL DEFAULT GETDATE()
);

-- ---------- SOFTWARE (detalle de licencias) ----------
IF OBJECT_ID('dbo.Software', 'U') IS NOT NULL DROP TABLE dbo.Software;
CREATE TABLE dbo.Software (
    id INT IDENTITY(1,1) PRIMARY KEY,
    activo_id INT NOT NULL FOREIGN KEY REFERENCES dbo.Activo(id),
    licencia VARCHAR(100) NULL,
    fecha_expiracion DATE NULL
);

-- ---------- TICKETS (mesa de ayuda) ----------
IF OBJECT_ID('dbo.Ticket', 'U') IS NOT NULL DROP TABLE dbo.Ticket;
CREATE TABLE dbo.Ticket (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario_id INT NOT NULL FOREIGN KEY REFERENCES dbo.Usuario(id),
    titulo VARCHAR(150) NOT NULL,
    descripcion VARCHAR(MAX) NULL,
    categoria VARCHAR(40) NOT NULL DEFAULT 'Soporte'
        CHECK (categoria IN ('Incidencia','Solicitud','Soporte')),
    prioridad VARCHAR(20) NOT NULL DEFAULT 'Media'
        CHECK (prioridad IN ('Baja','Media','Alta','Critica')),
    estado VARCHAR(30) NOT NULL DEFAULT 'Abierto'
        CHECK (estado IN ('Abierto','En Progreso','Resuelto','Cerrado')),
    asignado_a INT NULL FOREIGN KEY REFERENCES dbo.Usuario(id),
    creado_en DATETIME NOT NULL DEFAULT GETDATE(),
    actualizado_en DATETIME NOT NULL DEFAULT GETDATE()
);

-- ---------- AUDITORIA (protección) ----------
IF OBJECT_ID('dbo.LogAuditoria', 'U') IS NOT NULL DROP TABLE dbo.LogAuditoria;
CREATE TABLE dbo.LogAuditoria (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario_id INT NULL FOREIGN KEY REFERENCES dbo.Usuario(id),
    accion VARCHAR(100) NOT NULL,
    detalle VARCHAR(255) NULL,
    ip_origen VARCHAR(45) NULL,
    fecha DATETIME NOT NULL DEFAULT GETDATE()
);

-- =========================================================
-- GRUPO 3 - Centro de Seguridad
-- NOTA: los nombres de tabla aquí van en snake_case porque
-- así los define app/models.py (__tablename__). SQL Server
-- es case-insensitive por defecto, pero "ip_bloqueada" y
-- "IPBloqueada" NO son el mismo nombre de tabla (difieren en
-- guiones bajos), así que deben coincidir exactamente para
-- que SQLAlchemy no cree una tabla duplicada al arrancar.
-- =========================================================

-- ---------- REGLAS DE ALERTA ----------
IF OBJECT_ID('dbo.regla_alerta', 'U') IS NOT NULL DROP TABLE dbo.regla_alerta;
CREATE TABLE dbo.regla_alerta (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255) NULL,
    tipo_evento VARCHAR(50) NOT NULL,
    patron_deteccion VARCHAR(255) NULL,
    umbral INT NOT NULL DEFAULT 5,
    ventana_minutos INT NOT NULL DEFAULT 10,
    nivel VARCHAR(20) NOT NULL DEFAULT 'Alto',
    respuesta_automatica VARCHAR(100) NULL,
    activa BIT NOT NULL DEFAULT 1,
    creado_en DATETIME NOT NULL DEFAULT GETDATE()
);

-- ---------- ALERTAS DE SEGURIDAD ----------
IF OBJECT_ID('dbo.alerta_seguridad', 'U') IS NOT NULL DROP TABLE dbo.alerta_seguridad;
CREATE TABLE dbo.alerta_seguridad (
    id INT IDENTITY(1,1) PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    nivel VARCHAR(20) NOT NULL,
    mensaje VARCHAR(500) NOT NULL,
    ip_origen VARCHAR(45) NULL,
    usuario_id INT NULL FOREIGN KEY REFERENCES dbo.Usuario(id),
    regla_id INT NULL FOREIGN KEY REFERENCES dbo.regla_alerta(id),
    leida BIT NOT NULL DEFAULT 0,
    respondida_automaticamente BIT NOT NULL DEFAULT 0,
    respuesta_ejecutada VARCHAR(100) NULL,
    creado_en DATETIME NOT NULL DEFAULT GETDATE()
);

-- ---------- INCIDENTES DE SEGURIDAD ----------
IF OBJECT_ID('dbo.incidente_seguridad', 'U') IS NOT NULL DROP TABLE dbo.incidente_seguridad;
CREATE TABLE dbo.incidente_seguridad (
    id INT IDENTITY(1,1) PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    nivel VARCHAR(20) NOT NULL,
    descripcion VARCHAR(MAX) NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'Abierto',
    ip_origen VARCHAR(45) NULL,
    usuario_id INT NULL FOREIGN KEY REFERENCES dbo.Usuario(id),
    alerta_id INT NULL FOREIGN KEY REFERENCES dbo.alerta_seguridad(id),
    resuelto_por INT NULL FOREIGN KEY REFERENCES dbo.Usuario(id),
    resuelto_en DATETIME NULL,
    creado_en DATETIME NOT NULL DEFAULT GETDATE()
);

-- ---------- IPs BLOQUEADAS ----------
IF OBJECT_ID('dbo.ip_bloqueada', 'U') IS NOT NULL DROP TABLE dbo.ip_bloqueada;
CREATE TABLE dbo.ip_bloqueada (
    id INT IDENTITY(1,1) PRIMARY KEY,
    direccion_ip VARCHAR(45) NOT NULL UNIQUE,
    motivo VARCHAR(255) NULL,
    bloqueado_por INT NULL FOREIGN KEY REFERENCES dbo.Usuario(id),
    activo BIT NOT NULL DEFAULT 1,
    creado_en DATETIME NOT NULL DEFAULT GETDATE()
);

-- Índices útiles para el Grupo 3
CREATE INDEX IX_alerta_tipo ON dbo.alerta_seguridad(tipo);
CREATE INDEX IX_incidente_estado ON dbo.incidente_seguridad(estado);
CREATE INDEX IX_ip_bloqueada_direccion ON dbo.ip_bloqueada(direccion_ip);

-- Índices útiles para rendimiento y búsquedas frecuentes
CREATE INDEX IX_Ticket_estado ON dbo.Ticket(estado);
CREATE INDEX IX_Activo_estado ON dbo.Activo(estado);
CREATE INDEX IX_LogAuditoria_fecha ON dbo.LogAuditoria(fecha);
GO
