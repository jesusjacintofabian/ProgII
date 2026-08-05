  """
  Ejercicio 8.13 — Clases internas

Escriba un programa en Python que defina una clase externa 
llamada Externa que contenga una clase interna llamada Interna. 
La clase interna debe incluir un método display() que muestre un 
mensaje en pantalla. Luego, cree un objeto de la clase externa, 
utilice dicho objeto para crear una instancia de la clase interna y 
ejecute el método display() para mostrar el mensaje correspondiente.
    
  """

class Externa:
  def __init__(self):
    self.name = "Externa"

  class Interna:
    def __init__(self):
      self.name = "Interna"

    def display(self):
      print("Hola desde la clase interna")

ext = Externa()
int = ext.Interna()
int.display()