"""
scanner.py — Módulo de Auditoría Web Básica
============================================
Evalúa aspectos básicos de seguridad en una URL ingresada por el usuario:
  - Cabeceras HTTP de seguridad
  - Métodos HTTP habilitados (detecta métodos inseguros)
  - Exposición de información sensible en el contenido de la página

Genera un reporte en TXT y otro en PDF con diseño de tabla consistente
con el resto de módulos del proyecto (Autenticación, SSL).

Uso:
    python scanner.py
"""

import os
import requests
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime
from textwrap import wrap


# =============================================================================
# CONFIGURACIÓN INICIAL
# =============================================================================

# Directorio donde se guardan todos los reportes generados
CARPETA_REPORTES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")

# Cabeceras HTTP que se consideran buenas prácticas de seguridad
HEADERS_SEGURIDAD = [
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Strict-Transport-Security",
]

# Palabras clave que, si aparecen en el HTML, pueden indicar exposición de datos
PALABRAS_SENSIBLES = ["password", "token", "apikey", "secret", "admin"]

# Métodos HTTP que representan un riesgo si están habilitados públicamente
METODOS_INSEGUROS = ["PUT", "DELETE", "TRACE"]

# Colores de fondo para la fila de estado en el PDF (igual que los otros módulos)
COLORES_ESTADO = {
    "SEGURO":      (220, 245, 220),  # verde claro
    "ADVERTENCIA": (255, 243, 205),  # amarillo claro
    "RIESGO":      (255, 213, 213),  # rojo claro
}


# =============================================================================
# UTILIDADES
# =============================================================================

def safe(texto):
    """
    Convierte texto a latin-1 de forma segura para que FPDF no falle
    al encontrar caracteres fuera de ese rango (tildes, emojis, etc.).

    Args:
        texto: Cualquier valor convertible a string.

    Returns:
        str: El texto codificado en latin-1 con caracteres problemáticos
             reemplazados por '?'.
    """
    return str(texto).encode("latin-1", "replace").decode("latin-1")


def calcular_estado_general(cabeceras, metodos, sensibles):
    """
    Determina el nivel de alerta general de la auditoría basándose
    en los resultados de las tres categorías evaluadas.

    Lógica:
      - Si hay métodos inseguros o información sensible expuesta → RIESGO
      - Si faltan cabeceras de seguridad → ADVERTENCIA
      - Si todo está correcto → SEGURO

    Args:
        cabeceras (list[str]): Resultados del análisis de cabeceras.
        metodos   (list[str]): Resultados del análisis de métodos HTTP.
        sensibles (list[str]): Resultados del análisis de info sensible.

    Returns:
        str: "SEGURO", "ADVERTENCIA" o "RIESGO".
    """
    todos = cabeceras + metodos + sensibles
    if any("[RIESGO]" in r or "[ALERTA]" in r for r in todos):
        return "RIESGO"
    if any("[FALTA]" in r for r in todos):
        return "ADVERTENCIA"
    return "SEGURO"


# =============================================================================
# FUNCIONES DE AUDITORÍA
# =============================================================================

def verificar_cabeceras(url):
    """
    Verifica si la URL tiene las cabeceras HTTP de seguridad recomendadas.

    Comprueba la presencia de: Content-Security-Policy, X-Frame-Options,
    X-Content-Type-Options y Strict-Transport-Security.

    Args:
        url (str): URL completa a analizar.

    Returns:
        list[str]: Lista con el resultado de cada cabecera,
                   marcada como [OK] si está presente o [FALTA] si no.
    """
    resultado = []
    try:
        response = requests.get(url, timeout=10)
        for header in HEADERS_SEGURIDAD:
            if header in response.headers:
                resultado.append(f"[OK] {header}")
            else:
                resultado.append(f"[FALTA] {header}")
    except Exception as e:
        resultado.append(f"Error al conectar: {e}")
    return resultado


def verificar_metodos(url):
    """
    Detecta qué métodos HTTP están habilitados en el servidor
    y marca como riesgo los que no deberían estar expuestos públicamente.

    Utiliza la solicitud OPTIONS para obtener el encabezado 'Allow'
    y busca métodos peligrosos: PUT, DELETE, TRACE.

    Args:
        url (str): URL completa a analizar.

    Returns:
        list[str]: Lista con los métodos encontrados y alertas de riesgo
                   para los métodos inseguros detectados.
    """
    resultado = []
    try:
        response = requests.options(url, timeout=10)
        allow = response.headers.get("Allow", "No disponible")
        resultado.append(f"Metodos encontrados: {allow}")
        for metodo in METODOS_INSEGUROS:
            if metodo in allow:
                resultado.append(f"[RIESGO] Metodo habilitado: {metodo}")
    except Exception as e:
        resultado.append(f"Error al conectar: {e}")
    return resultado


