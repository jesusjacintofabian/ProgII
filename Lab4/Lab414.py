# Lab414: Extrae e imprime una parte de un objeto bytearray usando memoryview.
#Extraer parte de un buffer
archivo_binario=bytearray(range(100))
parte=memoryview(archivo_binario)[10:20]
print(parte.tolist())

