    """
    Ejercicio 97 — Uso de @final para impedir la sobrescritura de métodos

Escriba un programa en Python que defina una clase llamada Padre 
con un método metodo_sagrado() marcado con el decorador @final, 
indicando que dicho método no debe ser sobrescrito por las clases hijas. 
Luego, cree una clase Hijo que herede de Padre e intente sobrescribir 
el método metodo_sagrado(). 
El programa debe demostrar que herramientas de análisis estático 
como MyPy pueden detectar esta sobrescritura como un error.
    
    """

from typing import final

class Padre:
    @final
    def metodo_sagrado(self):
        print("No me cambies.")

class Hijo(Padre):
    # Un linter (como MyPy) marcará esto como ERROR:
    def metodo_sagrado(self):
        print("Intentando cambiarlo.")