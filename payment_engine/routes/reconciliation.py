"""
Reconciliation Routes
"""
from flask import Blueprint, jsonify, request
from models.reconciliation import ReconciliationRun
from utils.reconciliation_engine import ReconciliationEngine

reconciliation_bp = Blueprint('reconciliation', __name__)


@reconciliation_bp.route('/run', methods=['POST'])
def run_reconciliation():
    body         = request.get_json(force=True) or {}
    triggered_by = body.get('triggered_by', 'Manual')
    engine       = ReconciliationEngine()
    result       = engine.run(triggered_by=triggered_by)
    return jsonify({'message': 'Reconciliation complete.', 'run': result})


@reconciliation_bp.route('/history', methods=['GET'])
def history():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    paged    = ReconciliationRun.query.order_by(
        ReconciliationRun.run_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'runs':         [r.to_dict() for r in paged.items],
        'total':        paged.total,
        'pages':        paged.pages,
        'current_page': paged.page,
    })


@reconciliation_bp.route('/latest', methods=['GET'])
def latest():
    run = ReconciliationRun.query.order_by(ReconciliationRun.run_at.desc()).first()
    return jsonify(run.to_dict() if run else {})
