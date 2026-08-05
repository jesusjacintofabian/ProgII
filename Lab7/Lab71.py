    """
    Ejercicio 7.1 — Cálculo del factorial de un número

Escriba un programa en Python que solicite al usuario ingresar 
un número entero y calcule su factorial utilizando un ciclo for. 
El programa debe mostrar en pantalla el número ingresado y 
el resultado de su factorial.
    
    """

n = int(input("Introduce un número: "))
f = 1
for i in range(1, n + 1):
    f = f * i
print("El fac5torial de", n, "es:", f)