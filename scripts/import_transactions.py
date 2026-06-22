from app import create_app
from app.extensions import db
from app.models import Transaction
from app.services.importer import make_fingerprint, import_transactions_from_file
import pandas as pd
from pathlib import Path
import hashlib

csv_path = Path("./data/raw/credit_may_june.csv").resolve()

app = create_app()
with app.app_context():
    imported_count, skipped_count = import_transactions_from_file(csv_path)
    print(f"Imported: {imported_count} \n\n Skipped: {skipped_count}")
