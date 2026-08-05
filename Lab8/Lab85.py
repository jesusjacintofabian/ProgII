  """
  Ejercicio 8.5 — Método para obtener información de una persona

Escriba un programa en Python que defina una clase llamada Persona 
con un constructor que permita establecer el nombre y la edad de una 
persona. La clase debe incluir un método llamado obtener_informacion() 
que devuelva un mensaje indicando el nombre y la edad de la persona. 
Luego, cree un objeto de la clase y muestre en pantalla la 
información obtenida mediante dicho método.
  """


class Persona:
  def __init__(self, nom, ed):
    self.nombre = nom
    self.edad = ed

  def obtener_informacion(self):
    return f"{self.nombre} tiene {self.edad} años"

p1 = Persona("Fulano", 28)
print(p1.obtener_informacion())