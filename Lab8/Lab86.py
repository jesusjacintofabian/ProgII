  """
 Ejercicio 8.6 — Método para celebrar cumpleaños

Escriba un programa en Python que defina una clase llamada 
Persona con un constructor que permita establecer el nombre y la edad 
de una persona. La clase debe incluir un método celebrar_cumple() 
que incremente la edad de la persona en un año y muestre un mensaje 
indicando su nueva edad. Luego, cree un objeto de la clase y ejecute el 
método de cumpleaños dos veces para demostrar cómo se actualiza la edad. 

  """
class Persona:
  def __init__(self, nom, ed):
    self.nombre = nom
    self.edad = ed

  def obtener_informacion(self):
    return f"{self.nombre} tiene {self.edad} años"

  def celebrar_cumple(self):
    self.edad += 1
    print(f"Feliz cumpleaños! Ahora tienes {self.edad}")

p1 = Persona("Fulano", 28)
p1.celebrar_cumple()
p1.celebrar_cumple()