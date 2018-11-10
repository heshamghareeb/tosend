import os
import re
import random
import hashlib
import hmac
from string import letters
import jinja2
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from database_t import *

template_dir = os.path.dirname(__file__)

app = Flask(__name__, template_folder= template_dir+'templates',
            static_folder= template_dir+'static')

engine = create_engine('sqlite:///test0.db')
Base.metadata.bind = engine

session = scoped_session(sessionmaker(bind=engine))

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
        return resp
    else:
        return render_template('Login.html', error = "wrong login")

def check_secure_val(secure_val):
    val = secure_val.split('|')[1]
    return val == valid_cookie(val)


def logout(path):
    if path == '/Login':
        path = redirect('/Login')
    else:
        path = redirect('/')
    resp = app.make_response(redirect('/'))
    resp.set_cookie('userID', '')
    return resp

@app.route('/', methods=['GET', 'POST'])

def get():
    if request.method == 'GET':
        return render_template('index.html')
    name = request.form['name']
    email = request.form['email']
    comment = request.form['comment']
    if name and email and comment:
        session.rollback()
        data = Messages(name = name, email = email, comment = comment)
        session.add(data)
        session.commit()
        return logout('/')
    else:
        return render_template('index.html')

        
@app.route('/messages')
def Posts():
    cookies = request.cookies.get('userID')
    if cookies == '' or cookies == None:
        return redirect('/Login')
    elif len(cookies) > 30:
        if check_secure_val(cookies):
            posts = session.query(Messages).all()
            z = list(posts)
            return render_template('messages.html', posts = z)
    else:
        return render_template('Login.html', error = "Wrong Login")


@app.route('/Login', methods=['GET', 'POST'])
def getcookie():
    if request.method == 'GET':
        return  render_template('Login.html')
    elif request.method == 'POST':
        cookies = request.cookies.get('userID')
        name = request.form['username']
        pw = request.form['password']
        if name and pw:
            return Login(name, pw)
    return render_template('Login.html', error = "wrong login")


@app.route('/logout')
def out():
    if request.method == 'GET':
        return logout('/')
    elif request.method == 'POST':
        return logout('/')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
