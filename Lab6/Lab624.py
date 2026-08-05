# Lab624: Solicita por consola nombre y preferencias del usuario, y luego imprime un mensaje resumido usando esas entradas.
nombre = input("Ingrese su nombre:")
print(f"Hola {nombre}")

fav1 = input("Cual es la marca de computadora favorita? ")
fav2 = input("De que color le gusta? ")
fav3 = input("Cuantas ha tenido hasta ahora? ")
print(f"Quieres una {fav1} {fav2} con {fav3} nucleos?")