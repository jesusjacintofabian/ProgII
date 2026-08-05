  """
  Ejercicio 8.12 — Método privado y validación de datos

Escriba un programa en Python que defina una clase llamada Calculator
con un atributo result para almacenar el resultado de las operaciones. 
La clase debe incluir un método privado __validate() que compruebe si 
el valor proporcionado es un número entero o decimal. 
Además, debe implementar un método add() que utilice el método privado 
para validar el dato antes de sumarlo al resultado. 
Si el valor no es válido, debe mostrar un mensaje indicando que 
el número no es válido. Finalmente, cree un objeto de la clase, 
realice varias sumas y muestre el resultado acumulado.
  
  """


class Calculator:
  def __init__(self):
    self.result = 0

  def __validate(self, num):
    if not isinstance(num, (int, float)):
      return False
    return True

  def add(self, num):
    if self.__validate(num):
      self.result += num
    else:
      print("Invalid number")

calc = Calculator()
calc.add(10)
calc.add(5)
print(calc.result)
# calc.__validate(5)  # Esto daria error