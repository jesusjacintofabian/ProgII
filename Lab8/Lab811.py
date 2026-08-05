  """
  Ejercicio 8.11 — Uso de atributos protegidos

Escriba un programa en Python que defina una clase llamada Persona 
con atributos para almacenar el nombre y el salario. 
El atributo correspondiente al salario debe definirse como protegido 
utilizando un guion bajo (_). Luego, cree un objeto de la clase Persona
y muestre en pantalla el nombre y el salario almacenados en sus atributos.
    
  """


class Persona:
  def __init__(self, nombre, salario):
    self.nombre = nombre
    self._salario = salario

p1 = Persona("Fulano", 1000)
print(p1.nombre)
print(p1._salario)