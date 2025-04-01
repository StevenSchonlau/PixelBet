from flask import Blueprint, request, jsonify, render_template
from models import db, User, bcrypt, BetHistory

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
    
@game_bp.route('/update-bet-history/<uuid:user_id>', methods=['POST'])
def update_bet_history_route(user_id):
    # Look up the user by ID
    user = User.query.filter_by(id=str(user_id)).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.json
    if 'bets' not in data:
        return jsonify({'message': 'No bets provided'}), 400

    bets = data['bets']
    print(bets)
    try:
        for bet_data in bets:
            # Convert the date string to a datetime object if provided; else use current time
            date_str = bet_data.get('date')
            if date_str:
                bet_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            else:
                bet_date = datetime.utcnow()
            # Create a new BetHistory record using your model
            new_bet = BetHistory(
                user_id=user.id,
                date=bet_date,
                horse=bet_data['horse'],
                odds=bet_data['odds'],
                amount=bet_data['amount'],
                outcome=bet_data.get('outcome', 'undecided')
            )
            db.session.add(new_bet)
        db.session.commit()
        return jsonify({'message': 'Bet history updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update bet history', 'error': str(e)}), 500
    
@game_bp.route('/get-bet-history/<uuid:user_id>', methods=['GET'])
def get_bet_history_route(user_id):
    # Look up the user by id.
    user = User.query.filter_by(id=str(user_id)).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Query the BetHistory records for this user, ordering by date (most recent first)
    bets = BetHistory.query.filter_by(user_id=user.id).order_by(BetHistory.date.desc()).all()

    # Convert each bet to a serializable dictionary
    bet_history_data = [{
         "date": bet.date.strftime("%Y-%m-%d %H:%M:%S"),
         "horse": bet.horse,
         "odds": bet.odds,
         "amount": bet.amount,
         "outcome": bet.outcome
    } for bet in bets]

    return jsonify({"bet_history": bet_history_data}), 200

