
from flask import Blueprint, request, jsonify, render_template
from models import db, User, bcrypt

from datetime import datetime
import os
from flask_mailman import EmailMessage
import uuid

profiles_bp = Blueprint('profiles', __name__)

@profiles_bp.route('/profile/<uuid:user_uuid>', methods=['GET'])
def getProfile(user_uuid):
    print(user_uuid)
    users = User.query.with_entities(User.uuid_user).all()  # Fetch all UUIDs
    print(users)
    user = User.query.filter_by(uuid_user=str(user_uuid)).first()
    print(user)
    if user:
        return jsonify({"username": user.username, "id": user.id, "avatar": user.avatar})
    return jsonify({'message': 'User doesn\'t exist'}), 401