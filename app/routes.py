from flask import Blueprint, render_template, request
from app.models import Transaction
from app.extensions import db
from app.services.importer import import_transactions_from_file
import pandas as pd
import hashlib

def make_fingerprint(date, description, amount, duplicate_index):
    fingerprint = f"{date}|{description}|{round(float(amount), 2)}|{duplicate_index}"
    fingerprint_hex = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()
    return fingerprint_hex

main = Blueprint("main",__name__) # Blueprint object (collection of routes) created, called "main"

@main.route("/") # when "/" is visited, run function below
def home():
    return "Spending Tracker homepage"

@main.route("/transactions") # "/transactions" route
def transactions():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return render_template("transactions.html", transactions=transactions)

@main.route("/upload", methods=["GET","POST"]) # "/upload" route
def upload():
    if request.method == "GET":
        return render_template("upload.html")
    else:
        uploaded_file = request.files["csv_file"]
        imported_count, skipped_count = import_transactions_from_file(uploaded_file)
        return f"Imported: {imported_count} \n\n Skipped: {skipped_count}"

@main.route("/summary")
def summary():
    all_transactions = Transaction.query.all()
    month = request.args.get("month")
    transactions = all_transactions
    available_months = sorted(
        {f"{t.date.year}-{t.date.month}" for t in all_transactions},
        reverse=True
    )
    if month: # if month specified, filter to those transactions
        split = month.split("-")
        year = int(split[0])
        month_number = int(split[1])
        transactions = [t for t in transactions if t.date.year == year and t.date.month == month_number]
    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_spending = sum(t.amount for t in transactions if t.amount < 0)
    net_cashflow = total_income + total_spending
    transaction_count = len(transactions)
    return render_template(
        "summary.html",
        available_months=available_months,
        month=month,
        total_income=total_income,
        total_spending=total_spending,
        net_cashflow=net_cashflow,
        transaction_count=transaction_count
    )