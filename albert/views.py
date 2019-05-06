from flask import flash, json, jsonify, redirect, render_template, request, \
    url_for
from flask_login import current_user, login_user
from flask_mail import Mail, Message
from sqlalchemy import func
from validate_email import validate_email 

from . import app, db, lm, mail, basic_auth
from .dataset import newsSet
from .forms import CompanyForm, EmailForm, MenuForm, RegisterForm
from .models import CollectEmail, Company, FailedQn, PassedQn, User
from .naiveBayesClassifier.classifier import Classifier
from .naiveBayesClassifier.tokenizer import Tokenizer
from .naiveBayesClassifier.trainer import Trainer


token = Tokenizer()
faqTrainer = Trainer()

for news in newsSet:
    faqTrainer.train(news['question'], news['answer'])

faqClassifier = Classifier(faqTrainer.data, token)


@lm.user_loader
def load_user(userid):
    return User.query.get(int(userid))


@app.route('/')
def index():
    form = RegisterForm()
    return render_template('index.html', form=form)


@app.route('/process', methods=['POST'])
def process():

    email = request.form['email']
    name = request.form['name']
    surname = request.form['surname']

    print(
        "------------------------------{0}, {1}, {2}-------------".format(name, surname, email))

    if name and email:
        if validate_email(email, verify=True):

            message = "Welcome {}, what would you like to do <br/><br/><a href='https://kanzatu.stewardbank.co.zw/0771222727?view_campaign=fcee9faa-35c0-44d2-8add-66c41987de21' target='_blank'><button  style='background-color: #0080FF' class='btn btn-primary btn-block btn-round'>Donate to Cholera fund</button></a><br/>".format(name) + \
                    "<a href='#' onclick='apply(); return false;' style='color:white'><button id='btn1' style='background-color: #0080FF' class='btn btn-primary btn-block btn-round'>Apply for a Chatbot</a></button><br/><a href='#' onclick='about(); return false;' style='color:white'><button id='btn2' style='background-color: #0080FF; color:white' class='btn btn-primary btn-block btn-round'>About X Analytics</a></button>"

            user = User.find(email=email)

            if user:
                login_user(user, remember=True)
                return jsonify({'name': message})

            else:

                new = User(first_name=name, surname=surname, email=email)
                new.save()
                login_user(new, remember=True)
                return jsonify({'name': message})

        else:
            message = 'Please enter a valid email!'
            return jsonify({'name': message})

    return jsonify({'error': 'Please enter your details to proceed'})


@app.route('/send-mail', methods=['POST'])
def send_mail():
    print('+++++++++++++++++++++++++++ Got in Email ++++++++++++++++++++++++++++')


    try:
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        website = request.form['website']
        message = request.form['message']

        new = CollectEmail(name=name, email=email, phone=phone, message=message)
        new.save()
        return 'Mail sent!'
    except Exception as e:
        return(str(e))


