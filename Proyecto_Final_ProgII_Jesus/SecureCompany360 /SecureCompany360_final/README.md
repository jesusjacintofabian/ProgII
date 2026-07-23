# Secure Company 360 — Grupo 1 & Grupo 2

**Programación II — U.T.P. F.I.S.C. @ 1S3222 I-2026 — Prof. Regis Rivera**

Plataforma en Python que simula el ecosistema seguro de una empresa. Este repositorio
cubre el alcance del **Grupo 1** (Sistema de Recursos Humanos + Inventario + Protección)
y **Grupo 2** (Mesa de Ayuda + Administrador General + Protección).

📄 Ver `docs/ARQUITECTURA.md` y `docs/MODELO_DATOS.md` para el detalle técnico completo.

## Stack

- **Backend:** FastAPI + SQLAlchemy + SQL Server (con fallback a SQLite para desarrollo)
- **Seguridad:** bcrypt, JWT, RBAC, rate limiting, bloqueo por fuerza bruta, auditoría
- **Cliente:** Tkinter (escritorio)

## Estructura

```
SecureCompany360/
├── backend/            → API FastAPI (Grupo 1 y Grupo 2)
│   ├── app/
│   ├── seed.py          → crea roles + usuario admin inicial
│   └── requirements.txt (en la raíz)
├── database/
│   └── schema.sql       → DDL completo para SQL Server
├── gui/                 → Cliente Tkinter
│   ├── main_app.py
│   ├── api_client.py
│   └── screens/
├── docs/                → Arquitectura, modelo de datos
└── requirements.txt
```

## Instalación

### 1. Clonar e instalar dependencias

```bash
git clone <URL_DE_TU_REPO>
cd SecureCompany360
pip install -r requirements.txt
```

> **pyodbc (SQL Server):** en Windows necesitas tener instalado el
> [ODBC Driver 17/18 for SQL Server](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server).
> En Linux/Mac, instala `unixodbc` primero.

### 2. Configurar la base de datos

**Opción A — SQL Server (recomendado, como pide el proyecto):**

1. Ejecuta `database/schema.sql` en tu instancia de SQL Server (crea la BD y las tablas).
2. Copia `.env.example` a `.env` y ajusta `DATABASE_URL` con tus credenciales:
   ```
   DATABASE_URL=mssql+pyodbc://usuario:password@localhost/SecureCompany360?driver=ODBC+Driver+17+for+SQL+Server
   ```

**Opción B — SQLite (para probar rápido sin instalar SQL Server):**

No hagas nada — `config.py` ya trae un fallback a SQLite si no defines `DATABASE_URL`.

### 3. Poblar roles y usuario administrador inicial

```bash
cd backend
python seed.py
```

Esto crea el usuario `admin` / `Admin2026!` (rol Administrador). **Cámbialo antes de la demo.**

### 4. Levantar el backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

La API queda en `http://127.0.0.1:8000`. Documentación interactiva (solo en desarrollo,
desactívala en producción): `http://127.0.0.1:8000/docs`.

### 5. Levantar la interfaz Tkinter

En otra terminal (con el backend corriendo):

```bash
cd gui
python main_app.py
```

Inicia sesión con `admin` / `Admin2026!` para ver todas las pestañas
(RRHH, Inventario, Mesa de Ayuda, Admin/Dashboard).

## Flujo de demo sugerido (según el enunciado del profesor)

1. Login con el usuario admin.
2. Pestaña **RRHH**: registrar un empleado nuevo → crear su usuario con rol "Usuario".
3. Cerrar sesión, entrar con ese nuevo usuario.
4. Pestaña **Inventario**: solicitar un activo disponible.
5. Volver a entrar como admin → aprobar el activo solicitado.
6. Pestaña **Mesa de Ayuda**: crear un ticket de soporte.
7. Pestaña **Admin/Dashboard**: ver las métricas actualizadas en tiempo real y el log
   de auditoría (útil para mostrar durante la prueba de ataques: se ve cada intento
   fallido de login).

## Seguridad implementada (resumen — ver `docs/ARQUITECTURA.md` para el detalle)

- Contraseñas con **bcrypt** (nunca texto plano).
- Autenticación con **JWT** (access token 30 min + refresh token 7 días).
- **RBAC**: cada endpoint exige un rol específico.
- **Bloqueo de cuenta** tras 5 intentos fallidos (10 min).
- **Rate limiting** en `/auth/login` (5 intentos/minuto por IP).
- **Auditoría completa**: toda acción sensible queda en `LogAuditoria` con IP y timestamp.
- **Validación estricta** de entradas con Pydantic (anti-inyección, anti-payloads malformados).
- ORM con queries parametrizadas → inmune a inyección SQL clásica.
- Cabeceras de seguridad HTTP y CORS restringido por whitelist.
- Errores genéricos al cliente; el detalle técnico solo queda en logs internos.

