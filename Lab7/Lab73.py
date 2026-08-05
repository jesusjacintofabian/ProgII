 """
Ejercicio 7.3 — Análisis de texto

Escriba un programa en Python que solicite al usuario ingresar
un texto largo. El programa debe convertir el texto a minúsculas,
eliminar los signos de puntuación y determinar la cantidad de
palabras únicas, la palabra más larga y la frecuencia de cada
carácter alfabético.
"""

import string

# Solicitar texto
texto = input("Introduce un texto largo:\n")

# Pasar a minúsculas
texto_limpio = texto.lower()

# Eliminar signos de puntuación
for signo in string.punctuation:
    texto_limpio = texto_limpio.replace(signo, "")

# Separar palabras
palabras = texto_limpio.split()

# ---------------- PALABRAS ÚNICAS ----------------

palabras_unicas = set(palabras)

# ---------------- PALABRA MÁS LARGA ----------------

palabra_larga = max(palabras, key=len)

# ---------------- FRECUENCIA DE CARACTERES ----------------

frecuencias = {}
total_letras = 0

for caracter in texto_limpio:

    if caracter.isalpha():

        total_letras += 1

        if caracter in frecuencias:
            frecuencias[caracter] += 1
        else:
            frecuencias[caracter] = 1

# ---------------- REPORTE ----------------

print("\n----- REPORTE -----")

print("Cantidad de palabras únicas:", len(palabras_unicas))

print("Palabra más larga:", palabra_larga)

print("\nFrecuencia de caracteres:")

for letra, cantidad in frecuencias.items():

    porcentaje = (cantidad / total_letras) * 100

    print(letra, "=", cantidad,
          "veces |", round(porcentaje, 2), "%")