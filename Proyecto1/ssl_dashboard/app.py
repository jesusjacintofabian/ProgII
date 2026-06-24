import os
import io
import tempfile
from datetime import datetime

from flask import Flask, render_template, request, send_file, session, after_this_request
from fpdf import FPDF

from ssl_auditor import verificar_ssl, formatear_resultado_txt, formatear_resultado_para_tabla_pdf

# Crear aplicación Flask
app = Flask(__name__)

# Clave necesaria para utilizar sesiones
app.secret_key = "cambia-esto-por-una-clave-secreta"


@app.route("/", methods=["GET", "POST"])
def inicio():
    # Variable para almacenar el resultado de la auditoría
    resultado = None

    # Procesar formulario cuando se envía
    if request.method == "POST":
        dominio = request.form["dominio"]

        # Ejecutar auditoría SSL
        resultado = verificar_ssl(dominio)

        # Guardar resultado en sesión para futuras descargas
        session["ultimo_resultado"] = resultado

    return render_template("index.html", resultado=resultado)


@app.route("/descargar-txt")
def descargar_txt():
    # Obtener último resultado guardado
    resultado = session.get("ultimo_resultado")

    # Validar que exista una auditoría previa
    if not resultado:
        return "No hay ningún resultado para descargar. Realiza primero una auditoría.", 400

    # Construir contenido del reporte
    contenido = (
        "==================================================\n"
        "          REPORTE AUTOMÁTICO DE AUDITORÍA SSL      \n"
        f"          Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        "==================================================\n\n"
        + formatear_resultado_txt(resultado)
    )

    # Crear archivo en memoria
    buffer = io.BytesIO(contenido.encode("utf-8"))
    buffer.seek(0)

    # Descargar archivo TXT
    return send_file(
        buffer,
        mimetype="text/plain",
        as_attachment=True,
        download_name=f"reporte_ssl_{resultado['dominio']}.txt"
    )


@app.route("/descargar-pdf")
def descargar_pdf():
    # Obtener último resultado guardado
    resultado = session.get("ultimo_resultado")

    # Validar que exista una auditoría previa
    if not resultado:
        return "No hay ningún resultado para descargar. Realiza primero una auditoría.", 400

    # Crear documento PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Encabezado del reporte
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Reporte Automatizado de Seguridad SSL", ln=True, align="C")

    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(
        0,
        10,
        f"Fecha de emisión: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Módulo SSL",
        ln=True,
        align="C"
    )
    pdf.ln(10)

    # Colores según nivel de alerta
    colores_alerta = {
        "SEGURO": (220, 245, 220),
        "ADVERTENCIA": (255, 243, 205),
        "PELIGRO": (255, 213, 213),
        "CRÍTICO": (248, 215, 218),
        "ERROR_CONEXION": (230, 230, 230),
        "ERROR_INESPERADO": (230, 230, 230)
    }

    # Preparar datos para la tabla
    tabla_datos = formatear_resultado_para_tabla_pdf(resultado)
    fondo_rgb = colores_alerta.get(resultado["estado_alerta"], (255, 255, 255))

    # Mostrar dominio analizado
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(
        0,
        8,
        f"API Endpoint / Dominio: {resultado['dominio']}",
        ln=True,
        fill=True,
        border="B"
    )
    pdf.ln(2)

    # Crear tabla de resultados
    for i, fila in enumerate(tabla_datos):
        if i == 0:
            # Encabezados de tabla
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(70, 7, fila[0], border=1, fill=True)
            pdf.cell(120, 7, fila[1], border=1, fill=True, ln=True)
        else:
            # Filas de datos
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(70, 7, fila[0], border=1)

            pdf.set_font("Helvetica", "", 9)

            # Resaltar campos importantes
            if fila[0] in ["Severidad / Alerta", "Estado General"]:
                pdf.set_fill_color(*fondo_rgb)
                pdf.set_font("Helvetica", "B", 9)
                pdf.cell(120, 7, fila[1], border=1, fill=True, ln=True)
            else:
                pdf.cell(120, 7, fila[1], border=1, ln=True)

    # Crear archivo temporal para almacenar el PDF
    archivo_temp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    ruta_temp = archivo_temp.name
    archivo_temp.close()

    # Guardar PDF en disco
    pdf.output(ruta_temp)

    # Eliminar archivo temporal después de enviarlo
    @after_this_request
    def limpiar(response):
        try:
            os.remove(ruta_temp)
        except Exception:
            pass
        return response

    # Descargar PDF
    return send_file(
        ruta_temp,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"reporte_ssl_{resultado['dominio']}.pdf"
    )


# Ejecutar aplicación
if __name__ == "__main__":
    app.run(debug=True)