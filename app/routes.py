from flask import Blueprint, jsonify, send_from_directory
from app.services import *

router = Blueprint('api', __name__)

@router.route('/pokemon/random', methods=['GET'])
def get_random_pokemon():
    """Fetch a random Pokemon"""
    data = get_random_pokemon_data()
    return jsonify(data)

@router.route('/static/silhouettes/<path:filename>')
def serve_static(filename):
    return send_from_directory('../static/silhouettes', filename)