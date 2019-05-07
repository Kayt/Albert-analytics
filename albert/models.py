from datetime import datetime

from . import db
from flask_login import UserMixin

from sqlalchemy import func

class CollectEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(120))
    message = db.Column(db.Text)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __init__(self, name, email, phone, message):
        self.name = name
        self.email = email
        self.phone = phone 
        self.message = message

class Tracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_accessed = db.Column(db.DateTime)
    name = db.Column(db.String(200))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __init__(self, name):
        self.name = name
        self.time_accessed = datetime.utcnow()


class FailedQn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __init__(self, question):
        self.question = question


class PassedQn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    answer = db.Column(db.Text)
    accuracy = db.Column(db.String(120))

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def __init__(self, question, answer, accuracy):
        self.question = question
        self.answer = answer 
        self.accuracy = accuracy

class MenuOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    button_type = db.Column(db.String(200))
    payload = db.Column(db.String(200))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __init__(self, title, button_type, payload, company_id):
        self.title = title
        self.button_type = button_type
        self.payload = payload
        self.company_id = company_id


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    dataset = db.Column(db.String(200))
    menu = db.relationship('MenuOption', backref='company.id', lazy='dynamic')

    @staticmethod
    def get_menu(name):
        company = Company.query.filter(func.lower(name) == name).first()
        return company.menu

    @staticmethod
    def all():
        return [company.name.lower() for company in Company.query.all()]


    def save(self):
        db.session.add(self)
        db.session.commit()

    def __init__(self, name, dataset):
        self.name = name 
        self.dataset = dataset

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200))
    surname = db.Column(db.String(200))
    email = db.Column(db.String(200), unique=True)
    phone = db.Column(db.String(200))
    stage = db.Column(db.String(200))
    last_accessed = db.Column(db.DateTime)
    position = db.Column(db.Integer, default=0)
   

    def __init__(self, first_name, surname, email):
        self.first_name = first_name
        self.surname = surname
        self.email = email
        self.stage = "menu"
        self.last_accessed = datetime.utcnow()
        self.position = 0


    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_phone(cls, phone):
        return cls.query.filter_by(phone=phone).first()

    @classmethod 
    def find(cls, email):
        return cls.query.filter_by(email=email).first()