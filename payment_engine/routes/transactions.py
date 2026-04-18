"""
Transaction Routes — CRUD + filtering + settle/retry actions.
"""
from flask import Blueprint, request, jsonify
from database import db
from models.transaction import Transaction, generate_txn_id
from models.settlement import Settlement
from models.exception import TransactionException
from datetime import datetime

transactions_bp = Blueprint('transactions', __name__)


# ── LIST (with filter/search/paginate) ────────────────────────────────────────
@transactions_bp.route('/', methods=['GET'])
def list_transactions():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search   = request.args.get('search', '').strip()
    status   = request.args.get('status', '')
    txn_type = request.args.get('type', '')
    channel  = request.args.get('channel', '')

    query = Transaction.query

    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                Transaction.id.ilike(like),
                Transaction.sender.ilike(like),
                Transaction.receiver.ilike(like),
                Transaction.reference_no.ilike(like)
            )
        )
    if status:
        query = query.filter_by(status=status)
    if txn_type:
        query = query.filter_by(txn_type=txn_type)
    if channel:
        query = query.filter_by(channel=channel)

    query = query.order_by(Transaction.date.desc())
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'transactions': [t.to_dict() for t in paginated.items],
        'total':        paginated.total,
        'pages':        paginated.pages,
        'current_page': paginated.page,
        'per_page':     per_page,
    })


# ── GET SINGLE ────────────────────────────────────────────────────────────────
@transactions_bp.route('/<string:txn_id>', methods=['GET'])
def get_transaction(txn_id):
    txn = Transaction.query.get_or_404(txn_id)
    data = txn.to_dict()
    data['exceptions'] = [e.to_dict() for e in txn.exceptions]
    data['settlement'] = txn.settlement.to_dict() if txn.settlement else None
    return jsonify(data)


# ── CREATE ────────────────────────────────────────────────────────────────────
@transactions_bp.route('/', methods=['POST'])
def create_transaction():
    body = request.get_json(force=True)
    required = ['sender', 'receiver', 'amount', 'txn_type', 'channel']
    for field in required:
        if not body.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        amount = float(body['amount'])
        if amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'error': 'Amount must be a positive number'}), 400

    date_str = body.get('date')
    try:
        date = datetime.fromisoformat(date_str) if date_str else datetime.utcnow()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use ISO 8601.'}), 400

    txn = Transaction(
        id           = generate_txn_id(),
        date         = date,
        sender       = body['sender'].strip(),
        receiver     = body['receiver'].strip(),
        amount       = amount,
        txn_type     = body['txn_type'],
        channel      = body['channel'],
        status       = body.get('status', 'Pending'),
        notes        = body.get('notes', ''),
        reference_no = body.get('reference_no', '')
    )
    db.session.add(txn)

    # Auto-create exception if status is Exception
    if txn.status == 'Exception':
        exc = TransactionException(
            transaction_id = txn.id,
            exception_type = 'Manual Exception',
            severity       = 'Medium',
            status         = 'Open',
            description    = 'Exception flagged at creation.'
        )
        db.session.add(exc)

    # Auto-create settlement record if status is Settled
    if txn.status == 'Settled':
        stl = Settlement(
            transaction_id  = txn.id,
            settled_amount  = txn.amount,
            settlement_mode = 'Manual',
            remarks         = 'Settled at creation'
        )
        db.session.add(stl)

    db.session.commit()
    return jsonify(txn.to_dict()), 201


# ── UPDATE STATUS ─────────────────────────────────────────────────────────────
@transactions_bp.route('/<string:txn_id>/status', methods=['PATCH'])
def update_status(txn_id):
    txn    = Transaction.query.get_or_404(txn_id)
    body   = request.get_json(force=True)
    status = body.get('status')

    valid = ['Settled', 'Pending', 'Processing', 'Failed', 'Exception']
    if status not in valid:
        return jsonify({'error': f'Invalid status. Must be one of: {valid}'}), 400

    old_status = txn.status
    txn.status = status

    # Create settlement record when marking Settled
    if status == 'Settled' and not txn.settlement:
        stl = Settlement(
            transaction_id  = txn.id,
            settled_amount  = txn.amount,
            settlement_mode = 'Manual',
            remarks         = body.get('remarks', 'Manually settled')
        )
        db.session.add(stl)

    db.session.commit()
    return jsonify({'message': f'Status updated from {old_status} to {status}', 'transaction': txn.to_dict()})


# ── SETTLE ALL PENDING ────────────────────────────────────────────────────────
@transactions_bp.route('/actions/settle-all-pending', methods=['POST'])
def settle_all_pending():
    pending = Transaction.query.filter_by(status='Pending').all()
    count = 0
    for txn in pending:
        txn.status = 'Settled'
        if not txn.settlement:
            stl = Settlement(
                transaction_id  = txn.id,
                settled_amount  = txn.amount,
                settlement_mode = 'Auto',
                remarks         = 'Bulk auto-settlement'
            )
            db.session.add(stl)
        count += 1
    db.session.commit()
    return jsonify({'message': f'{count} transactions settled.', 'count': count})


# ── DELETE ────────────────────────────────────────────────────────────────────
@transactions_bp.route('/<string:txn_id>', methods=['DELETE'])
def delete_transaction(txn_id):
    txn = Transaction.query.get_or_404(txn_id)
    db.session.delete(txn)
    db.session.commit()
    return jsonify({'message': f'Transaction {txn_id} deleted.'})
