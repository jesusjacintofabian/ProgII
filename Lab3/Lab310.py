# Lab310: Pide una cadena y utiliza isalnum(), isdigit() e islower(). Muestra los resultados por pantalla.
# Ejercicio 10

texto = input("Ingrese una cadena: ")

# isalnum()
print("¿Es alfanumérica?", texto.isalnum())

# isdigit()
print("¿Son solo números?", texto.isdigit())

# islower()
print("¿Está en minúsculas?", texto.islower())