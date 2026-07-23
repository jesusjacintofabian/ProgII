import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from api_client import api, APIError


class AdminDashboardScreen(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)

        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True)

        izq = ttk.Frame(paned, padding=5)
        der = ttk.Frame(paned, padding=5)
        paned.add(izq, weight=1)
        paned.add(der, weight=2)

        self._build_metricas(izq)
        self._build_auditoria(der)
        self._build_btn_bar(izq)

        self.refrescar()

    def _build_metricas(self, parent):
        frame = ttk.LabelFrame(parent, text="Métricas del Sistema", padding=10)
        frame.pack(fill="x", pady=(0, 10))

        etiquetas = [
            ("total_usuarios_activos", "Usuarios activos"),
            ("total_empleados", "Empleados"),
            ("tickets_abiertos", "Tickets abiertos"),
            ("tickets_criticos", "Tickets críticos"),
            ("activos_disponibles", "Activos disponibles"),
            ("activos_asignados", "Activos asignados"),
            ("intentos_login_fallidos_24h", "Logins fallidos (24h)"),
        ]
        self.metric_labels = {}
        for i, (key, texto) in enumerate(etiquetas):
            ttk.Label(frame, text=f"{texto}:", font=("Segoe UI", 9)).grid(
                row=i, column=0, sticky="e", pady=2, padx=(0, 6)
            )
            lbl = ttk.Label(frame, text="-", font=("Segoe UI", 9, "bold"))
            lbl.grid(row=i, column=1, sticky="w", pady=2)
            self.metric_labels[key] = lbl

    def _build_btn_bar(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)
        ttk.Button(frame, text="Refrescar", command=self.refrescar).pack(fill="x", pady=2)
        ttk.Button(frame, text="Analisis de Logs", command=self._abrir_analizador).pack(fill="x", pady=2)
        ttk.Button(frame, text="Centro de Seguridad", command=self._abrir_seguridad).pack(fill="x", pady=2)

    def _build_auditoria(self, parent):
        frame = ttk.LabelFrame(parent, text="Log de Auditoría (últimos eventos)", padding=8)
        frame.pack(fill="both", expand=True)

        columnas = ("id", "usuario_id", "accion", "detalle", "ip", "fecha")
        self.tabla = ttk.Treeview(frame, columns=columnas, show="headings", height=14)
        for col, ancho in zip(columnas, (40, 65, 120, 180, 90, 130)):
            self.tabla.heading(col, text=col.capitalize())
            self.tabla.column(col, width=ancho)
        self.tabla.pack(fill="both", expand=True)

    def _abrir_analizador(self):
        LogAnalyzerWindow(self)

    def _abrir_seguridad(self):
        SeguridadWindow(self)

    def refrescar(self):
        try:
            metricas = api.dashboard()
            for key, label in self.metric_labels.items():
                label.config(text=str(metricas.get(key, "-")))
        except APIError as e:
            messagebox.showerror("Error", e.detail)

        for item in self.tabla.get_children():
            self.tabla.delete(item)
        try:
            for log in api.auditoria():
                self.tabla.insert("", "end", values=(
                    log["id"], log.get("usuario_id") or "-", log["accion"],
                    log.get("detalle") or "-", log.get("ip_origen") or "-", log["fecha"],
                ))
        except APIError as e:
            messagebox.showerror("Error", e.detail)


# =============================================================================
# VENTANA DE ANÁLISIS DE LOGS (existente, mejorada)
# =============================================================================

class LogAnalyzerWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Analizador de Logs y Ciberseguridad")
        self.geometry("720x620")
        self.minsize(600, 500)
        self.transient(parent)
        self.grab_set()

        self._datos = {}
        self._construir_ui()
        self._cargar_datos()

    def _construir_ui(self):
        header = ttk.Frame(self, padding=12)
        header.pack(fill="x")
        ttk.Label(header, text="Estado de Seguridad Global:", font=("Segoe UI", 12)).pack(side="left")
        self.riesgo_label = ttk.Label(header, text="Cargando...", font=("Segoe UI", 12, "bold"))
        self.riesgo_label.pack(side="left", padx=10)

        res_frame = ttk.LabelFrame(self, text="Métricas del Sistema y Auditoría", padding=10)
        res_frame.pack(fill="x", padx=12, pady=5)
        self.res_labels = {}
        campos = [
            ("total_log_archivo", "Líneas Log Técnico:"),
            ("total_log_auditoria", "Eventos Auditoría (DB):"),
            ("total_fallidos", "Intentos Fallidos:"),
            ("total_bloqueos", "Bloqueos Temporales:"),
            ("total_errores", "Errores Técnicos:"),
        ]
        for i, (key, label) in enumerate(campos):
            ttk.Label(res_frame, text=label, font=("Segoe UI", 9)).grid(
                row=i//2, column=(i%2)*2, sticky="e", padx=4, pady=2)
            val = ttk.Label(res_frame, text="-", font=("Segoe UI", 9, "bold"))
            val.grid(row=i//2, column=(i%2)*2+1, sticky="w", padx=4, pady=2)
            self.res_labels[key] = val

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=5)

        alert_frame = ttk.Frame(nb, padding=8)
        nb.add(alert_frame, text="Alertas")
        self.alert_text = tk.Text(alert_frame, wrap="word", height=8, font=("Segoe UI", 9))
        self.alert_text.pack(fill="both", expand=True, side="left")
        scroll_alert = ttk.Scrollbar(alert_frame, command=self.alert_text.yview)
        scroll_alert.pack(fill="y", side="right")
        self.alert_text.config(yscrollcommand=scroll_alert.set)

        rec_frame = ttk.Frame(nb, padding=8)
        nb.add(rec_frame, text="Recomendaciones")
        self.rec_text = tk.Text(rec_frame, wrap="word", height=8, font=("Segoe UI", 9))
        self.rec_text.pack(fill="both", expand=True)

        footer = ttk.Frame(self, padding=8)
        footer.pack(fill="x")
        ttk.Button(footer, text="Cerrar", command=self.destroy).pack(side="right", padx=4)
        ttk.Button(footer, text="Exportar Reporte (.md)", command=self._exportar).pack(side="right", padx=4)
        ttk.Button(footer, text="Recargar", command=self._cargar_datos).pack(side="right", padx=4)

    def _cargar_datos(self):
        self.riesgo_label.config(text="Cargando...", foreground="black")
        for w in (self.alert_text, self.rec_text):
            w.config(state="normal")
            w.delete("1.0", "end")

        try:
            res = api.analisis_logs()
            self._datos = res

            riesgo = res.get("nivel_riesgo", "Bajo")
            color = {"Bajo": "green", "Medio": "orange", "Alto": "red"}.get(riesgo, "black")
            self.riesgo_label.config(text=riesgo.upper(), foreground=color)

            resumen = res.get("resumen", {})
            for key, label in self.res_labels.items():
                label.config(text=str(resumen.get(key, 0)))

            for a in res.get("alertas", []):
                self.alert_text.insert("end", f"\u2022 [{a['nivel'].upper()}] ({a['tipo']}): {a['mensaje']}\n\n")
            if not res.get("alertas"):
                self.alert_text.insert("end", "No se detectaron anomalías de seguridad.\n")

            for r in res.get("recomendaciones", []):
                self.rec_text.insert("end", f"\u2714 {r}\n")

        except APIError as e:
            messagebox.showerror("Error", f"No se pudo cargar el análisis: {e.detail}")
            self.destroy()
            return

        for w in (self.alert_text, self.rec_text):
            w.config(state="disabled")

    def _exportar(self):
        if not self._datos:
            return
        try:
            import os
            filename = "reporte_auditoria_gui.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# Reporte de Seguridad - Secure Company 360\n\n")
                f.write(f"- **Riesgo:** {self._datos.get('nivel_riesgo', '?').upper()}\n")
                f.write(f"- **Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("## Resumen\n")
                for k, v in self._datos.get("resumen", {}).items():
                    f.write(f"- {k.replace('_',' ').capitalize()}: {v}\n")
                f.write("\n## Alertas\n")
                for a in self._datos.get("alertas", []):
                    f.write(f"- [{a['nivel']}] {a['mensaje']}\n")
                f.write("\n## Recomendaciones\n")
                for r in self._datos.get("recomendaciones", []):
                    f.write(f"- {r}\n")
            messagebox.showinfo("Éxito", f"Reporte exportado a {os.path.abspath(filename)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# =============================================================================
# CENTRO DE SEGURIDAD — Dashboard completo con pestañas
# =============================================================================

class SeguridadWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Centro de Seguridad - Secure Company 360")
        self.geometry("900x650")
        self.minsize(800, 550)
        self.transient(parent)
        self.grab_set()

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        self.tab_resumen = ttk.Frame(nb, padding=10)
        nb.add(self.tab_resumen, text="Resumen Seguridad")
        self._build_resumen()

        self.tab_alertas = ttk.Frame(nb, padding=10)
        nb.add(self.tab_alertas, text="Alertas")
        self._build_alertas()

        self.tab_incidentes = ttk.Frame(nb, padding=10)
        nb.add(self.tab_incidentes, text="Incidentes")
        self._build_incidentes()

        self.tab_ips = ttk.Frame(nb, padding=10)
        nb.add(self.tab_ips, text="IPs Bloqueadas")
        self._build_ips()

        self.tab_acciones = ttk.Frame(nb, padding=10)
        nb.add(self.tab_acciones, text="Respuestas Automáticas")
        self._build_acciones()

        self.tab_generador = ttk.Frame(nb, padding=10)
        nb.add(self.tab_generador, text="Generador de Logs")
        self._build_generador()

        self._actualizar_resumen()

    # ---- Pestaña 1: Resumen ----

    def _build_resumen(self):
        top = ttk.Frame(self.tab_resumen)
        top.pack(fill="x", pady=(0, 10))

        ttk.Label(top, text="Panorama General de Seguridad", font=("Segoe UI", 14, "bold")).pack(anchor="w")

        mid = ttk.Frame(self.tab_resumen)
        mid.pack(fill="x", pady=5)

        self.risk_label = ttk.Label(mid, text="Nivel de Riesgo: --",
                                    font=("Segoe UI", 16, "bold"))
        self.risk_label.pack(side="left", padx=(0, 20))

        ttk.Button(mid, text="Actualizar", command=self._actualizar_resumen).pack(side="left")

        frame = ttk.LabelFrame(self.tab_resumen, text="Métricas de Seguridad", padding=15)
        frame.pack(fill="both", expand=True)

        self.seg_labels = {}
        metricas = [
            ("alertas_no_leidas", "Alertas No Leídas"),
            ("incidentes_abiertos", "Incidentes Abiertos"),
            ("ips_bloqueadas", "IPs Bloqueadas"),
            ("usuarios_deshabilitados", "Usuarios Deshabilitados"),
            ("intentos_fallidos_24h", "Intentos Fallidos (24h)"),
            ("alertas_ultima_hora", "Alertas (última hora)"),
        ]
        for i, (key, texto) in enumerate(metricas):
            row, col = divmod(i, 3)
            ttk.Label(frame, text=texto, font=("Segoe UI", 10)).grid(
                row=row*2, column=col, sticky="w", pady=(10, 0), padx=10)
            lbl = ttk.Label(frame, text="-", font=("Segoe UI", 14, "bold"))
            lbl.grid(row=row*2+1, column=col, sticky="w", pady=(0, 5), padx=10)
            self.seg_labels[key] = lbl

    def _actualizar_resumen(self):
        try:
            data = api.dashboard_seguridad()
            riesgo = data.get("nivel_riesgo_actual", "Bajo")
            color = {"Bajo": "green", "Medio": "orange", "Alto": "red"}.get(riesgo, "black")
            self.risk_label.config(text=f"Nivel de Riesgo: {riesgo.upper()}", foreground=color)

            for key, lbl in self.seg_labels.items():
                lbl.config(text=str(data.get(key, 0)))
        except APIError as e:
            messagebox.showerror("Error", e.detail)

    # ---- Pestaña 2: Alertas ----

    def _build_alertas(self):
        toolbar = ttk.Frame(self.tab_alertas)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(toolbar, text="Cargar Alertas", command=self._cargar_alertas).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Evaluar Alertas", command=self._evaluar_alertas).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Marcar Leída", command=self._marcar_leida).pack(side="left", padx=3)

        columnas = ("id", "nivel", "tipo", "mensaje", "ip", "leida", "fecha")
        self.alert_tree = ttk.Treeview(self.tab_alertas, columns=columnas, show="headings", height=12)
        for col, ancho in zip(columnas, (40, 60, 120, 250, 100, 50, 130)):
            self.alert_tree.heading(col, text=col.capitalize())
            self.alert_tree.column(col, width=ancho, minwidth=30)
        self.alert_tree.pack(fill="both", expand=True)

    def _cargar_alertas(self):
        for item in self.alert_tree.get_children():
            self.alert_tree.delete(item)
        try:
            for a in api.listar_alertas():
                self.alert_tree.insert("", "end", values=(
                    a["id"], a["nivel"], a["tipo"], a["mensaje"][:80],
                    a.get("ip_origen") or "-",
                    "\u2713" if a["leida"] else "\u2717",
                    a["creado_en"][:19] if a["creado_en"] else "-",
                ))
        except APIError as e:
            messagebox.showerror("Error", e.detail)

    def _evaluar_alertas(self):
        try:
            res = api.evaluar_alertas()
            messagebox.showinfo("Evaluación Completa",
                                f"Alertas generadas: {res.get('alertas_generadas', 0)}")
            self._cargar_alertas()
        except APIError as e:
            messagebox.showerror("Error", e.detail)

    def _marcar_leida(self):
        sel = self.alert_tree.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione una alerta primero")
            return
        item = self.alert_tree.item(sel[0])
        alerta_id = item["values"][0]
        try:
            api.marcar_alerta_leida(alerta_id)
            self._cargar_alertas()
        except APIError as e:
            messagebox.showerror("Error", e.detail)

    # ---- Pestaña 3: Incidentes ----

    def _build_incidentes(self):
        toolbar = ttk.Frame(self.tab_incidentes)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(toolbar, text="Cargar Incidentes", command=self._cargar_incidentes).pack(side="left", padx=3)

        ttk.Label(toolbar, text="Estado:").pack(side="left", padx=(15, 3))
        self.estado_combo = ttk.Combobox(toolbar, values=["Abierto", "En_Investigacion", "Resuelto", "Cerrado"],
                                          state="readonly", width=16)
        self.estado_combo.pack(side="left")
        self.estado_combo.set("En_Investigacion")
        ttk.Button(toolbar, text="Actualizar Estado", command=self._actualizar_incidente).pack(side="left", padx=3)

        columnas = ("id", "nivel", "tipo", "descripcion", "estado", "ip", "fecha")
        self.inc_tree = ttk.Treeview(self.tab_incidentes, columns=columnas, show="headings", height=12)
        for col, ancho in zip(columnas, (40, 60, 120, 280, 90, 100, 130)):
            self.inc_tree.heading(col, text=col.capitalize())
            self.inc_tree.column(col, width=ancho, minwidth=30)
        self.inc_tree.pack(fill="both", expand=True)

    def _cargar_incidentes(self):
        for item in self.inc_tree.get_children():
            self.inc_tree.delete(item)
        try:
            for i in api.listar_incidentes():
                self.inc_tree.insert("", "end", values=(
                    i["id"], i["nivel"], i["tipo"], i["descripcion"][:80],
                    i["estado"], i.get("ip_origen") or "-",
                    i["creado_en"][:19] if i["creado_en"] else "-",
                ))
        except APIError as e:
            messagebox.showerror("Error", e.detail)

    def _actualizar_incidente(self):
        sel = self.inc_tree.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione un incidente primero")
            return
        item = self.inc_tree.item(sel[0])
        iid = item["values"][0]
        estado = self.estado_combo.get()
        try:
            api.actualizar_incidente(iid, estado)
            self._cargar_incidentes()
        except APIError as e:
            messagebox.showerror("Error", e.detail)

    # ---- Pestaña 4: IPs Bloqueadas ----

    def _build_ips(self):
        toolbar = ttk.Frame(self.tab_ips)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(toolbar, text="Cargar IPs", command=self._cargar_ips).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Bloquear IP", command=self._dialogo_bloquear_ip).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Desbloquear IP", command=self._desbloquear_ip).pack(side="left", padx=3)

        columnas = ("id", "direccion_ip", "motivo", "creado_en")
        self.ip_tree = ttk.Treeview(self.tab_ips, columns=columnas, show="headings", height=12)
        for col, ancho in zip(columnas, (40, 140, 350, 140)):
            self.ip_tree.heading(col, text=col.capitalize())
            self.ip_tree.column(col, width=ancho, minwidth=30)
        self.ip_tree.pack(fill="both", expand=True)

    def _cargar_ips(self):
        for item in self.ip_tree.get_children():
            self.ip_tree.delete(item)
        try:
            for ip in api.listar_ips_bloqueadas():
                self.ip_tree.insert("", "end", values=(
                    ip["id"], ip["direccion_ip"], ip.get("motivo") or "-",
                    ip["creado_en"][:19] if ip["creado_en"] else "-",
                ))
        except APIError as e:
            messagebox.showerror("Error", e.detail)

    def _dialogo_bloquear_ip(self):
        win = tk.Toplevel(self)
        win.title("Bloquear IP")
        win.geometry("400x200")
        win.transient(self)
        win.grab_set()

        ttk.Label(win, text="Dirección IP:").pack(pady=(15, 3))
        ip_var = tk.StringVar()
        ttk.Entry(win, textvariable=ip_var, width=30).pack(pady=3)

        ttk.Label(win, text="Motivo:").pack(pady=3)
        mot_var = tk.StringVar(value="Bloqueado desde Centro de Seguridad")
        ttk.Entry(win, textvariable=mot_var, width=50).pack(pady=3)

        def _ejecutar():
            if not ip_var.get().strip():
                messagebox.showwarning("Validación", "Ingrese una dirección IP")
                return
            try:
                res = api.bloquear_ip(ip_var.get().strip(), mot_var.get())
                messagebox.showinfo("Resultado", res["mensaje"])
                win.destroy()
                self._cargar_ips()
            except APIError as e:
                messagebox.showerror("Error", e.detail)

        ttk.Button(win, text="Bloquear", command=_ejecutar).pack(pady=15)

    def _desbloquear_ip(self):
        sel = self.ip_tree.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione una IP primero")
            return
        item = self.ip_tree.item(sel[0])
        ip_id, direccion = item["values"][0], item["values"][1]
        if messagebox.askyesno("Confirmar", f"\u00bfDesbloquear {direccion}?"):
            try:
                api.eliminar_ip_bloqueada(ip_id)
                self._cargar_ips()
            except APIError as e:
                messagebox.showerror("Error", e.detail)

    # ---- Pestaña 5: Respuestas Automáticas ----

    def _build_acciones(self):
        frame = ttk.LabelFrame(self.tab_acciones, text="Acciones de Respuesta Rápida", padding=15)
        frame.pack(fill="both", expand=True, pady=10)

        ttk.Label(frame, text="Deshabilitar Usuario",
                  font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", pady=(10, 3))
        ttk.Label(frame, text="ID de Usuario:").grid(row=1, column=0, sticky="w")
        self.des_id_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.des_id_var, width=10).grid(row=1, column=1, sticky="w", padx=5)
        ttk.Label(frame, text="Motivo:").grid(row=2, column=0, sticky="w")
        self.des_mot_var = tk.StringVar(value="Actividad sospechosa detectada")
        ttk.Entry(frame, textvariable=self.des_mot_var, width=40).grid(row=2, column=1, sticky="w", padx=5)
        ttk.Button(frame, text="Deshabilitar", command=self._deshabilitar_usuario_accion).grid(row=3, column=0, columnspan=2, pady=5)

        ttk.Separator(frame, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Label(frame, text="Enviar Correo (Simulado)",
                  font=("Segoe UI", 11, "bold")).grid(row=5, column=0, sticky="w", pady=(10, 3))
        ttk.Label(frame, text="Destinatario:").grid(row=6, column=0, sticky="w")
        self.correo_dest = tk.StringVar(value="admin@securecompany360.local")
        ttk.Entry(frame, textvariable=self.correo_dest, width=30).grid(row=6, column=1, sticky="w", padx=5)
        ttk.Label(frame, text="Asunto:").grid(row=7, column=0, sticky="w")
        self.correo_asunto = tk.StringVar(value="Alerta de Seguridad - Acción Requerida")
        ttk.Entry(frame, textvariable=self.correo_asunto, width=40).grid(row=7, column=1, sticky="w", padx=5)
        ttk.Label(frame, text="Cuerpo:").grid(row=8, column=0, sticky="nw")
        self.correo_cuerpo = tk.Text(frame, width=40, height=4, font=("Segoe UI", 9))
        self.correo_cuerpo.grid(row=8, column=1, sticky="w", padx=5, pady=2)
        self.correo_cuerpo.insert("1.0", "Se ha detectado una actividad sospechosa en el sistema.\n\nRevise el Centro de Seguridad para más detalles.")
        ttk.Button(frame, text="Enviar Correo", command=self._enviar_correo_accion).grid(row=9, column=0, columnspan=2, pady=5)

        ttk.Separator(frame, orient="horizontal").grid(row=10, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Label(frame, text="Generar Reporte de Seguridad",
                  font=("Segoe UI", 11, "bold")).grid(row=11, column=0, sticky="w", pady=(10, 3))
        ttk.Label(frame, text="Tipo:").grid(row=12, column=0, sticky="w")
        self.reporte_tipo = ttk.Combobox(frame, values=["completo", "resumen", "alertas"], state="readonly", width=15)
        self.reporte_tipo.grid(row=12, column=1, sticky="w", padx=5)
        self.reporte_tipo.set("completo")
        ttk.Button(frame, text="Generar Reporte", command=self._generar_reporte_accion).grid(row=13, column=0, columnspan=2, pady=5)

    def _deshabilitar_usuario_accion(self):
        uid = self.des_id_var.get().strip()
        if not uid or not uid.isdigit():
            messagebox.showwarning("Validación", "Ingrese un ID de usuario válido")
            return
        try:
            res = api.deshabilitar_usuario(int(uid), self.des_mot_var.get())
            messagebox.showinfo("Resultado", res["mensaje"])
        except APIError as e:
            messagebox.showerror("Error", e.detail)

    def _enviar_correo_accion(self):
        try:
            res = api.enviar_correo(
                self.correo_dest.get(),
                self.correo_asunto.get(),
                self.correo_cuerpo.get("1.0", "end-1c"),
            )
            messagebox.showinfo("Resultado", res["mensaje"])
        except APIError as e:
            messagebox.showerror("Error", e.detail)

    def _generar_reporte_accion(self):
        try:
            res = api.generar_reporte(self.reporte_tipo.get())
            msg = res["mensaje"]
            if res.get("archivo"):
                msg += f"\n\nArchivo: {res['archivo']}"
            messagebox.showinfo("Resultado", msg)
        except APIError as e:
            messagebox.showerror("Error", e.detail)

    # ---- Pestaña 6: Generador de Logs ----

    def _build_generador(self):
        frame = ttk.LabelFrame(self.tab_generador, text="Simulador de Eventos de Seguridad", padding=20)
        frame.pack(fill="both", expand=True, pady=10)

        ttk.Label(frame, text="Generador de Escenarios de Ataque",
                  font=("Segoe UI", 13, "bold")).pack(pady=(0, 15))

        ttk.Label(frame, text="Este módulo genera eventos simulados en el sistema para probar\nlas capacidades de detección del motor de alertas y respuestas automáticas.",
                  font=("Segoe UI", 9), foreground="gray").pack(pady=(0, 15))

        ttk.Button(frame, text="Fuerza Bruta (15 intentos desde IP extranjera)",
                   command=lambda: self._ejecutar_generador("fuerza_bruta"),
                   width=50).pack(pady=4)
        ttk.Button(frame, text="Inyección SQL (5 intentos con payloads)",
                   command=lambda: self._ejecutar_generador("inyeccion_sql"),
                   width=50).pack(pady=4)
        ttk.Button(frame, text="Acceso desde IP Extranjera",
                   command=lambda: self._ejecutar_generador("acceso_externo"),
                   width=50).pack(pady=4)
        ttk.Button(frame, text="Actividad en Horario Nocturno",
                   command=lambda: self._ejecutar_generador("actividad_nocturna"),
                   width=50).pack(pady=4)

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=12)

        ttk.Button(frame, text="SIMULACIÓN COMPLETA (todos los escenarios)",
                   command=lambda: self._ejecutar_generador("completo"),
                   width=50).pack(pady=4)
        ttk.Button(frame, text="Tráfico Normal (5 logins exitosos)",
                   command=lambda: self._ejecutar_generador("normal"),
                   width=50).pack(pady=4)

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=12)

        self.gen_result = tk.Text(frame, wrap="word", height=6, font=("Segoe UI", 9), state="disabled")
        self.gen_result.pack(fill="x", pady=5)

    def _ejecutar_generador(self, escenario):
        try:
            res = api.generar_logs(escenario)
            self.gen_result.config(state="normal")
            self.gen_result.delete("1.0", "end")
            self.gen_result.insert("end", f"Escenario: {res.get('escenario', escenario)}\n")
            self.gen_result.insert("end", f"Estado: Completado exitosamente\n")
            if "ip" in res:
                self.gen_result.insert("end", f"IP utilizada: {res['ip']}\n")
            if "pais" in res:
                self.gen_result.insert("end", f"País de origen: {res['pais']}\n")
            if "eventos" in res:
                self.gen_result.insert("end", f"Eventos generados: {res['eventos']}\n")
            if "eventos_generados" in res:
                for ev in res["eventos_generados"]:
                    self.gen_result.insert("end", f"  - {ev.get('escenario', '?')}: {ev.get('eventos', 0)} eventos\n")
            self.gen_result.config(state="disabled")

            if messagebox.askyesno("Evaluar Alertas", "¿Ejecutar evaluación de alertas ahora?"):
                res_eval = api.evaluar_alertas()
                messagebox.showinfo("Alertas Evaluadas",
                                    f"{res_eval.get('alertas_generadas', 0)} alerta(s) generada(s)")
        except APIError as e:
            messagebox.showerror("Error", e.detail)
