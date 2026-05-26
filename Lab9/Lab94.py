class Calculadora:
    @staticmethod
    def sumar(a, b):
        return a + b  # No usa 'self' ni 'cls'

# Se llama directamente sin instanciar
resultado = Calculadora.sumar(5, 3)

# Prueba
print(resultado)  # 8