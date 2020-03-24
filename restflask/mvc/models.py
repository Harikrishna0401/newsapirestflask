from flask_sqlalchemy import SQLAlchemy
from mvc import app
import os

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password123@localhost/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    pid = db.Column(db.Integer,primary_key=True)
    public_id = db.Column(db.Text, unique=True)
    name = db.Column(db.Text,nullable=False)
    password = db.Column(db.Text,nullable=False)
    admin = db.Column(db.Boolean)

class News(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   title =  db.Column(db.Text)
   description =  db.Column(db.Text)
   url =  db.Column(db.Text)
   content = db.Column(db.String(1000))
   category = db.Column(db.Text)