with open("archivo_demo.txt", "r") as f:
  print(f.read())
  f.close()

f = open("archivo_demo.txt")
print(f.readline())
f.close()