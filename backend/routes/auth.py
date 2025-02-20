from flask import Blueprint, request, jsonify, render_template
from models import db, User, bcrypt

from datetime import datetime
import os
from flask_mailman import EmailMessage
import uuid
#all REST API calls for login/auth


auth_bp = Blueprint('auth', __name__, template_folder="../templates")

def send_email(to_email, subject, message):
    email = EmailMessage(
        subject=subject,
        body=message,
        to=[to_email]
    )
    email.send()
    return "Email sent!"

def send_email_route(uuidUser, username, to_email="7808steven@gmail.com"):
    # Get email data from the request JSON
    if not to_email:
        return jsonify({"error": "Email is required"}), 400  # Return error if email is missing

    subject = "Welcome to PixelBet " + username + "!"
    message = "Thanks for signing up! Enjoy your betting experience. Go to " + os.getenv("SERVER_URL") + "confirm_email/" + uuidUser + " to confirm your email."

    try:
        send_email(to_email, subject, message)  # Call the send_email function
        print('sent email')
        return jsonify({"message": "Email sent successfully!"}), 200  # Success response
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Error handling



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
        send_email_route(user.uuid_user, user.username)
        return jsonify({'message': 'User registered!', 'id': user.id})
    except:
        return jsonify({'message': 'duplicate'})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Login successful', 'user_id': user.id})
    return jsonify({'message': 'denied'}), 401

@auth_bp.route('/reset-time', methods=['POST'])
def resend_email():
    data = request.json
    try:
        print(data)
        user = User.query.filter_by(id=str(data['id'])).first()
        print(user)
        user.sent_time_stamp = datetime.utcnow()
        user.uuid_user = uuid.uuid4()
        db.session.commit()
        print('set values')
        send_email_route(user.uuid_user, user.username)
        return jsonify({'message': 'Reset', 'user_id': user.id})
    except:
        return jsonify({'message': 'Error'})

@auth_bp.route('/get-user', methods=['GET'])
def get_user():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    print(user)
    if user:
        return jsonify({"username": user.username, "id": user.id})
    return jsonify({'message': 'User doesn\'t exist'}), 401

@auth_bp.route('/check-confirmation', methods=['GET'])
def check_confirmation():
    data = request.json
    user = User.query.filter_by(id=data['id']).first()
    print(user.email_confirmed)
    if user.email_confirmed:
        return jsonify({'message': 'confirmed'})
    return jsonify({'message': 'wait'})

@auth_bp.route('/confirm_email/<uuid:user_uuid>', methods=['GET'])
def confirm_email(user_uuid):
    user = User.query.filter_by(uuid_user=str(user_uuid)).first()

    if user:
        if not user.email_confirmed:
            # Mark the email as confirmed
            if (datetime.utcnow() - user.sent_time_stamp).seconds > 600:
                message = "Expired! Click send another one in the app."
            else:
                user.email_confirmed = True
                db.session.commit()
                print("success")
                message = "Your email has been successfully confirmed!"
        else:
            if (datetime.utcnow() - user.sent_time_stamp).seconds > 600:
                message = "Expired! But your email is already confirmed."
            else:
                message = "Your email has already been confirmed."

        return render_template("confirmation.html", message=message)
    
    return render_template("confirmation.html", message="Invalid confirmation link. Check your email if a more recent link was sent.")

    #return redirect(url_for('home'))  # Redirect to home or another page