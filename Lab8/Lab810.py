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