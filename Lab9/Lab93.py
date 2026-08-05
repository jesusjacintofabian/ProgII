    """
    Ejercicio 93 — Atributo de clase para contar objetos

Escriba un programa en Python que defina una clase llamada Persona 
con un atributo de clase contador inicializado en cero. 
El programa debe utilizar el constructor de la clase para incrementar 
el contador cada vez que se cree una nueva instancia de Persona. 
Luego, cree tres objetos de la clase y muestre en pantalla la cantidad 
total de objetos creados.
        
    """


class Persona:
    contador = 0

    def __init__(self):
        Persona.contador += 1

p1 = Persona()
p2 = Persona()
p3 = Persona()
print(Persona.contador)  # 3