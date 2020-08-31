from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

def connect_db(app)
    dp.app = app
    db.init_app(app)

class User(db.Model)
    id = db.Column(db.Integer, primary_key= True, autoincrement =True)

    username = db.Column(db.Text, nullable= False, unique= True)

    password = db.Column(db.Text, nullable= False)