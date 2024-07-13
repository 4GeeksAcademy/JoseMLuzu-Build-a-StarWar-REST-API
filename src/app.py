import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, Characters, Starships

app = Flask(__name__)
app.url_map.strict_slashes = False

# Configuración de la URL de la base de datos
db_url = os.getenv("DATABASE_URL", "sqlite:////tmp/test.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización de extensiones
db.init_app(app)
Migrate(app, db)
CORS(app)
setup_admin(app)

# Manejo de errores - maneja errores personalizados como objetos JSON
@app.errorhandler(APIException)
def handle_api_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# Generación de sitemap con todos los endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Endpoints para usuarios
@app.route('/user', methods=['GET'])
def get_all_users():
    all_users = User.query.all()
    users_serialized = [user.serialize() for user in all_users]
    return jsonify({"data": users_serialized}), 200

@app.route('/user', methods=['POST'])
def new_user():
    body = request.get_json()
    if not body or "email" not in body or "password" not in body or "is_active" not in body:
        return jsonify({"msg": "Los campos email, password e is_active son obligatorios"}), 400
    
    new_user = User(email=body["email"], password=body["password"], is_active=body["is_active"])
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"data": new_user.serialize()}), 201

@app.route('/user/<int:id>', methods=['GET'])
def get_single_user(id):
    single_user = User.query.get(id)
    if single_user is None:
        return jsonify({"msg": f"El usuario con el ID: {id} no existe"}), 404
    return jsonify({"data": single_user.serialize()}), 200

# Endpoints para planetas
@app.route('/planet', methods=['GET'])
def get_all_planets():
    all_planets = Planets.query.all()
    planets_serialized = [planet.serialize() for planet in all_planets]
    return jsonify({"data": planets_serialized}), 200

@app.route('/planet', methods=['POST'])
def new_planet():
    body = request.get_json()
    if not body or "name" not in body or "population" not in body:
        return jsonify({"msg": "Los campos name y population son obligatorios"}), 400
    
    new_planet = Planets(name=body["name"], population=body["population"])
    db.session.add(new_planet)
    db.session.commit()

    return jsonify({"msg": "Nuevo planeta creado", "data": new_planet.serialize()}), 201

@app.route('/planet/<int:id>', methods=['GET'])
def get_single_planet(id):
    single_planet = Planets.query.get(id)
    if single_planet is None:
        return jsonify({"msg": f"El planeta con el ID: {id} no existe"}), 404
    return jsonify({"data": single_planet.serialize()}), 200

@app.route('/planet/<int:id>', methods=["PUT"])
def update_planet(id):
    update_planet = Planets.query.get(id)
    if update_planet is None:
        return jsonify({"msg": f"El planeta con el ID {id} no fue encontrado"}), 404
    
    body = request.get_json()
    if "name" in body:
        update_planet.name = body["name"]
    if "population" in body:
        update_planet.population = body["population"]
    if "terrain" in body:
        update_planet.terrain = body["terrain"]
    if "climate" in body:
        update_planet.climate = body["climate"]
    
    db.session.commit()
    return jsonify({"data": update_planet.serialize()}), 200

@app.route('/planet/<int:id>', methods=["DELETE"])
def delete_planet(id):
    delete_planet = Planets.query.get(id)
    if delete_planet is None:
        return jsonify({"msg": f"El planeta con el ID {id} no existe"}), 404
    
    db.session.delete(delete_planet)
    db.session.commit()
    return jsonify({"msg": "El planeta se ha eliminado con éxito"}), 200

# Endpoints para personajes
@app.route('/character', methods=['GET'])
def get_all_characters():
    all_characters = Characters.query.all()
    characters_serialized = [character.serialize() for character in all_characters]
    return jsonify({"data": characters_serialized}), 200

@app.route('/character', methods=['POST'])
def new_character():
    body = request.get_json()
    if not body or "name" not in body or "height" not in body or "mass" not in body:
        return jsonify({"msg": "Los campos name, height y mass son obligatorios"}), 400
    
    new_character = Characters(name=body["name"], height=body["height"], mass=body["mass"])
    db.session.add(new_character)
    db.session.commit()
    return jsonify({"data": new_character.serialize()}), 201

@app.route('/character/<int:id>', methods=['GET'])
def get_single_character(id):
    single_character = Characters.query.get(id)
    if single_character is None:
        return jsonify({"msg": f"El personaje con el ID: {id} no existe"}), 404
    return jsonify({"data": single_character.serialize()}), 200

@app.route('/character/<int:id>', methods=["PUT"])
def update_character(id):
    update_character = Characters.query.get(id)
    if update_character is None:
        return jsonify({"msg": f"El personaje con el ID {id} no fue encontrado"}), 404
    
    body = request.get_json()
    if "name" in body:
        update_character.name = body["name"]
    if "last_name" in body:  # Corregido de "name" a "last_name"
        update_character.last_name = body["last_name"]  # Asignación corregida
    if "height" in body:
        update_character.height = body["height"]
    if "mass" in body:
        update_character.mass = body["mass"]
    
    db.session.commit()
    return jsonify({"data": update_character.serialize()}), 200

@app.route('/character/<int:id>', methods=["DELETE"])
def delete_character(id):
    delete_character = Characters.query.get(id)
    if delete_character is None:
        return jsonify({"msg": f"El personaje con el ID {id} no existe"}), 404
    
    db.session.delete(delete_character)
    db.session.commit()
    return jsonify({"msg": "El personaje se ha eliminado con éxito"}), 200

# Endpoints para naves estelares
@app.route('/starship', methods=["GET"])
def get_all_starships():
    all_starships = Starships.query.all()
    starships_serialized = [starship.serialize() for starship in all_starships]
    return jsonify({"data": starships_serialized}), 200

@app.route('/starship', methods=['POST'])
def new_starship():
    body = request.get_json()
    if not body or "model" not in body or "mass" not in body:
        return jsonify({"msg": "Los campos model y mass son obligatorios"}), 400
    
    new_starship = Starships(model=body["model"], mass=body["mass"])
    db.session.add(new_starship)
    db.session.commit()
    return jsonify({"data": new_starship.serialize()}), 201

@app.route('/starship/<int:id>', methods=['GET'])
def get_single_starship(id):
    single_starship = Starships.query.get(id)
    if single_starship is None:
        return jsonify({"msg": f"La nave con el ID: {id} no existe"}), 404
    return jsonify({"data": single_starship.serialize()}), 200

@app.route('/starship/<int:id>', methods=["PUT"])
def update_starship(id):
    update_starship = Starships.query.get(id)
    if update_starship is None:
        return jsonify({"msg": f"La nave con el ID {id} no fue encontrada"}), 404
    
    body = request.get_json()
    if "model" in body:
        update_starship.model = body["model"]
    if "manufacturer" in body:  # Corregido de "model" a "manufacturer"
        update_starship.manufacturer = body["manufacturer"]  # Asignación corregida
    if "mass" in body:
        update_starship.mass = body["mass"]
    
    db.session.commit()
    return jsonify({"data": update_starship.serialize()}), 200

@app.route('/starship/<int:id>', methods=["DELETE"])
def delete_starship(id):
    delete_starship = Starships.query.get(id)
    if delete_starship is None:
        return jsonify({"msg": f"La nave con el ID {id} no existe"}), 404
    
    db.session.delete(delete_starship)
    db.session.commit()
    return jsonify({"msg": "La nave se ha eliminado con éxito"}), 200

# Si tienes más endpoints o necesitas añadir funcionalidades adicionales, puedes hacerlo aquí

if __name__ == '__main__':
    app.run(debug=True)
