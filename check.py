import os
import re
import random
import hashlib
import hmac
from string import letters
import jinja2
from flask import Flask, render_template, request, redirect, url_for, flash

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_t import Base, Messages, User

template_dir = os.path.dirname(__file__)

app = Flask(__name__, template_folder= template_dir+'templates',
            static_folder= template_dir+'static')

engine = create_engine('sqlite:///test0.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# hash

##def make_salt(length = 5):
##    return ''.join(random.choice('sdtdsn7853485') for x in xrange(length))

def make_pw_hash(name, pw, salt):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)




def make_id_cookie_hash(id_user = '0', salt= None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(id_user + salt).hexdigest()
    return '%s,%s' % (salt, h)

### check

def valid_cookie(h):
    a = session.query(User).first()
    c = a.id_cookie
    salt = c.split(',')[0]
    if salt+','+h == make_id_cookie_hash('0', salt):
        return h
    else:
        return False

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


#login

def Login(name, pw):
    a = session.query(User).first()
    n = a.name
    h = a.pw_hash
    if valid_pw(name, pw, h) and name == n:
        c = a.id_cookie
        i = a.id
        z = c.split(',')[1]
        resp = app.make_response(redirect('/messages'))
        resp.set_cookie('userID', str(i)+ '|' +str(z), 'path', '/')
        #return redirect('/messages')
        #return render_template('messages.html'), set_cookie('userID', str(i)+ '|' +str(z), 'path', '/')
        return resp
    else:
        return render_template('Login.html', error = "wrong login")

def check_secure_val(secure_val):
    val = secure_val.split('|')[1]
    return val == valid_cookie(val)


def logout(path):
    if path == '/Login':
        path = 'Login.html'
    else:
        path = 'index.html'
    resp = app.make_response(render_template(path))
    resp.set_cookie('userID', '')
    return resp
