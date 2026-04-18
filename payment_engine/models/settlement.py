"""
Settlement Model
"""
from database import db
from datetime import datetime
import uuid


class Settlement(db.Model):
    __tablename__ = 'settlements'

    id              = db.Column(db.String(20), primary_key=True, default=lambda: 'STL' + uuid.uuid4().hex[:10].upper())
    transaction_id  = db.Column(db.String(20), db.ForeignKey('transactions.id'), nullable=False, unique=True)
    settled_at      = db.Column(db.DateTime,   default=datetime.utcnow)
    settled_amount  = db.Column(db.Float,      nullable=False)
    settlement_mode = db.Column(db.String(20), nullable=True)   # Auto / Manual
    remarks         = db.Column(db.String(255), nullable=True)
    created_at      = db.Column(db.DateTime,   default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':              self.id,
            'transaction_id':  self.transaction_id,
            'settled_at':      self.settled_at.isoformat(),
            'settled_amount':  self.settled_amount,
            'settlement_mode': self.settlement_mode,
            'remarks':         self.remarks or '',
            'created_at':      self.created_at.isoformat(),
        }

    def __repr__(self):
        return f'<Settlement {self.id} for {self.transaction_id}>'
