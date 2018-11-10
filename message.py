import os
import re
from string import letters
import webapp2
import jinja2

from google.appengine.ext import db


template_dir = os.path.dirname(__file__)
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


##### Message stuff

def Message_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Messages(db.Model):
    name = db.StringProperty(required = True)
    email = db.StringProperty(required = True)
    comment = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class BlogFront(BlogHandler):
    def get(self):
        posts = Messages.all().order('-created')
        self.render('messages.html', posts = posts)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class NewMessage(BlogHandler):
    def get(self):
        self.render('index.html')
            
    def post(self):
        name = self.request.get('name')
        email = self.request.get('email')
        comment = self.request.get('comment')

        if name and email and comment:
            data = Messages(parent = Message_key(), name = name, email = email, comment = comment)
            data.put()
            self.redirect('/')


app = webapp2.WSGIApplication([('/', NewMessage),
                               ('/messages', BlogFront),
                               ],
                              debug=True)
