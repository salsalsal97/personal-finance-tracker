from app import create_app
from app.models import Category
from app.extensions import db

app = create_app() # creates app
with app.app_context():
    categories = [
        "Salary",
        "Interest",
        "Rent & Bills",
        "Groceries",
        "Car",
        "Medical",
        "Subscriptions",
        "Investments",
        "Mum Gift",
        "Wise",
        "Shopping",
        "Food",
        "Holiday",
        "Other",
        "Travel",
        "Outing / Date"
    ]
    for category in categories:
        existing = Category.query.filter_by(name=category).first()
        if not existing:
            category_new = Category(name=category)
            db.session.add(category_new)
    db.session.commit()
    print("Categories seeded.")