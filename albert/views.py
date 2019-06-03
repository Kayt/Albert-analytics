import pandas as pd

from flask import flash, json, jsonify, redirect, render_template, request, \
    url_for
from flask_login import current_user, login_user
from flask_mail import Mail, Message
from sqlalchemy import func
from validate_email import validate_email 

from . import app, db, lm, mail, basic_auth
from .constants import *
from .faq import newsSet
from .helper_functions import *
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

data = pd.read_csv('callcentre.csv')


@lm.user_loader
def load_user(userid):
    return User.query.get(int(userid))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():

    email = request.form['email']
    name = request.form['name']
    surname = request.form['surname']

    print(
        "------------------------------{0}, {1}, {2}-------------".format(name, surname, email))

    if name and email:
        if validate_email(email, verify=True):

            message = welcome_msg.format(name)

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
    print("****************************{}************************".format(message))
    response = chat(message)
    print("****************************{}************************".format(response))
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
    keys = [k for k,v in data.category.value_counts().to_dict().items()][:20]
    values = data.category.value_counts().to_list()[:20]
    rvalues = values[::-1]
    further = values[20:40]
    context = {'keys': keys, 'values': values, 'rev':rvalues, 'far':further}
    return render_template('admin/index.html', context=context)

@app.route('/recommendations')
def recommend():
    return render_template('admin/recomendation.html')

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


# def ask():
#     message = request.form['messageText']
#     print("****************************{}************************".format(message))
    
#     button = "<a class='btn btn-danger' href='https://facebook.com'>Test<a>"
#     if current_user.is_authenticated:
#         state = get_state(current_user)
#         if state == "menu":
#             greetings = ['hello', 'hi', 'hey', 'yo',
#                          'wassup', 'ndeipi', 'how are you']
#             if message == "data" or "data" in message:
#                 current_user.stage = "data"
#                 current_user.save()
#                 return jsonify({'status': 'OK', 'answer': data_menu})
#             elif message == "money" or "money" in message:
#                 current_user.stage = "money"
#                 current_user.save()
#                 return jsonify({'status': 'OK', 'answer': money_menu})
#             elif message == "sms" or "sms" in message:
#                 current_user.stage = "sms"
#                 current_user.save()
#                 return jsonify({'status': 'OK', 'answer': sms_menu})
#             elif message == "airtime" or "airtime" in message:
#                 current_user.stage = "airtime"
#                 current_user.save()
#                 return jsonify({'status': 'OK', 'answer': airtime_menu})
#             elif message == "bundles" or "bundles" in message:
#                 current_user.stage = "bundles"
#                 current_user.save()
#                 return jsonify({'status': 'OK', 'answer': bundles_menu})
#             elif message == "vas" or "vas" in message:
#                 current_user.stage = "vas"
#                 current_user.save()
#                 return jsonify({'status': 'OK', 'answer': vas_menu})
#             elif message == "about" or "about" in message:
#                 current_user.stage = "about"
#                 current_user.save()
#                 return jsonify({'status': 'OK', 'answer': "Kindly visit any Oneworld(Netone) shop for assistance. Thank You.."})
#             elif message in greetings:
#                 return jsonify({'status': 'OK', 'answer': menu2})
#         elif state == "data":
#             return do_data(message)
#         elif state == "money":
#             return do_money(message)
#         elif state == "sms":
#             return do_sms(message)
#         elif state == "airtime":
#             return do_airtime(message)
#         elif state == "bundles":
#             return do_bundles(message)
#         elif state == "vas":
#             return do_vas(message)
#         elif state == "chat":
#             exits = ['bye', 'exit', 'go back', 'good bye']
#             if message in exits:
#                 current_user.stage = "menu"
#                 current_user.save()
#                 return jsonify({'status': 'OK', 'answer': 'Thank you for chatting with me'})
#             msg = chat(message)
#             return jsonify({'status': 'OK', 'answer': msg})
#         elif state == "phone":
#             if validate_phone(message):
#                 current_user.phone = message
#                 current_user.stage = "menu"
#                 current_user.save()
#                 return jsonify({'status': 'OK', 'answer': 'Thanks, our salesman will contact you soon to finalize your free 30 day trial'})
#             else:
#                 return jsonify({'status': 'OK', 'answer': 'please enter a valid phone number'})
#     else:
#         return jsonify({'status': 'OK', 'answer': 'Please provide your email and names so that i know you before we start communicating'})
#     return jsonify({'status': 'OK', 'answer': menu2})
