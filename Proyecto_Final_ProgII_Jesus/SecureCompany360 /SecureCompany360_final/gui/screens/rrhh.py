import tkinter as tk
from tkinter import ttk, messagebox

from api_client import api, APIError


class RRHHScreen(ttk.Frame):
    """Grupo 1 - Sistema de Recursos Humanos (Empleados y Usuarios)."""

    def __init__(self, parent):
        super().__init__(parent, padding=15)
        self._construir_formulario_empleado()
        self._construir_formulario_usuario()
        self._construir_tabla()
        self.refrescar()

    def _construir_formulario_empleado(self):
        frame = ttk.LabelFrame(self, text="Registrar Empleado", padding=10)
        frame.grid(row=0, column=0, sticky="nw", padx=(0, 10))

        self.nombre_var = tk.StringVar()
        self.cedula_var = tk.StringVar()
        self.cargo_var = tk.StringVar()
        self.depto_var = tk.StringVar()

        campos = [
            ("Nombre completo:", self.nombre_var),
            ("Cédula:", self.cedula_var),
            ("Cargo:", self.cargo_var),
            ("Departamento:", self.depto_var),
        ]
        for i, (label, var) in enumerate(campos):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky="e", pady=3)
            ttk.Entry(frame, textvariable=var, width=25).grid(row=i, column=1, pady=3)

        ttk.Button(frame, text="Registrar Empleado", command=self._crear_empleado).grid(
            row=len(campos), column=0, columnspan=2, pady=(8, 0)
        )

    def _construir_formulario_usuario(self):
        frame = ttk.LabelFrame(self, text="Crear Cuenta de Acceso", padding=10)
        frame.grid(row=0, column=1, sticky="nw")

        self.empleado_id_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.rol_var = tk.StringVar(value="Usuario")

        ttk.Label(frame, text="ID Empleado:").grid(row=0, column=0, sticky="e", pady=3)
        ttk.Entry(frame, textvariable=self.empleado_id_var, width=25).grid(row=0, column=1, pady=3)

        ttk.Label(frame, text="Username:").grid(row=1, column=0, sticky="e", pady=3)
        ttk.Entry(frame, textvariable=self.username_var, width=25).grid(row=1, column=1, pady=3)

        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky="e", pady=3)
        ttk.Entry(frame, textvariable=self.password_var, show="*", width=25).grid(row=2, column=1, pady=3)

        ttk.Label(frame, text="Rol:").grid(row=3, column=0, sticky="e", pady=3)
        ttk.Combobox(frame, textvariable=self.rol_var, width=22, state="readonly",
                     values=["Administrador", "RRHH", "Soporte", "Analista", "Usuario"]
                     ).grid(row=3, column=1, pady=3)

        ttk.Button(frame, text="Crear Usuario", command=self._crear_usuario).grid(
            row=4, column=0, columnspan=2, pady=(8, 0)
        )

    def _construir_tabla(self):
        frame = ttk.LabelFrame(self, text="Empleados registrados", padding=10)
        frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(15, 0))

        columnas = ("id", "nombre", "cedula", "cargo", "departamento")
        self.tabla = ttk.Treeview(frame, columns=columnas, show="headings", height=8)
        for col, ancho in zip(columnas, (40, 200, 100, 130, 130)):
            self.tabla.heading(col, text=col.capitalize())
            self.tabla.column(col, width=ancho)
        self.tabla.pack(fill="both", expand=True)

        ttk.Button(frame, text="Refrescar", command=self.refrescar).pack(pady=(6, 0))

    def _crear_empleado(self):
        try:
            api.crear_empleado({
                "nombre_completo": self.nombre_var.get().strip(),
                "cedula": self.cedula_var.get().strip(),
                "cargo": self.cargo_var.get().strip() or None,
                "departamento": self.depto_var.get().strip() or None,
            })
            messagebox.showinfo("Éxito", "Empleado registrado correctamente")
            self.nombre_var.set(""); self.cedula_var.set("")
            self.cargo_var.set(""); self.depto_var.set("")
            self.refrescar()
        except APIError as e:
            messagebox.showerror("Error", e.detail)

    def _crear_usuario(self):
        try:
            empleado_id = int(self.empleado_id_var.get())
        except ValueError:
            messagebox.showerror("Error", "El ID de empleado debe ser un número")
            return
        try:
            api.crear_usuario({
                "empleado_id": empleado_id,
                "username": self.username_var.get().strip(),
                "password": self.password_var.get(),
                "rol_nombre": self.rol_var.get(),
            })
            messagebox.showinfo("Éxito", "Usuario creado correctamente")
            self.empleado_id_var.set(""); self.username_var.set(""); self.password_var.set("")
        except APIError as e:
            messagebox.showerror("Error", e.detail)

    def refrescar(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        try:
            for emp in api.listar_empleados():
                self.tabla.insert("", "end", values=(
                    emp["id"], emp["nombre_completo"], emp["cedula"],
                    emp.get("cargo") or "-", emp.get("departamento") or "-",
                ))
        except APIError as e:
            messagebox.showerror("Error", e.detail)
