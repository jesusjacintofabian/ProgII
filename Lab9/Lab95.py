class Usuario:
    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad

    @classmethod
    def crear_anonimo(cls):
        # 'cls' es equivalente a usar 'Usuario'
        return cls("Anónimo", 0)

# Uso del constructor alternativo
invitado = Usuario.crear_anonimo()

#Prueba
invitado = Usuario.crear_anonimo()
print(invitado.nombre, invitado.edad)