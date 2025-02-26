from flask import Blueprint, jsonify
from app.services import *

api_bp = Blueprint('api', __name__)

@api_bp.route('/pokemon/random', methods=['GET'])
def get_random_pokemon():
    """Fetch a random Pokemon"""
    data = get_random_pokemon_data()
    return jsonify(data)