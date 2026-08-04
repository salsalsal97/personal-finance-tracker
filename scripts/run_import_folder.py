from app import create_app
from app.services.importer import import_transactions_from_file
from pathlib import Path
import shutil

app = create_app()

def get_statement_type(filename):
    if filename.startswith("hsbc_credit"):
        return "hsbc_credit"
    elif filename.startswith("hsbc_current"):
        return "hsbc_current"
    elif filename.startswith("hsbc_savings"):
        return "hsbc_savings"
    elif filename.startswith("amex"):
        return "amex"
    elif filename.startswith("legacy"):
        return "legacy"
    else:
        return None

with app.app_context():
    inbox_path = Path("data/inbox").resolve()
    archive_path = Path("data/archive").resolve()
    files = [f for f in inbox_path.iterdir() if f.is_file()]
    if not files:
        print("No files found.")
        exit()
    files_processed = 0
    total_imported = 0
    total_skipped = 0
    failed_files = 0
    for file in files:
        print()
        print(f"Processing: {file.name}")
        statement_type = get_statement_type(file.name.lower())
        if statement_type is None:
            print("Skipped: filename does not match a supported statement type.")
            continue
        try:
            imported_count, skipped_count = import_transactions_from_file(file, statement_type)
            print(f"Statement type: {statement_type}")
            print(f"Transactions imported: {imported_count}")
            print(f"Transactions skipped: {skipped_count}")
            archive_destination = archive_path / file.name
            if archive_destination.exists():
                print("Warning: a file with this name already exists in the archive.")
                print("The imported file has been left in the inbox.")
                continue
            shutil.move(str(file), str(archive_destination))
            print(f"Archived to: {archive_destination}")
            files_processed += 1
            total_imported += imported_count
            total_skipped += skipped_count
        except Exception as exc:
            failed_files += 1
            print(f"Failed: {exc}")
            print("The file has been left in the inbox.")
    print()
    print("=" * 40)
    print("Import complete")
    print("=" * 40)
    print(f"Files processed successfully: {files_processed}")
    print(f"Transactions imported: {total_imported}")
    print(f"Transactions skipped: {total_skipped}")
    print(f"Failed files: {failed_files}")