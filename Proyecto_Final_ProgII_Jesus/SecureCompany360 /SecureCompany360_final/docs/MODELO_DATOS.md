# Modelo de Datos — Secure Company 360 (Grupo 1, Grupo 2 y Grupo 3)

## Entidades

### Rol
| Campo | Tipo | Notas |
|---|---|---|
| id | INT PK | |
| nombre | VARCHAR(30) | Administrador, Analista, RRHH, Soporte, Usuario |

### Empleado (Grupo 1 — RRHH)
| Campo | Tipo | Notas |
|---|---|---|
| id | INT PK | |
| nombre_completo | VARCHAR(120) | |
| cedula | VARCHAR(20) UNIQUE | |
| cargo | VARCHAR(80) | |
| departamento | VARCHAR(80) | |
| fecha_ingreso | DATE | |
| activo | BIT | soft delete |

### Usuario (Grupo 1 — RRHH / Autenticación)
| Campo | Tipo | Notas |
|---|---|---|
| id | INT PK | |
| empleado_id | INT FK → Empleado | |
| username | VARCHAR(50) UNIQUE | |
| password_hash | VARCHAR(255) | bcrypt |
| rol_id | INT FK → Rol | |
| intentos_fallidos | INT | default 0 |
| bloqueado_hasta | DATETIME NULL | |
| activo | BIT | |
| creado_en | DATETIME | |

### Activo (Grupo 1 — Inventario)
| Campo | Tipo | Notas |
|---|---|---|
| id | INT PK | |
| tipo | VARCHAR(30) | Equipo, Software, Otro |
| nombre | VARCHAR(120) | |
| numero_serie | VARCHAR(60) UNIQUE NULL | |
| estado | VARCHAR(30) | Disponible, Asignado, Solicitado, Baja |
| asignado_a | INT FK → Empleado NULL | |
| fecha_registro | DATETIME | |

### Software (Grupo 1 — Inventario, detalle de licencias)
| Campo | Tipo | Notas |
|---|---|---|
| id | INT PK | |
| activo_id | INT FK → Activo | |
| licencia | VARCHAR(100) | |
| fecha_expiracion | DATE NULL | |

### Ticket (Grupo 2 — Mesa de Ayuda)
| Campo | Tipo | Notas |
|---|---|---|
| id | INT PK | |
| usuario_id | INT FK → Usuario | quien reporta |
| titulo | VARCHAR(150) | |
| descripcion | TEXT | |
| categoria | VARCHAR(40) | Incidencia, Solicitud, Soporte |
| prioridad | VARCHAR(20) | Baja, Media, Alta, Crítica |
| estado | VARCHAR(30) | Abierto, En Progreso, Resuelto, Cerrado |
| asignado_a | INT FK → Usuario NULL | agente de soporte |
| creado_en | DATETIME | |
| actualizado_en | DATETIME | |

### LogAuditoria (Protección — todos los grupos)
| Campo | Tipo | Notas |
|---|---|---|
| id | INT PK | |
| usuario_id | INT FK → Usuario NULL | null si login fallido de user inexistente |
| accion | VARCHAR(100) | LOGIN_OK, LOGIN_FAIL, CREATE_TICKET, ... |
| detalle | VARCHAR(255) | |
| ip_origen | VARCHAR(45) | |
| fecha | DATETIME | |

### ReglaAlerta (Grupo 3 — Centro de Seguridad)
Define qué patrón dispara una alerta y qué respuesta automática ejecutar.

| Campo | Tipo | Notas |
|---|---|---|
| id | INT PK | |
| nombre | VARCHAR(100) UNIQUE | ej. "Fuerza Bruta por IP" |
| descripcion | VARCHAR(255) | |
| tipo_evento | VARCHAR(50) | qué tipo de evento evalúa |
| patron_deteccion | VARCHAR(255) | patrón/regex usado por el analizador |
| umbral | INT | default 5 (ej. intentos fallidos) |
| ventana_minutos | INT | default 10 (ventana de tiempo evaluada) |
| nivel | VARCHAR(20) | Bajo, Medio, Alto, Crítico |
| respuesta_automatica | VARCHAR(100) NULL | bloquear_ip, deshabilitar_usuario, etc. |
| activa | BIT | |
| creado_en | DATETIME | |

