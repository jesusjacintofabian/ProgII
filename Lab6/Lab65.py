  """
  Ejercicio 6.5 — Uso de match para identificar el día de la semana

Escriba un programa en Python que establezca un número correspondiente 
a un día de la semana y utilice la estructura match para determinar y 
mostrar el nombre del día. El programa debe mostrar Lunes para el número 
1, Martes para el 2, Miércoles para el 3, Jueves para el 4, Viernes 
para el 5, Sábado para el 6 y Domingo para el 7.
  
  """

dia = 4
match dia:
  case 1:
    print("Lunes")
  case 2:
    print("Martes")
  case 3:
    print("Miercoles")
  case 4:
    print("Jueves")
  case 5:
    print("Viernes")
  case 6:
    print("Sabado")
  case 7:
    print("Domingo")