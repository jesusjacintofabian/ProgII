# Lab69: Escribe una función que convierta grados Fahrenheit a Celsius y pruébala llamándola con diferentes valores.
def fahrenheit_to_celsius(fahrenheit):
  return (fahrenheit - 32) * 5 / 9

print(fahrenheit_to_celsius(77))
print(fahrenheit_to_celsius(95))
print(fahrenheit_to_celsius(50))