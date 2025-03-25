from flask import Blueprint, request, jsonify, render_template
from models import db, User, bcrypt

from datetime import datetime
import os
from flask_mailman import EmailMessage
import uuid

profiles_bp = Blueprint('profiles', __name__)


@profiles_bp.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    users_data = [{
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar,
        "uuid_user": user.uuid_user
    } for user in users]
    return jsonify(users_data), 200


@profiles_bp.route('/profile/<uuid:user_id>', methods=['GET'])
def getProfile(user_id):
    user = User.query.filter_by(id=str(user_id)).first()
    if user:
        return jsonify({"username": user.username, "id": user.id, "avatar": user.avatar, "net_worth": user.net_worth})
    return jsonify({'message': 'User doesn\'t exist'}), 401

@profiles_bp.route('/profile/<uuid:user_id>', methods=['POST'])
def updateProfile(user_id):
    user = User.query.filter_by(id=str(user_id)).first()
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
    


@profiles_bp.route('/set-user-notification-preferences', methods=['POST'])
def set_user_notification_preferences():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.notification_preference = data['preference']
    try:
        db.session.commit()
        return jsonify({'message': 'Preference updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update preference', 'error': str(e)}), 500
    
@profiles_bp.route('/get-user-notification-preferences', methods=['GET'])
def get_user_notification_preferences():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    try:
        return jsonify({'preference': user.notification_preference})
    except Exception as e:
        return jsonify({'message': 'Failed to get preference', 'error': str(e)}), 500