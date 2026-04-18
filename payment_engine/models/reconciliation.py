"""
Reconciliation Run Log Model
"""
from database import db
from datetime import datetime
import uuid


class ReconciliationRun(db.Model):
    __tablename__ = 'reconciliation_runs'

    id              = db.Column(db.String(20),  primary_key=True, default=lambda: 'RCN' + uuid.uuid4().hex[:8].upper())
    run_at          = db.Column(db.DateTime,    default=datetime.utcnow)
    total_checked   = db.Column(db.Integer,     default=0)
    matched         = db.Column(db.Integer,     default=0)
    unmatched       = db.Column(db.Integer,     default=0)
    exceptions_found= db.Column(db.Integer,     default=0)
    match_rate      = db.Column(db.Float,       default=0.0)
    status          = db.Column(db.String(20),  default='Completed')
    summary         = db.Column(db.String(500), nullable=True)
    triggered_by    = db.Column(db.String(50),  default='Auto')

    def to_dict(self):
        return {
            'id':               self.id,
            'run_at':           self.run_at.isoformat(),
            'total_checked':    self.total_checked,
            'matched':          self.matched,
            'unmatched':        self.unmatched,
            'exceptions_found': self.exceptions_found,
            'match_rate':       round(self.match_rate, 2),
            'status':           self.status,
            'summary':          self.summary or '',
            'triggered_by':     self.triggered_by,
        }
