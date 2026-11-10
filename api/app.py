import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración de base de datos MySQL por variables de entorno
DB_USER = os.getenv('MYSQL_USER', 'usuario')
DB_PASS = os.getenv('MYSQL_PASSWORD', 'password123')
DB_HOST = os.getenv('MYSQL_HOST', 'pipeline_db')
DB_NAME = os.getenv('MYSQL_DATABASE', 'ventas_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de base de datos
class Resultado(db.Model):
    __tablename__ = 'resultados'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clave = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.BigInteger, nullable=False)
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

with app.app_context():
    db.create_all()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

# Endpoint de escritura (CRUD / Carga de datos)
@app.route('/cargar', methods=['POST'])
def cargar():
    data = request.get_json()
    if not data or 'clave' not in data or 'valor' not in data:
        return jsonify({'error': 'Datos incompletos'}), 400
    
    nuevo = Resultado(clave=data['clave'], valor=int(data['valor']))
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({'mensaje': 'Guardado exitosamente', 'id': nuevo.id}), 201

# Endpoint para listar todos los resultados
@app.route('/resultados', methods=['GET'])
def obtener_resultados():
    registros = Resultado.query.all()
    salida = [
        {'id': r.id, 'clave': r.clave, 'valor': r.valor, 'creado_en': r.creado_en}
        for r in registros
    ]
    return jsonify(salida), 200

# Endpoint de filtro por clave (Parte D)
@app.route('/resultados/<clave>', methods=['GET'])
def obtener_resultado_por_clave(clave):
    registro = Resultado.query.filter_by(clave=clave).first()
    if registro:
        return jsonify({'id': registro.id, 'clave': registro.clave, 'valor': registro.valor, 'creado_en': registro.creado_en}), 200
    
    # Búsqueda por coincidencia parcial (ejemplo: 'Efectivo' o 'Lunes')
    registros = Resultado.query.filter(Resultado.clave.like(f"%{clave}%")).all()
    if registros:
        return jsonify([{'id': r.id, 'clave': r.clave, 'valor': r.valor, 'creado_en': r.creado_en} for r in registros]), 200
        
    return jsonify({'error': f'Clave "{clave}" no encontrada'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

    