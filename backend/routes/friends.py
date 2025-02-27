from flask import Blueprint, request, jsonify, render_template
from models import db, User, bcrypt

from datetime import datetime
import os
from flask_mailman import EmailMessage
import uuid

friends_bp = Blueprint('friends', __name__)



@friends_bp.route('/search/<string:username>', methods=['GET'])
def search_for_friend(username):
    friend = User.query.filter_by(username=str(username)).first()
    if friend:
        return jsonify({"username": friend.username, "id": friend.id}), 200
    return jsonify({"message": "user not found"}), 400

@friends_bp.route('/friends/<uuid:user_id>', methods=['GET'])
def get_friends(user_id):
    user = User.query.filter_by(id=str(user_id)).first()

    try:
        friends = user.friends
        print(friends)
        if friends:
            friend_data = [{
                "username": friend.username,
                "id": friend.id
            } for friend in friends]
            return jsonify(friend_data), 200
        return jsonify({"message": "No friends found"}), 201
    except:
        return jsonify({"message": "Failed"}), 400
        


@friends_bp.route('/is-friend/<uuid:user_id>/<uuid:friend_id>', methods=['GET'])
def is_friend(user_id, friend_id):
    user = User.query.filter_by(id=str(user_id)).first()
    friend = User.query.filter_by(id=str(friend_id)).first()

    try:
        if user.is_friend(friend):
            return jsonify({'is_friend': True}), 200
        else:
            return jsonify({'is_friend': False}), 200
    except:
        return jsonify({'message': "Couldn't find user or friend"}), 400


@friends_bp.route('/friend-request/<uuid:user_id>/<uuid:friend_id>', methods=['POST'])
def request_friend(user_id, friend_id):
    user = User.query.filter_by(id=str(user_id)).first()
    friend = User.query.filter_by(id=str(friend_id)).first()

    try:
        result = user.send_friend_request(friend)
        if not result:
            return jsonify({'message': 'A request has already been sent'}), 400
        return jsonify({'message': 'Request sent!'}), 200
    except:
        return jsonify({"message": "Failed"}), 400


@friends_bp.route('/pending-sent/<uuid:user_id>', methods=['GET'])
def get_pending_sent(user_id):
    user = User.query.filter_by(id=str(user_id)).first()
    requests = user.pending_sent_requests

    try:
        pending_friends = []
        for request in requests:
            print(request.friend_id)
            pending_friends.append(User.query.filter_by(id=request.friend_id).first())

        if pending_friends:
            pending_data = [{
                "username": friend.username,
                "id": friend.id
            } for friend in pending_friends]
            return jsonify(pending_data), 200
        return jsonify({"message": "No pending requests"}), 201
    except:
        return jsonify({"message": "Failed"}), 400


@friends_bp.route('/pending-received/<uuid:user_id>', methods=['GET'])
def get_pending_received(user_id):
    user = User.query.filter_by(id=str(user_id)).first()
    requests = user.pending_received_requests

    try:
        pending_friends = []
        for request in requests:
            print(request.friend_id)
            pending_friends.append(User.query.filter_by(id=request.friend_id).first())

        if pending_friends:
            pending_data = [{
                "username": friend.username,
                "id": friend.id
            } for friend in pending_friends]
            return jsonify(pending_data), 200
        return jsonify({"message": "No pending requests"}), 201
    except:
        return jsonify({"message": "Failed"}), 400


@friends_bp.route('/reject-request/<uuid:user_id>/<uuid:friend_id>', methods=['POST'])
def reject_request(user_id, friend_id):
    user = User.query.filter_by(id=str(user_id)).first()
    friend = User.query.filter_by(id=str(friend_id)).first()

    try:
        result = user.reject_friend_request(friend)
        if result:
            return jsonify({"message": "Success!"}), 200
        return jsonify({"message": "Failed to cancel"}), 400
    except:
        return jsonify({"message": "Failed to cancel"}), 400


@friends_bp.route('/accept-request/<uuid:user_id>/<uuid:friend_id>', methods=['POST'])
def accept_request(user_id, friend_id):
    user = User.query.filter_by(id=str(user_id)).first()
    friend = User.query.filter_by(id=str(friend_id)).first()

    try:
        result = user.accept_friend_request(friend)
        if result:
            return jsonify({"message": "Success!"}), 200
        return jsonify({"message": "Failed to accept"}), 400
    except:
        return jsonify({"message": "Failed to accept"}), 400


@friends_bp.route('/remove-friend/<uuid:user_id>/<uuid:friend_id>', methods=['POST'])
def remove_friend(user_id, friend_id):
    user = User.query.filter_by(id=str(user_id)).first()
    friend = User.query.filter_by(id=str(friend_id)).first()

    try:
        if user.remove_friend(friend):
            return jsonify({"message": "Success!"}), 200
        return jsonify({"message": "Failed"}), 400
    except:
        return jsonify({"message": "Failed"}), 400