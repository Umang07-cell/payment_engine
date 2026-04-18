"""
Payment Settlement & Transaction Exception Engine
Main Flask Application Entry Point
"""

from flask import Flask
from database import db
from routes.transactions import transactions_bp
from routes.settlements import settlements_bp
from routes.exceptions import exceptions_bp
from routes.reconciliation import reconciliation_bp
from routes.dashboard import dashboard_bp
import os


def create_app():
    app = Flask(__name__)

    # ── Configuration ──────────────────────────────────────────────────────────
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'payment-engine-secret-2024')

    # Fix for Render PostgreSQL URL
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'payment_engine.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)
    elif database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Init Extensions ─────────────────────────────────────────────────────────
    db.init_app(app)

    # ── Register Blueprints ─────────────────────────────────────────────────────
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(settlements_bp,  url_prefix='/api/settlements')
    app.register_blueprint(exceptions_bp,   url_prefix='/api/exceptions')
    app.register_blueprint(reconciliation_bp, url_prefix='/api/reconciliation')

    # ── Create DB tables & seed data ────────────────────────────────────────────
    with app.app_context():
        db.create_all()
        from utils.seeder import seed_database
        seed_database()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
