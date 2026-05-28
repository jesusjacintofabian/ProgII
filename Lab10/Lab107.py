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