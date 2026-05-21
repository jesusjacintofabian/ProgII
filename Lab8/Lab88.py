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