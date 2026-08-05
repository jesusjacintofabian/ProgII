# Lab411: Usa un frozenset como clave en un diccionario e imprime el valor asociado.
#Clave de diccionario
categorias= frozenset(["Frutas","Verduras",])
inventario={categorias:"seccion A"}
print(inventario[categorias])

