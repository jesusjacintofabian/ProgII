    """
    Ejercicio 94 — Uso de métodos estáticos

Escriba un programa en Python que defina una clase llamada Calculadora 
con un método estático sumar() que reciba dos números y devuelva su suma.
El método debe utilizar el decorador @staticmethod y poder ser llamado 
directamente desde la clase sin necesidad de crear una instancia. 
Finalmente, realice una suma y muestre el resultado en pantalla.

    """

class Calculadora:
    @staticmethod
    def sumar(a, b):
        return a + b  # No usa 'self' ni 'cls'

# Se llama directamente sin instanciar
resultado = Calculadora.sumar(5, 3)

# Prueba
print(resultado)  # 8