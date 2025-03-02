from flask import Blueprint, jsonify, send_from_directory, request
from flask_restx import Api, Resource, fields
from app.services import *

router = Blueprint('api', __name__)

# for swagger documentation initialize flask-restx
api = Api(router, version="1.0", title="Pokemon API", description="API for Pokemon guessing game")

ns = api.namespace("pokemon", description="Pokemon operations")
static_ns = api.namespace("static", description="getting static contents")

api.add_namespace(ns, path="/pokemon")

pokemon_model = api.model("RandomPokemon", {
    "id": fields.Integer(description="Pokemon ID"),
    "silhouetteImage": fields.String(description="URL of the Pokemon silhouette image"),
    "options": fields.List(fields.String, description="List of possible Pokemon names"),
})

guess_model = api.model("Guess", {
    "id": fields.Integer(required=True, description="Pokemon ID"),
    "guessedName": fields.String(required=True, description="Guessed Pokemon name"),
})

response_model = api.model("GuessResponse", {
    "correctName": fields.String(description="Correct Pokemon name"),
    "fullImage": fields.String(description="URL of full Pokemon image"),
    "guessCorrect": fields.Boolean(description="True if guess was correct. False otherwise."),
})


@ns.route("/random")
class RandomPokemon(Resource):
    @api.marshal_with(pokemon_model)
    def get(self):
        """Get a random Pokemon silhouette and options"""
        data = get_random_pokemon_data()
        return data


@static_ns.route("/silhouettes/<path:filename>")
class ServeSilhouettes(Resource):
    def get(self, filename):
        """Serve Pokemon silhouette images"""
        return send_from_directory("../static/silhouettes", filename)


@ns.route("/guess")
class GuessPokemon(Resource):
    @api.expect(guess_model)
    @api.marshal_with(response_model)
    def post(self):
        """Check if the player guessed correct name and return result"""
        data = request.json
        pokemon_id = data.get("id")
        guessed_name = data.get("guessedName")

        if not pokemon_id:
            return jsonify({"error": "Missing required field id"}), 400

        if not guessed_name:
            return jsonify({"error": "Missing required field guessedName"}), 400

        result = check_pokemon_guess(pokemon_id, guessed_name)
        return result


@static_ns.route("/realImages/<path:filename>")
class ServeSilhouettes(Resource):
    def get(self, filename):
        """Serve Pokemon real images"""
        return send_from_directory("../static/realImages", filename)
