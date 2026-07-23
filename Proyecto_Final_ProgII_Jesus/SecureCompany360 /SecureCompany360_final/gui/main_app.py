"""
Secure Company 360 - Cliente de escritorio (Tkinter)
Grupo 1 (RRHH + Inventario) y Grupo 2 (Mesa de Ayuda + Admin General)

Ejecutar:
    cd gui
    python main_app.py

Requiere que el backend (FastAPI) esté corriendo en http://127.0.0.1:8000
"""
import tkinter as tk
from tkinter import ttk

from api_client import api
from screens.login import LoginScreen
from screens.rrhh import RRHHScreen
from screens.inventario import InventarioScreen
from screens.mesa_ayuda import MesaAyudaScreen
from screens.admin_dashboard import AdminDashboardScreen


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Company 360")
        self.geometry("980x600")
        self.minsize(860, 520)

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self._mostrar_login()

    def _mostrar_login(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        LoginScreen(self.container, on_login_success=self._mostrar_app).pack(
            fill="both", expand=True
        )

    def _mostrar_app(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        # ---- Barra superior con usuario/rol y logout ----
        top_bar = ttk.Frame(self.container, padding=8)
        top_bar.pack(fill="x")
        ttk.Label(
            top_bar, text=f"Sesión: {api.username}  |  Rol: {api.rol}",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")
        ttk.Button(top_bar, text="Cerrar sesión", command=self._logout).pack(side="right")

        # ---- Pestañas visibles según el rol ----
        notebook = ttk.Notebook(self.container)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        rol = api.rol

        if rol in ("Administrador", "RRHH", "Analista"):
            notebook.add(RRHHScreen(notebook), text="RRHH (Grupo 1)")

        # Inventario visible para todos: cualquiera puede solicitar un activo
        notebook.add(InventarioScreen(notebook), text="Inventario (Grupo 1)")

        # Mesa de ayuda visible para todos: cualquiera reporta tickets
        notebook.add(MesaAyudaScreen(notebook), text="Mesa de Ayuda (Grupo 2)")

        if rol == "Administrador":
            notebook.add(AdminDashboardScreen(notebook), text="Admin / Dashboard (Grupo 2)")

    def _logout(self):
        api.logout()
        self._mostrar_login()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
