    """
    Ejercicio 105 — Cálculo del factorial mediante una clase

Escriba un programa en Python que defina una clase llamada Factorial 
que permita almacenar un número y calcular su factorial mediante un método
llamado calcular(). 
El programa debe solicitar al usuario un número entero, crear un objeto 
de la clase Factorial utilizando dicho número y mostrar en pantalla el 
resultado de su factorial.
    
    """

class Factorial:
    def __init__(self, n):
        self.n = n

    def calcular(self):
        f = 1
        for i in range(1, self.n + 1):
            f *= i
        return f

n = int(input("Ingresa un número: "))
obj = Factorial(n)
print("El factorial es:", obj.calcular())