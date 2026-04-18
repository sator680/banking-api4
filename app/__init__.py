from flask import Flask
from flasgger import Swagger
from app.config import Config
from app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialisation de la base de données
    db.init_app(app)

    # Configuration Swagger
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Banking Transaction API",
            "description": "API de gestion des transactions bancaires — Flask + Neon PostgreSQL",
            "version": "3.0.0",
        },
        "tags": [
            {"name": "Utilisateurs", "description": "Gestion des utilisateurs"},
            {"name": "Transactions",  "description": "Dépôts, retraits et historique"},
        ],
        "securityDefinitions": {
            "AdminKey": {
                "type": "apiKey",
                "in": "header",
                "name": "X-Admin-Key",
            }
        },
    }
    Swagger(app, template=swagger_template)

    # Enregistrement des routes
    from app.controllers.user_controller import user_bp
    app.register_blueprint(user_bp, url_prefix="/api/users")

    # Création automatique des tables dans Neon
    with app.app_context():
        db.create_all()

    return app
