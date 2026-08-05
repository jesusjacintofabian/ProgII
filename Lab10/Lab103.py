  """
  Ejercicio 103 — Modificación y sobrescritura de archivos

Escriba un programa en Python que abra un archivo de texto llamado archivo
_demo.txt en modo anexar ("a") para agregar nuevo contenido al final del 
archivo. Luego, muestre en pantalla el contenido actualizado. 
Después, abra nuevamente el archivo en modo escritura ("w") para 
sobrescribir y reemplazar todo su contenido con un nuevo texto. 
Finalmente, vuelva a abrir el archivo y muestre el contenido 
resultante después de sobrescribirlo.
  
  """


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