def buscar_info_sensible(url):
    """
    Busca palabras clave asociadas a información sensible en el contenido
    HTML de la página (texto visible y código fuente).

    Las palabras que busca son: password, token, apikey, secret, admin.
    La búsqueda no distingue mayúsculas de minúsculas.

    Args:
        url (str): URL completa a analizar.

    Returns:
        list[str]: Lista de alertas por cada palabra sensible encontrada,
                   o mensaje vacío si no se detecta nada.
    """
    resultado = []
    try:
        response = requests.get(url, timeout=10)
        contenido = response.text.lower()
        encontrado = False
        for palabra in PALABRAS_SENSIBLES:
            if palabra in contenido:
                resultado.append(f"[ALERTA] Posible informacion sensible: '{palabra}'")
                encontrado = True
        if not encontrado:
            resultado.append("[OK] No se detecto informacion sensible expuesta")
    except Exception as e:
        resultado.append(f"Error al conectar: {e}")
    return resultado


# =============================================================================
# GENERACIÓN DE REPORTES
# =============================================================================

def generar_reporte_txt(url, fecha, cabeceras, metodos, sensibles, estado):
    """
    Genera un reporte de auditoría en formato TXT y lo guarda en la
    carpeta 'reports/'.

    El archivo se nombra 'reporte_scanner.txt' y se sobreescribe
    cada vez que se ejecuta el script.

    Args:
        url       (str):       URL auditada.
        fecha     (str):       Fecha y hora de la auditoría formateada.
        cabeceras (list[str]): Resultados del análisis de cabeceras.
        metodos   (list[str]): Resultados del análisis de métodos.
        sensibles (list[str]): Resultados del análisis de info sensible.
        estado    (str):       Estado general: "SEGURO", "ADVERTENCIA" o "RIESGO".
    """
    ruta = os.path.join(CARPETA_REPORTES, "reporte_scanner.txt")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("==================================================\n")
        f.write("       REPORTE DE AUDITORIA WEB BASICA            \n")
        f.write(f"       Generado el: {fecha}\n")
        f.write("==================================================\n\n")
        f.write(f"Sitio auditado : {url}\n")
        f.write(f"Estado general : {estado}\n\n")

        f.write("CABECERAS HTTP DE SEGURIDAD\n")
        f.write("-" * 40 + "\n")
        for item in cabeceras:
            f.write(item + "\n")
        f.write("\n")

        f.write("METODOS HTTP HABILITADOS\n")
        f.write("-" * 40 + "\n")
        for item in metodos:
            f.write(item + "\n")
        f.write("\n")

        f.write("INFORMACION SENSIBLE EXPUESTA\n")
        f.write("-" * 40 + "\n")
        for item in sensibles:
            f.write(item + "\n")
        f.write("\n")
        f.write("==================================================\n")
        f.write("Fin del reporte\n")

    print("Reporte TXT generado: " + ruta)


