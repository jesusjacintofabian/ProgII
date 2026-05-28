with open("archivo_demo.txt", "a") as f:
  f.write("¡Ahora el archivo tiene más contenido!")

#Abrir y leer el archivo después de agregarlo:
with open("archivo_demo.txt") as f:
  print(f.read())

with open("archivo_demo.txt", "w") as f:
  f.write("¡Ups! ¡He borrado el contenido!")

#Abrir y leer el archivo después de sobrescribirlo:
with open("archivo_demo.txt") as f:
  print(f.read())