#!/usr/bin/env python3
import sys

clave_actual = None
total_unidades = 0

for linea in sys.stdin:
    linea = linea.strip()
    if not linea:
        continue

    partes = linea.split("\t")
    if len(partes) != 2:
        continue

    clave, cantidad_str = partes

    try:
        cantidad = int(cantidad_str)
    except ValueError:
        continue

    if clave_actual == clave:
        total_unidades += cantidad
    else:
        if clave_actual is not None:
            print(f"{clave_actual}\t{total_unidades}")
        clave_actual = clave
        total_unidades = cantidad

if clave_actual is not None:
    print(f"{clave_actual}\t{total_unidades}")