def generar_reporte_pdf(url, fecha, cabeceras, metodos, sensibles, estado):
    """
    Genera un reporte de auditoría en formato PDF con diseño de tabla
    consistente con los módulos de Autenticación y SSL del proyecto.

    Incluye:
      - Encabezado con título y subtítulo (fecha y módulo).
      - Tabla de resumen general (URL, fecha, estado con color).
      - Tabla de resultados por categoría (cabeceras, métodos, info sensible).

    El archivo se guarda como 'reporte_scanner.pdf' en la carpeta 'reports/'.

    Args:
        url       (str):       URL auditada.
        fecha     (str):       Fecha y hora de la auditoría formateada.
        cabeceras (list[str]): Resultados del análisis de cabeceras.
        metodos   (list[str]): Resultados del análisis de métodos.
        sensibles (list[str]): Resultados del análisis de info sensible.
        estado    (str):       Estado general: "SEGURO", "ADVERTENCIA" o "RIESGO".
    """
    ruta = os.path.join(CARPETA_REPORTES, "reporte_scanner.pdf")
    fondo_rgb = COLORES_ESTADO.get(estado, (255, 255, 255))

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # --- Encabezado principal ---
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Reporte de Auditoria Web Basica",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 8, "Fecha de emision: " + fecha + " | Modulo de Vulnerabilidades",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(8)

    # --- Tabla resumen general ---
    tabla_resumen = [
        ("Campo",          "Valor"),
        ("Sitio auditado", url),
        ("Fecha y hora",   fecha),
        ("Estado General", estado),
    ]

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, "Resumen de la Auditoria",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True, border="B")
    pdf.ln(2)

    for i, fila in enumerate(tabla_resumen):
        if i == 0:
            # Fila de encabezado de tabla — fondo gris oscuro
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(70, 7, safe(fila[0]), border=1, fill=True)
            pdf.cell(120, 7, safe(fila[1]), border=1, fill=True,
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(70, 7, safe(fila[0]), border=1)
            pdf.set_font("Helvetica", "", 9)
            if fila[0] == "Estado General":
                # Fila de estado con color según severidad
                pdf.set_fill_color(*fondo_rgb)
                pdf.set_font("Helvetica", "B", 9)
                pdf.cell(120, 7, safe(fila[1]), border=1, fill=True,
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            else:
                pdf.cell(120, 7, safe(fila[1]), border=1,
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(6)

    # --- Función auxiliar para secciones de detalle ---
    def escribir_seccion_tabla(titulo, items):
        """
        Escribe una sección de detalle con encabezado de sección y
        los ítems como filas de tabla de una sola columna.

        Args:
            titulo (str):       Título de la sección (ej. "Cabeceras HTTP").
            items (list[str]):  Lista de resultados a mostrar.
        """
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 8, titulo,
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True, border="B")
        pdf.ln(2)

        # Encabezado de tabla
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(200, 200, 200)
        pdf.cell(190, 7, "Resultado", border=1, fill=True,
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_font("Helvetica", "", 9)
        if not items:
            pdf.cell(190, 7, "(sin resultados)", border=1,
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            for item in items:
                # Texto largo se parte en líneas de 85 caracteres
                lineas = wrap(item, 85) or [""]
                for linea in lineas:
                    pdf.cell(190, 7, safe(linea), border=1,
                             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.ln(4)

    # --- Secciones de detalle ---
    escribir_seccion_tabla("Cabeceras HTTP de Seguridad", cabeceras)
    escribir_seccion_tabla("Metodos HTTP Habilitados",    metodos)
    escribir_seccion_tabla("Informacion Sensible Expuesta", sensibles)

    pdf.output(ruta)
    print("Reporte PDF generado: " + ruta)


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

def main():
    """
    Función principal del script.

    Flujo:
      1. Solicita al usuario la URL a auditar.
      2. Normaliza la URL (agrega https:// si no tiene esquema).
      3. Ejecuta las tres verificaciones de seguridad.
      4. Calcula el estado general.
      5. Genera el reporte TXT y el reporte PDF en la carpeta 'reports/'.
    """
    print("=" * 50)
    print("  Auditor de Vulnerabilidades Web")
    print("=" * 50)

    # Entrada del usuario
    url = input("Ingrese URL a evaluar: ").strip()
    if not url:
        print("Error: debe ingresar una URL.")
        return

    # Normalizar URL — agregar esquema si falta
    if not url.startswith("http"):
        url = "https://" + url

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nAnalizando: {url}\n")

    # Ejecutar auditorías
    print("Verificando cabeceras HTTP...")
    cabeceras = verificar_cabeceras(url)

    print("Verificando metodos HTTP...")
    metodos   = verificar_metodos(url)

    print("Buscando informacion sensible...")
    sensibles = buscar_info_sensible(url)

    # Calcular estado general
    estado = calcular_estado_general(cabeceras, metodos, sensibles)
    print(f"\nEstado general: {estado}")

    # Crear carpeta de reportes si no existe
    os.makedirs(CARPETA_REPORTES, exist_ok=True)

    # Generar reportes
    print("\nGenerando reportes...")
    generar_reporte_txt(url, fecha, cabeceras, metodos, sensibles, estado)
    generar_reporte_pdf(url, fecha, cabeceras, metodos, sensibles, estado)

    print("\nListo. Reportes guardados en: " + CARPETA_REPORTES)


if __name__ == "__main__":
    main()