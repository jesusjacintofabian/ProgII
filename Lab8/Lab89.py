  """
  Ejercicio 8.9 — Polimorfismo mediante métodos en diferentes clases

Escriba un programa en Python que defina una clase Vehiculo con atributos
para almacenar la marca y el modelo, además de un método mover()
que indique el desplazamiento por carretera. Luego, cree las clases
Carro, Bote y Avion que hereden de Vehiculo. 
Cada clase debe implementar el método mover() de acuerdo con su medio
de transporte: el carro se desplaza por carretera, el bote navega
y el avión vuela. Finalmente, cree un objeto de cada tipo de vehículo 
y utilice un ciclo para mostrar su marca, modelo y forma de desplazamiento.
  
  """
class Vehiculo:
  def __init__(self, mrc, mdl):
    self.marca = mrc
    self.modelo = mdl

  def mover(self):
    print("Desplazarse en carretera!")

class Carro(Vehiculo):
  pass

class Bote(Vehiculo):
  def mover(self):
    print("Navegar!")

class Avion(Vehiculo):
  def mover(self):
    print("Vuelo del avion!")

carro1 = Carro("Toyota", "Yaris")
bote1 = Bote("Ibiza", "Touring 20")
avion1 = Avion("Boeing", "747")

for x in (carro1, bote1, avion1):
  print(x.marca)
  print(x.modelo)
  x.mover()