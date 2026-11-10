#!/usr/bin/env python3
import sys
import time
from datetime import datetime

DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

def procesar_secuencial(ruta_csv, ruta_salida):
    totales = {}
    inicio = time.time()

    with open(ruta_csv, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("id,"):
                continue
            
            partes = linea.split(",")
            if len(partes) != 8:
                continue

            try:
                fecha_obj = datetime.strptime(partes[1], "%Y-%m-%d %H:%M:%S")
                dia = DIAS[fecha_obj.weekday()]
                unidades = int(partes[5])
                pago = partes[7]
                clave = f"{pago}_{dia}"

                totales[clave] = totales.get(clave, 0) + unidades
            except (ValueError, IndexError):
                continue

    duracion = time.time() - inicio

    with open(ruta_salida, "w", encoding="utf-8") as out:
        for clave in sorted(totales.keys()):
            out.write(f"{clave}\t{totales[clave]}\n")

    print(f"Secuencial completado en: {duracion:.2f} s")
    return duracion

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python secuencial.py <archivo.csv> [salida.txt]")
        sys.exit(1)
    
    salida = sys.argv[2] if len(sys.argv) > 2 else "salida_secuencial.txt"
    procesar_secuencial(sys.argv[1], salida)