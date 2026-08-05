"""
Ejercicio 112 — Conexión a MySQL y creación de una tabla

Escriba un programa en Python que establezca una conexión con una base de
datos llamada mydatabase en un servidor MySQL utilizando la biblioteca 
mysql.connector. El programa debe verificar que la conexión se haya 
realizado correctamente y crear una tabla llamada customers con los 
campos name y address. Además, debe manejar posibles errores durante la 
conexión o creación de la tabla y cerrar correctamente el cursor y la 
conexión al finalizar el programa.

"""

import mysql.connector
from mysql.connector import Error

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin123",
        database="mydatabase",
    )
    if mydb.is_connected():
        print("Conectado exitosamente a la base de datos 'mydatabase'")

    mycursor = mydb.cursor()
    try:
        mycursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                name VARCHAR(255),
                address VARCHAR(255)
            )
        """)
        print("Tabla 'customers' creada o verificada exitosamente.")
    except Error as e:
        print(f"Error al crear la tabla: {e}")
    finally:
        mycursor.close()
except Error as err:
    print(f"Ocurrió un error de conexión: {err}")
finally:
    if 'mydb' in locals() and mydb.is_connected():
        mydb.close()
        print("Conexión cerrada.")
