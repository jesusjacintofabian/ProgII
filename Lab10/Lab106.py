    """
    Ejercicio 106 — Clases abstractas y cálculo de áreas

Escriba un programa en Python que defina una clase abstracta llamada Figura
con un método abstracto calcularArea(). Luego, cree las clases Circulo, 
Rectangulo y Triangulo, que hereden de Figura e implementen el método 
calcularArea() según la fórmula correspondiente a cada figura. 
Finalmente, cree objetos de cada figura, almacénelos en una lista 
y utilice un ciclo para mostrar el nombre de cada figura junto con el 
área calculada.
    
    """

from abc import ABC, abstractmethod
import math

class Figura(ABC):
    @abstractmethod
    def calcularArea(self):
        pass

class Circulo(Figura):
    def __init__(self, radio):
        self.radio = radio

    def calcularArea(self):
        return math.pi * self.radio ** 2

class Rectangulo(Figura):
    def __init__(self, base, altura):
        self.base = base
        self.altura = altura

    def calcularArea(self):
        return self.base * self.altura

class Triangulo(Figura):
    def __init__(self, base, altura):
        self.base = base
        self.altura = altura

    def calcularArea(self):
        return (self.base * self.altura) / 2

figuras = [Circulo(5), Rectangulo(4, 6), Triangulo(3, 8)]

for figura in figuras:
    print(f"{figura.__class__.__name__}: área = {figura.calcularArea():.2f}")