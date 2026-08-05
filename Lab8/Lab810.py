  """
  Ejercicio 8.10 — Encapsulamiento y validación de atributos

Escriba un programa en Python que defina una clase llamada 
Persona con atributos para almacenar el nombre y la edad. 
La edad debe ser un atributo privado y debe poder consultarse 
mediante un método obtener_edad(). Además, la clase debe incluir 
un método asignar_edad() que permita modificar la edad únicamente 
cuando el valor ingresado sea mayor que cero. 
Si se introduce una edad igual o menor que cero, el programa debe 
mostrar un mensaje indicando que la edad debe ser un valor positivo. 
Finalmente, cree un objeto de la clase Persona, muestre su edad inicial, modifíquela y muestre nuevamente la edad actualizada.

  """

class Persona:
  def __init__(self, nom, ape):
    self.nombre = nom
    self.__edad = ape

  def obtener_edad(self):
    return self.__edad

  def asignar_edad(self, edad):
    if edad > 0:
      self.__edad = edad
    else:
      print("La edad debe ser un valor positovo")

p1 = Persona("Fulano", 28)
print(p1.obtener_edad())

p1.asignar_edad(29)
print(p1.obtener_edad())