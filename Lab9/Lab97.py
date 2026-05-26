from typing import final

class Padre:
    @final
    def metodo_sagrado(self):
        print("No me cambies.")

class Hijo(Padre):
    # Un linter (como MyPy) marcará esto como ERROR:
    def metodo_sagrado(self):
        print("Intentando cambiarlo.")