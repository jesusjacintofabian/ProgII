  """
  Ejercicio 6.2 — Clasificación de calificaciones

Escriba un programa en Python que establezca una calificación numérica
y determine la letra correspondiente según el sistema de evaluación. 
El programa debe asignar una calificación A para valores de 90 o más, 
B para valores de 80 a 89, C para valores de 70 a 79 y D para valores 
de 60 a 69, mostrando el resultado correspondiente en pantalla.

  """

calificacion = 75

if calificacion >= 90:
  print("Resultado: A")
elif calificacion >= 80:
  print("Resultado: B")
elif calificacion >= 70:
  print("Resultado: C")
elif calificacion >= 60:
  print("Resultado: D")