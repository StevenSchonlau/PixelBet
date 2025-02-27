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