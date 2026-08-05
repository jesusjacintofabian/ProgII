# Lab622: Usa el módulo datetime para mostrar la fecha y hora actual, y crear una fecha personalizada. Imprime año y día de la semana.
import datetime

x = datetime.datetime.now()
print(x)

#retorna en formato: año, mes, día, hora, minuto, segundo y microsegundo.

print(x.year)
print(x.strftime("%A"))
#imprime año y dia de semana en ingles

y = datetime.datetime(2010, 5, 11)
print(y)
#crear fecha personalizada con formado año, mes, dia