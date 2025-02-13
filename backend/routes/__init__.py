from flask import Flask
from config import Config
from models import db, bcrypt
from routes.auth import auth_bp

#Need to register routes here if a new file is created


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp)

    return app