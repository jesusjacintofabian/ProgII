import os


os.system("echo Hola Mundo")


# ***** NOTAS *********************
# B605 Bandit detectará el uso de os.system(puede facilitar ataque de inyeccion)
# /bin/sh en linux   cmd.exe windows


#B607 El comando echo se ejecuta sin especificar la ruta completa
# como no tiene ruta definida pueden ejecutar un programa diferente al esperado
#/bin/echo Hola mundo