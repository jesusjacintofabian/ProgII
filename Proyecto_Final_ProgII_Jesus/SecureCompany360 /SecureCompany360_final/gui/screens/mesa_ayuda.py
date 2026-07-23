import tkinter as tk
from tkinter import ttk, messagebox

from api_client import api, APIError


class MesaAyudaScreen(ttk.Frame):
    """Grupo 2 - Mesa de Ayuda (Tickets, Incidencias, Soporte)."""

    def __init__(self, parent):
        super().__init__(parent, padding=15)
        self._construir_formulario()
        self._construir_actualizacion()
        self._construir_tabla()
        self.refrescar()

    def _construir_formulario(self):
        frame = ttk.LabelFrame(self, text="Nuevo Ticket", padding=10)
        frame.grid(row=0, column=0, sticky="nw", padx=(0, 10))

        self.titulo_var = tk.StringVar()
        self.categoria_var = tk.StringVar(value="Soporte")
        self.prioridad_var = tk.StringVar(value="Media")

        ttk.Label(frame, text="Título:").grid(row=0, column=0, sticky="e", pady=3)
        ttk.Entry(frame, textvariable=self.titulo_var, width=28).grid(row=0, column=1, pady=3)

        ttk.Label(frame, text="Descripción:").grid(row=1, column=0, sticky="ne", pady=3)
        self.descripcion_text = tk.Text(frame, width=28, height=4)
        self.descripcion_text.grid(row=1, column=1, pady=3)

        ttk.Label(frame, text="Categoría:").grid(row=2, column=0, sticky="e", pady=3)
        ttk.Combobox(frame, textvariable=self.categoria_var, state="readonly", width=25,
                     values=["Incidencia", "Solicitud", "Soporte"]).grid(row=2, column=1, pady=3)

        ttk.Label(frame, text="Prioridad:").grid(row=3, column=0, sticky="e", pady=3)
        ttk.Combobox(frame, textvariable=self.prioridad_var, state="readonly", width=25,
                     values=["Baja", "Media", "Alta", "Critica"]).grid(row=3, column=1, pady=3)

        ttk.Button(frame, text="Crear Ticket", command=self._crear_ticket).grid(
            row=4, column=0, columnspan=2, pady=(8, 0)
        )

    def _construir_actualizacion(self):
        frame = ttk.LabelFrame(self, text="Actualizar Ticket (Soporte/Admin)", padding=10)
        frame.grid(row=0, column=1, sticky="nw")

        self.ticket_id_var = tk.StringVar()
        self.nuevo_estado_var = tk.StringVar(value="En Progreso")

        ttk.Label(frame, text="ID Ticket:").grid(row=0, column=0, sticky="e", pady=3)
        ttk.Entry(frame, textvariable=self.ticket_id_var, width=22).grid(row=0, column=1, pady=3)

        ttk.Label(frame, text="Nuevo estado:").grid(row=1, column=0, sticky="e", pady=3)
        ttk.Combobox(frame, textvariable=self.nuevo_estado_var, state="readonly", width=19,
                     values=["Abierto", "En Progreso", "Resuelto", "Cerrado"]
                     ).grid(row=1, column=1, pady=3)

        ttk.Button(frame, text="Actualizar", command=self._actualizar_ticket).grid(
            row=2, column=0, columnspan=2, pady=(8, 0)
        )

    def _construir_tabla(self):
        frame = ttk.LabelFrame(self, text="Tickets", padding=10)
        frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(15, 0))

        columnas = ("id", "titulo", "categoria", "prioridad", "estado", "usuario_id")
        self.tabla = ttk.Treeview(frame, columns=columnas, show="headings", height=8)
        for col, ancho in zip(columnas, (40, 200, 90, 80, 100, 80)):
            self.tabla.heading(col, text=col.capitalize())
            self.tabla.column(col, width=ancho)
        self.tabla.pack(fill="both", expand=True)

        ttk.Button(frame, text="Refrescar", command=self.refrescar).pack(pady=(6, 0))

    def _crear_ticket(self):
        try:
            api.crear_ticket({
                "titulo": self.titulo_var.get().strip(),
                "descripcion": self.descripcion_text.get("1.0", "end").strip(),
                "categoria": self.categoria_var.get(),
                "prioridad": self.prioridad_var.get(),
            })
            messagebox.showinfo("Éxito", "Ticket creado")
            self.titulo_var.set("")
            self.descripcion_text.delete("1.0", "end")
            self.refrescar()
        except APIError as e:
            messagebox.showerror("Error", e.detail)

    def _actualizar_ticket(self):
        try:
            ticket_id = int(self.ticket_id_var.get())
        except ValueError:
            messagebox.showerror("Error", "ID de ticket inválido")
            return
        try:
            api.actualizar_ticket(ticket_id, {"estado": self.nuevo_estado_var.get()})
            messagebox.showinfo("Éxito", "Ticket actualizado")
            self.refrescar()
        except APIError as e:
            messagebox.showerror("Error", e.detail)

    def refrescar(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        try:
            for t in api.listar_tickets():
                self.tabla.insert("", "end", values=(
                    t["id"], t["titulo"], t["categoria"], t["prioridad"],
                    t["estado"], t["usuario_id"],
                ))
        except APIError as e:
            messagebox.showerror("Error", e.detail)
