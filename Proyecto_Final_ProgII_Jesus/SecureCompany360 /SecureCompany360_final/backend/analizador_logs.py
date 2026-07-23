"""
Herramienta de Consola para el Análisis de Logs de Seguridad y Auditoría.

Uso:
    python backend/analizador_logs.py [--export]
"""
import sys
import argparse
from app.database import SessionLocal
from app.security.log_analyzer import generar_analisis_completo

def renderizar_consola(analisis):
    print("=" * 60)
    print("       ANALIZADOR DE LOGS - SECURE COMPANY 360")
    print("=" * 60)
    
    riesgo = analisis["nivel_riesgo"]
    color_reset = "\033[0m"
    if riesgo == "Alto":
        color_riesgo = "\033[91m"  # Rojo
    elif riesgo == "Medio":
        color_riesgo = "\033[93m"  # Amarillo
    else:
        color_riesgo = "\033[92m"  # Verde
        
    print(f"Nivel de Riesgo Global: {color_riesgo}{riesgo.upper()}{color_reset}")
    print("-" * 60)
    
    print("RESUMEN DE MÉTRICAS:")
    res = analisis["resumen"]
    print(f"  - Líneas en log técnico (archivo): {res['total_log_archivo']}")
    print(f"  - Eventos de auditoría (DB):      {res['total_log_auditoria']}")
    print(f"  - Intentos fallidos de login:     {res['total_fallidos']}")
    print(f"  - Cuentas bloqueadas:             {res['total_bloqueos']}")
    print(f"  - Errores de sistema detectados:  {res['total_errores']}")
    print("-" * 60)

    print("ALERTAS DE SEGURIDAD DETECTADAS:")
    if not analisis["alertas"]:
        print("  Ninguna alerta detectada.")
    for a in analisis["alertas"]:
        lvl = a["nivel"]
        col = "\033[91m" if lvl == "Alto" else "\033[93m"
        print(f"  [{col}{lvl}{color_reset}] {a['mensaje']}")
    print("-" * 60)

    print("IPs CON MÁS INTENTOS FALLIDOS:")
    if not analisis["ips_fallidas"]:
        print("  Ningún intento fallido registrado.")
    for item in analisis["ips_fallidas"][:5]:
        print(f"  - IP: {item['ip']:<20} | Intentos: {item['cantidad']}")
    print("-" * 60)

    print("USUARIOS MÁS ACTIVOS:")
    if not analisis["usuarios_activos"]:
        print("  Ninguna actividad de usuario registrada.")
    for item in analisis["usuarios_activos"]:
        print(f"  - Usuario: {item['usuario']:<15} | Acciones: {item['acciones']}")
    print("-" * 60)

    print("ÚLTIMOS ERRORES TÉCNICOS DETECTADOS:")
    if not analisis["errores_recientes"]:
        print("  Ningún error registrado.")
    for err in analisis["errores_recientes"][-5:]:
        print(f"  [{err['timestamp']}] {err['mensaje'][:80]}...")
    print("-" * 60)

    print("RECOMENDACIONES DE MITIGACIÓN:")
    for rec in analisis["recomendaciones"]:
        print(f"  * {rec}")
    print("=" * 60)


def exportar_markdown(analisis, filename="reporte_auditoria.md"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Reporte de Auditoría y Análisis de Logs\n\n")
        f.write(f"**Fecha de generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Nivel de Riesgo Global:** {analisis['nivel_riesgo'].upper()}\n\n")
        
        f.write("## Resumen de Métricas\n")
        res = analisis["resumen"]
        f.write(f"- Líneas de log técnico (archivo): {res['total_log_archivo']}\n")
        f.write(f"- Eventos de auditoría (Base de Datos): {res['total_log_auditoria']}\n")
        f.write(f"- Intentos fallidos de login: {res['total_fallidos']}\n")
        f.write(f"- Cuentas bloqueadas temporales: {res['total_bloqueos']}\n")
        f.write(f"- Errores de sistema: {res['total_errores']}\n\n")
        
        f.write("## Alertas de Seguridad\n")
        if not analisis["alertas"]:
            f.write("No se detectaron anomalías o alertas de seguridad.\n")
        else:
            for a in analisis["alertas"]:
                f.write(f"- **[{a['nivel']}]** {a['mensaje']}\n")
        f.write("\n")
        
        f.write("## Direcciones IP con más intentos fallidos\n")
        f.write("| Dirección IP | Intentos Fallidos |\n")
        f.write("| --- | --- |\n")
        for item in analisis["ips_fallidas"]:
            f.write(f"| {item['ip']} | {item['cantidad']} |\n")
        f.write("\n")
        
        f.write("## Usuarios más activos\n")
        f.write("| Usuario | Total de Operaciones |\n")
        f.write("| --- | --- |\n")
        for item in analisis["usuarios_activos"]:
            f.write(f"| {item['usuario']} | {item['acciones']} |\n")
        f.write("\n")
        
        f.write("## Recomendaciones de Ciberseguridad\n")
        for rec in analisis["recomendaciones"]:
            f.write(f"- {rec}\n")
            
    print(f"\n[OK] Reporte exportado a {filename}")


if __name__ == "__main__":
    from datetime import datetime
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", action="store_true", help="Exportar reporte a reporte_auditoria.md")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        analisis = generar_analisis_completo(db)
        renderizar_consola(analisis)
        if args.export:
            exportar_markdown(analisis)
    finally:
        db.close()
