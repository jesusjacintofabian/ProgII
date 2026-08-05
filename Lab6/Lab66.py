  """
  Ejercicio 6.7 — Uso de while y continue

Escriba un programa en Python que utilice un ciclo while 
para recorrer los números del 1 al 6. 
El programa debe utilizar la instrucción continue para omitir 
el número 3 y mostrar en pantalla todos los demás números.
    
  """
i = 0
while i < 6:
  i += 1
  if i == 3:
    continue
  print(i)