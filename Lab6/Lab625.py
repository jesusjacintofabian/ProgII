y = True
while y == True:
  x = input("Ingrese un numero:")
  try:
    x = float(x);
    y = False
  except:
    print("Entrada incorrecta, intentelo de nuevo")

print("Gracias!")