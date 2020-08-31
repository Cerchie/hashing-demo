from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key= True, autoincrement =True)

    username = db.Column(db.Text, nullable= False, unique= True)

    password = db.Column(db.Text, nullable= False)

    @classmethod
    def register(cls, username, pwd)

    hashed = bcrypt.generate_password_hash(pwd)
    hashed_utf8 = hashed.decode("utf8")

    return cls(username=username, password=hashed_utf8)