# Initializes the Flask app.

from flask import Flask
from app.routes import router

def create_app():
    app = Flask(__name__)
    app.register_blueprint(router)  # Register routes
    return app