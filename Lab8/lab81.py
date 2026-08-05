  """
  Ejercicio 8.1 — Creación y eliminación de objetos de una clase

Escriba un programa en Python que defina una clase llamada MiClase 
con un atributo x cuyo valor sea 5. Luego, cree tres objetos 
de dicha clase y muestre el valor del atributo x de cada uno. 
Finalmente, elimine uno de los objetos utilizando la instrucción del.
  
  """

class MiClase:
  x = 5

p1 = MiClase()
p2 = MiClase()
p3 = MiClase()

print(p1.x)
print(p2.x)
print(p3.x)

del p1