"""
Exception Routes — list, resolve, detect.
"""
from flask import Blueprint, jsonify, request
from database import db
from models.exception import TransactionException
from utils.exception_engine import ExceptionEngine

exceptions_bp = Blueprint('exceptions', __name__)


@exceptions_bp.route('/', methods=['GET'])
def list_exceptions():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    severity = request.args.get('severity', '')
    status   = request.args.get('status', '')
    txn_id   = request.args.get('txn_id', '')

    query = TransactionException.query
    if severity: query = query.filter_by(severity=severity)
    if status:   query = query.filter_by(status=status)
    if txn_id:   query = query.filter_by(transaction_id=txn_id)
    query = query.order_by(TransactionException.detected_at.desc())
    paged = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'exceptions':   [e.to_dict() for e in paged.items],
        'total':        paged.total,
        'pages':        paged.pages,
        'current_page': paged.page,
        'open_count':   TransactionException.query.filter_by(status='Open').count(),
    })


@exceptions_bp.route('/<string:exc_id>', methods=['GET'])
def get_exception(exc_id):
    exc = TransactionException.query.get_or_404(exc_id)
    return jsonify(exc.to_dict())


@exceptions_bp.route('/<string:exc_id>/resolve', methods=['POST'])
def resolve_exception(exc_id):
    exc  = TransactionException.query.get_or_404(exc_id)
    body = request.get_json(force=True) or {}
    exc.resolve(
        resolved_by=body.get('resolved_by', 'Operator'),
        note=body.get('note', '')
    )
    db.session.commit()
    return jsonify({'message': 'Exception resolved.', 'exception': exc.to_dict()})


@exceptions_bp.route('/actions/resolve-all', methods=['POST'])
def resolve_all():
    open_excs = TransactionException.query.filter_by(status='Open').all()
    count = 0
    for exc in open_excs:
        exc.resolve(resolved_by='Bulk Action', note='Bulk resolution')
        count += 1
    db.session.commit()
    return jsonify({'message': f'{count} exceptions resolved.', 'count': count})


@exceptions_bp.route('/actions/detect', methods=['POST'])
def detect_exceptions():
    """Run the exception detection engine."""
    engine = ExceptionEngine()
    new_count = engine.run()
    return jsonify({'message': f'Detection complete. {new_count} new exceptions flagged.', 'new_exceptions': new_count})


@exceptions_bp.route('/summary', methods=['GET'])
def summary():
    total    = TransactionException.query.count()
    open_c   = TransactionException.query.filter_by(status='Open').count()
    review   = TransactionException.query.filter_by(status='In Review').count()
    resolved = TransactionException.query.filter_by(status='Resolved').count()

    by_sev = {}
    for sev in ['Critical', 'High', 'Medium', 'Low']:
        by_sev[sev] = TransactionException.query.filter_by(severity=sev).count()

    return jsonify({
        'total': total, 'open': open_c, 'in_review': review, 'resolved': resolved,
        'by_severity': by_sev
    })
