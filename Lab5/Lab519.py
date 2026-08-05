# Lab519: Utiliza un diccionario para almacenar información de un automóvil, agrega un nuevo campo y muestra el resultado.
# Lab519.py
thisdict = {
    "brand": "Ford",
    "model": "Mustang",
    "year": 1964
}

thisdict.update({"color": "red"})
print(thisdict)