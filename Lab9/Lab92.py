    """_
    Ejercicio 92 — Clases abstractas como interfaz para encriptación

Escriba un programa en Python que defina una clase abstracta llamada 
Encriptador utilizando el módulo abc. La clase debe establecer los 
métodos abstractos encriptar() y desencriptar(), los cuales deberán ser 
implementados obligatoriamente por las clases que hereden de ella. 
Luego, cree una clase EncriptadorAES que herede de Encriptador e 
implemente ambos métodos para simular el proceso de encriptación y 
desencriptación de datos mediante AES. Finalmente, cree un objeto de 
EncriptadorAES y utilice sus métodos para encriptar y desencriptar un 
mensaje, mostrando los resultados en pantalla.
    
    """

from abc import ABC, abstractmethod

class Encriptador(ABC):  # Actúa como interfaz pura
    @abstractmethod
    def encriptar(self, datos: str) -> str:
        pass

    @abstractmethod
    def desencriptar(self, datos: str) -> str:
        pass

class EncriptadorAES(Encriptador):
    def encriptar(self, datos: str) -> str:
        return f"AES({datos})"

    def desencriptar(self, datos: str) -> str:
        return datos.replace("AES(", "").replace(")", "")

# Si olvidas implementar un método, Python lanzará un TypeError al instanciar.

#Demostración
enc = EncriptadorAES()
print(enc.encriptar("Hola Mundo"))
print(enc.desencriptar("AES(Hola Mundo)"))
