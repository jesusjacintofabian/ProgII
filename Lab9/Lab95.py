    """
    Ejercicio 8.19 — Uso de métodos de clase

Escriba un programa en Python que defina una clase llamada Usuario 
con atributos para almacenar el nombre y la edad. 
La clase debe incluir un método de clase crear_anonimo() utilizando el 
decorador @classmethod, que permita crear un usuario con valores 
predeterminados: nombre "Anónimo" y edad 0. Finalmente, utilice este 
método para crear un usuario anónimo y muestre en pantalla su nombre 
y edad.
    _
    """

class Usuario:
    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad

    @classmethod
    def crear_anonimo(cls):
        # 'cls' es equivalente a usar 'Usuario'
        return cls("Anónimo", 0)

# Uso del constructor alternativo
invitado = Usuario.crear_anonimo()

#Prueba
invitado = Usuario.crear_anonimo()
print(invitado.nombre, invitado.edad)