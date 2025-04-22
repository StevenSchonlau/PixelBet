from flask import Blueprint, request, jsonify, render_template
from models import db, User, bcrypt

from decimal import Decimal

from datetime import datetime
import os
from flask_mailman import EmailMessage
import uuid

profiles_bp = Blueprint('profiles', __name__)


def send_email(to_email, subject, message):
    email = EmailMessage(
        subject=subject,
        body=message,
        to=[to_email]
    )
    email.send()
    return "Email sent!"

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
        return jsonify({
            "username": user.username,
            "id": user.id,
            "avatar": user.avatar,
            "net_worth": user.net_worth,
            "active_shirt": user.active_shirt,
            "active_room": user.active_room,
            "owns_shirts_list": user.owns_shirts_list,
            "owns_room_list": user.owns_room_list,
            "active_theme": user.active_theme,
            "owns_themes": user.owns_themes,
            "resolution_width":  user.resolution_width,
            "resolution_height": user.resolution_height,
        })
    return jsonify({'message': 'User doesn\'t exist'}), 401

@profiles_bp.route('/profile/<uuid:user_id>', methods=['POST'])
def updateProfile(user_id):
    user = User.query.filter_by(id=str(user_id)).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.json
    if not data:
        return jsonify({'message': 'Failed to update profile'}), 500
    if 'username' in data:
        user.username = data['username']
    if 'avatar' in data:
        user.avatar = data['avatar']
    if 'active_shirt' in data:
        user.active_shirt = int(data['active_shirt'])
    if 'active_room' in data:
        user.active_room = int(data['active_room'])
    if 'active_theme' in data:
        user.active_theme = int(data['active_theme'])
    if 'resolution' in data:
        try:
            w, h = map(int, data['resolution'].split('x'))
            user.resolution_width  = w
            user.resolution_height = h
        except ValueError:
            return jsonify({'message': "Invalid resolution format, expected 'WIDTHxHEIGHT'"}), 400

    try:
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update profile', 'error': str(e)}), 500
    
@profiles_bp.route('/profile/buyshirt/<uuid:user_id>', methods=['POST'])
def buyShirt(user_id):
    user = User.query.filter_by(id=str(user_id)).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.json
    if not data:
        return jsonify({'message': 'Data not found'}), 404

    user.net_worth -= Decimal(data['cost'])
    user.owns_shirts_list.append(data['shirt'])

    try:
        db.session.commit()
        return jsonify({'message': 'Shirt added successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update profile', 'error': str(e)}), 500

@profiles_bp.route('/profile/buytheme/<uuid:user_id>', methods=['POST'])
def buyTheme(user_id):
    user = User.query.filter_by(id=str(user_id)).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.json
    if not data:
        return jsonify({'message': 'Data not found'}), 404

    user.net_worth -= Decimal(data['cost'])
    user.owns_themes.append(data['theme'])

    try:
        db.session.commit()
        return jsonify({'message': 'Theme added successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update profile', 'error': str(e)}), 500

@profiles_bp.route('/profile/buyroom/<uuid:user_id>', methods=['POST'])
def buyRoom(user_id):
    user = User.query.filter_by(id=str(user_id)).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.json
    if not data:
        return jsonify({'message': 'Data not found'}), 404

    user.net_worth -= Decimal(data['cost'])
    user.owns_room_list.append(data['room'])

    try:
        db.session.commit()
        return jsonify({'message': 'Room added successfully'})
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
    

@profiles_bp.route('/set-user-notification-preferences-results', methods=['POST'])
def set_user_notification_preferences_results():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.notification_preference_result = data['preference']
    try:
        db.session.commit()
        return jsonify({'message': 'Preference updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update preference', 'error': str(e)}), 500
    
@profiles_bp.route('/get-user-notification-preferences-results', methods=['GET'])
def get_user_notification_preferences_results():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    try:
        return jsonify({'preference': user.notification_preference_result})
    except Exception as e:
        return jsonify({'message': 'Failed to get preference', 'error': str(e)}), 500
    

@profiles_bp.route('/set-user-notification-preferences-networth', methods=['POST'])
def set_user_notification_preferences_networth():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.notification_preference_networth = data['preference']
    try:
        db.session.commit()
        return jsonify({'message': 'Preference updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update preference', 'error': str(e)}), 500
    
@profiles_bp.route('/get-user-notification-preferences-networth', methods=['GET'])
def get_user_notification_preferences_networth():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    try:
        return jsonify({'preference': user.notification_preference_networth})
    except Exception as e:
        return jsonify({'message': 'Failed to get preference', 'error': str(e)}), 500


@profiles_bp.route('/set-user-networth-min-max', methods=['POST'])
def set_user_networth_min_max():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.net_worth_min = data['min']
    user.net_worth_max = data['max']
    try:
        db.session.commit()
        return jsonify({'message': 'Preference updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update preference', 'error': str(e)}), 500
    
