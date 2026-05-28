class Factorial:
    def __init__(self, n):
        self.n = n

    def calcular(self):
        f = 1
        for i in range(1, self.n + 1):
            f *= i
        return f

n = int(input("Ingresa un número: "))
obj = Factorial(n)
print("El factorial es:", obj.calcular())