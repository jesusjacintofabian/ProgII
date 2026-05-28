with open("archivo_demo.txt") as f:
  print(f.readline())
  print(f.readline())

with open("archivo_demo.txt") as f:
  for x in f:
    print(x)