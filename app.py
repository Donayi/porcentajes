from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///porcentajes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Porcentaje(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto = db.Column(db.Integer, nullable=False)
    indice = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'producto': self.producto,
            'indice': self.indice,
            'valor': self.valor
        }

def init_db():
    with app.app_context():
        db.create_all()
        # Insertar valores predeterminados si la tabla está vacía
        if not Porcentaje.query.first():
            valores_default = [
                (1, 1, 100), (2, 1, 60), (3, 1, 50), (4, 1, 40), (5, 1, 30), (6, 1, 30),
                (2, 2, 40), (3, 2, 30), (4, 2, 30), (5, 2, 25), (6, 2, 25),
                (3, 3, 20), (4, 3, 20), (5, 3, 20), (6, 3, 20),
                (4, 4, 10), (5, 4, 15), (6, 4, 15),
                (5, 5, 10), (6, 5, 5),
                (6, 6, 5)
            ]
            for prod, ind, val in valores_default:
                db.session.add(Porcentaje(producto=prod, indice=ind, valor=val))
            db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/porcentajes', methods=['GET'])
def get_porcentajes():
    porcentajes = Porcentaje.query.all()
    return jsonify([p.to_dict() for p in porcentajes])

@app.route('/api/guardar', methods=['POST'])
def guardar_porcentajes():
    datos = request.json
    try:
        # Borrar datos existentes
        Porcentaje.query.delete()
        # Insertar nuevos datos
        for item in datos:
            porcentaje = Porcentaje(
                producto=item['producto'],
                indice=item['indice'],
                valor=item['valor']
            )
            db.session.add(porcentaje)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/reiniciar', methods=['POST'])
def reiniciar():
    try:
        Porcentaje.query.delete()
        db.session.commit()
        init_db()  # Reiniciar con valores predeterminados
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000, debug=True)