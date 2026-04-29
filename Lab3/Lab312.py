# 1. Literal de bytes (forma mas comun)
my_byte=b"\xFF"

# 2. Constructor bytes a partir de un entero()
my_byte_dos=bytes([255])

# Verificacion
print(type(my_byte)) #<class 'bytes'>
print(my_byte[0]) # 255



