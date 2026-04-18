"""
Transaction Model
"""
from database import db
from datetime import datetime
import uuid


def generate_txn_id():
    return 'TXN' + uuid.uuid4().hex[:10].upper()


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id            = db.Column(db.String(20),  primary_key=True, default=generate_txn_id)
    date          = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)
    sender        = db.Column(db.String(100), nullable=False)
    receiver      = db.Column(db.String(100), nullable=False)
    amount        = db.Column(db.Float,       nullable=False)
    txn_type      = db.Column(db.String(20),  nullable=False)   # Credit/Debit/Refund/Transfer
    channel       = db.Column(db.String(20),  nullable=False)   # UPI/NEFT/RTGS/IMPS/Card/Wallet
    status        = db.Column(db.String(20),  nullable=False, default='Pending')
    notes         = db.Column(db.String(255), nullable=True)
    reference_no  = db.Column(db.String(50),  nullable=True)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    exceptions    = db.relationship('TransactionException', backref='transaction', lazy=True, cascade='all, delete-orphan')
    settlement    = db.relationship('Settlement', backref='transaction', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id':          self.id,
            'date':        self.date.isoformat(),
            'sender':      self.sender,
            'receiver':    self.receiver,
            'amount':      self.amount,
            'txn_type':    self.txn_type,
            'channel':     self.channel,
            'status':      self.status,
            'notes':       self.notes or '',
            'reference_no': self.reference_no or '',
            'created_at':  self.created_at.isoformat(),
            'updated_at':  self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Transaction {self.id} | {self.status} | ₹{self.amount}>'
