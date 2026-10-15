"""Construct the Flask app, register API services, and initialize the database."""

import os
from flask import Flask
from backend.app.config import config_by_name
from backend.app.extensions import db, cors
from backend.app.api.routes import api_bp
from backend.app.services.db_seeder import seed_database_if_empty

def create_app(config_name=None):
    if not config_name:
        config_name = os.getenv("FLASK_ENV", "development")
        
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))
    
    # Initialize extensions
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Create tables and seed initial database
    with app.app_context():
        db.create_all()
        seed_database_if_empty(app)
        
    return app
