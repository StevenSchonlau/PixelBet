from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template
from flask_mailman import EmailMessage
from models import db, User, bcrypt, BetHistory
from sqlalchemy import select
import os
import uuid

game_bp = Blueprint('game', __name__)

@game_bp.route('/all-net', methods=['GET'])
def get_all_net():
    def get_last_sunday():
        today = datetime.utcnow()
        # Weekday: Monday=0, Sunday=6 → adjust so Sunday is 0
        days_since_sunday = (today.weekday() + 1) % 7
        last_sunday = today - timedelta(days=days_since_sunday)
        return last_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
    last_sunday = get_last_sunday()
    users = User.query.all()

    if not users:
        return jsonify({"message": "Failed"}), 400

    user_data = []
    for user in users:
        # Get all relevant bets for the user in the last 7 days
        weekly_bets = db.session.execute(
            select(BetHistory)
            .where(BetHistory.user_id == user.id)
            .where(BetHistory.date >= last_sunday)
        ).scalars().all()

        # Calculate net result from those bets
        net = 0
        for bet in weekly_bets:
            if bet.outcome == 'win':
                net += bet.amount * bet.odds  # assuming this is the return
            elif bet.outcome == 'loss':
                net -= bet.amount

        user_data.append({
            "username": user.username,
            "id": user.id,
            "net_worth": user.net_worth,
            "weekly_net_worth": net
        })

    return jsonify(user_data), 200
    
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

@game_bp.route('/update-streak/<uuid:user_id>', methods=['GET'])
def update_streak(user_id):
    user = User.query.filter_by(id=str(user_id)).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    data = request.get_json()
    try:
        user.streak = data['streak']
        db.session.commit()
        return jsonify({'message': 'Streak updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update streak', 'error': str(e)}), 500
