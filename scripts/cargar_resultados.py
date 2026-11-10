import sys
import requests

API_URL = "http://api:5000/resultados"

def cargar(ruta_archivo):
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        for linea in f:
            partes = linea.strip().split("\t")
            if len(partes) == 2:
                clave, valor = partes[0], int(partes[1])
                res = requests.post(API_URL, json={"clave": clave, "valor": valor})
                print(f"[{res.status_code}] {clave}: {valor}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cargar(sys.argv[1])
    else:
        print("Uso: python3 cargar_resultados.py <ruta_archivo_part>")