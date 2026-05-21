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