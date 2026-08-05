    """
    Ejercicio 111 — Conexión a MySQL y creación de una base de datos

Escriba un programa en Python que establezca una conexión con un servidor
MySQL utilizando la biblioteca mysql.connector. 
El programa debe verificar que la conexión se haya realizado correctamente
y crear una base de datos llamada mydatabase. Además, debe manejar posible
s errores durante la conexión o creación de la base de datos y cerrar 
correctamente el cursor y la conexión al finalizar el programa.
        
    """

import mysql.connector
from mysql.connector import Error

try:
    # Conectar al servidor MySQL
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin123",
    )
    if mydb.is_connected():
        print("Conexión exitosa a MySQL")
    
    mycursor = mydb.cursor()
    try:
        mycursor.execute("CREATE DATABASE mydatabase")
        print("Base de datos 'mydatabase' creada exitosamente.")
    except Error as e:
        print(f"Error al crear la base de datos: {e}")
    finally:
        mycursor.close()
except Error as err:
    print(f"Ocurrió un error de conexión: {err}")
finally:
    if 'mydb' in locals() and mydb.is_connected():
        mydb.close()
        print("Conexión cerrada.")
