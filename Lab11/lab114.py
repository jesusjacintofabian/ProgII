    """
    Ejercicio 114 — Consulta y visualización de registros en MySQL

Escriba un programa en Python que establezca una conexión con la base de 
datos mydatabase de un servidor MySQL utilizando mysql.connector. 
El programa debe consultar todos los registros almacenados en la tabla 
customers mediante una sentencia SELECT. Luego, debe mostrar en pantalla 
el nombre y la dirección de cada cliente. 
Si la tabla no contiene registros, debe indicar que no hay registros para 
mostrar. Además, debe manejar posibles errores y cerrar correctamente el 
cursor y la conexión al finalizar el programa.
    
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
            mycursor.execute("SELECT * FROM customers")
            myresult = mycursor.fetchall()
            print("\nRegistros en la tabla 'customers':")
            if len(myresult) == 0:
                print("No hay registros para mostrar.")
            else:
                for i, row in enumerate(myresult, 1):
                    print(f"[{i}] Nombre: {row[0]} | Dirección: {row[1]}")
        except Error as e:
            print(f"Error al consultar registros: {e}")
        finally:
            mycursor.close()
    except Error as err:
        print(f"Ocurrió un error de conexión: {err}")
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()
            print("Conexión cerrada.")
