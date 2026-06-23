from fpdf import FPDF

contenido = '''
Explicaciones de salidas de laboratorios
======================================

Laboratorio lab111.py
---------------------
Este script se conecta a un servidor MySQL y crea una nueva base de datos llamada "mydatabase". Si la base de datos se crea exitosamente, el script no imprime ningún mensaje en pantalla. Solamente manda información al servidor de base de datos. 

**Salida típica:**
(Sin salida en consola)

**Posibles errores:**
Si la base de datos ya existe, podrías ver el siguiente mensaje de error en la terminal:

    mysql.connector.errors.DatabaseError: 1007 (HY000): Can't create database 'mydatabase'; database exists

Laboratorio lab112.py
---------------------
Este código se conecta a la base de datos "mydatabase" y crea una tabla llamada "customers" con dos campos de texto: "name" y "address". Si la creación es exitosa, no verás mensajes en pantalla.

**Salida típica:**
(Sin salida en consola)

**Posibles errores:**
Si la tabla ya existe, verás el siguiente error:

    mysql.connector.errors.ProgrammingError: 1050 (42S01): Table 'customers' already exists

Laboratorio lab113.py
---------------------
El programa conecta a la base de datos y agrega un registro en la tabla "customers" con los datos ('John', 'Highway 21'). Imprime la cantidad de registros insertados.

**Salida típica:**
    1 record inserted.

Esto significa que un registro fue añadido exitosamente.

Laboratorio lab114.py
---------------------
Este script selecciona y muestra todos los registros de la tabla "customers". Recorre cada registro y lo imprime como una tupla (nombre, dirección).

**Salida típica:**
    ('John', 'Highway 21')

Si existen más registros, se mostrarán todos.

Laboratorio lab115.py
---------------------
Actualiza la dirección de todos los clientes cuya dirección es 'Valley 345' y la cambia por 'Canyon 123'. Imprime la cantidad de registros modificados.

**Salida típica:**
    0 record(s) affected

Esto ocurre si no existen registros con la dirección 'Valley 345'. Si existieran, aquí verías el total de registros cambiados, por ejemplo: "2 record(s) affected".

'''

pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_font("Arial", size=11)
for linea in contenido.split('\n'):
    pdf.multi_cell(0, 7, linea)

pdf.output("Explicaciones_laboratorios.pdf")
print("PDF generado: Explicaciones_laboratorios.pdf")