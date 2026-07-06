# 🛡️ Scanner de Vulnerabilidades "Junior"

Herramienta de auditoría de seguridad en **Python** que combina cinco módulos independientes para analizar código, detectar credenciales expuestas, verificar integridad de archivos y demostrar (de forma práctica) una inyección de comandos y su mitigación. Cada módulo genera su propio reporte en **PDF** con diseño profesional.

---

## 📋 Tabla de contenidos

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Módulos](#-módulos)
  - [1. Análisis estático (Bandit)](#1-análisis-estático-bandit)
  - [2. Búsqueda de fugas de credenciales (Leaks)](#2-búsqueda-de-fugas-de-credenciales-leaks)
  - [3. Validador de integridad (SHA-256)](#3-validador-de-integridad-sha-256)
  - [4. Laboratorio de ataque y defensa](#4-laboratorio-de-ataque-y-defensa)
  - [5. Reporte ejecutivo consolidado](#5-reporte-ejecutivo-consolidado)
- [Estructura de archivos generados](#-estructura-de-archivos-generados)
- [Notas y limitaciones conocidas](#-notas-y-limitaciones-conocidas)

---

## ✨ Características

- Menú interactivo de consola con 6 opciones.
- Análisis estático de código con **Bandit**.
- Detección de credenciales hardcodeadas mediante expresiones regulares (AWS keys, GitHub tokens, contraseñas, llaves privadas, cadenas de conexión, etc.).
- Verificación de integridad de archivos con hashes **SHA-256**.
- Demostración educativa de inyección de comandos (`shell=True` vs. `shell=False`), compatible con Windows y Unix.
- Reporte ejecutivo consolidado que une los resultados de todos los módulos.
- Todos los reportes se generan como **PDF** con una identidad visual consistente (clase `ReportePDF`).

---

## 🧰 Requisitos

- Python 3.8 o superior

### Librerías externas (requieren `pip install`)

| Librería | Instalación | Uso en el proyecto |
|---|---|---|
| Bandit | `pip install bandit` | Módulo 1 — se ejecuta como programa externo vía `subprocess` |
| bleach | `pip install bleach` | Módulo 4 — sanitización de texto en la demo de defensa |
| fpdf2 | `pip install fpdf2` | Todos los módulos — generación de reportes PDF (se importa como `from fpdf import FPDF`) |

### Librerías estándar de Python (ya incluidas, no requieren instalación)

`os`, `re`, `json`, `hashlib`, `platform`, `subprocess`, `datetime`

## ⚙️ Instalación

```bash
git clone https://github.com/<tu-usuario>/<tu-repo>.git
cd <tu-repo>

pip install bandit bleach fpdf2
```

## ▶️ Uso

```bash
python proyecto2.py
```

Al ejecutarlo, verás el menú principal:

```
=======================================================
          HERRAMIENTA DE CIBERSEGURIDAD
=======================================================
1. Analizar código local de forma automática (Bandit)
2. Buscar fugas de credenciales y API Keys (Leaks)
3. Ejecutar validador de integridad de archivos
4. Demostración de ataque y defensa (mala práctica)
5. Generar reporte ejecutivo consolidado
6. Salir del programa
=======================================================
```

> 💡 **Orden recomendado:** ejecuta primero las opciones 1, 2 y/o 3 antes de la opción 5, ya que el reporte consolidado solo *lee* los resultados que esos módulos ya generaron en la misma sesión/carpeta — no vuelve a escanear nada por su cuenta (salvo la integridad, que sí se recalcula en vivo).

---

## 🔍 Módulos

### 1. Análisis estático (Bandit)

Ejecuta [Bandit](https://bandit.readthedocs.io/) como subproceso sobre la ruta indicada, usando una lista de argumentos (nunca `shell=True`):

```python
subprocess.run(["bandit", "-r", ruta, "-f", "json", "-o", archivo], check=False)
```

Lee el JSON resultante, clasifica cada hallazgo por severidad (**HIGH / MEDIUM / LOW**) y genera un PDF con archivo, línea y descripción de cada vulnerabilidad.

### 2. Búsqueda de fugas de credenciales (Leaks)

Recorre un archivo individual o una carpeta completa (`os.walk` recursivo) y prueba cada línea contra un diccionario de patrones regex (`PATRONES_LEAKS`), detectando:

- AWS Access Key ID / Secret
- Google API Key
- GitHub Token
- Slack Token
- API Key / Secret / Token genérico
- Contraseñas hardcodeadas
- Llaves privadas (PEM)
- Cadenas de conexión (MongoDB, PostgreSQL, MySQL)

Genera `reporte_leaks.json` y un PDF con tipo, archivo, línea y fragmento de cada hallazgo.

### 3. Validador de integridad (SHA-256)

Calcula la huella digital del propio script principal (`proyecto2.py`) y la compara contra una base de referencia guardada en `hashes.json`.

- Si `hashes.json` no existe, se crea automáticamente en la primera ejecución (tomando el hash actual como "versión de confianza").
- En ejecuciones posteriores, compara el hash actual contra el guardado y clasifica el archivo como **Íntegro**, **Alterado** o **Eliminado**.

### 4. Laboratorio de ataque y defensa

Demuestra en la misma ejecución dos escenarios con un payload simulado de inyección de comandos:

| Escenario | Implementación | Resultado |
|---|---|---|
| 🔴 Vulnerable | `subprocess.run(comando, shell=True)` con texto concatenado | El separador de comandos se interpreta y el "ataque" se ejecuta |
| 🟢 Seguro | `bleach.clean()` + lista rígida de argumentos + `shell=False` | El contenido hostil se imprime como texto plano, sin ejecutarse |

El separador de inyección usado en la demo se adapta según el sistema operativo detectado (`platform.system()`): `;` en Linux/Mac, `&` en Windows (cmd.exe no interpreta `;` como separador de comandos).

### 5. Reporte ejecutivo consolidado

Une en un solo PDF:

- El conteo de hallazgos de Bandit (leyendo `reporte_seguridad.json`, si existe).
- El conteo de hallazgos de Leaks (leyendo `reporte_leaks.json`, si existe).
- El estado de integridad recalculado en vivo.

Si un módulo no se ejecutó antes en la sesión, se marca honestamente como **"No ejecutado / N/A"** en vez de mostrar un falso 0.

---

## 📁 Estructura de archivos generados

```
.
├── proyecto2.py
├── hashes.json               # Base de hashes de integridad (se crea automáticamente)
├── reporte_seguridad.json    # Resultado crudo de Bandit
├── reporte_leaks.json        # Resultado crudo de la búsqueda de leaks
└── reportes/
    ├── bandit_<timestamp>.pdf
    ├── leaks_<timestamp>.pdf
    ├── integridad_<timestamp>.pdf
    ├── ataque_defensa_<timestamp>.pdf
    └── consolidado_<timestamp>.pdf
```

---

## ⚠️ Notas y limitaciones conocidas

- El módulo 3 (integridad) solo vigila `Proyecto2-CtC.py` por defecto. Para vigilar otros archivos, agrégalos manualmente en la lista `archivos` dentro de `crear_base_integridad()`.
- El módulo 2 (leaks) acepta tanto la ruta de un archivo individual como la de una carpeta completa.
- El módulo 5 (consolidado) depende de que los módulos 1 y 2 se hayan ejecutado antes en la misma sesión/carpeta; no repite el escaneo por su cuenta.
- Este proyecto tiene fines educativos/demostrativos (curso de ciberseguridad); no reemplaza una auditoría de seguridad profesional.

---

## 📄 Licencia

Proyecto académico de uso educativo.
