from app.extensions import db

class Category(db.Model): # Category inherits functionality from db.Model, e.g. querying abilities
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Transaction(db.Model): # Transaction inherits functionality from db.Model, e.g. Transaction.query, Transaction.query.all() etc.
    id = db.Column(db.Integer, primary_key=True) # creates Column object
    account_name = db.Column(db.String(100), nullable=False)
    fingerprint = db.Column(db.String(64), unique= True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
    category = db.relationship("Category", backref="transactions")
    date = db.Column(db.Date, nullable=False)
    description_raw = db.Column(db.String(255), nullable=False)
    description_clean = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    duplicate_index = db.Column(db.Integer, nullable=False, default=0)