from app.extensions import db

class Transaction(db.Model): # Transaction inherits functionality from db.Model, e.g. Transaction.query, Transaction.query.all() etc.
    id = db.Column(db.Integer, primary_key=True) # creates Column object
    fingerprint = db.Column(db.String(64), unique= True, nullable = False)
    date = db.Column(db.Date, nullable=False)
    description_raw = db.Column(db.String(255), nullable=False)
    description_clean = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    duplicate_index = db.Column(db.Integer, nullable=False, default=0)