# Lab621: Practica el uso de iteradores sobre tuplas y cadenas, accediendo a los elementos con next() y bucles.
miTupla = ("asignacion", "laboratorio", "python")
myit = iter(miTupla)

print(next(myit))
print(next(myit))
print(next(myit))

mystr = "casa"
myit = iter(mystr)

print(next(myit))
print(next(myit))
print(next(myit))
print(next(myit))

for x in mystr:
  print(x)