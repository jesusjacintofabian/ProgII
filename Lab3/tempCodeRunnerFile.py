# Ejercicio 9

texto = input("Ingrese una cadena: ")

# capitalize()
capitalizado = texto.capitalize()
print("Con capitalize():", capitalizado)

# count()
letra = input("Ingrese una letra para contar: ")
cantidad = texto.count(letra)
print(f"La letra '{letra}' aparece {cantidad} veces")

# endswith()
termina = input("Ingrese una terminación: ")
if texto.endswith(termina):
    print("La cadena SÍ termina con ese valor")
else:
    print("La cadena NO termina con ese valor")