# Arquitectura de Alto Nivel — Secure Company 360
## Grupo 1 (RRHH + Inventario + Protección), Grupo 2 (Mesa de Ayuda + Admin General + Protección) & Grupo 3 (Centro de Seguridad)

## 1. Visión general

Secure Company 360 se construye como una **API REST central (FastAPI)** respaldada por
**SQL Server**, y consumida por un **cliente de escritorio en Tkinter**. Los 3 grupos
comparten la misma API, la misma base de datos y el mismo sistema de autenticación/roles —
no son 3 aplicaciones separadas, sino 3 conjuntos de módulos integrados en una sola
plataforma.

```
                    ┌─────────────────────────┐
                    │   Cliente Tkinter (GUI)  │
                    │  Login / RRHH / Inv /    │
                    │  Mesa de Ayuda / Admin / │
                    │  Centro de Seguridad     │
                    └────────────┬─────────────┘
                                 │ HTTPS + JWT (Bearer Token)
                                 ▼
                    ┌─────────────────────────┐
                    │     API FastAPI          │
                    │  (uvicorn, asgi)         │
                    │                          │
                    │  Middlewares:            │
                    │   - CORS restrictivo     │
                    │   - Rate limiting        │
                    │   - Security headers     │
                    │   - Logging/Auditoría    │
                    │   - Bloqueo real de IPs  │
                    │     (Grupo 3)            │
                    │                          │
                    │  Routers:                │
                    │   /auth   (login/roles)  │
                    │   /rrhh   (Grupo 1)      │
                    │   /inventario (Grupo 1)  │
                    │   /mesa-ayuda (Grupo 2)  │
                    │   /admin  (Grupo 2 y 3)  │
                    └────────────┬─────────────┘
                                 │ SQLAlchemy ORM (queries parametrizadas)
                                 ▼
                    ┌─────────────────────────┐
                    │   SQL Server             │
                    │  (Base de datos común)   │
                    └─────────────────────────┘
```

## 2. Por qué FastAPI (justificación de seguridad)

El profesor pidió el framework "más difícil de vulnerar" porque van a recibir pruebas de
ataque reales. Elegimos FastAPI sobre Flask/Django porque:

- **Validación de tipos obligatoria (Pydantic):** todo request se valida contra un
  esquema antes de tocar la lógica de negocio. Esto bloquea automáticamente payloads
  malformados, tipos incorrectos, campos extra, overflow de strings, etc.
- **Async nativo:** mejor resistencia a ataques de denegación de servicio leve (muchas
  conexiones concurrentes) comparado con Flask sync puro.
- **OpenAPI/Swagger se puede desactivar en producción** (`docs_url=None`), reduciendo
  superficie de reconocimiento para el equipo atacante.
- **Dependency Injection** para forzar auth/roles en cada endpoint de forma consistente
  (no se nos puede "olvidar" proteger una ruta).
- SQLAlchemy ORM (no SQL crudo) → inmune a inyección SQL clásica por diseño.

## 3. Capas de "Protección" implementadas (Grupo 1 y Grupo 2)

| Capa | Mecanismo | Dónde |
|---|---|---|
| Contraseñas | Hash bcrypt (nunca texto plano) | `security/auth.py` |
| Autenticación | JWT firmado, expiración corta (30 min) + refresh token | `security/auth.py`, `routers/auth.py` |
| Autorización | RBAC — roles: Administrador, Analista, Usuario, RRHH, Soporte | `security/permissions.py` |
| Fuerza bruta | Bloqueo de cuenta tras 5 intentos fallidos (10 min) | `security/auth.py` |
| Fuerza bruta / DoS | Rate limiting por IP (slowapi) en `/auth/login` y endpoints sensibles | `main.py` |
| Inyección SQL | ORM con queries parametrizadas, jamás f-strings en SQL | `models.py`, routers |
| Inyección / payloads inválidos | Validación estricta Pydantic (tipos, longitud, regex) | `schemas.py` |
| Fuga de información | Errores genéricos al cliente, detalle solo en logs internos | `main.py` (exception handlers) |
| Auditoría | Tabla `LogAuditoria`: quién hizo qué, cuándo, desde qué IP | `models.py`, dependencia `log_action` |
| Transporte | Recomendación HTTPS/TLS en despliegue (Uvicorn tras Nginx/Caddy) | `docs/SEGURIDAD.md` |
| CORS | Whitelist explícita de orígenes permitidos | `main.py` |
| Cabeceras HTTP | `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security` | `main.py` middleware |
| Secretos | `.env` fuera del repo (`.gitignore`), nunca hardcodeados | `config.py` |
| Permisos por dato | Un "Usuario" normal solo ve su propio ticket/activo; Admin ve todo | Lógica en cada router |

## 4. Grupo 3 — Centro de Seguridad (Monitoreo, Auditoría y Análisis)

El Grupo 3 no es un sistema aparte: se conecta a la **misma base de datos** y **al mismo
LogAuditoria** que generan Grupo 1 y Grupo 2, y añade una capa de detección y respuesta
sobre esa actividad ya existente. Es decir, cada login, cada ticket, cada activo que se
mueve en Grupo 1/2 es materia prima para el análisis del Grupo 3 — por eso un intento real
de inyección SQL contra el login (Grupo 1) puede terminar bloqueado por el Centro de
Seguridad (Grupo 3) sin que haga falta duplicar nada.

