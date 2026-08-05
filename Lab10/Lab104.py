  """
  Ejercicio 104 — Eliminación de archivos

Escriba un programa en Python que verifique si existe un archivo llamado 
archivo_demo.txt. Si el archivo existe, debe eliminarlo utilizando el 
módulo os. Si el archivo no existe, debe mostrar un mensaje indicando 
que el archivo no existe.
    
  """

import os
if os.path.exists("archivo_demo.txt"):
  os.remove("archivo_demo.txt")
else:
  print("The file does not exist")