
# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

load_dotenv()

# Extensions (no app bound yet)
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # Config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'change-me')

    # Bind extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register blueprints ONLY after extensions are bound
    with app.app_context():
        from .routes import main as main_bp
        from .routes_customer import cust as cust_bp
        app.register_blueprint(main_bp)
        app.register_blueprint(cust_bp)

    # (Optional) quick visibility
    print("DB URI in use:", app.config['SQLALCHEMY_DATABASE_URI'])
    return app
