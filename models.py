from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(15), nullable=False, unique=True)
    password = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(10), nullable=False, unique=True)


class Cash(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(15), nullable=False, unique=True)
    operations = db.Column(db.Text, nullable=True) # {operation_name, profit/expense, monney}