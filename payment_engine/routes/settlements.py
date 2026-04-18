"""
Settlement Routes
"""
from flask import Blueprint, jsonify, request
from database import db
from models.settlement import Settlement
from models.transaction import Transaction
from sqlalchemy import func

settlements_bp = Blueprint('settlements', __name__)


@settlements_bp.route('/', methods=['GET'])
def list_settlements():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    mode     = request.args.get('mode', '')

    query = Settlement.query
    if mode:
        query = query.filter_by(settlement_mode=mode)
    query = query.order_by(Settlement.settled_at.desc())
    paged = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'settlements': [s.to_dict() for s in paged.items],
        'total':       paged.total,
        'pages':       paged.pages,
        'current_page':paged.page,
    })


@settlements_bp.route('/summary', methods=['GET'])
def summary():
    total_settled = Settlement.query.count()
    total_txn     = Transaction.query.count()
    total_amount  = db.session.query(func.sum(Settlement.settled_amount)).scalar() or 0
    auto_count    = Settlement.query.filter_by(settlement_mode='Auto').count()
    manual_count  = Settlement.query.filter_by(settlement_mode='Manual').count()
    rate          = round((total_settled / total_txn * 100), 2) if total_txn else 0

    return jsonify({
        'total_settled':  total_settled,
        'total_amount':   round(total_amount, 2),
        'settlement_rate':rate,
        'auto_count':     auto_count,
        'manual_count':   manual_count,
    })


@settlements_bp.route('/<string:stl_id>', methods=['GET'])
def get_settlement(stl_id):
    stl = Settlement.query.get_or_404(stl_id)
    data = stl.to_dict()
    txn  = Transaction.query.get(stl.transaction_id)
    data['transaction'] = txn.to_dict() if txn else None
    return jsonify(data)
