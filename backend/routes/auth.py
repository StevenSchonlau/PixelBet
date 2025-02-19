from flask import Blueprint, request, jsonify
from models import db, User, bcrypt

#all REST API calls for login/auth


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if data['username'] == "":
        return jsonify({'message': 'invalid'})
    elif data['password'] == "":
        return jsonify({'message': 'invalid'})
    elif data['email'] == "":
        return jsonify({'message': 'invalid'})
    elif "@" not in data['email'] or "." not in data['email']:
        return jsonify({'message': 'invalid'})
    try:
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = User(username=data['username'], password=hashed_password, email=data['email'])
        print(user)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User registered!', 'user_id': user.id})
    except:
        return jsonify({'message': 'duplicate'})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Login successful', 'user_id': user.id})
    return jsonify({'message': 'denied'}), 401

@auth_bp.route('/get-user', methods=['GET'])
def get_user():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    print(user)
    if user:
        return jsonify({"username": user.username, "id": user.id})
    return jsonify({'message': 'User doesn\'t exist'}), 401