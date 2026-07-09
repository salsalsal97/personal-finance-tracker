import hashlib
import pandas as pd
from app.models import Transaction, Category
from app.extensions import db

CATEGORY_RULES = {
    "Salary": [],
    "Interest": [],
    "Rent & Bills": ["WATER"],
    "Groceries": ["SAINSBURYS","TESCO","ALDI","MARKS AND SPENCER"],
    "Car": [],
    "Medical": ["BELGRAVIA"],
    "Subscriptions": ["APPLE"],
    "Investments": [],
    "Mum Gift": [],
    "Wise": [],
    "Shopping": [],
    "Food": ["KFC","SUBWAY","CHICKEN LAND","PEPE","NANDOS","MCDONALDS","JOLLIBEE","UBER   *EATS","UBER *EATS","VENDMASTER","CAFE","RESTAURANT"],
    "Holiday": [],
    "Other": [],
    "Travel": ["TFL","UBER   *TRIP","UBER *TRIP","UBER *ONE","UBER   *ONE"],
    "Outing / Date": ["VUE"],
}

def make_fingerprint(date, description, amount, duplicate_index):
    fingerprint = f"{date}|{description}|{round(float(amount), 2)}|{duplicate_index}"
    fingerprint_hex = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()
    return fingerprint_hex

def categorise_transaction(description):
    desc = description.upper().strip()
    categories = Category.query.all()
    for row in categories:
        category_name = row.name
        category_id = row.id
        keywords = CATEGORY_RULES.get(category_name, [])
        for keyword in keywords:
            if keyword.upper().strip() in desc:
                return category_id
    return None

def import_transactions_from_file(file):
    df = pd.read_csv(file)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df["description_clean"] = (df["Transaction Description"].str.upper().str.strip())
    df["duplicate_index"] = df.groupby(["Date", "Transaction Description", "Amount"]).cumcount()
    imported_count = 0
    skipped_count = 0
    for _, row in df.iterrows():
        fingerprint = make_fingerprint(row["Date"],row["Transaction Description"],row["Amount"], row["duplicate_index"]) # unique identifier
        category = categorise_transaction(row["description_clean"])
        existing = Transaction.query.filter_by(fingerprint=fingerprint).first() # checks if unique identifier exists in table
        if existing:
            skipped_count+=1
            continue
        else:
            transaction = Transaction(
                fingerprint = fingerprint,
                category_id = category,
                date = row["Date"].date(),
                description_raw = row["Transaction Description"],
                description_clean = row["description_clean"],
                amount = row["Amount"],
                duplicate_index = row["duplicate_index"]
            )
            db.session.add(transaction)
            imported_count+=1
    db.session.commit()
    return imported_count, skipped_count
