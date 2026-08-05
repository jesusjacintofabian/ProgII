# Lab58: Filtra de una lista todas las frutas que contienen la letra 'a' y guárdalas en una nueva lista.
fruits = ["apple", "banana", "cherry", "kiwi", "mango"]
newlist = []

for x in fruits:
    if "a" in x:
        newlist.append(x)

print(newlist)