# =====================================================================
# PROYECTO: SCANNER DE VULNERABILIDADES "JUNIOR"
# -----------------------------------------------------------------
# Objetivo: crear un script que analice la seguridad de otros scripts
# de Python (o de una red local), combinando:
#   - Analisis estatico de codigo con Bandit
#   - Busqueda de fugas de credenciales (API keys, contraseñas, etc.)
#   - Validador de integridad de archivos (hashes SHA-256)
#   - Demostracion practica de un ataque de inyeccion de comandos
#     y su respectiva defensa (mala practica vs. buena practica)
#
# Cada modulo genera su propio reporte en PDF con diseño profesional,
# y ademas puede generarse un reporte ejecutivo consolidado con el
# resumen de todos los resultados obtenidos.
# =====================================================================

import os
import re
import json
import hashlib
import platform
import subprocess
import bleach
from datetime import datetime
from fpdf import FPDF

# =====================================================================
# BASE DE DATOS LIMPIA (referencia para el validador de integridad)
# =====================================================================
# Registra los hashes originales de los archivos que se desean vigilar.
# Se pueden agregar mas archivos manualmente con su ruta como clave.
BASE_DATOS_LIMPIA = {}
ARCHIVO_HASHES = "hashes.json"

# =====================================================================
# DISEÑO VISUAL DE LOS REPORTES (paleta de colores y clase base PDF)
# =====================================================================

COLOR_BARRA          = (30, 60, 90)      # Azul corporativo (encabezado)
COLOR_TEXTO_BARRA     = (255, 255, 255)
COLOR_HEADER_TABLA    = (222, 226, 230)  # Gris azulado (encabezados de tabla)
COLOR_OK              = (211, 240, 216)  # Verde suave (todo correcto)
COLOR_ALERTA_ALTA     = (248, 210, 210)  # Rojo suave (severidad alta / hallazgo)
COLOR_ALERTA_MEDIA    = (252, 228, 197)  # Naranja suave (severidad media)
COLOR_ALERTA_BAJA     = (255, 247, 205)  # Amarillo suave (severidad baja)
COLOR_PIE_PAGINA      = (120, 120, 120)


class ReportePDF(FPDF):
    """
    Clase base para todos los reportes del scanner. Define un encabezado
    y un pie de página consistentes (marca, título del módulo y numeración
    de páginas), para que todos los PDF generados compartan una misma
    identidad visual profesional.
    """

    def __init__(self, titulo_modulo):
        super().__init__()
        self.titulo_modulo = titulo_modulo
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        # Barra superior de color corporativo
        self.set_fill_color(*COLOR_BARRA)
        self.rect(0, 0, 210, 24, style="F")

        self.set_text_color(*COLOR_TEXTO_BARRA)
        self.set_font("Helvetica", "B", 15)
        self.set_xy(12, 6)
        self.cell(0, 8, "Scanner de Vulnerabilidades Junior")

        self.set_font("Helvetica", "", 10)
        self.set_xy(12, 15)
        self.cell(0, 6, self.titulo_modulo)

        self.set_text_color(0, 0, 0)
        self.set_y(30)

    def footer(self):
        self.set_y(-15)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*COLOR_PIE_PAGINA)
        marca_tiempo = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cell(0, 10, f"Generado el {marca_tiempo}    |    Pagina {self.page_no()}", align="C")


def _carpeta_reportes():
    """Crea (si no existe) y devuelve la ruta de la carpeta 'reportes'."""
    carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reportes")
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


