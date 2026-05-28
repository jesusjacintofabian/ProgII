import os
if os.path.exists("archivo_demo.txt"):
  os.remove("archivo_demo.txt")
else:
  print("The file does not exist")