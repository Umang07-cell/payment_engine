"""
Dashboard Route — serves the main HTML page and summary stats API.
"""
from flask import Blueprint, render_template, jsonify
from database import db
from models.transaction import Transaction
from models.exception import TransactionException
from models.settlement import Settlement
from models.reconciliation import ReconciliationRun
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    return render_template('index.html')


@dashboard_bp.route('/api/dashboard/stats')
def stats():
    total     = Transaction.query.count()
    settled   = Transaction.query.filter_by(status='Settled').count()
    pending   = Transaction.query.filter_by(status='Pending').count()
    failed    = Transaction.query.filter_by(status='Failed').count()
    exc_count = Transaction.query.filter_by(status='Exception').count()
    processing= Transaction.query.filter_by(status='Processing').count()

    total_amount   = db.session.query(func.sum(Transaction.amount)).scalar() or 0
    settled_amount = db.session.query(func.sum(Settlement.settled_amount)).scalar() or 0
    open_exceptions= TransactionException.query.filter_by(status='Open').count()

    settlement_rate = round((settled / total * 100), 2) if total else 0

    # Volume last 7 days
    volume = []
    for i in range(6, -1, -1):
        d = datetime.utcnow() - timedelta(days=i)
        day_start = d.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end   = day_start + timedelta(days=1)
        count = Transaction.query.filter(
            Transaction.date >= day_start,
            Transaction.date <  day_end
        ).count()
        volume.append({'date': day_start.strftime('%a'), 'count': count})

    # By channel
    channel_data = db.session.query(
        Transaction.channel, func.count(Transaction.id)
    ).group_by(Transaction.channel).all()

    # By type amounts
    type_data = db.session.query(
        Transaction.txn_type, func.sum(Transaction.amount)
    ).group_by(Transaction.txn_type).all()

    last_recon = ReconciliationRun.query.order_by(ReconciliationRun.run_at.desc()).first()

    return jsonify({
        'total':           total,
        'settled':         settled,
        'pending':         pending,
        'failed':          failed,
        'exception':       exc_count,
        'processing':      processing,
        'total_amount':    round(total_amount, 2),
        'settled_amount':  round(settled_amount, 2),
        'open_exceptions': open_exceptions,
        'settlement_rate': settlement_rate,
        'volume_7d':       volume,
        'by_channel':      [{'channel': c, 'count': n} for c, n in channel_data],
        'by_type_amount':  [{'type': t, 'amount': round(a or 0, 2)} for t, a in type_data],
        'last_recon':      last_recon.to_dict() if last_recon else None,
    })