### AlertaSeguridad (Grupo 3 — Centro de Seguridad)
Cada vez que el Motor de Alertas detecta un patrón, genera una fila aquí.

| Campo | Tipo | Notas |
|---|---|---|
| id | INT PK | |
| tipo | VARCHAR(50) | FUERZA_BRUTA_IP, INYECCION_SQL, ACCESO_EXTRANJERO, ... |
| nivel | VARCHAR(20) | Bajo, Medio, Alto, Crítico |
| mensaje | VARCHAR(500) | |
| ip_origen | VARCHAR(45) NULL | |
| usuario_id | INT FK → Usuario NULL | |
| regla_id | INT FK → ReglaAlerta NULL | qué regla la generó |
| leida | BIT | |
| respondida_automaticamente | BIT | si la Respuesta Automática se disparó sola |
| respuesta_ejecutada | VARCHAR(100) NULL | qué acción se ejecutó (bloquear_ip, etc.) |
| creado_en | DATETIME | |

### IncidenteSeguridad (Grupo 3 — Centro de Seguridad)
Las alertas de nivel Crítico escalan a un incidente formal con seguimiento.

| Campo | Tipo | Notas |
|---|---|---|
| id | INT PK | |
| tipo | VARCHAR(50) | |
| nivel | VARCHAR(20) | |
| descripcion | TEXT | |
| estado | VARCHAR(30) | Abierto, En_Investigacion, Resuelto, Cerrado |
| ip_origen | VARCHAR(45) NULL | |
| usuario_id | INT FK → Usuario NULL | |
| alerta_id | INT FK → AlertaSeguridad NULL | alerta que lo originó |
| resuelto_por | INT FK → Usuario NULL | |
| resuelto_en | DATETIME NULL | |
| creado_en | DATETIME | |

### IPBloqueada (Grupo 3 — Respuesta Automática)
| Campo | Tipo | Notas |
|---|---|---|
| id | INT PK | |
| direccion_ip | VARCHAR(45) UNIQUE | |
| motivo | VARCHAR(255) | manual o "Bloqueo automático por alerta de seguridad" |
| bloqueado_por | INT FK → Usuario NULL | null si lo bloqueó el sistema automáticamente |
| activo | BIT | si sigue vigente el bloqueo |
| creado_en | DATETIME | |

## Relaciones clave
- `Empleado 1—1 Usuario` (todo empleado con acceso al sistema tiene un usuario).
- `Usuario N—1 Rol`.
- `Activo N—1 Empleado` (asignación).
- `Ticket N—1 Usuario` (reportante) y `Ticket N—1 Usuario` (agente asignado).
- `LogAuditoria N—1 Usuario`.
- `AlertaSeguridad N—1 ReglaAlerta` (qué regla disparó la alerta).
- `AlertaSeguridad N—1 Usuario` (a quién/desde dónde se detectó la actividad).
- `IncidenteSeguridad N—1 AlertaSeguridad` (de qué alerta escaló el incidente).
- `IPBloqueada N—1 Usuario` (quién la bloqueó, si fue manual).

## Diagrama simplificado
```
Rol ──< Usuario >── Empleado ──< Activo
                │                  │
                │                  └──< Software
                ├──< Ticket (reporta)
                ├──< Ticket (asignado_a)
                ├──< LogAuditoria
                ├──< AlertaSeguridad ──< IncidenteSeguridad
                │         │
                │         └── ReglaAlerta (qué la disparó)
                └──< IPBloqueada (si él la bloqueó manualmente)
```

Ver `database/schema.sql` para el DDL completo en T-SQL (SQL Server), incluyendo las 11
tablas: las 7 de Grupo 1/2 más las 4 del Grupo 3 (`regla_alerta`, `alerta_seguridad`,
`incidente_seguridad`, `ip_bloqueada`).

