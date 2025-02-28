from flask import Blueprint, jsonify, send_from_directory, request
from app.services import *

router = Blueprint('api', __name__)

@router.route('/pokemon/random', methods=['GET'])
def get_random_pokemon():
    """Fetch a random Pokemon"""
    data = get_random_pokemon_data()
    return jsonify(data)

@router.route('/static/silhouettes/<path:filename>')
def serve_static_silhouettes(filename):
    return send_from_directory('../static/silhouettes', filename)

@router.route('/pokemon/guess', methods=['POST'])
def guess_pokemon():
    """Check if the player guessed correct name and return result"""
    data = request.json
    pokemon_id = data.get("id")
    guessed_name = data.get("guessedName")

    if not pokemon_id :
        return jsonify({"error": "Missing required field id"}), 400

    if not guessed_name :
        return jsonify({"error": "Missing required field guessedName"}), 400

    result = check_pokemon_guess(pokemon_id, guessed_name)
    return jsonify(result)

@router.route('/static/realImages/<path:filename>')
def serve_static_realImages(filename):
    return send_from_directory('../static/realImages', filename)