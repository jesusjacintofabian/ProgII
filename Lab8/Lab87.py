  """
  Ejercicio 8.7 — Herencia de clases

Escriba un programa en Python que defina una clase llamada Persona
con atributos para almacenar el nombre y apellido, y un método 
imprimir_nombre() que muestre ambos datos. Luego, cree una clase 
llamada Estudiante que herede de la clase Persona y utilice el método 
heredado para mostrar el nombre y apellido de un estudiante.
  
  """
class Persona:
  def __init__(self, nom, ape):
    self.nombre = nom
    self.apellido = ape

  def imprimir_nombre(self):
    print(self.nombre, self.apellido)

p1 = Persona("Fulano", "De Tal")
p1.imprimir_nombre()

class Estudiante(Persona):
  pass

x = Estudiante("Mengano", "De Tal")
x.imprimir_nombre()