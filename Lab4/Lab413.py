# Lab413: Manipula un arreglo tipo bytearray, cámbiale la primera letra por código ASCII y muestra el resultado.
#Manipulacion de Bytes
datos= bytearray(b"Hola Mundo")
vista= memoryview(datos)
vista[0]= 104 #Cambia 'H' por 'h' (ASCII 104)
print(datos) 


