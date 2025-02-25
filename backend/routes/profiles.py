from flask import Blueprint, request, jsonify, render_template
from models import db, User, bcrypt

from datetime import datetime
import os
from flask_mailman import EmailMessage
import uuid

profiles_bp = Blueprint('profiles', __name__)

@profiles_bp.route('/profile/<uuid:user_uuid>', methods=['GET'])
def getProfile(user_uuid):
    user = User.query.filter_by(uuid_user=str(user_uuid)).first()
    if user:
        return jsonify({"username": user.username, "id": user.id, "avatar": user.avatar})
    return jsonify({'message': 'User doesn\'t exist'}), 401

@profiles_bp.route('/profile/<uuid:user_uuid>', methods=['POST'])
def updateProfile(user_uuid):
    user = User.query.filter_by(uuid_user=str(user_uuid)).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.json
    if 'username' in data:
        user.username = data['username']
    if 'avatar' in data:
        user.avatar = data['avatar']

    try:
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update profile', 'error': str(e)}), 500