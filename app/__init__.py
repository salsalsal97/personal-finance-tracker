from flask import Flask
from sqlalchemy import func
from app.extensions import db
from datetime import datetime

def create_app():
    app = Flask(__name__) # creates Flask app
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///spending_tracker.db" # essentially specifies location of database (app.config is a dictionary)
    app.config["SECRET_KEY"] = "replace-this-with-a-random-secret"
    db.init_app(app) # links database to Flask app
    from app import models # imports Transaction class (creates db)
    from app.routes import main # imports blueprint
    from app.models import Transaction
    app.register_blueprint(main) # adds routes to application
    @app.context_processor
    def inject_latest_month():
        latest_date = db.session.query(
            func.max(Transaction.date)
        ).scalar()

        if latest_date is None:
            latest_month = None
        else:
            latest_month = latest_date.strftime("%Y-%m")

        return {
            "latest_month": latest_month
        }
    return app