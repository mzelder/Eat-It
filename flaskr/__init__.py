from flask import Flask, render_template, request, abort, session, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import os
import re

# create and configure the app
app = Flask(__name__)
app.config["SECRET_KEY"] = "5fqsWngZk4UX_b8lZtBvzw"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)

with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    error_message = None
    
    if request.method == "POST":
        form_type = request.form.get("form_type")
        
        if form_type == "create_account":
            # The account creation logic using SQLAlchemy
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            # Check if user already exists
            user = User.query.filter_by(email=email).first()
            if user:
                message = False
            else:
                # Hash the password and create new user
                pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
                new_user = User(email=email, password=pw_hash)
                db.session.add(new_user)
                db.session.commit()
                message = True
                session["user_email"] = email.split("@")[0]

        elif form_type == "signin":
            # The sign-in logic using SQLAlchemy
            email = request.form.get("email_login")
            password = request.form.get("password_login")

            # Find user by email
            user = User.query.filter_by(email=email).first()
            if user and bcrypt.check_password_hash(user.password, password):
                session["user_email"] = email.split("@")[0]
                error_message = False
            else:
                error_message = True
            
    return render_template("index.html", message=message, error_message=error_message, user=check_status())

@app.route("/signout", methods=["POST"])
def signout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/delivery")
def delivery():
    return render_template("delivery.html")

@app.route("/business", methods=["GET"])
def business_index():
    return render_template("business_index.html")

@app.route("/business/login")
def business_login():
    return render_template("business_login.html")

@app.route("/business/admin")
def business_admin():
    return render_template("business_admin.html")

def check_status():
    if "user_email" in session:
        return session["user_email"]
    else:
        return None