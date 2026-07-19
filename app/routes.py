from flask import Blueprint, render_template, request, redirect, url_for
from app.models import Transaction, Category
from app.extensions import db
from app.services.importer import import_transactions_from_file

main = Blueprint("main",__name__) # Blueprint object (collection of routes) created, called "main"

@main.route("/") # when "/" is visited, run function below
def home():
    return render_template("home.html")

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
        if not uploaded_file or not uploaded_file.filename:
            return render_template("upload_missing.html")
        statement_type = request.form.get("statement_types")
        imported_count, skipped_count = import_transactions_from_file(uploaded_file, statement_type)
        return render_template(
            "upload_result.html",
            imported_count=imported_count,
            skipped_count=skipped_count
        )

@main.route("/summary")
def summary():
    all_transactions = Transaction.query.all()
    month = request.args.get("month")
    transactions = all_transactions
    available_months = sorted(
        {f"{t.date.year}-{t.date.month:02d}" for t in all_transactions},
        reverse=True
    )
    if month: # if month specified, filter to those transactions
        split = month.split("-")
        year = int(split[0])
        month_number = int(split[1])
        transactions = [t for t in transactions if t.date.year == year and t.date.month == month_number]
    valid_transactions = [t for t in transactions if t.exclude_from_summary is False]
    excluded_transactions = set(transactions) - set(valid_transactions)
    total_income = sum(t.amount for t in valid_transactions if t.amount > 0)
    total_spending = sum(t.amount for t in valid_transactions if t.amount < 0)
    net_cashflow = total_income + total_spending
    transaction_count = len(valid_transactions)
    category_totals = {}
    for transaction in valid_transactions:
        if transaction.amount < 0:
            if transaction.category:
                category_name = transaction.category.name
            else:
                category_name = "Uncategorised"
            category_totals[category_name] = category_totals.get(category_name, 0) + abs(transaction.amount)
    category_totals = sorted(
        category_totals.items(),
        key=lambda item: item[1],
        reverse=True
    )
    category_names = []
    category_amounts = []
    for name_amount in category_totals:
        category_names.append(name_amount[0])
        category_amounts.append(name_amount[1])
    exclude_transactions_count = len(excluded_transactions)
    return render_template(
        "summary.html",
        available_months=available_months,
        month=month,
        total_income=total_income,
        total_spending=total_spending,
        net_cashflow=net_cashflow,
        transaction_count=transaction_count,
        category_totals=category_totals,
        category_names=category_names,
        category_amounts=category_amounts,
        exclude_transactions_count=exclude_transactions_count
    )

@main.route("/categorise", methods=["GET","POST"])
def categorise():
    if request.method == "POST":
        transaction_id = request.form.get("transaction_id")
        category_id = request.form.get("category_id")
        transaction = db.session.get(Transaction, int(transaction_id))
        if transaction:
            transaction.category_id = category_id
        db.session.commit()
        return redirect(url_for("main.categorise"))
    else:
        transactions = Transaction.query.filter_by(category_id=None).order_by(Transaction.date.desc()).all()
        categories = Category.query.order_by(Category.name).all()
        return render_template(
            "categorise.html",
            transactions=transactions,
            categories=categories
        )