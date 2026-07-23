import tkinter as tk
from tkinter import ttk, messagebox

from api_client import api, APIError


class InventarioScreen(ttk.Frame):
    """Grupo 1 - Sistema de Inventario (Activos y Software)."""

    def __init__(self, parent):
        super().__init__(parent, padding=15)
        self._construir_formulario()
        self._construir_solicitud()
        self._construir_tabla()
        self.refrescar()

    def _construir_formulario(self):
        frame = ttk.LabelFrame(self, text="Registrar Activo", padding=10)
        frame.grid(row=0, column=0, sticky="nw", padx=(0, 10))

        self.tipo_var = tk.StringVar(value="Equipo")
        self.nombre_var = tk.StringVar()
        self.serie_var = tk.StringVar()

        ttk.Label(frame, text="Tipo:").grid(row=0, column=0, sticky="e", pady=3)
        ttk.Combobox(frame, textvariable=self.tipo_var, state="readonly", width=22,
                     values=["Equipo", "Software", "Otro"]).grid(row=0, column=1, pady=3)

        ttk.Label(frame, text="Nombre:").grid(row=1, column=0, sticky="e", pady=3)
        ttk.Entry(frame, textvariable=self.nombre_var, width=25).grid(row=1, column=1, pady=3)

        ttk.Label(frame, text="N° Serie:").grid(row=2, column=0, sticky="e", pady=3)
        ttk.Entry(frame, textvariable=self.serie_var, width=25).grid(row=2, column=1, pady=3)

        ttk.Button(frame, text="Registrar Activo", command=self._registrar).grid(
            row=3, column=0, columnspan=2, pady=(8, 0)
        )

    def _construir_solicitud(self):
        frame = ttk.LabelFrame(self, text="Solicitar / Aprobar Activo", padding=10)
        frame.grid(row=0, column=1, sticky="nw")

        self.activo_id_var = tk.StringVar()
        self.empleado_id_var = tk.StringVar()

        ttk.Label(frame, text="ID Activo:").grid(row=0, column=0, sticky="e", pady=3)
        ttk.Entry(frame, textvariable=self.activo_id_var, width=20).grid(row=0, column=1, pady=3)

        ttk.Label(frame, text="ID Empleado:").grid(row=1, column=0, sticky="e", pady=3)
        ttk.Entry(frame, textvariable=self.empleado_id_var, width=20).grid(row=1, column=1, pady=3)

        ttk.Button(frame, text="Solicitar", command=self._solicitar).grid(row=2, column=0, pady=(8, 0))
        ttk.Button(frame, text="Aprobar (Admin/RRHH)", command=self._aprobar).grid(row=2, column=1, pady=(8, 0))

    def _construir_tabla(self):
        frame = ttk.LabelFrame(self, text="Activos", padding=10)
        frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(15, 0))

        columnas = ("id", "tipo", "nombre", "serie", "estado", "asignado_a")
        self.tabla = ttk.Treeview(frame, columns=columnas, show="headings", height=8)
        for col, ancho in zip(columnas, (40, 80, 180, 100, 100, 90)):
            self.tabla.heading(col, text=col.capitalize())
            self.tabla.column(col, width=ancho)
        self.tabla.pack(fill="both", expand=True)

        ttk.Button(frame, text="Refrescar", command=self.refrescar).pack(pady=(6, 0))

    def _registrar(self):
        try:
            api.registrar_activo({
                "tipo": self.tipo_var.get(),
                "nombre": self.nombre_var.get().strip(),
                "numero_serie": self.serie_var.get().strip() or None,
            })
            messagebox.showinfo("Éxito", "Activo registrado")
            self.nombre_var.set(""); self.serie_var.set("")
            self.refrescar()
        except APIError as e:
            messagebox.showerror("Error", e.detail)

    def _solicitar(self):
        try:
            api.solicitar_activo(int(self.activo_id_var.get()), int(self.empleado_id_var.get()))
            messagebox.showinfo("Éxito", "Activo solicitado")
            self.refrescar()
        except (ValueError, APIError) as e:
            messagebox.showerror("Error", e.detail if isinstance(e, APIError) else "IDs inválidos")

    def _aprobar(self):
        try:
            api.aprobar_activo(int(self.activo_id_var.get()))
            messagebox.showinfo("Éxito", "Activo asignado")
            self.refrescar()
        except (ValueError, APIError) as e:
            messagebox.showerror("Error", e.detail if isinstance(e, APIError) else "ID inválido")

    def refrescar(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        try:
            for a in api.listar_activos():
                self.tabla.insert("", "end", values=(
                    a["id"], a["tipo"], a["nombre"], a.get("numero_serie") or "-",
                    a["estado"], a.get("asignado_a") or "-",
                ))
        except APIError as e:
            messagebox.showerror("Error", e.detail)
