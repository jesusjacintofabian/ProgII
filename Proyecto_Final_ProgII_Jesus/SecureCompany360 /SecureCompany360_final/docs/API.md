# Documentación de la API de Secure Company 360

Este documento detalla la especificación de los endpoints del backend, con énfasis en la nueva sección de **Analizador de Logs y Auditoría** de Administración.

## Autenticación e Identificación

Toda petición a endpoints protegidos (a excepción de `/auth/login` y `/auth/refresh`) debe adjuntar la cabecera HTTP estándar de autorización con el token JWT:
```http
Authorization: Bearer <su_token_jwt>
```

---

## 🔐 Endpoints del Administrador General (`/admin`)

### 1. Obtener Análisis de Logs y Ciberseguridad

Realiza una inspección inteligente consolidando los archivos de log en disco (`secure_company_360.log`) y los registros de auditoría almacenados en la base de datos (`LogAuditoria`).

* **Ruta:** `/admin/analisis-logs`
* **Método:** `GET`
* **Acceso:** Restringido. Exige el rol `"Administrador"`.
* **Respuesta Exitosa (200 OK):**
  ```json
  {
    "nivel_riesgo": "Alto",
    "resumen": {
      "total_log_archivo": 1420,
      "total_log_auditoria": 542,
      "total_errores": 12,
      "total_bloqueos": 3,
      "total_fallidos": 47
    },
    "alertas": [
      {
        "nivel": "Alto",
        "tipo": "FUERZA_BRUTA_IP",
        "mensaje": "IP 192.168.1.15 registra 8 intentos de inicio de sesión fallidos."
      }
    ],
    "ips_fallidas": [
      {
        "ip": "192.168.1.15",
        "cantidad": 8
      }
    ],
    "usuarios_activos": [
      {
        "usuario": "admin",
        "acciones": 340
      }
    ],
    "errores_recientes": [
      {
        "timestamp": "2026-07-20 20:54:10,123",
        "mensaje": "Error no controlado en /auth/login: connection timeout"
      }
    ],
    "recomendaciones": [
      "Considerar bloquear la dirección IP 192.168.1.15 mediante firewall o regla de red.",
      "Monitorear el estado de las cuentas bloqueadas y confirmar con los empleados si fueron ellos."
    ]
  }
  ```

---

### 2. Consultar Log de Auditoría Histórico

Lista los últimos eventos de auditoría que se han guardado en la base de datos.

* **Ruta:** `/admin/auditoria`
* **Método:** `GET`
* **Parámetros de consulta (Query params):**
  - `limite` (int, default: 100): Cantidad máxima de registros a retornar (máx. 500).
* **Acceso:** Restringido. Exige el rol `"Administrador"`.
* **Respuesta Exitosa (200 OK):**
  ```json
  [
    {
      "id": 125,
      "usuario_id": 2,
      "accion": "LOGIN_OK",
      "detalle": "Login exitoso",
      "ip_origen": "127.0.0.1",
      "fecha": "2026-07-20T20:54:10.123000"
    }
  ]
  ```

---

### 3. Métricas Generales del Dashboard

Devuelve estadísticas en tiempo real sobre el estado del sistema.

* **Ruta:** `/admin/dashboard`
* **Método:** `GET`
* **Acceso:** Restringido. Exige el rol `"Administrador"`.
* **Respuesta Exitosa (200 OK):**
  ```json
  {
    "total_usuarios_activos": 12,
    "total_empleados": 24,
    "tickets_abiertos": 3,
    "tickets_criticos": 1,
    "activos_disponibles": 8,
    "activos_asignados": 14,
    "intentos_login_fallidos_24h": 5
  }
  ```
