import uuid
from sqlalchemy.dialects.mysql import CHAR
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class FriendAssociation(db.Model):
    __tablename__ = 'friends'
    user_id = db.Column(CHAR(36), db.ForeignKey('user.id'), primary_key=True)
    friend_id = db.Column(CHAR(36), db.ForeignKey('user.id'), primary_key=True)
    pending = db.Column(db.Boolean, default=True, nullable=False)

class User(db.Model):
    id = db.Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    uuid_user = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    sent_time_stamp = db.Column(db.DateTime, default=datetime.utcnow)
    email_confirmed = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(80))

    sent_requests = db.relationship(
        'FriendAssociation',
        foreign_keys='FriendAssociation.user_id',
        backref='requester',
        lazy='dynamic',
        cascade="all, delete-orphan"
    )
    received_requests = db.relationship(
        'FriendAssociation',
        foreign_keys='FriendAssociation.friend_id',
        backref='receiver',
        lazy='dynamic',
        cascade="all, delete-orphan"
    )

    @property
    def friends(self):
        """Returns a list of accepted friends (i.e. requests that are not pending)"""
        sent = self.sent_requests.filter_by(pending=False).all()
        received = self.received_requests.filter_by(pending=False).all()
        # For sent requests, the friend is the receiver; for received, the friend is the requester.
        return [assoc.receiver for assoc in sent] + [assoc.requester for assoc in received]

    @property
    def pending_sent_requests(self):
        """Returns the list of friend requests sent by the user that are still pending."""
        return self.sent_requests.filter_by(pending=True).all()

    @property
    def pending_received_requests(self):
        """Returns the list of friend requests received by the user that are still pending."""
        return self.received_requests.filter_by(pending=True).all()

    def send_friend_request(self, friend):
        if friend.id == self.id:
            return False
        if self.has_pending_request(friend) or self.is_friend(friend):
            return False
        request = FriendAssociation(user_id=self.id, friend_id=friend.id, pending=True)
        db.session.add(request)
        db.session.commit()
        return True

    def cancel_friend_request(self, friend):
        request = self.sent_requests.filter_by(friend_id=friend.id, pending=True).first()
        if request:
            db.session.delete(request)
            db.session.commit()
            return True
        return False

    def accept_friend_request(self, friend):
        request = self.received_requests.filter_by(user_id=friend.id, pending=True).first()
        if request:
            request.pending = False
            # Create reciprocal record if it doesn't already exist
            reciprocal = self.sent_requests.filter_by(friend_id=friend.id, pending=False).first()
            if not reciprocal:
                new_record = FriendAssociation(user_id=self.id, friend_id=friend.id, pending=False)
                db.session.add(new_record)
            db.session.commit()
            return True
        return False

    def reject_friend_request(self, friend):
        request = self.received_requests.filter_by(user_id=friend.id, pending=True).first()
        if request:
            db.session.delete(request)
            db.session.commit()
            return True
        return False

    def remove_friend(self, friend):
        sent = self.sent_requests.filter_by(friend_id=friend.id, pending=False).first()
        received = self.received_requests.filter_by(user_id=friend.id, pending=False).first()
        if sent:
            db.session.delete(sent)
        if received:
            db.session.delete(received)
        db.session.commit()
        return True

    def is_friend(self, friend):
        return friend in self.friends

    def has_pending_request(self, friend):
        """
        Check if there is a pending friend request either sent to or received from the specified user.
        """
        pending_sent = self.sent_requests.filter_by(friend_id=friend.id, pending=True).first() is not None
        pending_received = self.received_requests.filter_by(user_id=friend.id, pending=True).first() is not None
        return pending_sent or pending_received
