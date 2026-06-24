import socket
import ssl
from datetime import datetime


def verificar_ssl(dominio: str) -> dict:
    """
    Evalúa un dominio y obtiene información del certificado SSL.
    """

    # Limpia la URL para obtener únicamente el dominio
    dominio_limpio = dominio.replace("https://", "").replace("http://", "").split('/')[0]

    # Diccionario con valores iniciales
    resultado = {
        "dominio": dominio_limpio,
        "valido": False,
        "emisor": "Desconocido",
        "fecha_expiracion": None,
        "dias_restantes": None,
        "estado_alerta": "DESCONOCIDO",
        "mensaje_alerta": "No se pudo evaluar el certificado.",
        "error": None
    }

    try:
        # Crear contexto SSL seguro
        contexto = ssl.create_default_context()

        # Conectar al servidor mediante HTTPS (puerto 443)
        with socket.create_connection((dominio_limpio, 443), timeout=5.0) as sock:
            with contexto.wrap_socket(sock, server_hostname=dominio_limpio) as ssock:

                # Obtener certificado SSL
                certificado = ssock.getpeercert()

                # Extraer entidad emisora del certificado
                emisor_datos = certificado.get('issuer', [])
                for campo in emisor_datos:
                    for subcampo in campo:
                        if subcampo[0] == 'organizationName':
                            resultado["emisor"] = subcampo[1]

                # Obtener fecha de expiración
                fecha_exp_str = certificado.get('notAfter')
                formato_fecha_ssl = r'%b %d %H:%M:%S %Y %Z'
                fecha_exp = datetime.strptime(fecha_exp_str, formato_fecha_ssl)

                resultado["fecha_expiracion"] = fecha_exp.strftime('%Y-%m-%d %H:%M:%S')

                # Calcular días restantes de vigencia
                dias_restantes = (fecha_exp - datetime.utcnow()).days
                resultado["dias_restantes"] = dias_restantes

                # Clasificar nivel de alerta
                if dias_restantes <= 0:
                    resultado["valido"] = False
                    resultado["estado_alerta"] = "CRÍTICO"
                    resultado["mensaje_alerta"] = "El certificado SSL ha expirado. La API no es segura."

                elif dias_restantes <= 14:
                    resultado["valido"] = True
                    resultado["estado_alerta"] = "PELIGRO"
                    resultado["mensaje_alerta"] = f"Urgente: El certificado expira en {dias_restantes} días."

                elif dias_restantes <= 30:
                    resultado["valido"] = True
                    resultado["estado_alerta"] = "ADVERTENCIA"
                    resultado["mensaje_alerta"] = f"Atención: El certificado expira en {dias_restantes} días."

                else:
                    resultado["valido"] = True
                    resultado["estado_alerta"] = "SEGURO"
                    resultado["mensaje_alerta"] = f"El certificado es válido. Quedan {dias_restantes} días."

    # Manejo de errores SSL
    except ssl.CertificateError as e:
        resultado["estado_alerta"] = "CRÍTICO"
        resultado["error"] = f"Error de coincidencia en el dominio o certificado inválido: {e}"

    except ssl.SSLError as e:
        resultado["estado_alerta"] = "CRÍTICO"
        resultado["error"] = f"Error en el protocolo SSL/TLS: {e}"

    # Manejo de errores de conexión
    except (socket.error, socket.timeout) as e:
        resultado["estado_alerta"] = "ERROR_CONEXION"
        resultado["error"] = f"No se pudo conectar al servidor por el puerto 443: {e}"

    # Captura cualquier otro error inesperado
    except Exception as e:
        resultado["estado_alerta"] = "ERROR_INESPERADO"
        resultado["error"] = f"Error inesperado al procesar SSL: {e}"

    return resultado


def formatear_resultado_txt(datos_ssl: dict) -> str:
    """
    Convierte el resultado de la auditoría en texto plano.
    """

    # Mostrar información de error si existe
    if datos_ssl.get("error"):
        return (
            "==================================================\n"
            f"AUDITORÍA SSL: {datos_ssl['dominio']}\n"
            "==================================================\n"
            f" ESTADO:   [ ❌ {datos_ssl['estado_alerta']} ]\n"
            f" DETALLE:  {datos_ssl['error']}\n"
            "--------------------------------------------------\n"
        )

    # Generar reporte normal
    estado_visual = f"[ {datos_ssl['estado_alerta']} ]"

    return (
        "==================================================\n"
        f"AUDITORÍA SSL: {datos_ssl['dominio']}\n"
        "==================================================\n"
        f" Estado del SSL:     {estado_visual}\n"
        f" ¿Es válido hoy?:    {'Sí' if datos_ssl['valido'] else 'No'}\n"
        f" Entidad Emisora:    {datos_ssl['emisor']}\n"
        f" Fecha Expiración:   {datos_ssl['fecha_expiracion']} UTC\n"
        f" Días Restantes:     {datos_ssl['dias_restantes']} días\n"
        f" Diagnóstico:        {datos_ssl['mensaje_alerta']}\n"
        "--------------------------------------------------\n"
    )


def formatear_resultado_para_tabla_pdf(datos_ssl: dict) -> list:
    """
    Convierte los resultados en una estructura adecuada para PDF.
    """

    # Tabla para errores
    if datos_ssl.get("error"):
        return [
            ["Parámetro de Auditoría", "Resultado Evaluado"],
            ["Estado General", f"FALLIDO / {datos_ssl['estado_alerta']}"],
            ["Detalle Técnico", datos_ssl["error"]]
        ]

    # Tabla para resultados exitosos
    return [
        ["Parámetro de Auditoría", "Resultado Evaluado"],
        ["Certificado Válido", "SÍ" if datos_ssl["valido"] else "NO"],
        ["Autoridad Certificadora (Emisor)", datos_ssl["emisor"]],
        ["Fecha de Vencimiento", datos_ssl["fecha_expiracion"]],
        ["Días de Vigencia Restantes", f"{datos_ssl['dias_restantes']} días"],
        ["Severidad / Alerta", datos_ssl["estado_alerta"]],
        ["Recomendación", datos_ssl["mensaje_alerta"]]
    ]


# =====================================================================
# BLOQUE PRINCIPAL DE EJECUCIÓN
# =====================================================================

if __name__ == "__main__":

    # Solicitar dominio a evaluar
    dominio_usuario = input("👉 Ingrese el dominio o URL de la API a auditar: ")

    print("\n🚀 Iniciando Auditoría SSL...\n")

    # Ejecutar auditoría
    res = verificar_ssl(dominio_usuario)

    # Generar archivos de reporte
    ruta_txt = "reporte_auditoria_ssl.txt"
    ruta_pdf = "reporte_auditoria_ssl.pdf"

    # Crear reporte TXT
    try:
        ...
    except Exception as e:
        ...

    # Crear reporte PDF
    try:
        ...
    except Exception as e:
        ...