# Initializes the Flask app.

from flask import Flask, jsonify
from flask_cors import CORS
from app.routes import router


def create_app():
    app = Flask(__name__)
    #CORS(app, origins=["http://localhost:4200"])
    CORS(app,origins=["*"])
    app.register_blueprint(router)  # Register routes

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app
