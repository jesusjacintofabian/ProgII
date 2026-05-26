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
