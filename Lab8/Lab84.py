  """
Ejercicio 8.4 — Creación de una clase calculadora

Escriba un programa en Python que defina una clase llamada Calculadora
con dos métodos: sumar(), que permita sumar dos números,
y multiplicar(), que permita multiplicar dos números. 
Luego, cree un objeto de la clase y utilice ambos métodos para realizar y mostrar los resultados de una suma y una multiplicación.

  """

class Calculadora:
  def sumar(self, a, b):
    return a + b

  def multiplicar(self, a, b):
    return a * b

calc = Calculadora()
print(calc.sumar(5, 3))
print(calc.multiplicar(4, 7))