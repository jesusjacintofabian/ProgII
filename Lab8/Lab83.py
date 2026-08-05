  """
Ejercicio 8.3 — Creación de métodos en una clase

Escriba un programa en Python que defina una clase llamada Persona 
con un constructor que permita establecer el nombre y la edad de 
una persona. La clase debe incluir un método llamado saludar() 
que muestre un mensaje de saludo utilizando el nombre de la persona. 
Luego, cree un objeto de la clase y utilice el método saludar() 
para mostrar el mensaje correspondiente.
  
  """

class Persona:
  def __init__(self, nom, ed):
    self.nombre = nom
    self.edad = ed

  def saludar(self):
    print("Hola, mi nombre es: " + self.nombre)

p1 = Persona("Fulano", 28)

p1.saludar()