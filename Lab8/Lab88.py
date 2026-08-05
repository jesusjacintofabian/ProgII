  """
  Ejercicio 8.8 — Herencia y uso del constructor de la clase padre

Escriba un programa en Python que defina una clase llamada Persona 
con atributos para almacenar el nombre y apellido, y un método 
imprimir_nombre() que muestre ambos datos. Luego, cree una clase 
llamada Estudiante que herede de Persona y defina su propio constructor, 
utilizando el constructor de la clase padre para inicializar los atributos. 
Finalmente, cree un objeto de la clase Estudiante y utilice el método 
heredado para mostrar su nombre y apellido.
  
  """
class Persona:
  def __init__(self, nom, ape):
    self.nombre = nom
    self.apellido = ape

  def imprimir_nombre(self):
    print(self.nombre, self.apellido)

class Estudiante(Persona):
  def __init__(self, nom, ape):
    Persona.__init__(self, nom, ape)

x = Estudiante("Mengano", "De Tal")
x.imprimir_nombre()