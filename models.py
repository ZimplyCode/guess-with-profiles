import os
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite"))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    name = db.Column(db.String)
    password = db.Column(db.String)
    session_token = db.Column(db.String)
    secret_number = db.Column(db.Integer)
    best_game = db.Column(db.Integer)
    total_guesses = db.Column(db.Integer)
    games_won = db.Column(db.Integer)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String)
    comment = db.Column(db.String)
