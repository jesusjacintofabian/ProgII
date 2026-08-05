    """
    Ejercicio 115 — Actualización de registros en MySQL

Escriba un programa en Python que establezca una conexión con la base de 
datos mydatabase de un servidor MySQL utilizando mysql.connector. 
El programa debe solicitar al usuario el valor actual de una dirección 
y el nuevo valor que desea establecer. Luego, debe actualizar la dirección
de los registros correspondientes en la tabla customers mediante una 
sentencia UPDATE. Finalmente, debe confirmar los cambios con commit() 
e indicar cuántas filas fueron actualizadas. Si ningún registro coincide 
con el valor proporcionado, debe mostrar un mensaje informativo. 
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
        campo_busqueda = input("Actualizar dirección. ¿Valor actual de address?: ")
        nuevo_valor = input("¿Nuevo valor de address?: ")
        sql = "UPDATE customers SET address = %s WHERE address = %s"
        valores = (nuevo_valor, campo_busqueda)
        mycursor.execute(sql, valores)
        mydb.commit()
        print(f"{mycursor.rowcount} fila(s) actualizada(s) correctamente.")
        if mycursor.rowcount == 0:
            print("Ningún registro fue afectado. Revisa los valores proporcionados.")
    except Error as e:
        print(f"Error al actualizar registros: {e}")
    finally:
        mycursor.close()
except Error as err:
    print(f"Ocurrió un error de conexión: {err}")
finally:
    if 'mydb' in locals() and mydb.is_connected():
        mydb.close()
        print("Conexión cerrada.")
