    """
    Ejercicio 96 — Uso del decorador @final

Escriba un programa en Python que defina una clase llamada Base 
utilizando el decorador @final para indicar que dicha clase no debe ser 
heredada. Luego, intente crear una clase Derivada que herede de Base, 
demostrando que herramientas de análisis estático como MyPy 
pueden detectar y señalar esta herencia como un error.
        
    """

from typing import final

@final
class Base:
    pass

# Un linter (como MyPy) marcará esto como ERROR:
class Derivada(Base):
    pass