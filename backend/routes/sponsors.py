# sponsorship.py
from flask import Blueprint, request, jsonify
from models import db, User, Sponsorship
from datetime import datetime
import json

sponsor_bp = Blueprint('sponsorship', __name__, url_prefix='/sponsorship')

# your predefined tiers
SPONSOR_TIERS = {
    "Bronze": {"cost": 100, "boost": 0.05},
    "Silver": {"cost": 300, "boost": 0.10},
    "Gold":   {"cost": 500, "boost": 0.20},
}
TIER_ORDER = {"Bronze": 1, "Silver": 2, "Gold": 3}

@sponsor_bp.route('/get-sponsorships', methods=['GET'])
def get_sponsorships():
    data = request.get_json()
    user = User.query.get(data.get('id'))
    if not user:
        return jsonify({'message':'denied'}), 401

    # collect per-horse info
    result = {}
    for sp in user.sponsorships:
        info = result.setdefault(sp.horse_name, {'owned': [], 'active': None})
        info['owned'].append(sp.tier)
        if sp.active:
            info['active'] = sp.tier

    return jsonify({
        'message': 'success',
        'sponsorships': result,
        'net_worth': float(user.net_worth)
    }), 200

@sponsor_bp.route('/buy-sponsorship', methods=['POST'])
def buy_sponsorship():
    data = request.get_json()
    user = User.query.get(data.get('id'))
    if not user:
        return jsonify({'message':'denied'}), 401

    horse = data['horse_name']
    tier  = data['tier']
    if tier not in SPONSOR_TIERS:
        return jsonify({'message':'invalid_tier'}), 400

    cost  = SPONSOR_TIERS[tier]['cost']
    boost = SPONSOR_TIERS[tier]['boost']

    # already bought this tier?
    existing = Sponsorship.query.filter_by(
        user_id=user.id, horse_name=horse, tier=tier
    ).first()
    if existing:
        return jsonify({'message':'already_owned'}), 200

    if float(user.net_worth) < cost:
        return jsonify({'message':'insufficient_funds'}), 402

    # purchase, default active=False
    user.net_worth -= cost
    sp = Sponsorship(
        user_id    = user.id,
        horse_name = horse,
        tier       = tier,
        boost      = boost,
        cost       = cost
    )
    db.session.add(sp)
    db.session.commit()

    return jsonify({'message':'success','net_worth':float(user.net_worth)}), 200

@sponsor_bp.route('/activate-sponsorship', methods=['POST'])
def activate_sponsorship():
    data = request.get_json()
    user = User.query.get(data.get('id'))
    horse = data['horse_name']
    tier  = data['tier']

    # must already own that exact tier
    sp = Sponsorship.query.filter_by(
        user_id=user.id, horse_name=horse, tier=tier
    ).first()
    if not sp:
        return jsonify({'message':'not_owned'}), 400

    # deactivate all other tiers for this horse
    Sponsorship.query.filter_by(
        user_id=user.id, horse_name=horse
    ).update({'active': False})
    # activate this one
    sp.active = True
    db.session.commit()

    return jsonify({'message':'activated'}), 200

@sponsor_bp.route('/deactivate-sponsorship', methods=['POST'])
def deactivate_sponsorship():
    data = request.get_json()
    user = User.query.get(data.get('id'))
    horse = data.get('horse_name')
    # find the active row
    sp = Sponsorship.query.filter_by(
        user_id=user.id, horse_name=horse, active=True
    ).first()
    if not sp:
        return jsonify({'message':'none_active'}), 400

    sp.active = False
    db.session.commit()
    return jsonify({'message':'deactivated'}), 200