def _timestamp_archivo():
    """Marca de tiempo apta para nombres de archivo (evita sobrescribir reportes previos)."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# =====================================================================
# MODULO 1: ANALISIS ESTATICO DE CODIGO (BANDIT)
# =====================================================================

def ejecutar_bandit(ruta_carpeta):
    """
    Invoca a Bandit de manera interna usando subprocess.
    Analiza la carpeta indicada, exporta los fallos en formato JSON
    y genera un reporte PDF individual con el detalle de cada hallazgo.
    """
    print(f"\n[+] Iniciando análisis estático (SAST) en: '{ruta_carpeta}'...")

    if not os.path.exists(ruta_carpeta):
        print("[-] Error: La ruta especificada no existe en el sistema.")
        return

    archivo_reporte = "reporte_seguridad.json"

    # Comando estructurado de forma segura (arreglo de argumentos, SIN shell=True)
    comando = ["bandit", "-r", ruta_carpeta, "-f", "json", "-o", archivo_reporte]

    try:
        subprocess.run(comando, check=False)
        print("[✅] ¡Escaneo de Bandit finalizado con éxito!")

        if os.path.exists(archivo_reporte):
            with open(archivo_reporte, "r", encoding="utf-8") as f:
                datos = json.load(f)
            fallos = datos.get("results", [])
            print(f"[!] Diagnóstico: Se detectaron {len(fallos)} vulnerabilidades en el código fuente.")
            print(f"👉 Reporte JSON guardado en: '{archivo_reporte}'")
            generar_pdf_bandit(fallos)

    except FileNotFoundError:
        print("[❌] Error crítico: El ejecutable 'bandit' no fue encontrado. Instálalo con 'pip install bandit'.")


def generar_pdf_bandit(fallos):
    """Genera el reporte PDF individual del análisis estático de Bandit."""
    nombre = os.path.join(_carpeta_reportes(), f"bandit_{_timestamp_archivo()}.pdf")
    pdf = ReportePDF("Analisis Estatico de Codigo (Bandit)")
    pdf.add_page()

    total = len(fallos)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(*(COLOR_OK if total == 0 else COLOR_ALERTA_ALTA))
    pdf.cell(0, 10, f"Total de vulnerabilidades detectadas: {total}", border=1, fill=True, ln=True)
    pdf.ln(4)

    if fallos:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(*COLOR_HEADER_TABLA)
        pdf.cell(22, 7, "Severidad", border=1, fill=True)
        pdf.cell(22, 7, "Test ID", border=1, fill=True)
        pdf.cell(55, 7, "Archivo", border=1, fill=True)
        pdf.cell(16, 7, "Linea", border=1, fill=True)
        pdf.cell(75, 7, "Descripcion", border=1, fill=True, ln=True)

        colores_severidad = {
            "HIGH": COLOR_ALERTA_ALTA,
            "MEDIUM": COLOR_ALERTA_MEDIA,
            "LOW": COLOR_ALERTA_BAJA,
        }
        pdf.set_font("Helvetica", "", 8)
        for fallo in fallos:
            severidad = fallo.get("issue_severity", "N/A")
            pdf.set_fill_color(*colores_severidad.get(severidad, (255, 255, 255)))
            pdf.cell(22, 6, severidad, border=1, fill=True)
            pdf.cell(22, 6, fallo.get("test_id", ""), border=1)
            archivo_corto = os.path.basename(fallo.get("filename", ""))[:32]
            pdf.cell(55, 6, archivo_corto, border=1)
            pdf.cell(16, 6, str(fallo.get("line_number", "")), border=1)
            texto = fallo.get("issue_text", "")
            texto_corto = (texto[:60] + "...") if len(texto) > 60 else texto
            pdf.cell(75, 6, texto_corto, border=1, ln=True)
    else:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, "No se encontraron vulnerabilidades. El codigo analizado esta limpio.", ln=True)

    pdf.output(nombre)
    print(f"👉 Reporte PDF generado: {nombre}")
    return nombre


# =====================================================================
# MODULO 2: BUSQUEDA DE FUGAS DE CREDENCIALES (LEAKS)
# =====================================================================

# Diccionario de patrones (regex) para detectar credenciales hardcodeadas.
PATRONES_LEAKS = {

    # AWS
    "AWS Access Key ID":
        r"AKIA[0-9A-Z]{16}",

    "AWS Secret Access Key":
        r"(?i)aws_secret_access_key\s*[:=]\s*['\"][A-Za-z0-9/+=]{40}['\"]",

    # Google
    "Google API Key":
        r"AIza[0-9A-Za-z\-_]{35}",

    # GitHub
    "GitHub Token":
        r"gh[pousr]_[A-Za-z0-9]{36}",

    # Slack
    "Slack Token":
        r"xox[baprs]-[A-Za-z0-9\-]{10,48}",

    # API Key genérica
    "Generic API Key":
        r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"][^'\"]{8,}['\"]",

    # Secret o Token
    "Generic Secret":
        r"(?i)(secret|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]",

    # Password
    "Password Hardcodeada":
        r"(?i)(password|passwd|pass|pwd|contrase[ñn]a)\s*[:=]\s*['\"][^'\"]{4,}['\"]",

    # Llaves privadas
    "Private Key":
        r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",

    # MongoDB
    "MongoDB Connection":
        r"mongodb(\+srv)?:\/\/[^:\s]+:[^@\s]+@[^\s'\"]+",

    # PostgreSQL
    "PostgreSQL Connection":
        r"postgres:\/\/[^:\s]+:[^@\s]+@[^\s'\"]+",

    # MySQL
    "MySQL Connection":
        r"mysql:\/\/[^:\s]+:[^@\s]+@[^\s'\"]+",
}

# Extensiones de archivo que tiene sentido escanear en busca de texto/código
EXTENSIONES_VALIDAS = (
    ".py", ".js", ".ts", ".java", ".env", ".txt", ".json",
    ".yml", ".yaml", ".xml", ".ini", ".cfg", ".conf", ".sh"
)


def escanear_archivo_en_busca_de_leaks(ruta):
    """
    Abre un archivo de texto y aplica cada patrón de PATRONES_LEAKS
    para detectar posibles credenciales expuestas. Devuelve una lista
    de coincidencias encontradas (tipo, línea y fragmento sanitizado).
    """
    hallazgos = []

    with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
        for num_linea, linea in enumerate(f, 1):
            for tipo_patron, regex in PATRONES_LEAKS.items():
                if re.search(regex, linea):
                    hallazgos.append({
                        "archivo": ruta,
                        "linea": num_linea,
                        "tipo": tipo_patron,
                        "fragmento": linea.strip()
                    })

    return hallazgos
   


def buscador_de_leaks(ruta_carpeta):
    """
    Recorre recursivamente la carpeta indicada buscando fugas de
    credenciales (API keys, contraseñas, tokens, etc.) en archivos de
    texto/código, genera un reporte JSON y un reporte PDF individual.
    """
    print(f"\n[+] Iniciando búsqueda de fugas de credenciales (leaks) en: '{ruta_carpeta}'...")

    if not os.path.exists(ruta_carpeta):
        print("[-] Error: La ruta especificada no existe en el sistema.")
        return

    todos_los_hallazgos = []

    if os.path.isfile(ruta_carpeta):
        # El usuario indicó un archivo individual en vez de una carpeta.
        if ruta_carpeta.lower().endswith(EXTENSIONES_VALIDAS):
            todos_los_hallazgos.extend(escanear_archivo_en_busca_de_leaks(ruta_carpeta))
        else:
            print("[-] Advertencia: la extensión del archivo no está entre las analizadas.")
    else:
        for carpeta_actual, _subcarpetas, archivos in os.walk(ruta_carpeta):
            for nombre_archivo in archivos:
                if nombre_archivo.lower().endswith(EXTENSIONES_VALIDAS):
                    ruta_completa = os.path.join(carpeta_actual, nombre_archivo)
                    todos_los_hallazgos.extend(escanear_archivo_en_busca_de_leaks(ruta_completa))

    if todos_los_hallazgos:
        print(f"[⚠️] ¡Se encontraron {len(todos_los_hallazgos)} posibles fugas de credenciales!\n")
        for h in todos_los_hallazgos:
            print(f"   -> [{h['tipo']}] en '{h['archivo']}' (línea {h['linea']}): {h['fragmento']}")
    else:
        print("[✅] No se detectaron credenciales hardcodeadas con los patrones conocidos.")

    archivo_reporte = "reporte_leaks.json"
    with open(archivo_reporte, "w", encoding="utf-8") as f:
        json.dump(
            {"total_hallazgos": len(todos_los_hallazgos), "hallazgos": todos_los_hallazgos},
            f, indent=2, ensure_ascii=False
        )
    print(f"👉 Reporte JSON guardado en: '{archivo_reporte}'")

    generar_pdf_leaks(todos_los_hallazgos)


def generar_pdf_leaks(hallazgos):
    """Genera el reporte PDF individual de la búsqueda de fugas de credenciales."""
    nombre = os.path.join(_carpeta_reportes(), f"leaks_{_timestamp_archivo()}.pdf")
    pdf = ReportePDF("Busqueda de Fugas de Credenciales (Leaks)")
    pdf.add_page()

    total = len(hallazgos)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(*(COLOR_OK if total == 0 else COLOR_ALERTA_ALTA))
    pdf.cell(0, 10, f"Total de credenciales expuestas encontradas: {total}", border=1, fill=True, ln=True)
    pdf.ln(4)

    if hallazgos:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(*COLOR_HEADER_TABLA)
        pdf.cell(45, 7, "Tipo", border=1, fill=True)
        pdf.cell(65, 7, "Archivo", border=1, fill=True)
        pdf.cell(16, 7, "Linea", border=1, fill=True)
        pdf.cell(64, 7, "Fragmento detectado", border=1, fill=True, ln=True)

        pdf.set_font("Helvetica", "", 8)
        for h in hallazgos:
            pdf.set_fill_color(*COLOR_ALERTA_ALTA)
            pdf.cell(45, 6, h["tipo"][:28], border=1, fill=True)
            pdf.cell(65, 6, os.path.basename(h["archivo"])[:38], border=1)
            pdf.cell(16, 6, str(h["linea"]), border=1)
            fragmento_corto = h["fragmento"][:38] + ("..." if len(h["fragmento"]) > 38 else "")
            pdf.cell(64, 6, fragmento_corto, border=1, ln=True)
    else:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, "No se detectaron credenciales hardcodeadas con los patrones conocidos.", ln=True)

    pdf.output(nombre)
    print(f"👉 Reporte PDF generado: {nombre}")
    return nombre


# =====================================================================
# MODULO 3: VALIDADOR DE INTEGRIDAD DE ARCHIVOS (SHA-256)
# =====================================================================

def calcular_hash_sha256(ruta_archivo):
    """Calcula la huella digital SHA-256 de un archivo por bloques de memoria."""
    sha256_hash = hashlib.sha256()
    try:
        with open(ruta_archivo, "rb") as f:
            for bloque in iter(lambda: f.read(4096), b""):
                sha256_hash.update(bloque)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None




def crear_base_integridad():
    """Crea o regenera la base de hashes limpia."""
    archivos = ["proyecto2.py"]
    hashes = {}
    for archivo in archivos:
        h = calcular_hash_sha256(archivo)
        if h:
            hashes[archivo] = h
    with open(ARCHIVO_HASHES,"w",encoding="utf-8") as f:
        json.dump(hashes,f,indent=4)
    print("[✅] Base de hashes creada correctamente.")

def verificar_integridad():
    """
    Compara el estado actual de los archivos registrados en
    BASE_DATOS_LIMPIA contra sus hashes de referencia, muestra el
    resultado por consola y genera un reporte PDF individual.
    """
    print("\n=======================================================")
    print("      VERIFICADOR DE INTEGRIDAD DEL SISTEMA (SHA-256)   ")
    print("=======================================================")

    if not os.path.exists(ARCHIVO_HASHES):
        print("[ℹ️] No existe una base de hashes. Se creará automáticamente.")
        crear_base_integridad()

    with open(ARCHIVO_HASHES,"r",encoding="utf-8") as f:
        base=json.load(f)

    resultados=[]
    for archivo, hash_correcto in base.items():
        hash_actual=calcular_hash_sha256(archivo)
        if hash_actual is None:
            estado="Eliminado"
            print(f"[❌] ALERTA CRÍTICA: ¡El archivo '{archivo}' ha sido removido o destruido!")
        elif hash_actual==hash_correcto:
            estado="Integro"
            print(f"[✅] Archivo '{archivo}': Estado Íntegro (Sin modificaciones detectadas).")
        else:
            estado="Alterado"
            print(f"[⚠️] ALERTA DE SEGURIDAD: ¡El archivo '{archivo}' sufrió alteraciones no autorizadas!")
        resultados.append({"archivo":archivo,"estado":estado,"hash_actual":hash_actual})

    generar_pdf_integridad(resultados)


def generar_pdf_integridad(resultados):
    """Genera el reporte PDF individual del validador de integridad."""
    nombre = os.path.join(_carpeta_reportes(), f"integridad_{_timestamp_archivo()}.pdf")
    pdf = ReportePDF("Validador de Integridad de Archivos (SHA-256)")
    pdf.add_page()

    hay_alteraciones = any(r["estado"] != "Integro" for r in resultados)
    estado_general = "Se detectaron alteraciones en uno o mas archivos" if hay_alteraciones else "Todos los archivos estan integros"

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(*(COLOR_ALERTA_ALTA if hay_alteraciones else COLOR_OK))
    pdf.cell(0, 10, estado_general, border=1, fill=True, ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(*COLOR_HEADER_TABLA)
    pdf.cell(55, 7, "Archivo", border=1, fill=True)
    pdf.cell(30, 7, "Estado", border=1, fill=True)
    pdf.cell(105, 7, "Hash SHA-256 actual", border=1, fill=True, ln=True)

    pdf.set_font("Helvetica", "", 8)
    for r in resultados:
        color = COLOR_OK if r["estado"] == "Integro" else COLOR_ALERTA_ALTA
        pdf.cell(55, 6, r["archivo"], border=1)
        pdf.set_fill_color(*color)
        pdf.cell(30, 6, r["estado"], border=1, fill=True)
        pdf.cell(105, 6, r["hash_actual"] or "N/A", border=1, ln=True)

    pdf.output(nombre)
    print(f"👉 Reporte PDF generado: {nombre}")
    return nombre


# =====================================================================
# MODULO 4: DEMOSTRACION DE ATAQUE Y DEFENSA (INYECCION DE COMANDOS)
# =====================================================================

def demostrar_ataque_defensa():
    """
    Muestra los peligros de la inyección de comandos por malas prácticas
    en subprocess, y cómo solucionarlo aplicando sanitización con bleach
    y estructuras rígidas (lista de argumentos + shell=False).
    Es multiplataforma: detecta el sistema operativo (Windows, Linux o
    Mac) y arma los comandos de forma que funcionen igual en cualquiera
    de los tres. Al finalizar, genera un reporte PDF documentando ambos
    escenarios.
    """
    print("\n=======================================================")
    print("        LABORATORIO SIMULADO: ATAQUE Y DEFENSA          ")
    print("=======================================================")

    # Detectamos el sistema operativo para armar comandos válidos en cada uno.
    es_windows = platform.system() == "Windows"

    # El separador de comandos para shell=True depende de la terminal:
    # - cmd.exe (Windows) usa '&' o '&&', NO interpreta ';' como separador.
    # - bash/sh (Linux/Mac) sí usa ';' como separador de comandos.
    separador_inyeccion = "&" if es_windows else ";"
    payload_atacante = f"127.0.0.1 {separador_inyeccion} echo 'PIRATERÍA: Acceso root concedido'"
    print(f"[-] Entrada maliciosa del usuario: {payload_atacante}")

    # -----------------------------------------------------------------
    # PARTE 1: EL ATAQUE (Mala práctica tradicional)
    # -----------------------------------------------------------------
    print("\n[!] Escenario Vulnerable (Uso inseguro de shell=True):")
    print("-> Ejecutando en consola sin filtros...")

    # Al concatenar texto crudo y usar shell=True, el sistema ejecuta la inyección.
    # NOTA: Bandit alertará sobre esta línea exacta con criticidad ALTA (B602).
    comando_vulnerable = f"echo Evaluando destino: {payload_atacante}"
    subprocess.run(comando_vulnerable, shell=True)

    # -----------------------------------------------------------------
    # PARTE 2: LA DEFENSA (Buenas prácticas aplicadas)
    # -----------------------------------------------------------------
    print("\n[+] Escenario Seguro (Defensa Activa implementada):")

    # LINEAMIENTO 1: Sanitización de datos de entrada con Bleach
    entrada_limpia = bleach.clean(payload_atacante)

    # LINEAMIENTO 2: Romper la inyección usando una LISTA de argumentos rígida con shell=False
    if es_windows:
        comando_blindado = ["cmd", "/c", "echo", f"Evaluando destino de manera segura: {entrada_limpia}"]
    else:
        comando_blindado = ["echo", f"Evaluando destino de manera segura: {entrada_limpia}"]

    subprocess.run(comando_blindado, shell=False)
    print("[✅] Conclusión: El ataque fue mitigado. El comando hostil se neutralizó como texto plano.")

    generar_pdf_ataque_defensa(payload_atacante, comando_vulnerable, comando_blindado, separador_inyeccion)


def generar_pdf_ataque_defensa(payload, comando_vulnerable, comando_seguro, separador_inyeccion=";"):
    """Genera el reporte PDF individual del laboratorio de ataque y defensa."""
    nombre = os.path.join(_carpeta_reportes(), f"ataque_defensa_{_timestamp_archivo()}.pdf")
    pdf = ReportePDF("Laboratorio de Ataque y Defensa (Inyeccion de Comandos)")
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(*COLOR_HEADER_TABLA)
    pdf.cell(0, 8, "Entrada utilizada en la simulacion", border=1, fill=True, ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 6, payload, border=1)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(*COLOR_ALERTA_ALTA)
    pdf.cell(0, 8, "Escenario vulnerable (shell=True)", border=1, fill=True, ln=True)
    pdf.set_font("Helvetica", "", 9)
    texto_vulnerable = (
        f"Comando ejecutado: {comando_vulnerable}\n\n"
        f"Riesgo: al usar shell=True con texto sin validar, el caracter '{separador_inyeccion}' "
        "permite inyectar comandos adicionales que el sistema ejecuta sin "
        "ninguna restriccion. Bandit detecta este patron con criticidad ALTA (B602)."
    )
    pdf.multi_cell(0, 6, texto_vulnerable, border=1)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(*COLOR_OK)
    pdf.cell(0, 8, "Escenario seguro (defensa aplicada)", border=1, fill=True, ln=True)
    pdf.set_font("Helvetica", "", 9)
    texto_seguro = (
        f"Comando ejecutado: {comando_seguro}\n\n"
        "Mitigacion: se sanitiza la entrada con la libreria bleach y se "
        "reemplaza la cadena de texto por una lista rigida de argumentos "
        "con shell=False, lo que neutraliza cualquier intento de inyeccion "
        "de comandos, imprimiendo el contenido hostil como texto plano."
    )
    pdf.multi_cell(0, 6, texto_seguro, border=1)

    pdf.output(nombre)
    print(f"👉 Reporte PDF generado: {nombre}")
    return nombre


# =====================================================================
# REPORTE EJECUTIVO CONSOLIDADO
# =====================================================================

def _leer_conteo_bandit():
    """Lee 'reporte_seguridad.json' (si existe) y devuelve (ejecutado, cantidad_fallos)."""
    archivo = "reporte_seguridad.json"
    if not os.path.exists(archivo):
        return False, 0
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
        return True, len(datos.get("results", []))
    except (json.JSONDecodeError, OSError):
        return False, 0


def _leer_conteo_leaks():
    """Lee 'reporte_leaks.json' (si existe) y devuelve (ejecutado, cantidad_hallazgos)."""
    archivo = "reporte_leaks.json"
    if not os.path.exists(archivo):
        return False, 0
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
        return True, datos.get("total_hallazgos", 0)
    except (json.JSONDecodeError, OSError):
        return False, 0


def _evaluar_integridad_actual():
    """Recalcula en caliente el estado de integridad, sin imprimir en consola."""
    hash_actual_principal = calcular_hash_sha256("proyecto2.py")
    if hash_actual_principal:
        BASE_DATOS_LIMPIA["proyecto2.py"] = hash_actual_principal

    for archivo, hash_correcto in BASE_DATOS_LIMPIA.items():
        hash_actual = calcular_hash_sha256(archivo)
        if hash_actual is None or hash_actual != hash_correcto:
            return False
    return True


def generar_reporte_consolidado():
    """
    Genera un reporte PDF ejecutivo que resume el resultado de los tres
    módulos de análisis (Bandit, Leaks e Integridad) en una sola vista.
    Util para presentar un resumen general despues de correr los demas
    modulos del scanner.
    """
    print("\n[+] Generando reporte ejecutivo consolidado...")

    bandit_ejecutado, fallos_bandit = _leer_conteo_bandit()
    leaks_ejecutado, hallazgos_leaks = _leer_conteo_leaks()
    integridad_ok = _evaluar_integridad_actual()

    nombre = os.path.join(_carpeta_reportes(), f"consolidado_{_timestamp_archivo()}.pdf")
    pdf = ReportePDF("Reporte Ejecutivo Consolidado")
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(*COLOR_HEADER_TABLA)
    pdf.cell(90, 7, "Modulo", border=1, fill=True)
    pdf.cell(40, 7, "Ejecutado", border=1, fill=True)
    pdf.cell(60, 7, "Resultado", border=1, fill=True, ln=True)

    filas = [
        ("Analisis estatico de codigo (Bandit)", bandit_ejecutado, fallos_bandit),
        ("Busqueda de credenciales expuestas (Leaks)", leaks_ejecutado, hallazgos_leaks),
    ]

    pdf.set_font("Helvetica", "", 9)
    for nombre_modulo, ejecutado, cantidad in filas:
        pdf.cell(90, 7, nombre_modulo, border=1)
        pdf.cell(40, 7, "Si" if ejecutado else "No ejecutado", border=1)
        color = COLOR_OK if (not ejecutado or cantidad == 0) else COLOR_ALERTA_ALTA
        pdf.set_fill_color(*color)
        texto_resultado = f"{cantidad} hallazgo(s)" if ejecutado else "N/A"
        pdf.cell(60, 7, texto_resultado, border=1, fill=True, ln=True)

    pdf.cell(90, 7, "Integridad de archivos", border=1)
    pdf.cell(40, 7, "Si", border=1)
    pdf.set_fill_color(*(COLOR_OK if integridad_ok else COLOR_ALERTA_ALTA))
    pdf.cell(60, 7, "Integro" if integridad_ok else "Alterado", border=1, fill=True, ln=True)

    pdf.ln(8)

    hay_problemas = (fallos_bandit > 0) or (hallazgos_leaks > 0) or (not integridad_ok)
    estado_general = "AUDITORIA CON HALLAZGOS" if hay_problemas else "AUDITORIA LIMPIA"
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(*(COLOR_ALERTA_ALTA if hay_problemas else COLOR_OK))
    pdf.cell(0, 10, estado_general, border=1, fill=True, ln=True, align="C")

    pdf.output(nombre)
    print(f"[✅] Reporte ejecutivo generado: {nombre}")
    return nombre


# =====================================================================
# MENU PRINCIPAL
# =====================================================================

def menu_principal():
    while True:
        print("\n=======================================================")
        print("          HERRAMIENTA DE CIBERSEGURIDAD                ")
        print("=======================================================")
        print("1. Analizar código local de forma automática (Bandit)")
        print("2. Buscar fugas de credenciales y API Keys (Leaks)")
        print("3. Ejecutar validador de integridad de archivos")
        print("4. Demostración de ataque y defensa (mala práctica)")
        print("5. Generar reporte ejecutivo consolidado")
        print("6. Salir del programa")
        print("=======================================================")

        opcion = input("Seleccione una opción (1-6): ").strip()

        if opcion == "1":
            ruta = input("[?] Ingrese la ruta de la carpeta a analizar (use '.' para la actual): ").strip()
            ejecutar_bandit(ruta)
        elif opcion == "2":
            ruta = input("[?] Ingrese la ruta de la carpeta a analizar en busca de leaks (use '.' para la actual): ").strip()
            buscador_de_leaks(ruta)
        elif opcion == "3":
            verificar_integridad()
        elif opcion == "4":
            demostrar_ataque_defensa()
        elif opcion == "5":
            generar_reporte_consolidado()
        elif opcion == "6":
            print("\nCerrando el scanner de seguridad. ¡Buen día!")
            break
        else:
            print("[❌] Opción inválida. Intente nuevamente.")


# Lanzador de la aplicación
if __name__ == "__main__":
    menu_principal()