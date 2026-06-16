import os
from flask import Flask
from flask_sqlalchemy import SQLALchemy
from dotenv import load_dotenv

# initialize SQLALchemy database object
db = SQLALchemy()

# Application factory function which create and configure flask application
def create_app():

    #load environment variable from .env file
    load_dotenv()

    #creates flask application instance
    app = Flask(__name__)

    #----- Configuration -----

    #secret key for session encryption and CSRF protection
    app.config["SECRET_KEY"] = os.getenv("SECRET_KET","dev-secret-change-me")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI","sqlite:///aura_db")#fall backs to sqlite if db_uri not found

    #disable modificatiuon tracking for better performance
    app.congif["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["BRAND_WHATSAPP_NUMBER"] = os.getenv("BRAND_WHATSAPP_NUMBER",9199999999)#for business contact

    #initialize database with the flask app and this connects the db object to the app
    db.init_app(app)

    #creates all database tables based on models
    with app.app_context():
        app.create_all()

    # Blueprint Register
    from .routes import bp
    app.register_blueprint(bp)

    return app
