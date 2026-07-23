import requests

BASE_URL = "http://127.0.0.1:8000"


class APIError(Exception):
    def __init__(self, detail: str, status_code: int = 0):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class APIClient:
    def __init__(self):
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.rol: str | None = None
        self.username: str | None = None

    # ---------- Sesión ----------

    def login(self, username: str, password: str) -> None:
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=10,
        )
        if resp.status_code != 200:
            raise APIError(self._detalle(resp), resp.status_code)
        data = resp.json()
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.rol = data["rol"]
        self.username = username

    def logout(self) -> None:
        self.access_token = None
        self.refresh_token = None
        self.rol = None
        self.username = None

    def esta_autenticado(self) -> bool:
        return self.access_token is not None

    # ---------- Helpers internos ----------

    def _headers(self) -> dict:
        if not self.access_token:
            raise APIError("No hay sesión activa")
        return {"Authorization": f"Bearer {self.access_token}"}

    @staticmethod
    def _detalle(resp: requests.Response) -> str:
        try:
            return resp.json().get("detail", f"Error HTTP {resp.status_code}")
        except ValueError:
            return f"Error HTTP {resp.status_code}"

    def _request(self, metodo: str, ruta: str, **kwargs) -> dict | list:
        resp = requests.request(
            metodo, f"{BASE_URL}{ruta}", headers=self._headers(), timeout=10, **kwargs
        )
        if resp.status_code >= 400:
            raise APIError(self._detalle(resp), resp.status_code)
        if resp.status_code == 204 or not resp.content:
            return {}
        return resp.json()

    # ---------- RRHH (Grupo 1) ----------

    def crear_empleado(self, datos: dict) -> dict:
        return self._request("POST", "/rrhh/empleados", json=datos)

    def listar_empleados(self) -> list:
        return self._request("GET", "/rrhh/empleados")

    def crear_usuario(self, datos: dict) -> dict:
        return self._request("POST", "/rrhh/usuarios", json=datos)

    def listar_usuarios(self) -> list:
        return self._request("GET", "/rrhh/usuarios")

    # ---------- Inventario (Grupo 1) ----------

    def registrar_activo(self, datos: dict) -> dict:
        return self._request("POST", "/inventario/activos", json=datos)

    def listar_activos(self) -> list:
        return self._request("GET", "/inventario/activos")

    def solicitar_activo(self, activo_id: int, empleado_id: int) -> dict:
        return self._request(
            "POST", "/inventario/activos/solicitar",
            json={"activo_id": activo_id, "empleado_id": empleado_id},
        )

    def aprobar_activo(self, activo_id: int) -> dict:
        return self._request("PATCH", f"/inventario/activos/{activo_id}/aprobar")

    # ---------- Mesa de Ayuda (Grupo 2) ----------

    def crear_ticket(self, datos: dict) -> dict:
        return self._request("POST", "/mesa-ayuda/tickets", json=datos)

    def listar_tickets(self) -> list:
        return self._request("GET", "/mesa-ayuda/tickets")

    def actualizar_ticket(self, ticket_id: int, datos: dict) -> dict:
        return self._request("PATCH", f"/mesa-ayuda/tickets/{ticket_id}", json=datos)

    # ---------- Admin / Dashboard (Grupo 2) ----------

    def dashboard(self) -> dict:
        return self._request("GET", "/admin/dashboard")

    def auditoria(self) -> list:
        return self._request("GET", "/admin/auditoria")

    def analisis_logs(self) -> dict:
        return self._request("GET", "/admin/analisis-logs")

    # ========== SEGURIDAD / ALERTAS (Nuevo) ==========

    def generar_logs(self, escenario: str = "completo") -> dict:
        return self._request("POST", "/admin/logs/generar", json={"escenario": escenario})

    def listar_alertas(self, no_leidas: bool = False) -> list:
        params = "?no_leidas=true" if no_leidas else ""
        return self._request("GET", f"/admin/alertas{params}")

    def evaluar_alertas(self) -> dict:
        return self._request("POST", "/admin/alertas/evaluar")

    def marcar_alerta_leida(self, alerta_id: int) -> dict:
        return self._request("PATCH", f"/admin/alertas/{alerta_id}/leer")

    def listar_incidentes(self) -> list:
        return self._request("GET", "/admin/incidentes")

    def actualizar_incidente(self, incidente_id: int, estado: str) -> dict:
        return self._request("PATCH", f"/admin/incidentes/{incidente_id}?estado={estado}")

    def listar_ips_bloqueadas(self) -> list:
        return self._request("GET", "/admin/ips-bloqueadas")

    def bloquear_ip(self, direccion_ip: str, motivo: str = "") -> dict:
        return self._request("POST", "/admin/respuestas/bloquear-ip",
                             json={"direccion_ip": direccion_ip, "motivo": motivo})

    def desbloquear_ip(self, direccion_ip: str) -> dict:
        return self._request("POST", "/admin/respuestas/desbloquear-ip",
                             json={"direccion_ip": direccion_ip})

    def eliminar_ip_bloqueada(self, ip_id: int) -> dict:
        return self._request("DELETE", f"/admin/ips-bloqueadas/{ip_id}")

    def deshabilitar_usuario(self, usuario_id: int, motivo: str = "") -> dict:
        return self._request("POST", "/admin/respuestas/deshabilitar-usuario",
                             json={"usuario_id": usuario_id, "motivo": motivo})

    def habilitar_usuario(self, usuario_id: int) -> dict:
        return self._request("POST", "/admin/respuestas/habilitar-usuario",
                             json={"usuario_id": usuario_id})

    def enviar_correo(self, destinatario: str, asunto: str, cuerpo: str) -> dict:
        return self._request("POST", "/admin/respuestas/enviar-correo",
                             json={"destinatario": destinatario, "asunto": asunto, "cuerpo": cuerpo})

    def generar_reporte(self, tipo: str = "completo") -> dict:
        return self._request("POST", f"/admin/respuestas/generar-reporte?tipo={tipo}")

    def dashboard_seguridad(self) -> dict:
        return self._request("GET", "/admin/seguridad/dashboard")


api = APIClient()
