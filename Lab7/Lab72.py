    """
    Ejercicio 7.2 — Generación de una matriz identidad

Escriba un programa en Python que solicite al usuario ingresar un 
número entero par y genere una matriz identidad de tamaño N × N. 
El programa debe colocar el valor 1 en la diagonal principal y 0 
en las demás posiciones. Si el número ingresado no es par, 
el programa debe mostrar un mensaje indicando que el número debe ser par.
    
    """

N = int(input("Introduce un número par: "))


if N % 2 == 0:

    # Generar la matriz identidad
    for i in range(N):
        for j in range(N):

            if i == j:
                print(1, end=" ")
            else:
                print(0, end=" ")

        print()

else:
    print("El número debe ser par")