from flask import Blueprint, request, jsonify
from models import db, User, bcrypt

#all REST API calls for login/auth


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'], password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered!', 'user_id': user.id})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Login successful', 'user_id': user.id})
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/get-user', methods=['GET'])
def get_user():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    print(user)
    if user:
        return jsonify({"username": user.username, "id": user.id})
    return jsonify({'message': 'User doesn\'t exist'}), 401