  """
  Ejercicio 102 — Lectura de líneas de un archivo

Escriba un programa en Python que abra un archivo de texto llamado archivo
_demo.txt en modo lectura y muestre sus dos primeras líneas utilizando el 
método readline(). Luego, vuelva a abrir el archivo y utilice un ciclo for
para recorrer y mostrar todas las líneas contenidas en el archivo.
  
  """

with open("archivo_demo.txt") as f:
  print(f.readline())
  print(f.readline())

with open("archivo_demo.txt") as f:
  for x in f:
    print(x)