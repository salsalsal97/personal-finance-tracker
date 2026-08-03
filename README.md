# Personal Finance Tracker

A personal finance web application built with Flask for importing, categorising, and analysing transactions from multiple bank accounts.

## Features

* Upload transaction statements through a web interface
* Supports:

  * HSBC Current Account
  * HSBC Credit Card
  * HSBC Savings Account
  * American Express
* Normalises different statement formats into a common transaction structure
* Prevents duplicate imports using transaction fingerprints
* Automatically categorises transactions using description-based rules
* Provides a manual review page for uncategorised transactions
* Excludes internal transfers and card repayments from income and spending totals
* Filters summaries by month
* Displays:

  * Total money in
  * Total money out
  * Net cashflow
  * Spending by category
  * Category spending chart

## Tech Stack

* Python
* Flask
* Flask-SQLAlchemy
* SQLite
* pandas
* Jinja
* Chart.js

## Project Structure

```text
app/
├── services/
│   └── importer.py
├── templates/
├── __init__.py
├── extensions.py
├── models.py
└── routes.py

scripts/
└── seed_categories.py
└── statement_to_csv.py

create_db.py
run.py
requirements.txt
```

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv venv
pip install -r requirements.txt
```

Create the database:

```bash
python create_db.py
```

Seed the initial categories:

```bash
python scripts/seed_categories.py
```

Start the application:

```bash
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

Useful pages:

```text
/upload
/transactions
/categorise
/summary
```

## Data Privacy

Bank statements, uploaded transaction files, and the local SQLite database are excluded from version control through `.gitignore`.

## Current Limitations

* Categorisation rules are currently defined in Python
* Positive card transactions are generally treated as repayments, so refunds may require manual review
* The application currently uses Flask's local development server
* Legacy historical spreadsheet imports are not yet supported

## Planned Improvements

* Legacy Excel import
* Improved user interface and navigation
* Editable categorisation and exclusion rules
* Additional financial visualisations
* Production deployment
* Automated statement-processing workflow
