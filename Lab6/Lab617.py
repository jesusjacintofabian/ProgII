# Lab617: Define una función generadora simple que devuelva tres valores con yield. Recorre e imprime sus valores.
def my_generator():
  yield 1
  yield 2
  yield 3

for value in my_generator():
  print(value)