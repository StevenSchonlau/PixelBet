from flask import Flask
from config import Config
from models import db, bcrypt
from routes.auth import auth_bp
from routes.profiles import profiles_bp
from routes.friends import friends_bp
from routes.game import game_bp

from flask_mailman import Mail
#Need to register routes here if a new file is created


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    mail = Mail(app)
    mail.init_app(app)  # Initialize Flask-Mailman

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(friends_bp)
    app.register_blueprint(game_bp)

    return app