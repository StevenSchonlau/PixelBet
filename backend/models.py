import uuid
from sqlalchemy.dialects.mysql import CHAR
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

#add object models here!

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    #used for unique links
    uuid_user = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    #timestamp for sent links
    sent_time_stamp = db.Column(db.DateTime, default=datetime.utcnow)
    email_confirmed = db.Column(db.Boolean, default=False)