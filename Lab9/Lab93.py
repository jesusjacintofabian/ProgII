class Persona:
    contador = 0

    def __init__(self):
        Persona.contador += 1

p1 = Persona()
p2 = Persona()
p3 = Persona()
print(Persona.contador)  # 3