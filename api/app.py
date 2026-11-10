from flask import Flask, jsonify, request
import mysql.connector
import os
import time

app = Flask(__name__)

def get_db_connection():
    retries = 10
    while retries > 0:
        try:
            return mysql.connector.connect(
                host=os.getenv("DB_HOST", "db"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "secret_password"),
                database=os.getenv("DB_NAME", "hadoop_pipeline")
            )
        except mysql.connector.Error:
            retries -= 1
            time.sleep(2)
    raise Exception("No se pudo conectar a la base de datos.")

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resultados (
            id INT AUTO_INCREMENT PRIMARY KEY,
            clave VARCHAR(255) NOT NULL,
            valor BIGINT NOT NULL,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/resultados", methods=["GET"])
def listar_resultados():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT clave, valor, creado_en FROM resultados")
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(filas), 200

@app.route("/resultados", methods=["POST"])
def guardar_resultado():
    datos = request.get_json()
    if not datos or "clave" not in datos or "valor" not in datos:
        return jsonify({"error": "Parámetros 'clave' y 'valor' requeridos"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO resultados (clave, valor) VALUES (%s, %s)", (datos["clave"], datos["valor"]))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensaje": "Registro insertado"}), 201

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)