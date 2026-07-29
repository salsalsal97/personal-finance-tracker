from flask import Flask
from app.extensions import db

def create_app():
    app = Flask(__name__) # creates Flask app
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///spending_tracker.db" # essentially specifies location of database (app.config is a dictionary)
    app.config["SECRET_KEY"] = "replace-this-with-a-random-secret"
    db.init_app(app) # links database to Flask app
    from app import models # imports Transaction class (creates db)
    from app.routes import main # imports blueprint
    app.register_blueprint(main) # adds routes to application
    return app