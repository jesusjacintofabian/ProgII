    """
    Ejercicio 113 — Inserción de registros en una tabla MySQL

Escriba un programa en Python que establezca una conexión con la base de 
datos mydatabase de un servidor MySQL utilizando mysql.connector. 
El programa debe solicitar al usuario el nombre y la dirección de un 
cliente, e insertar estos datos en la tabla customers. 
Luego, debe confirmar los cambios mediante commit() y mostrar la 
cantidad de registros insertados. 
Además, debe manejar posibles errores y cerrar correctamente el cursor y 
la conexión al finalizar el programa.
        
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
        nombre = input("Ingresa el nombre del cliente: ")
        direccion = input("Ingresa la dirección del cliente: ")
        sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
        val = (nombre, direccion)
        mycursor.execute(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "registro insertado.")
    except Error as e:
        print(f"Error al insertar el registro: {e}")
    finally:
        mycursor.close()
except Error as err:
    print(f"Ocurrió un error de conexión: {err}")
finally:
    if 'mydb' in locals() and mydb.is_connected():
        mydb.close()
        print("Conexión cerrada.")
