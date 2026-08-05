  """
  Ejercicio 8.14 — Comunicación entre una clase interna y una clase externa

Escriba un programa en Python que defina una clase externa llamada 
Externa con un atributo name y una clase interna llamada Interna. 
La clase interna debe recibir como parámetro una referencia al objeto 
de la clase externa y utilizarla para acceder a su atributo name. 
Además, debe incluir un método display() que muestre el nombre de la 
clase externa. Finalmente, cree un objeto de la clase externa, 
utilícelo para crear una instancia de la clase interna y ejecute 
el método display().

  """

class Externa:
  def __init__(self):
    self.name = "EML"

  class Interna:
    def __init__(self, ext):
      self.ext = ext

    def display(self):
      print(f"El nombre de la clase exterior: {self.ext.name}")

ext = Externa()
int = ext.Interna(ext)
int.display()