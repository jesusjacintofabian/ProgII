# Lab615: Escribe una función que acepte cualquier cantidad de argumentos y devuelva la suma de todos ellos.
def my_function(*numeros):
  total = 0
  for num in numeros:
    total += num
  return total

print(my_function(1, 2, 3))
print(my_function(10, 20, 30, 40))
print(my_function(5))