@profiles_bp.route('/get-user-networth-min-max', methods=['GET'])
def get_user_networth_min_max():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    try:
        return jsonify({'min': user.net_worth_min, 'max': user.net_worth_max})
    except Exception as e:
        return jsonify({'message': 'Failed to get preference', 'error': str(e)}), 500

@profiles_bp.route("/send-networth-email", methods=['POST'])
def send_networth_email():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    try:
        if float(data['min']) == -1:
            send_email(os.getenv('EMAIL_USERNAME', 'your_email@gmail.com'), "Your networth rose!", f"Hello, {user.username}! Your networth is now ${data['nw']:.2f}, which is higher than ${data['max']:.2f}, the amount you set in notifications.") #temporary value of my email
        else:
            send_email(os.getenv('EMAIL_USERNAME', 'your_email@gmail.com'), "Your networth dropped!", f"Hello, {user.username}! Your networth is now ${data['nw']:.2f}, which is lower than ${data['min']:.2f}, the amount you set in notifications.") #temporary value of my email
        return jsonify({'message': "success"})
    except Exception as e:
        return jsonify({'message': 'Failed to send email', 'error': str(e)}), 500

@profiles_bp.route("/send-notification-email", methods=['GET'])
def send_notification_email():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    try:
        send_email(os.getenv('EMAIL_USERNAME', 'your_email@gmail.com'), "Important Upcoming Game", f"Hello, {user.username}! There is an upcoming game in one minute! You can change these settings in your profile.") #temporary value of my email
        return jsonify({'message': "success"})
    except Exception as e:
        return jsonify({'message': 'Failed to send email', 'error': str(e)}), 500


@profiles_bp.route("/send-progress-email", methods=['POST'])
def send_progress_email():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    print(data['id'])
    if not user:
        return jsonify({'message': 'User not found'}), 404
    try:
        music_str = user.music_selected
        if music_str == None:
            music_str = "nothing"
        send_email(os.getenv('EMAIL_USERNAME', 'your_email@gmail.com'), f"{user.username}'s PixelBet Progress", f"Hello, {data['email']}! User {user.username} wanted to send you their progress in Pixel Bet.\nThey currently have ${user.net_worth}, are listening to {music_str}, and last logged in at {user.last_login}.\nYou can send something similar through PixelBet from your profile.") #temporary value of my email
        return jsonify({'message': "success"})
    except Exception as e:
        return jsonify({'message': 'Failed to send email', 'error': str(e)}), 500

@profiles_bp.route("/send-bet-email", methods=['POST'])
def send_bet_email():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    print(data['id'])
    if not user:
        return jsonify({'message': 'User not found'}), 404
    try:
        if data['win'] == True:
            send_email(os.getenv('EMAIL_USERNAME', 'your_email@gmail.com'), "You WON", f"Hello, {user.username}! This email is to notify you that you have won a bet of ${data['amount']:.2f} from {data['wh']}. Keep up the streak!") #temporary value of my email
        else:
            send_email(os.getenv('EMAIL_USERNAME', 'your_email@gmail.com'), "You LOST", f"Hello, {user.username}! This email is to notify you that you have lost a bet of ${data['amount']:.2f} with {data['lh']} to the winner {data['wh']}. Better luck next time!") #temporary value of my email
        return jsonify({'message': "success"})
    except Exception as e:
        return jsonify({'message': 'Failed to send email', 'error': str(e)}), 500



@profiles_bp.route('/set-user-has-time-limit', methods=['POST'])
def set_user_has_time_limit():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.has_time_limit = data['preference']
    try:
        db.session.commit()
        return jsonify({'message': 'Preference updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update preference', 'error': str(e)}), 500
    
@profiles_bp.route('/get-user-has-time-limit', methods=['GET'])
def get_user_has_time_limit():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    try:
        return jsonify({'preference': user.has_time_limit})
    except Exception as e:
        return jsonify({'message': 'Failed to get preference', 'error': str(e)}), 500
    
@profiles_bp.route('/set-user-time-limit', methods=['POST'])
def set_user_time_limit():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.time_limit = data['time limit']
    try:
        db.session.commit()
        return jsonify({'message': 'Preference updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update time limit', 'error': str(e)}), 500
    
@profiles_bp.route('/get-user-time-limit', methods=['GET'])
def get_user_time_limit():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    try:
        return jsonify({'time limit': user.time_limit})
    except Exception as e:
        return jsonify({'message': 'Failed to get time limit', 'error': str(e)}), 500
    

@profiles_bp.route('/set-user-total-time-day', methods=['POST'])
def set_user_total_time_day():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.total_time_day = data['total time']
    try:
        db.session.commit()
        return jsonify({'message': 'Preference updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update time limit', 'error': str(e)}), 500
    
@profiles_bp.route('/get-user-total-time-day', methods=['GET'])
def get_user_total_time_day():
    data = request.json
    user = User.query.filter_by(id=str(data['id'])).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    try:
        return jsonify({'total time': user.total_time_day})
    except Exception as e:
        return jsonify({'message': 'Failed to get time limit', 'error': str(e)}), 500