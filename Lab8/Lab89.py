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