"""
Exception Detection Engine
Applies rule-based checks to detect transaction anomalies.
"""
from database import db
from models.transaction import Transaction
from models.exception import TransactionException
from datetime import datetime, timedelta
from collections import defaultdict


class ExceptionEngine:
    """
    Core engine that scans transactions and flags anomalies.
    Returns a list of newly created TransactionException objects.
    """

    RULES = [
        'check_duplicate_transactions',
        'check_high_value_anomaly',
        'check_failed_transactions',
        'check_stale_pending',
        'check_round_trip_amounts',
    ]

    def run(self, transactions=None):
        """Run all detection rules. Returns count of new exceptions created."""
        if transactions is None:
            transactions = Transaction.query.all()

        new_exceptions = 0
        for rule_name in self.RULES:
            rule = getattr(self, rule_name)
            new_exceptions += rule(transactions)

        db.session.commit()
        return new_exceptions

    # ── Rule 1: Duplicate Transactions ──────────────────────────────────────────
    def check_duplicate_transactions(self, transactions):
        created = 0
        seen = defaultdict(list)
        for txn in transactions:
            key = (txn.sender, txn.receiver, txn.amount, txn.date.date())
            seen[key].append(txn)

        for key, txns in seen.items():
            if len(txns) > 1:
                for txn in txns[1:]:   # Flag all duplicates after the first
                    if not self._exception_exists(txn.id, 'Duplicate Entry'):
                        exc = TransactionException(
                            transaction_id = txn.id,
                            exception_type = 'Duplicate Entry',
                            severity       = 'Critical',
                            status         = 'Open',
                            description    = f'Duplicate found: same sender, receiver, amount and date as {txns[0].id}'
                        )
                        db.session.add(exc)
                        txn.status = 'Exception'
                        created += 1
        return created

    # ── Rule 2: High-Value Anomaly (> ₹90,000) ──────────────────────────────────
    def check_high_value_anomaly(self, transactions):
        THRESHOLD = 90_000
        created = 0
        for txn in transactions:
            if txn.amount > THRESHOLD:
                if not self._exception_exists(txn.id, 'High Value Anomaly'):
                    exc = TransactionException(
                        transaction_id = txn.id,
                        exception_type = 'High Value Anomaly',
                        severity       = 'High',
                        status         = 'Open',
                        description    = f'Transaction amount ₹{txn.amount:,.2f} exceeds threshold ₹{THRESHOLD:,}. Manual review required.'
                    )
                    db.session.add(exc)
                    created += 1
        return created

    # ── Rule 3: Failed Transactions ──────────────────────────────────────────────
    def check_failed_transactions(self, transactions):
        created = 0
        for txn in transactions:
            if txn.status == 'Failed':
                if not self._exception_exists(txn.id, 'Transaction Failed'):
                    exc = TransactionException(
                        transaction_id = txn.id,
                        exception_type = 'Transaction Failed',
                        severity       = 'High',
                        status         = 'Open',
                        description    = f'Transaction {txn.id} failed. Channel: {txn.channel}. Retry or investigate.'
                    )
                    db.session.add(exc)
                    created += 1
        return created

    # ── Rule 4: Stale Pending (> 24 hours) ──────────────────────────────────────
    def check_stale_pending(self, transactions):
        cutoff = datetime.utcnow() - timedelta(hours=24)
        created = 0
        for txn in transactions:
            if txn.status == 'Pending' and txn.date < cutoff:
                if not self._exception_exists(txn.id, 'Stale Pending'):
                    exc = TransactionException(
                        transaction_id = txn.id,
                        exception_type = 'Stale Pending',
                        severity       = 'Medium',
                        status         = 'Open',
                        description    = f'Transaction has been Pending for over 24 hours. Date: {txn.date.strftime("%Y-%m-%d %H:%M")}.'
                    )
                    db.session.add(exc)
                    created += 1
        return created

    # ── Rule 5: Round-Trip / Refund Loop ────────────────────────────────────────
    def check_round_trip_amounts(self, transactions):
        created = 0
        pairs = defaultdict(list)
        for txn in transactions:
            pairs[(txn.sender, txn.receiver, txn.amount)].append(txn)
            pairs[(txn.receiver, txn.sender, txn.amount)].append(txn)

        flagged = set()
        for key, txns in pairs.items():
            if len(txns) >= 2:
                ids = tuple(sorted(t.id for t in txns))
                if ids not in flagged:
                    flagged.add(ids)
                    for txn in txns:
                        if not self._exception_exists(txn.id, 'Round-Trip Amount'):
                            exc = TransactionException(
                                transaction_id = txn.id,
                                exception_type = 'Round-Trip Amount',
                                severity       = 'Medium',
                                status         = 'Open',
                                description    = f'Matching round-trip amount ₹{txn.amount:,.2f} detected between {key[0]} and {key[1]}.'
                            )
                            db.session.add(exc)
                            created += 1
        return created

    # ── Helper ───────────────────────────────────────────────────────────────────
    @staticmethod
    def _exception_exists(txn_id, exc_type):
        return TransactionException.query.filter_by(
            transaction_id=txn_id, exception_type=exc_type
        ).first() is not None
