class Persona:
  def __init__(self, nom, ed):
    self.nombre = nom
    self.edad = ed

  def saludar(self):
    print("Hola, mi nombre es: " + self.nombre)

p1 = Persona("Fulano", 28)

p1.saludar()