from flask import Blueprint, request, jsonify, render_template
from models import db, User, bcrypt

from datetime import datetime, timedelta
import os
from flask_mailman import EmailMessage
import uuid

import traceback

music_bp = Blueprint('music', __name__, template_folder="../templates")



@music_bp.route('/get-music-owned', methods=['GET'])
def get_music_owned():
    data = request.json
    user = User.query.filter_by(id=data['id']).first()
    print(user, data['id'])
    if user:
        if user.music:
            return jsonify({'message': 'success', "music": "" + user.music})
        else:
            return jsonify({'message': 'success', "music": ""})
    return jsonify({'message': 'denied'}), 401


@music_bp.route('/get-music-selected', methods=['GET'])
def get_music_selected():
    data = request.json
    user = User.query.filter_by(id=data['id']).first()
    print(user, data['id'])
    if user:
        if user.music_selected:
            return jsonify({'message': 'success', "music": "" + user.music_selected})
        else:
            return jsonify({'message': 'success', "music": ""})
    return jsonify({'message': 'denied'}), 401

@music_bp.route('/set-music-owned', methods=['POST'])
def set_music_owned():
    data = request.json
    user = User.query.filter_by(id=data['id']).first()
    if user:
        user.music = data['music']
        db.session.commit()
        return jsonify({'message': 'success'})
    return jsonify({'message': 'denied'}), 401


@music_bp.route('/set-music-selected', methods=['POST'])
def set_music_selected():
    data = request.json
    user = User.query.filter_by(id=data['id']).first()
    if user:
        user.music_selected = data['music']
        db.session.commit()
        return jsonify({'message': 'success'})
    return jsonify({'message': 'denied'}), 401