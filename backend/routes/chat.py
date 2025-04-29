# chat.py
from flask import Blueprint, request, jsonify
from models import db, ChatMessage, User
from datetime import datetime

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/get-messages', methods=['GET'])
def get_messages():
    data  = request.get_json() or {}
    me    = User.query.get(data.get('user_id'))
    if not me:
        return jsonify({'message':'denied'}), 401

    q = ChatMessage.query
    other = data.get('other_id')
    if other:
        q = q.filter(
            ((ChatMessage.sender_id   == me.id) & (ChatMessage.receiver_id == other)) |
            ((ChatMessage.sender_id   == other) & (ChatMessage.receiver_id == me.id))
        )
    since = data.get('since')
    if since:
        try:
            dt = datetime.fromisoformat(since)
            q = q.filter(ChatMessage.timestamp > dt)
        except ValueError:
            pass

    msgs = q.order_by(ChatMessage.timestamp).all()
    out  = []
    for m in msgs:
        out.append({
            'id'              : m.id,
            'sender_id'       : m.sender_id,
            'sender_username' : m.sender.username,
            'receiver_id'     : m.receiver_id,
            'receiver_username' : m.receiver.username if m.receiver else None,
            'body'            : m.body,
            'timestamp'       : m.timestamp.isoformat()
        })

    return jsonify({'message':'success','messages':out}), 200



@chat_bp.route('/send-message', methods=['POST'])
def send_message():
    """
    Request JSON:
      {
        "sender_id":   <your_id>,
        "receiver_id": <peer_id>,    # optional
        "body":        "<the text>"
      }
    Response JSON:
      { "message":"success", "id":<new_msg_id>, "timestamp":<ISO ts> }
    """
    data = request.get_json() or {}
    sender = User.query.get(data.get('sender_id'))
    if not sender:
        return jsonify({'message': 'denied'}), 401

    body = (data.get('body') or '').strip()
    if not body:
        return jsonify({'message': 'empty'}), 400

    m = ChatMessage(
        sender_id   = sender.id,
        receiver_id = data.get('receiver_id'),
        body        = body
    )
    db.session.add(m)
    db.session.commit()

    return jsonify({
        'message':   'success',
        'id':        m.id,
        'timestamp': m.timestamp.isoformat()
    }), 201