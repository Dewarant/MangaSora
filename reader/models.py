from reader import app, db
from sqlalchemy.sql import func
from dataclasses import dataclass
from datetime import datetime
from flask_login import UserMixin
from reader import manager


@dataclass
class Book(db.Model):
    id: int
    title: str
    author: str
    genre: str
    cover: str
    rating: int
    description: str
    notes: str
    price: int
    created_at: str
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(20), nullable=False)
    rating = db.Column(db.Integer)
    cover = db.Column(db.String(50), nullable=False, default='default.jpg')
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False, default=1960)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Book {self.title}>'


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    psw = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer, default=1)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Users {self.id}>'


@manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)