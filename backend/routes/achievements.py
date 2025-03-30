from flask import Blueprint, request, jsonify
from models import db, User
from achievement_sys import achievement_sys

achievements_bp = Blueprint('achievements', __name__)

@achievements_bp.route('/<uuid:user_id>', methods=['GET'])
def get_user_achievements(user_id):
    user = User.query.filter_by(id=str(user_id)).first()
    if user:
        achievements_list = []
        # If user.achievements is None, default to an empty list.
        for achievement_id in (user.achievements or []):
            achievement = achievement_sys.global_achievements.get(achievement_id)
            if achievement:
                achievements_list.append({
                    'id': achievement.id,
                    'title': achievement.title,
                    'description': achievement.description,
                    'icon_path': achievement.icon_path,
                })
        return jsonify({'achievements': achievements_list}), 200
    return jsonify({'message': "User doesn't exist"}), 404

@achievements_bp.route('/definitions', methods=['GET'])
def get_achievement_definitions():
    """
    Return every achievement’s ID, title, description, and icon_path so the frontend
    knows all possible milestones and their unlock rules.
    """
    payload = [
        {
            'id': ach.id,
            'title': ach.title,
            'description': ach.description,
            'icon_path': ach.icon_path,
        }
        for ach in achievement_sys.global_achievements.values()
    ]
    return jsonify({'achievements': payload}), 200

@achievements_bp.route('/acknowledge', methods=['POST'])
def acknowledge_achievement():
    data = request.get_json()
    user_id = data.get('user_id')
    achievement_id = data.get('achievement_id')
    
    print("Received payload:", data)  # Debug print
    
    user = User.query.filter_by(id=str(user_id)).first()
    if not user:
        print("User not found!")
        return jsonify({'message': 'User not found'}), 404

    if user.achievements is None:
        user.achievements = []
    
    if achievement_id not in user.achievements:
        user.achievements.append(achievement_id)
        db.session.commit()
        print(f"Achievement {achievement_id} added for user {user_id}")
        return jsonify({'message': 'Achievement acknowledged'}), 200
    else:
        print(f"Achievement {achievement_id} already acknowledged for user {user_id}")
        return jsonify({'message': 'Achievement already acknowledged'}), 200


