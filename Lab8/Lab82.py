  """
Ejercicio 8.2 — Creación de una clase con constructor

Escriba un programa en Python que defina una clase llamada Persona
con un constructor que permita establecer el nombre y la edad de una
persona. Luego, cree un objeto de la clase proporcionando un nombre 
y una edad, y muestre en pantalla los valores correspondientes 
a sus atributos.  
    
  """

class Persona:
  def __init__(self, nom, ed):
    self.nombre = nom
    self.edad = ed

p1 = Persona("Fulano", 28)

print(p1.nombre)
print(p1.edad)