#!/usr/bin/env python3
import sys
from datetime import datetime

DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

for linea in sys.stdin:
    linea = linea.strip()
    if not linea:
        continue
    
    partes = linea.split(",")
    if partes[0] == "id" or len(partes) != 8:
        continue

    fecha_hora_str = partes[1]
    cantidad_str = partes[5]
    metodo_pago = partes[7]

    try:
        fecha_obj = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M:%S")
        dia_semana = DIAS[fecha_obj.weekday()]
        cantidad = int(cantidad_str)

        clave = f"{metodo_pago}_{dia_semana}"
        print(f"{clave}\t{cantidad}")
    except (ValueError, IndexError):
        continue