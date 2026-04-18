"""
Reconciliation Engine
Matches transactions against settlement records and flags mismatches.
"""
from database import db
from models.transaction import Transaction
from models.settlement import Settlement
from models.exception import TransactionException
from models.reconciliation import ReconciliationRun
from datetime import datetime


class ReconciliationEngine:
    """
    Compares transaction records against settlement records.
    Flags unmatched, missing, or mismatched entries as exceptions.
    """

    def run(self, triggered_by='Auto'):
        """
        Execute a full reconciliation pass.
        Returns a ReconciliationRun summary dict.
        """
        transactions    = Transaction.query.all()
        settlements     = {s.transaction_id: s for s in Settlement.query.all()}

        total           = len(transactions)
        matched         = 0
        unmatched       = 0
        exceptions_found= 0

        for txn in transactions:
            if txn.status == 'Settled':
                stl = settlements.get(txn.id)
                if stl:
                    # Check amount mismatch
                    if abs(stl.settled_amount - txn.amount) > 0.01:
                        exc = self._flag(
                            txn.id,
                            'Amount Mismatch',
                            'Critical',
                            f'Transaction amount ₹{txn.amount:,.2f} ≠ settled amount ₹{stl.settled_amount:,.2f}.'
                        )
                        if exc:
                            exceptions_found += 1
                        unmatched += 1
                    else:
                        matched += 1
                else:
                    # Settled in transaction but no settlement record
                    exc = self._flag(
                        txn.id,
                        'Missing Settlement Record',
                        'High',
                        f'Transaction {txn.id} is marked Settled but has no corresponding settlement record.'
                    )
                    if exc:
                        exceptions_found += 1
                    unmatched += 1

            elif txn.status in ('Failed', 'Exception'):
                unmatched += 1
                # Already handled by ExceptionEngine — just count
            else:
                # Pending / Processing — not matched yet
                unmatched += 1

        match_rate = round((matched / total) * 100, 2) if total else 0

        run = ReconciliationRun(
            total_checked    = total,
            matched          = matched,
            unmatched        = unmatched,
            exceptions_found = exceptions_found,
            match_rate       = match_rate,
            status           = 'Completed',
            summary          = (
                f'{matched}/{total} transactions matched at {match_rate}% rate. '
                f'{exceptions_found} new exceptions flagged.'
            ),
            triggered_by     = triggered_by
        )
        db.session.add(run)
        db.session.commit()
        return run.to_dict()

    @staticmethod
    def _flag(txn_id, exc_type, severity, description):
        """Create exception only if it doesn't already exist."""
        exists = TransactionException.query.filter_by(
            transaction_id=txn_id, exception_type=exc_type
        ).first()
        if not exists:
            exc = TransactionException(
                transaction_id = txn_id,
                exception_type = exc_type,
                severity       = severity,
                status         = 'Open',
                description    = description
            )
            db.session.add(exc)
            return exc
        return None
