# Programa para generar una matriz identidad de orden N


N = int(input("Introduce un número par: "))


if N % 2 == 0:

    # Generar la matriz identidad
    for i in range(N):
        for j in range(N):

            if i == j:
                print(1, end=" ")
            else:
                print(0, end=" ")

        print()

else:
    print("El número debe ser par")