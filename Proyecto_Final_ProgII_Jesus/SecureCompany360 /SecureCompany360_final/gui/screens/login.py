import tkinter as tk
from tkinter import ttk, messagebox

from api_client import api, APIError


class LoginScreen(ttk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, padding=40)
        self.on_login_success = on_login_success

        ttk.Label(self, text="Secure Company 360", font=("Segoe UI", 20, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 4)
        )
        ttk.Label(self, text="Grupo 1 (RRHH + Inventario) / Grupo 2 (Mesa de Ayuda + Admin)",
                  font=("Segoe UI", 9)).grid(row=1, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(self, text="Usuario:").grid(row=2, column=0, sticky="e", pady=6)
        self.username_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.username_var, width=28).grid(row=2, column=1, pady=6)

        ttk.Label(self, text="Contraseña:").grid(row=3, column=0, sticky="e", pady=6)
        self.password_var = tk.StringVar()
        entry_pass = ttk.Entry(self, textvariable=self.password_var, show="*", width=28)
        entry_pass.grid(row=3, column=1, pady=6)
        entry_pass.bind("<Return>", lambda e: self._login())

        self.mensaje = ttk.Label(self, text="", foreground="red")
        self.mensaje.grid(row=4, column=0, columnspan=2, pady=(4, 4))

        ttk.Button(self, text="Iniciar sesión", command=self._login).grid(
            row=5, column=0, columnspan=2, pady=(10, 0), sticky="ew"
        )

    def _login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            self.mensaje.config(text="Completa usuario y contraseña")
            return

        try:
            api.login(username, password)
            self.mensaje.config(text="")
            self.on_login_success()
        except APIError as e:
            if e.status_code == 429:
                self.mensaje.config(text="Cuenta bloqueada temporalmente. Intenta más tarde.")
            else:
                self.mensaje.config(text=e.detail)
        except Exception:
            self.mensaje.config(text="No se pudo conectar al servidor. ¿Está corriendo la API?")
