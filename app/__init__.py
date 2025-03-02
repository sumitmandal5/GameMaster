# Initializes the Flask app.

from flask import Flask
from flask_cors import CORS
from app.routes import router


def create_app():
    app = Flask(__name__)
    #CORS(app, origins=["http://localhost:4200"])
    CORS(app,origins=["*"])
    app.register_blueprint(router)  # Register routes
    return app
