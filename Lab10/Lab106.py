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