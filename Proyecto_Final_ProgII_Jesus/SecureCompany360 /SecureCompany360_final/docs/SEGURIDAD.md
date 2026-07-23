# Protección — Seguridad del Sistema (Grupo 1 y Grupo 2)

Este documento responde directamente la pregunta del enunciado: *"¿Qué aspectos
debemos proteger? ¿Cómo?"*

## 1. ¿Qué protegemos?

| Activo | Riesgo si se compromete |
|---|---|
| Credenciales de usuarios | Acceso no autorizado a todo el sistema |
| Datos de empleados (RRHH) | Fuga de información personal (cédulas, cargos) |
| Inventario de activos | Manipulación de asignaciones, robo lógico de equipos |
| Tickets de soporte | Exposición de incidentes internos, manipulación de estados |
| Endpoints de administración | Escalación de privilegios, visión total del sistema |
| Disponibilidad de la API | Que un atacante la tumbe con fuerza bruta o flooding |

## 2. ¿Cómo protegemos cada cosa?

### Credenciales
- Hash **bcrypt** (nunca se guarda ni se transmite en texto plano más de lo necesario).
- Contraseña mínima 8 caracteres, con al menos una mayúscula y un número (validado en
  `schemas.py` antes de tocar la base de datos).

### Autenticación y sesión
- **JWT firmado** con `SECRET_KEY` (nunca hardcodeado, vive en `.env`).
- Access token de vida corta (30 min) + refresh token (7 días) para no forzar re-login
  constante pero limitar la ventana de un token robado.

### Autorización (quién puede hacer qué)
- **RBAC** con 5 roles: Administrador, RRHH, Soporte, Analista, Usuario.
- Cada endpoint declara explícitamente qué roles puede usarlo
  (`Depends(requiere_rol(...))`), así nadie "olvida" proteger una ruta nueva.
- Un usuario común solo ve/edita sus propios tickets y solo puede solicitar activos
  para sí mismo — nunca para otro empleado.

### Fuerza bruta
- Contador `intentos_fallidos` por usuario en base de datos.
- Tras 5 intentos fallidos → bloqueo de 10 minutos (`bloqueado_hasta`).
- **Rate limiting** adicional a nivel de IP en `/auth/login` (5 intentos/minuto) —
  esto detiene ataques distribuidos contra múltiples usuarios desde una misma IP,
  que el contador por usuario no cubre.

### Inyección SQL
- Todo acceso a datos pasa por **SQLAlchemy ORM** con queries parametrizadas.
- Nunca se concatenan strings para construir SQL.
- Se probó explícitamente con payloads tipo `' OR 1=1--` en el campo username → el
  sistema los trata como texto literal, no como código SQL, y responde con el mismo
  error genérico que una contraseña incorrecta normal.

### Fuga de información / reconocimiento
- Los mensajes de error de login son **genéricos** ("Usuario o contraseña
  incorrectos") sin importar si el usuario existe o no — así un atacante no puede
  enumerar usuarios válidos por ensayo y error.
- Excepciones no controladas nunca exponen trazas ni detalles internos al cliente;
  se registran solo en el log del servidor.
- En producción, Swagger/OpenAPI (`/docs`) se puede desactivar (`docs_url=None`) para
  no regalar el mapa completo de la API a quien la esté atacando.

### Auditoría
- Tabla `LogAuditoria`: registra login exitoso, login fallido, bloqueos, creación de
  empleados/usuarios/activos/tickets, aprobaciones y actualizaciones — con usuario,
  IP y timestamp.
- El Administrador puede consultar este log desde el Dashboard (`GET /admin/auditoria`),
  lo que permite ver en vivo, durante la prueba de ataques, qué está intentando hacer
  el equipo atacante.

### Transporte y cabeceras HTTP
- Recomendación: desplegar detrás de HTTPS/TLS (Nginx/Caddy reverse proxy) — Uvicorn
  solo no maneja TLS de forma robusta en producción.
- Cabeceras de seguridad en cada respuesta: `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: DENY`, `Strict-Transport-Security`, `Referrer-Policy: no-referrer`.
- CORS restringido a una whitelist explícita de orígenes (nunca `*`).

### Datos sensibles
- `.env` está fuera del control de versiones (`.gitignore`), así el `SECRET_KEY` y
  las credenciales de la base de datos nunca llegan al repo público de GitHub.

## 3. Qué NO cubre esta capa (para ser honestos en la presentación)

- No implementa 2FA/MFA (se puede mencionar como mejora futura).
- No cifra los datos en reposo dentro de SQL Server (se podría añadir Always Encrypted
  o TDE como extensión).
- La protección contra DDoS a gran escala requeriría infraestructura adicional
  (WAF, Cloudflare, etc.) fuera del alcance de un proyecto académico.
