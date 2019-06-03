from flask import (flash, json, jsonify, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_user
from flask_mail import Mail, Message
from sqlalchemy import func
from validate_email import validate_email

from . import app, basic_auth, db, lm, mail
from .constants import *
from .faq import newsSet
from .forms import CompanyForm, EmailForm, MenuForm, RegisterForm
from .models import User

def validate_phone(number):
    if len(number) == 10:
        return number.isnumeric()
    elif len(number) == 13:
        return number.split('+')[1].isnumeric()
    else:
        return False

def do_data(message):
    print("*****************************************", message)
    if "one fusion" in message.lower():
        return jsonify({'status': 'OK', 'answer': "Would you like to purchase bundle or make and enquiry?"})
    elif "one fi" in message.lower():
        current_user.stage = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': "Netone offers Home Wifi would you like to purchase data. Dial *171*99# to purchase"})
    elif "settings" in message.lower():
        current_user.stage = "menu"
        current_user.save()
        message = '''
            Go to Settings on your mobile phone
            Choose Cellular Networks
            Next, click on Access Point Names
            Click on the plus sign to the top right of your screen to set up your APN
            Name the APN “Netone”
            The APN for Netone is internet.netone
            Leave the Proxy, Port, Username, Password, Server , MMSC, MMSC proxy and MMS Port as is.
            Make sure that the MCC is set at 648
            The MNC should be set at 01
            Leave Authentication type and APN type unset
            The APN protocol should be IPv4/IPv6
            Leave everything else as is.
            Now Save everything. You do this by clicking on the three dots to the top right of your screen and choosing “Save.”
            Thank You
        '''
        return jsonify({'status': 'OK', 'answer': message})
    elif "purchase" or "bundles" in message.lower():
        current_user.stage = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': "Dial *400# to purchase bundle. Thank You"})
    elif "enquiry" or "balance" in message.lower():
        current_user.stage = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': "Dial *400# to make balance enquiry. Thank You"})
    elif "data" or "mo data" in message.lower():
        current_user.stage = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': "We have whatsapp bundles and Data Bundles. Dial *171# and choose option 3"})
    else:
        current_user.stage = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': "Please select any of the options provided or click menu"})

def do_money(message):
    if current_user.position == 0:
        if "register" in message.lower():
            message = '''
                Dial *111# and follow instructions
                when done please visit any Netone shop to complete registration
                Thank you for chosing One Money
            '''
            current_user.position = "menu"
            current_user.save()
            return jsonify({'status': 'OK', 'answer': message})
        elif "reset pin" in message.lower():
            current_user.position = 1
            current_user.save()
            return jsonify({'status': 'OK', 'answer': "Please enter your phone number"})
        elif "transfer money" or "transfer" in message.lower():
            current_user.stage = "menu"
            current_user.save()
            return jsonify({'status': 'OK', 'answer': "dial *111*1*1#. Thank you for chosing One Money"})
        elif "airtime" in message.lower():
            current_user.stage = "menu"
            current_user.save()
            return jsonify({'status': 'OK', 'answer': "dial *111*4#. Thank you for chosing One Money"})
        elif "zesa" in message.lower():
            current_user.stage = "menu"
            current_user.save()
            return jsonify({'status': 'OK', 'answer': "dial *111*2*1*1#. Thank you for chosing One Money"})
        else:
            current_user.stage = "menu"
            current_user.save()
            return jsonify({'status': 'OK', 'answer': "Please select any of the options provided or click menu"})
    elif current_user.position == 1:
        if validate_phone(message):
            current_user.position = 2
            current_user.save()
            return jsonify({'status': 'OK', 'answer': "Please eneter your ID number"})
        else:
            return jsonify({'status': 'OK', 'answer': "Please eneter a valid phone number"})
    elif current_user.position == 2:
        current_user.menu = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': "Thank You our customer service will contact you for further assistance. Thank you for chosing One Money"})


def do_sms(message):
    if "purchase" in message.lower():
        message = '''
            Dial *171# , choose option 3 and choose option 3 again
            Thank you for chosing One Money
        '''
        current_user.position = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': message})
    elif "enquiry" or "account" in message.lower():
        message = '''
            Dial *171# , choose option 3 and choose option 3 again
            Thank you for chosing One Money
        '''
        current_user.position = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': message})
    else:
        current_user.stage = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': "Please select any of the options provided or click menu"})

def do_airtime(message):
    if "recharge" in message.lower():
        message = '''
            Dial *133*recharge pin#, 
            Thank you for chosing One Money
        '''
        current_user.position = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': message})
    elif "balance" or "enquiry" in message.lower():
        message = '''
            Dial *134#, 
            Thank you for chosing One Money
        '''
        current_user.position = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': message})
    elif "transfer" in message.lower():
        message = '''
            Dial *171# and choose option 7, 
            Thank you for chosing One Money
        '''
        current_user.position = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': message})
    else:
        current_user.stage = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': "Please select any of the options provided or click menu"})

def do_bundles(message):
    if "data" in message.lower():
        message = '''
            Dial *171# choose option 3, 
            Thank you for chosing One Money
        '''
        current_user.position = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': message})
    elif "dollar" in message.lower():
        message = '''
            Dial *171#, 
            Thank you for chosing One Money
        '''
        current_user.position = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': message})
    elif "khuluma" in message.lower():
        message = '''
            Dial *171# , 
            Thank you for chosing One Money
        '''
        current_user.position = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': message})
    else:
        current_user.stage = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': "Please select any of the options provided or click menu"})


def do_vas(message):
    if "one music" in message.lower():
        message = '''
            Dial 335 to subscribe and listen to your favourite music wherever, whenever!, 
            Thank you for chosing One Money
        '''
        current_user.position = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': message})
    elif "one radio" in message.lower():
        message = '''
            Dial 336 and choose the show you want to listen to instantly, 
            Thank you for chosing One Money
        '''
        current_user.position = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': message})
    elif "news" or "on one" in message.lower():
        message = '''
            Dial 337 and subscribe from as little as $0,10 to hear the latest news, 
            Thank you for chosing One Money
        '''
        current_user.position = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': message})
    elif "global" or "international" in message.lower():
        message = '''
            Stay connected anywhere in the world while you travel with OneGlobal, 
            To activate OneGlobal SMS ROAMON to 34444
            Safe travels and Thank you for chosing One Money
        '''
        current_user.position = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': message})
    else:
        current_user.stage = "menu"
        current_user.save()
        return jsonify({'status': 'OK', 'answer': "Please select any of the options provided or click menu"})