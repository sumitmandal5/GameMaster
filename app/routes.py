from flask import Blueprint, jsonify, send_from_directory, request, abort
from flask_restx import Api, Resource, fields
from werkzeug.exceptions import NotFound

from app.services import *
import logging

router = Blueprint('api', __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# for swagger documentation initialize flask-restx
api = Api(router, version="1.0", title="Pokemon API", description="API for Pokemon guessing game")

ns = api.namespace("pokemon", description="Pokemon operations")
static_ns = api.namespace("static", description="getting static contents")

api.add_namespace(ns, path="/pokemon")
api.add_namespace(static_ns, path="/static")

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

error_model = api.model("ErrorResponse", {
    "error": fields.String(description="Error message"),
})


@ns.route("/random")
class RandomPokemon(Resource):
    @api.marshal_with(pokemon_model)
    @api.response(200, 'Success', pokemon_model)
    @api.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Get a random Pokemon silhouette and options for the player to guess from"""
        try:
            data = get_random_pokemon_data()
        except Exception as ex:
            logger.error(f"error in /random: {ex}")
            abort(500, description="Internal server error")
        return data


@static_ns.route("/silhouettes/<path:filename>")
class ServeSilhouettes(Resource):
    @api.response(200, 'Success')
    @api.response(404, 'Not Found', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    def get(self, filename):
        """Serve Pokemon silhouette images"""
        try:
            return send_from_directory("../static/silhouettes", filename)
        except NotFound:
            logger.error(f"Silhouette image not found: {filename}")
            abort(404, description="Silhouette image not found")
        except Exception as ex:
            logger.error(f"Unexpected error serving silhouette image {filename}: {ex}")
            abort(500, description="Internal server error")


@ns.route("/guess")
class GuessPokemon(Resource):
    @api.expect(guess_model)
    @api.marshal_with(response_model)
    @api.response(200, 'Success', response_model)
    @api.response(400, 'Bad Request', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    def post(self):
        """Check if the player guessed correct name and return result"""
        data = request.json
        pokemon_id = data.get("id")
        guessed_name = data.get("guessedName")

        if not pokemon_id:
            logger.error("Missing required field: id")
            abort(400, description="Missing required field: id")

        if not guessed_name:
            logger.error("Missing required field: guessedName")
            abort(400, description="Missing required field: guessedName")

        if pokemon_id<=0 or pokemon_id>50:
            logger.error(f"Invalid Pokemon ID {pokemon_id}")
            abort(400, description=f"Invalid Pokemon ID {pokemon_id}")

        try:
            result = check_pokemon_guess(pokemon_id, guessed_name)
            if "error" in result:
                logger.error(f"Failed to check guess for Pokemon ID {pokemon_id}: {result['error']}")
                abort(400, description=f"Failed to check guess for Pokemon ID {pokemon_id}")
            return result
        except Exception as ex:
            logger.error(f"Error in /guess: {ex}")
            abort(500, description="Internal server error")

@static_ns.route("/realImages/<path:filename>")
class ServeSilhouettes(Resource):
    @api.response(200, 'Success')
    @api.response(404, 'Not Found', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    def get(self, filename):
        """Serve Pokemon real images"""
        try:
            return send_from_directory("../static/realImages", filename)
        except NotFound:
            logger.error(f"Real image not found: {filename}")
            abort(404, description="Real image not found")
        except Exception as ex:
            logger.error(f"Unexpected error serving real image {filename}: {ex}")
            abort(500, description="Internal server error")