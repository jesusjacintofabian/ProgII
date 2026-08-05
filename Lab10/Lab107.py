    """
    Ejercicio 107 — Clases abstractas para evaluar funciones matemáticas

Escriba un programa en Python que defina una clase abstracta llamada 
FuncionMatematica con un método abstracto evaluar(x). 
Luego, cree las clases FuncionLineal, FuncionCuadratica y 
FuncionExponencial, que hereden de FuncionMatematica e implementen 
el método evaluar() de acuerdo con la fórmula correspondiente a cada 
función. Finalmente, cree objetos de cada tipo de función, solicite al 
usuario un valor de x y utilice un ciclo para evaluar y mostrar el 
resultado de cada función matemática.
    
    """

from abc import ABC, abstractmethod
import math

class FuncionMatematica(ABC):
    @abstractmethod
    def evaluar(self, x):
        pass

class FuncionLineal(FuncionMatematica):
    def __init__(self, m, b):
        self.m = m
        self.b = b

    def evaluar(self, x):
        return self.m * x + self.b

class FuncionCuadratica(FuncionMatematica):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def evaluar(self, x):
        return self.a * x**2 + self.b * x + self.c

class FuncionExponencial(FuncionMatematica):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def evaluar(self, x):
        return self.a * math.e ** (self.b * x)

funciones = [FuncionLineal(2, 3), FuncionCuadratica(1, -2, 1), FuncionExponencial(2, 0.5)]

x = float(input("Ingresa el valor de x: "))

for funcion in funciones:
    print(f"{funcion.__class__.__name__}: f({x}) = {funcion.evaluar(x):.2f}")