@app.route('/ask', methods=["POST"])
def ask():
    message = request.form['messageText']
    button = "<a class='btn btn-danger' href='https://facebook.com'>Test<a>"
    if current_user.is_authenticated:
        state = get_state(current_user)
        if state == "menu":
            greetings = ['hello', 'hi', 'hey', 'yo',
                         'wassup', 'ndeipi', 'how are you']
            if message == "apply":
                current_user.stage = "company"
                current_user.save()
                return jsonify({'status': 'OK', 'answer': 'Before we setup your 30 day free trial, which company do you represent?'})
            elif message == "about" or "about" in message:
                current_user.stage = "chat"
                current_user.save()
                return jsonify({'status': 'OK', 'answer': 'What would you like to know about us? Type bye to exit to main menu'})
            elif message in greetings:
                response = "How are you what would you like to do <br/><br/><a href='https://kanzatu.stewardbank.co.zw/0771222727?view_campaign=fcee9faa-35c0-44d2-8add-66c41987de21' target='_blank'><button  style='background-color: #0080FF' class='btn btn-primary btn-block btn-round'>Donate to Cholera fund</button></a><br/>" + \
                    "<a href='#' onclick='apply(); return false;' style='color:white'><button id='btn1' style='background-color: #0080FF' class='btn btn-primary btn-block btn-round'>Apply for a Chatbot</a></button><br/><a href='#' onclick='about(); return false;' style='color:white'><button id='btn2' style='background-color: #0080FF; color:white' class='btn btn-primary btn-block btn-round'>About X Analytics</a></button>"
                return jsonify({'status': 'OK', 'answer': response})
        elif state == "company":
            if check_company(message):
                return True
            else:
                new = Company(name=message, dataset=current_user.email)
                new.save()
                current_user.stage = "phone"
                current_user.save()
                return jsonify({'status': 'OK', 'answer': "Oops! Your Company is not registered for a free 30 day trial, kindly provide your phone number so that I register you for a chatbot?"})
        elif state == "chat":
            exits = ['bye', 'exit', 'go back', 'good bye']
            if message in exits:
                current_user.stage = "menu"
                current_user.save()
                return jsonify({'status': 'OK', 'answer': 'Thank you for chatting with me'})
            msg = chat(message)
            return jsonify({'status': 'OK', 'answer': msg})
        elif state == "phone":
            if validate_phone(message):
                current_user.phone = message
                current_user.stage = "menu"
                current_user.save()
                return jsonify({'status': 'OK', 'answer': 'Thanks, our salesman will contact you soon to finalize your free 30 day trial'})
            else:
                return jsonify({'status': 'OK', 'answer': 'please enter a valid phone number'})
    else:
        return jsonify({'status': 'OK', 'answer': 'Please provide your email and names so that i know you before we start communicating'})
    response = "How are you what would you like to do <br/><br/><a href='https://kanzatu.stewardbank.co.zw/0771222727?view_campaign=fcee9faa-35c0-44d2-8add-66c41987de21' target='_blank'><button  style='background-color: #0080FF' class='btn btn-primary btn-block btn-round'>Donate to Cholera fund</button></a><br/>" + \
        "<a href='#' onclick='apply(); return false;' style='color:white'><button id='btn1' style='background-color: #0080FF' class='btn btn-primary btn-block btn-round'>Apply for a Chatbot</a></button><br/><a href='#' onclick='about(); return false;' style='color:white'><button id='btn2' style='background-color: #0080FF; color:white' class='btn btn-primary btn-block btn-round'>About X Analytics</a></button>"
    return jsonify({'status': 'OK', 'answer': response})


def get_state(current_user):
    return str(current_user.stage)


def check_company(name):
    company = Company.query.filter(func.lower(
        Company.name) == name.lower()).first()
    print("----------------------got: {}--------------------".format(company))
    if company is not None:
        return True
    else:
        return False


def chat(message):
    classification = faqClassifier.classify(str(message))
    for cl in classification[:1]:
        print(
            "---------------------classification at --------------------", cl[1])
        if cl[1] == 0:
            new = FailedQn(question=message)
            new.save()
            response = "Sorry i didnt understand that"
        else:
            response = str(cl[0])
            new = PassedQn(question=message, answer=response,
                           accuracy=round(cl[1], 4))
            new.save()
    return response


def validate_phone(number):
    if len(number) == 10:
        return number.isnumeric()
    elif len(number) == 13:
        return number.split('+')[1].isnumeric()
    else:
        return False

    
############################################ Admin Views ############################################################

@app.route('/admin')
@basic_auth.required
def admin():
    companies = Company.query.all()
    questions = PassedQn.query.all()
    failed = FailedQn.query.all()
    # emails = CollectEmail.query.all()
    users = User.query.all()
    return render_template('admin/index.html', companies=companies, users=users, questions=questions, failed=failed)

@app.route('/company/<id>', methods=['GET', 'POST'])
def company(id):
    company = Company.query.get(id)
    return render_template('admin/company.html', company=company)

@app.route('/add_company', methods=['GET', 'POST'])
def add_company():
    form = CompanyForm()
    if form.validate_on_submit():                                    
        company = Company(name=form.name.data, dataset=form.dataset.data)
        company.save()
        flash('Company successfully added!')
        return redirect(url_for('admin')) 
    return render_template('addcompany.html', form=form)                                                                       


@app.route('/add_menu/<id>', methods=['GET', 'POST'])
def add_menu(id):
    form = MenuForm()
    if form.validate_on_submit():
        new = MenuOption(title=form.title.data, button_type=form.button_type.data, payload=form.payload.data, company_id=id)
        new.save()
        flash('Menu succefully Added')
        return redirect(url_for('company', id=id))
    return render_template('addmenu.html', form=form)

@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    new = User.query.get(id)
    db.session.delete(new)
    db.session.commit()
    return redirect(url_for('admin'))
