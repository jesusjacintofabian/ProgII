# Lab614: Crea una función que reciba varios nombres y escriba el nombre del último recibido en la llamada.
def my_function(*kids):
  print("El niño mas joven es " + kids[2])

my_function("Pedro", "Juan", "Jose")