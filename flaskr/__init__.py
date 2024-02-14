# Hide all informations 

# USER form
# TODO -> security for modals
# TODO -> regex for creating account on backend
# TODO -> checking if the password == confirm_password

# BUSINESS form
# TODO -> regex for creating account on backend
# abort when some of the data are not given and html is changed 

from flask import Flask, render_template, request, abort, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import re

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)

class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False) 

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    price = db.Column(db.Integer, unique=False, nullable=False)

with app.app_context():
    db.create_all()

def create_account(email, password):
    """Create a new user account."""
    user = User.query.filter_by(email=email).first()
    if user: 
        return False
    pw_hash = generate_password_hash(password)
    new_user = User(email=email, password=pw_hash)
    db.session.add(new_user)
    db.session.commit()
    session["user_email"] = email.split("@")[0]
    return True

def sign_in(email, password):
    """Sign in existing user."""
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session["user_email"] = email.split("@")[0]
        return True
    return False

def check_status():
    """Looking is user is loged in to the session."""
    if "user_email" in session:
        return session["user_email"]
    else:
        return None

def process_form_request():
    """Process the incoming form request."""
    form_type = request.form.get("form_type")
    if form_type == "create_account":
        email = request.form.get("email")
        password = request.form.get("password")
        return create_account(email, password), None  
    elif form_type == "signin":
        email = request.form.get("email_login")
        password = request.form.get("password_login")
        success = sign_in(email, password)
        return None, not success  
    return None, None 

@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    error_message = None
    
    if request.method == "POST":
        message, error_message = process_form_request()
            
    return render_template("/user/index.html", message=message, error_message=error_message, user=check_status())

@app.route("/signout", methods=["POST"])
def signout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/delivery")
def delivery():
    return render_template("/user/delivery.html")

@app.route("/business", methods=["GET"])
def business_index():
    return render_template("/business/index.html")

@app.route("/business/login")
def business_login():
    return render_template("/business/login.html")

@app.route("/admin/dashboard")
def business_admin():
    return render_template("admin/dashboard.html")

@app.route("/admin/menu")
def business_admin_menu():
    return render_template("admin/menu.html")
