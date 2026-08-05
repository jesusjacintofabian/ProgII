# Lab612: Define una función con parámetro por defecto e invócala varias veces con distintos valores.
def my_function(pais = "Panama"): 
  print("Soy de ", pais)

my_function("Argentina")
my_function("Mexico")
my_function()
my_function("Canada")