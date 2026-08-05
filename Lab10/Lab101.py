  """
  Ejercicio 8.22 — Lectura de archivos de texto

Escriba un programa en Python que abra un archivo de texto llamado archivo
_demo.txt en modo lectura y muestre todo su contenido en pantalla. 
Luego, vuelva a abrir el archivo y utilice el método readline() 
para leer y mostrar únicamente la primera línea del archivo.
  
  """

with open("archivo_demo.txt", "r") as f:
  print(f.read())
  f.close()

f = open("archivo_demo.txt")
print(f.readline())
f.close()