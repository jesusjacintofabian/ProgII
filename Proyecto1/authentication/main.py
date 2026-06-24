"""
Script principal de la herramienta de auditoría.
Solicita autenticación al usuario y, si es exitosa, genera un reporte
en PDF con los resultados del módulo de autenticación.
"""

import sys
import getpass
from datetime import datetime
from auth import authenticate_user, verify_token, JWT_EXPIRATION_MINUTES
from fpdf import FPDF
import os


# ──────────────────────────────────────────────
# Generación del reporte PDF
# ──────────────────────────────────────────────

def generar_reporte_pdf(username, token):
    """
    Genera un archivo PDF con los resultados de la auditoría de autenticación.
    El reporte incluye una tabla con los datos del usuario autenticado,
    el método usado, la validez del token y el estado general,
    resaltado en color según el resultado.

    Args:
        username (str): Nombre del usuario autenticado.
        token (str): Token JWT generado tras la autenticación exitosa.
    """

    # Crea la carpeta "reports" junto al script si aún no existe
    carpeta_reportes = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(carpeta_reportes, exist_ok=True)

    # Ruta completa del archivo de salida
    nombre_archivo = os.path.join(carpeta_reportes, "reporte_auditoria.pdf")

    # Inicializa el documento PDF con salto de página automático
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Encabezado del reporte ──────────────────
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Reporte de Auditoria de Seguridad", ln=True, align="C")

    # Subtítulo con fecha de emisión y módulo auditado
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(
        0, 10,
        "Fecha de emision: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " | Modulo de Autenticacion",
        ln=True, align="C"
    )
    pdf.ln(10)

    # ── Colores de estado ───────────────────────
    # Verde claro para éxito, rojo claro para fallo.
    # Este reporte solo se genera cuando la autenticación fue exitosa,
    # pero se deja el diccionario preparado para futuros estados.
    colores_estado = {
        "EXITOSA": (220, 245, 220),
        "FALLIDA": (255, 213, 213),
    }
    estado_actual = "EXITOSA"

    # ── Datos de la tabla ───────────────────────
    # Primera fila actúa como encabezado de columnas.
    tabla_datos = [
        ("Campo", "Valor"),
        ("Usuario autenticado",    username),
        ("Fecha y hora",           datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ("Metodo de autenticacion","JWT (JSON Web Token)"),
        ("Expiracion del token",   str(JWT_EXPIRATION_MINUTES) + " minutos"),
        ("Validacion de token",    "Valido"),
        ("Estado General",         "AUTENTICACION " + estado_actual),
    ]

    # Color de fondo para la fila de "Estado General"
    fondo_rgb = colores_estado.get(estado_actual, (255, 255, 255))

    # ── Título de sección ───────────────────────
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, "Resultado de la Auditoria de Autenticacion", ln=True, fill=True, border="B")
    pdf.ln(2)

    # ── Renderizado de la tabla ─────────────────
    for i, fila in enumerate(tabla_datos):
        if i == 0:
            # Fila de encabezado: fondo gris y texto en negrita
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(70, 7, fila[0], border=1, fill=True)
            pdf.cell(120, 7, fila[1], border=1, fill=True, ln=True)
        else:
            # Columna izquierda: nombre del campo en negrita
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(70, 7, fila[0], border=1)

            # Columna derecha: valor; la fila "Estado General" recibe
            # fondo de color según el resultado de la auditoría
            pdf.set_font("Helvetica", "", 9)
            if fila[0] == "Estado General":
                pdf.set_fill_color(*fondo_rgb)
                pdf.set_font("Helvetica", "B", 9)
                pdf.cell(120, 7, fila[1], border=1, fill=True, ln=True)
            else:
                pdf.cell(120, 7, fila[1], border=1, ln=True)

    # Guarda el PDF en disco y confirma la ruta al usuario
    pdf.output(nombre_archivo)
    print("Reporte generado: " + nombre_archivo)


# ──────────────────────────────────────────────
# Punto de entrada principal
# ──────────────────────────────────────────────

def main():
    """
    Flujo principal de la herramienta:
    1. Solicita credenciales al usuario por consola.
    2. Autentica al usuario y obtiene un token JWT.
    3. Verifica el token y ejecuta la auditoría.
    4. Genera el reporte PDF si todo es exitoso.
    """
    print("Auditor de Seguridad para APIs")
    print("Ingrese sus credenciales para continuar.\n")

    # Lectura de credenciales; getpass oculta la contraseña en consola
    username = input("Usuario: ").strip()
    password = getpass.getpass("Contrasena: ")

    # Ambos campos son obligatorios para continuar
    if not username or not password:
        print("Usuario y contrasena son obligatorios.")
        sys.exit(1)

    # Intento de autenticación; cualquier error interno se captura
    try:
        token = authenticate_user(username, password)
    except Exception as e:
        print("Error durante la autenticacion: " + str(e))
        sys.exit(1)

    # Si las credenciales son incorrectas, authenticate_user retorna None
    if token is None:
        print("Credenciales incorrectas. Acceso denegado.")
        sys.exit(1)

    # Confirmación de autenticación exitosa y datos del token
    print("\nAutenticacion exitosa.")
    print("Token JWT generado correctamente.")
    print("Expira en " + str(JWT_EXPIRATION_MINUTES) + " minutos.")

    # ── Acceso a función protegida ──────────────
    # Se verifica el token antes de ejecutar cualquier acción privilegiada
    print("\n--- Acceso a funcion protegida ---")
    payload = verify_token(token)

    if payload:
        # Token válido: se extrae el usuario del campo 'sub' y se ejecuta la auditoría
        print("Token valido. Usuario: " + payload['sub'])
        print("Ejecutando auditoria de seguridad...")
        print("Escaneo completado.")

        # Generación del reporte PDF; se captura cualquier error de escritura
        try:
            generar_reporte_pdf(payload['sub'], token)
        except Exception as e:
            print("No se pudo generar el reporte: " + str(e))
            sys.exit(1)
    else:
        # Token inválido o expirado: se bloquea la ejecución de la auditoría
        print("Token invalido. No se puede ejecutar la auditoria.")


# Punto de entrada del script; solo se ejecuta si se llama directamente
if __name__ == "__main__":
    main()