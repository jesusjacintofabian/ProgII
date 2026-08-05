# Lab613: Define una función que acepte dos parámetros con argumentos nombrados e imprima frases con ellos.
def my_function(mascota, nombre):
  print("Tengo un", mascota)
  print("Mi", mascota + " se llama", nombre)

my_function(mascota = "perro", nombre = "Manchas")