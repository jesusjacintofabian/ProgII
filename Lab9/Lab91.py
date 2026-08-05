    """
    Ejercicio 91 — Clases abstractas y métodos abstractos

Escriba un programa en Python que defina una clase abstracta llamada 
Vehiculo utilizando el módulo abc. La clase debe contener un método 
abstracto arrancar(), que obligatoriamente deberá ser implementado 
por las clases que hereden de ella, y un método normal pitar() 
que muestre un mensaje. Luego, 
cree una clase Moto que herede de Vehiculo e implemente el método 
arrancar(). Finalmente, cree un objeto de la clase Moto y utilice 
sus métodos para mostrar los mensajes correspondientes.
    
    """


from abc import ABC, abstractmethod

class Vehiculo(ABC):  # Heredar de ABC la hace abstracta

    @abstractmethod
    def arrancar(self):
        """Método abstracto: obligatorio implementar en el hijo."""
        pass

    def pitar(self):
        """Método normal: ya tiene lógica heredable."""
        print("¡Beep beep!")

class Moto(Vehiculo):
    def arrancar(self):
        print("La moto ha arrancado.")

# Uso
# mi_vehiculo = Vehiculo()  # ERROR: No se puede instanciar
mi_moto = Moto()
mi_moto.arrancar()  # Imprime: La moto ha arrancado.
mi_moto.pitar()     # Imprime: ¡Beep beep!