import os 

basedir = os.path.abspath(os.path.dirname(__file__))

#SQLALCHEMY DATABASE CONFIGURATIONS
if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'x.db')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SECRET_KEY="powerful secretkey"
WTF_CSRF_SECRET_KEY="a csrf secret key"
