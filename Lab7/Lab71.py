# Programa para calcular el factorial de un número

n = int(input("Introduce un número: "))
f = 1
for i in range(1, n + 1):
    f = f * i
print("El fac5torial de", n, "es:", f)