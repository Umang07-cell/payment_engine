"""
Database Seeder — populates initial sample data on first run.
"""
import random
from datetime import datetime, timedelta
from database import db
from models.transaction import Transaction, generate_txn_id
from models.settlement import Settlement
from models.exception import TransactionException
from models.reconciliation import ReconciliationRun


SENDERS = [
    'HDFC Bank', 'ICICI Bank', 'SBI', 'Axis Bank', 'Kotak Mahindra',
    'Paytm', 'PhonePe', 'Google Pay', 'NPCI', 'RazorPay',
    'Yes Bank', 'IndusInd Bank', 'IDFC First', 'Punjab National Bank', 'Bank of Baroda'
]
RECEIVERS = [
    'Amazon Pay', 'Flipkart', 'Swiggy', 'Zomato', 'BookMyShow',
    'BigBasket', 'Nykaa', 'Meesho', 'Dunzo', 'Juspay',
    'Ola', 'Uber', 'MakeMyTrip', 'IRCTC', 'LIC India'
]
CHANNELS  = ['UPI', 'NEFT', 'RTGS', 'IMPS', 'Card', 'Wallet']
TYPES     = ['Credit', 'Debit', 'Refund', 'Transfer']
STATUSES  = ['Settled'] * 5 + ['Pending'] * 2 + ['Processing', 'Failed', 'Exception']
NOTES     = [
    'Monthly subscription', 'EMI payment', 'Refund initiated',
    'Order payment', 'Wallet topup', 'Vendor payout',
    'Tax payment', 'Salary credit', 'Insurance premium', 'Service charge',
    'Utility bill', 'School fees', 'Loan repayment', 'Medical expense', 'Travel booking'
]
EXCEPTION_TYPES = [
    'Duplicate Entry', 'Amount Mismatch', 'Missing Record',
    'Network Timeout', 'Insufficient Funds', 'Auth Failure',
    'Invalid Account', 'Reversed Transaction', 'Blacklisted Entity'
]
SEVERITIES = ['Critical', 'High', 'Medium', 'Low']


def random_date(days_back=30):
    delta = timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    return datetime.utcnow() - delta


def seed_database():
    """Seed only if the DB is empty."""
    if Transaction.query.count() > 0:
        return  # already seeded

    print("[Seeder] Seeding database with sample data…")

    transactions = []
    for _ in range(60):
        status = random.choice(STATUSES)
        txn = Transaction(
            id          = generate_txn_id(),
            date        = random_date(),
            sender      = random.choice(SENDERS),
            receiver    = random.choice(RECEIVERS),
            amount      = round(random.uniform(100, 99999), 2),
            txn_type    = random.choice(TYPES),
            channel     = random.choice(CHANNELS),
            status      = status,
            notes       = random.choice(NOTES),
            reference_no= 'REF' + str(random.randint(100000, 999999))
        )
        transactions.append(txn)
        db.session.add(txn)

    db.session.flush()  # get IDs assigned

    # Create settlements for Settled transactions
    for txn in transactions:
        if txn.status == 'Settled':
            stl = Settlement(
                transaction_id  = txn.id,
                settled_amount  = txn.amount,
                settlement_mode = random.choice(['Auto', 'Manual']),
                remarks         = 'Settled successfully',
                settled_at      = txn.date + timedelta(seconds=random.randint(1, 10))
            )
            db.session.add(stl)

        # Create exceptions for Exception/Failed transactions
        if txn.status in ('Exception', 'Failed'):
            exc = TransactionException(
                transaction_id  = txn.id,
                exception_type  = random.choice(EXCEPTION_TYPES),
                severity        = random.choice(SEVERITIES),
                status          = random.choice(['Open', 'In Review', 'Resolved']),
                description     = f'Auto-detected by reconciliation engine during processing of {txn.id}',
                detected_at     = txn.date + timedelta(seconds=random.randint(1, 5))
            )
            db.session.add(exc)

    # Seed one reconciliation run
    total = len(transactions)
    matched = sum(1 for t in transactions if t.status == 'Settled')
    unmatched = total - matched
    exc_count = sum(1 for t in transactions if t.status in ('Exception', 'Failed'))
    recon = ReconciliationRun(
        total_checked    = total,
        matched          = matched,
        unmatched        = unmatched,
        exceptions_found = exc_count,
        match_rate       = round((matched / total) * 100, 2) if total else 0,
        status           = 'Completed',
        summary          = f'Initial seed run: {matched}/{total} matched, {exc_count} exceptions.',
        triggered_by     = 'Seeder'
    )
    db.session.add(recon)
    db.session.commit()
    print(f"[Seeder] Done — {total} transactions, {matched} settled, {exc_count} exceptions seeded.")
