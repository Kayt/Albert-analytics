from flask import Flask, jsonify, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Required


# app = Flask(__name__)
# app.secret_key = 'example'

class EmailForm(FlaskForm):
    name = StringField('name', validators=[Required('Please Enter Your Name')])
    email = StringField('name', validators=[Required('Please Enter Your email')])
    phone = StringField('name', validators=[Required('Please Enter Your phone')])
    message = TextAreaField('name', validators=[Required('Please Enter Your Message')])

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[Required('Please Enter Your Name')], render_kw={
        "placeholder": "Name"})
    email = StringField('Email', validators=[Required('Please Enter Your Email')], render_kw={
        "placeholder": "Email"})


class CompanyForm(FlaskForm):
    name = StringField('name: ', validators=[DataRequired()])
    dataset = StringField('dataset', validators=[DataRequired()])


class MenuForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    button_type = StringField('type', validators=[DataRequired()])
    payload = StringField('payload', validators=[DataRequired()])
