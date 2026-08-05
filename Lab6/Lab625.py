# Lab625: Solicita repetidamente un número al usuario hasta que ingrese un valor válido (float). Usa try-except para la validación.
y = True
while y == True:
  x = input("Ingrese un numero:")
  try:
    x = float(x);
    y = False
  except:
    print("Entrada incorrecta, intentelo de nuevo")

print("Gracias!")