```
 Grupo 1 / Grupo 2                    Grupo 3
┌───────────────────┐        ┌──────────────────────────┐
│ Cada acción del    │        │ Generador de Logs        │
│ usuario genera un  │──────▶ │ (simula tráfico/ataques  │
│ registro en        │        │  para pruebas)           │
│ LogAuditoria       │        └────────────┬─────────────┘
└───────────────────┘                      ▼
                              ┌──────────────────────────┐
                              │ Analizador de Logs        │
                              │ (patrones, errores,       │
                              │  eventos) → log_analyzer  │
                              └────────────┬─────────────┘
                                           ▼
                              ┌──────────────────────────┐
                              │ Motor de Alertas          │
                              │ (ReglaAlerta define       │
                              │  umbral + patrón)         │
                              │ → genera AlertaSeguridad  │
                              └────────────┬─────────────┘
                                           ▼
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
        ┌──────────────────────┐                    ┌──────────────────────────┐
        │ Alertas Críticas      │                    │ Respuesta Automática      │
        │ escalan a            │                    │ (según ReglaAlerta):      │
        │ IncidenteSeguridad   │                    │  - Bloquear IP (real,     │
        └──────────────────────┘                    │    vía middleware)        │
                                                      │  - Deshabilitar usuario   │
                                                      │  - Enviar correo (simul.) │
                                                      │  - Generar reporte        │
                                                      └──────────────────────────┘
```

**Componentes y dónde viven:**

| Componente | Descripción | Archivo |
|---|---|---|
| Generador de Logs | Simula escenarios de ataque (fuerza bruta, inyección SQL, IP extranjera, horario nocturno) para poder demostrar la detección sin esperar un ataque real | `security/log_generator.py` |
| Analizador de Logs | Recorre `LogAuditoria` y el log técnico buscando patrones, errores y eventos sospechosos | `security/log_analyzer.py`, `analizador_logs.py` (CLI) |
| Motor de Alertas | Evalúa los eventos contra las `ReglaAlerta` configuradas (umbral + ventana de tiempo) y genera `AlertaSeguridad` | `security/alert_engine.py` |
| Respuesta Automática | Si la regla que disparó la alerta tiene `respuesta_automatica` configurada, se ejecuta sola en el momento (sin esperar a que un admin le dé clic) | `security/auto_response.py`, disparado desde `alert_engine.py` |
| Bloqueo real de IP | Middleware en `main.py` que rechaza con `403` cualquier request de una IP marcada en `IPBloqueada` (con excepción de loopback, para que el sistema nunca se bloquee a sí mismo) | `main.py` |
| Dashboard de Seguridad | Métricas en vivo: alertas no leídas, incidentes abiertos, IPs bloqueadas, nivel de riesgo | `routers/seguridad.py`, GUI `admin_dashboard.py` |

**Por qué la Respuesta Automática es segura de dejar corriendo sola:** el middleware de
bloqueo nunca actúa sobre `127.0.0.1`/`localhost` — esto evita que, durante pruebas o si
atacante y administrador comparten red, el propio sistema termine bloqueándose a sí mismo
y dejando a todos sin acceso, incluido quien necesitaría desbloquearlo.

## 5. Flujo de la Demo en vivo

1. **Registro/Login** → `/auth/login` devuelve JWT + rol.
2. **RRHH (Grupo 1):** Admin registra un Empleado → se crea su Usuario con rol y permisos.
3. **Inventario (Grupo 1):** Empleado solicita un Activo → queda en estado "Solicitado".
4. **Mesa de Ayuda (Grupo 2):** Empleado genera un Ticket de soporte.
5. **Admin General (Grupo 2):** Admin revisa Dashboard con métricas (usuarios activos,
   tickets abiertos, activos asignados).
6. **Centro de Seguridad (Grupo 3):** Se genera un escenario de ataque simulado (fuerza
   bruta) → se evalúan las alertas → el Motor de Alertas detecta el patrón → la Respuesta
   Automática bloquea la IP y notifica por correo, todo sin intervención manual.
7. **Prueba de ataque real:** el equipo atacante intenta login por fuerza bruta / inyección
   / escalar privilegios → Grupo 1/2 bloquea y responde con error genérico (401/403) →
   Grupo 3 detecta el mismo intento en el log de auditoría, genera una alerta/incidente, y
   puede terminar bloqueando esa IP automáticamente si supera el umbral configurado.

## 6. Repositorio (estructura sugerida para GitHub)

```
SecureCompany360/
├── backend/
│   ├── analizador_logs.py          (Grupo 3, CLI standalone)
│   ├── seed.py
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       ├── security/
│       │   ├── auth.py
│       │   ├── permissions.py
│       │   ├── rate_limit.py
│       │   ├── log_generator.py    (Grupo 3)
│       │   ├── log_analyzer.py     (Grupo 3)
│       │   ├── alert_engine.py     (Grupo 3)
│       │   └── auto_response.py    (Grupo 3)
│       └── routers/
│           ├── auth.py
│           ├── rrhh.py
│           ├── inventario.py
│           ├── mesa_ayuda.py
│           ├── admin.py
│           └── seguridad.py         (Grupo 3)
├── database/
│   └── schema.sql                   (incluye las 11 tablas: Grupo 1/2 + Grupo 3)
├── gui/
│   ├── main_app.py
│   ├── api_client.py
│   └── screens/
│       ├── login.py
│       ├── rrhh.py
│       ├── inventario.py
│       ├── mesa_ayuda.py
│       └── admin_dashboard.py       (incluye ventana de Centro de Seguridad)
├── docs/
│   ├── ARQUITECTURA.md
│   ├── MODELO_DATOS.md
│   ├── SEGURIDAD.md
│   └── API.md
├── requirements.txt
├── .env.example
└── README.md
```
