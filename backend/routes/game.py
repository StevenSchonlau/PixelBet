from flask import Blueprint, request, jsonify, render_template
from models import db, User, bcrypt

from datetime import datetime
import os
from flask_mailman import EmailMessage
import uuid

game_bp = Blueprint('game', __name__)

@game_bp.route('/all-net', methods=['GET'])
def get_all_net():
    users = User.query.all()
    
    if users:
        user_data = [{
            "username": user.username,
            "id": user.id,
            "net_worth": user.net_worth
        } for user in users]
        return jsonify(user_data), 200
    else:
        return jsonify({"message": "Failed"}), 400
    
@game_bp.route('/get-net-worth/<uuid:user_id>', methods=['GET']) 
def get_net_worth(user_id):
    user = User.query.filter_by(id=str(user_id)).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'username': user.username,
        'id': user.id,
        'net_worth': user.net_worth
    }), 200
    
@game_bp.route('/update-net-worth/<uuid:user_id>', methods=['POST'])
def update_net_worth(user_id):
    user = User.query.filter_by(id=str(user_id)).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.json
    if 'net_worth' not in data:
        return jsonify({'message': 'Net worth is required'}), 400

    try:
        user.net_worth = data['net_worth']
        db.session.commit()
        return jsonify({'message': 'Net worth updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update net worth', 'error': str(e)}), 500