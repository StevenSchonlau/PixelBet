from flask import Flask
from config import Config
from models import db, bcrypt
from routes.auth import auth_bp
from routes.profiles import profiles_bp
from routes.friends import friends_bp
from routes.game import game_bp
from routes.music import music_bp
from routes.achievements import achievements_bp
from routes.sponsors import sponsor_bp
from routes.chat import chat_bp


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
    app.register_blueprint(music_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(friends_bp)
    app.register_blueprint(game_bp, url_prefix="/game")
    app.register_blueprint(achievements_bp, url_prefix="/achievements")
    app.register_blueprint(sponsor_bp)
    app.register_blueprint(chat_bp)

    return app