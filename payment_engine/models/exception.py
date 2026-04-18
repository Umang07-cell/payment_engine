"""
Transaction Exception Model
"""
from database import db
from datetime import datetime
import uuid


class TransactionException(db.Model):
    __tablename__ = 'transaction_exceptions'

    id              = db.Column(db.String(20),  primary_key=True, default=lambda: 'EXC' + uuid.uuid4().hex[:8].upper())
    transaction_id  = db.Column(db.String(20),  db.ForeignKey('transactions.id'), nullable=False)
    exception_type  = db.Column(db.String(60),  nullable=False)
    severity        = db.Column(db.String(20),  nullable=False, default='Medium')  # Critical/High/Medium/Low
    status          = db.Column(db.String(20),  nullable=False, default='Open')    # Open/In Review/Resolved
    description     = db.Column(db.String(500), nullable=True)
    detected_at     = db.Column(db.DateTime,    default=datetime.utcnow)
    resolved_at     = db.Column(db.DateTime,    nullable=True)
    resolved_by     = db.Column(db.String(100), nullable=True)
    resolution_note = db.Column(db.String(255), nullable=True)
    created_at      = db.Column(db.DateTime,    default=datetime.utcnow)

    def resolve(self, resolved_by='System', note=''):
        self.status       = 'Resolved'
        self.resolved_at  = datetime.utcnow()
        self.resolved_by  = resolved_by
        self.resolution_note = note

    def to_dict(self):
        return {
            'id':              self.id,
            'transaction_id':  self.transaction_id,
            'exception_type':  self.exception_type,
            'severity':        self.severity,
            'status':          self.status,
            'description':     self.description or '',
            'detected_at':     self.detected_at.isoformat(),
            'resolved_at':     self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by':     self.resolved_by or '',
            'resolution_note': self.resolution_note or '',
            'created_at':      self.created_at.isoformat(),
        }

    def __repr__(self):
        return f'<Exception {self.id} | {self.severity} | {self.status}>'
