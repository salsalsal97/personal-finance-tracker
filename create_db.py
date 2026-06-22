from app import create_app
from app.extensions import db

app = create_app() # creates app

with app.app_context(): # make this app the active application
    db.create_all() # creates tables