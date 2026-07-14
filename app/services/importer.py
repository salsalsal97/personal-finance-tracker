import hashlib
import pandas as pd
from app.models import Transaction, Category
from app.extensions import db

CATEGORY_RULES = {
    "Salary": [],
    "Interest": [],
    "Rent & Bills": ["WATER"],
    "Groceries": ["SAINSBURYS","TESCO STORE","TESCO STORES","ALDI","MARKS AND SPENCER"],
    "Car": ["TESCO PETROL"],
    "Medical": ["BELGRAVIA"],
    "Subscriptions": ["APPLE"],
    "Investments": [],
    "Mum Gift": [],
    "Wise": ["WISE LONDON"],
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

def normalise_statement(file, statement_type):
    if statement_type == "amex":
        df = pd.read_csv(file)
        df.columns = ["Date", "Transaction Description", "Amount"]
        account_name = "AMEX"
    elif statement_type == "hsbc_credit":
        df = pd.read_csv(file, header=None)
        df.columns = ["Date", "Transaction Description", "Amount"]
        account_name = "HSBC Credit"
    elif statement_type == "hsbc_current":
        df = pd.read_csv(file, header=None)
        df.columns = ["Date", "Transaction Description", "Amount"]
        account_name = "HSBC Current"
    elif statement_type == "legacy":
        pass
    df["Amount"] = (
        df["Amount"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .astype(float)
    )
    if statement_type == "amex":
        df["Amount"] = -1*df["Amount"]
    return account_name, df

def classify_exclusion(account_name, amount, description):
    current_exclusions = {"Card_Payment_Patterns":"AMERICAN EXP", "Internal_Transfer_Patterns":"400400 13953912 INTERNET TRANSFER TFR"}
    exclude_from_summary = False
    exclusion_reason = None
    if account_name == "HSBC Credit" and amount > 0: # Later consider refunds
        exclude_from_summary = True
        exclusion_reason = "Credit card repayment"
    elif account_name == "AMEX" and amount > 0:
        exclude_from_summary = True
        exclusion_reason = "AMEX card repayment"
    elif account_name == "HSBC Current":
        if current_exclusions["Card_Payment_Patterns"] in description:
            exclude_from_summary = True
            exclusion_reason = "AMEX card repayment"
        elif current_exclusions["Internal_Transfer_Patterns"] in description:
            exclude_from_summary = True
            exclusion_reason = "Internal transfer"
    return exclude_from_summary, exclusion_reason

def import_transactions_from_file(file, statement_type):
    account_name, df = normalise_statement(file, statement_type)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df["description_clean"] = (df["Transaction Description"].str.upper().str.strip())
    df["duplicate_index"] = df.groupby(["Date", "Transaction Description", "Amount"]).cumcount()
    imported_count = 0
    skipped_count = 0
    for _, row in df.iterrows():
        exclude_from_summary, exclusion_reason = classify_exclusion(account_name,row["Amount"],row["description_clean"])
        fingerprint = make_fingerprint(row["Date"],row["Transaction Description"],row["Amount"],row["duplicate_index"]) # unique identifier
        category = categorise_transaction(row["description_clean"])
        existing = Transaction.query.filter_by(fingerprint=fingerprint).first() # checks if unique identifier exists in table
        if existing:
            skipped_count+=1
            continue
        else:
            transaction = Transaction(
                fingerprint = fingerprint,
                account_name = account_name,
                category_id = category,
                date = row["Date"].date(),
                description_raw = row["Transaction Description"],
                description_clean = row["description_clean"],
                amount = row["Amount"],
                exclude_from_summary = exclude_from_summary,
                exclusion_reason = exclusion_reason,
                duplicate_index = row["duplicate_index"]
            )
            db.session.add(transaction)
            imported_count+=1
    db.session.commit()
    return imported_count, skipped_count
