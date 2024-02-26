# Hide all informations 

# USER form
# TODO -> security for modals
# TODO -> regex for creating account on backend
# TODO -> checking if the password == confirm_password

# BUSINESS form
# TODO -> regex for creating account on backend
# abort when some of the data are not given and html is changed 

# ADMIN
# protect admin roots

from flask import Flask, render_template, request, abort, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from functools import wraps
import os
import re
import string
import random


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
UPLOAD_FOLDER = "flaskr/static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), unique=False, nullable=False)

class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), unique=False, nullable=False) 
    restaurant = db.relationship('Restaurant', backref='owner', uselist=False)

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False) 
    photo = db.Column(db.String(80), unique=False, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), unique=True)
    foods = db.relationship('Items', backref='restaurant', lazy=True)

# adding description
# adding photo of the item
# restart database
class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    price = db.Column(db.Integer, unique=False, nullable=False)
    category = db.Column(db.String(80), unique=False, nullable=False)
    # description = db.Column(db.String(80), unique=False, nullable=False)
    # image_path = db.Column(db.String(80), unique=False, nullable=False) 
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(80), unique=False, nullable=False)
    street = db.Column(db.String(80), unique=False, nullable=False)
    street_number = db.Column(db.String(80), unique=False, nullable=False)
    postal_code = db.Column(db.String(80), unique=False, nullable=False)
    phone_number = db.Column(db.String(80), unique=False, nullable=False)
    # adding country? 

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

def sign_in(email, password, who):
    """Sign in existing user."""
    if who == "user":
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_email"] = email.split("@")[0]
            return True
    elif who == "owner":
        owner = Owner.query.filter_by(email=email).first()
        if owner and check_password_hash(owner.password, password):
            session["owner_email"] = email
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
        success = sign_in(email, password, "user")
        return None, not success  
    return None, None 

def generate_password(length):
    """Generating hashed password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "owner_email" not in session:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    error_message = None
    
    if request.method == "POST":
        message, error_message = process_form_request()
            
    return render_template("/user/index.html", message=message, error_message=error_message, user=check_status())

@app.route("/signout", methods=["POST", "GET"])
def signout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/delivery")
def delivery():
    restaurants = Restaurant.query.all() 
    return render_template("/user/delivery.html", restaurants=restaurants, user=check_status())

@app.route("/menu/<restaurant_name>")
def menu(restaurant_name):
    # Keep track of the last restaurant so the add-to-cart function know where to redirect
    session["last_restaurant"] = restaurant_name
    restaurant = Restaurant.query.filter_by(name=restaurant_name).first()
    items = Items.query.filter_by(restaurant_id=restaurant.id).all()

    # Sort items by category
    items_by_category = {}
    for item in items:
        if item.category in items_by_category:
            items_by_category[item.category].append(item)
        else:
            items_by_category[item.category] = [item]

    return render_template("/user/menu.html", items_by_category=items_by_category, restaurant=restaurant, user=check_status())

@app.route("/increase-quantity/<int:id>", methods=["POST"])
def increase_quantity(id):
    # Initialize the shopping cart if it doesn't exist
    if 'shopping_cart' not in session:
        session['shopping_cart'] = []
    
    # Setup flag
    item_exists = False
    
    # Query the item by ID
    item = Items.query.get_or_404(id)

    # Check if item already exists in cart
    for cart_item in session['shopping_cart']:
        if cart_item['id'] == item.id:
            cart_item['quantity'] += 1  # Increase the quantity
            cart_item['total_price'] = cart_item["price"] * cart_item["quantity"]
            item_exists = True
            break

    # Add item details to the shopping cart
    if not item_exists:
        session['shopping_cart'].append({
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'total_price': item.price,
            'category': item.category,
            'quantity': 1
        })

    session.modified = True
    print(session["shopping_cart"])
    return redirect(url_for('menu', restaurant_name=session.get("last_restaurant")))

@app.route("/decrease-quantity/<int:id>", methods=["POST"])
def decrease_quantity(id):
    pass

@app.route("/business", methods=["GET", "POST"])
def business_index():
    if request.method == "POST":
        first_name = request.form.get("name")
        surname = request.form.get("surname")
        phone_number = request.form.get("phone_number")
        street_number = request.form.get("street_number")
        street = request.form.get("street_name")
        city = request.form.get("city")
        postal_code = request.form.get("postal_code")
        email = request.form.get("email")
        restaurant_name = request.form.get("restaurant_name")
        
        # Ensure all informations are given
        if not all([first_name, surname, city, street, street_number, postal_code, phone_number]):
            return abort(405)

        # Send password to the owner of the restaurant
        password = generate_password(length=12)
        msg = Message(subject="EatIt | Your password", sender=os.environ.get("EMAIL_EATIT"), recipients=[f"{email}"])
        msg.body = f"Your password: {password} \n Log in to admin panel via: http://127.0.0.1:5000/business/login"
        mail.send(msg)
        
        # Add owner of the restaurant to the database
        owner = Owner(email=email, password=generate_password_hash(password))
        db.session.add(owner)
        db.session.commit()

        # Add restaurant to database
        restaurant = Restaurant(name=restaurant_name, owner_id=owner.id)
        db.session.add(restaurant)
        db.session.commit()

        # Add address of the restaurant to database
        address = Address(
            city = city,
            street = street,
            street_number = street_number, 
            postal_code = postal_code, 
            phone_number = phone_number
        )
        db.session.add(address)
        db.session.commit()
        return f"You will find your password on this email: {email}"
        
    return render_template("/business/index.html")

@app.route("/business/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if sign_in(email, password, "owner"):
            # adding owner to session
            owner = Owner.query.filter_by(email=email).first()
            session["owner_id"] = owner.id
            
            # adding restaurant to session
            restaurant = Restaurant.query.filter_by(owner_id = owner.id).first()
            session["restaurant_name"] = restaurant.name
            return redirect(url_for("admin"))
    return render_template("/business/login.html")

@app.route("/admin/dashboard")
@owner_required
def admin():
    return render_template("admin/dashboard.html")

@app.route("/admin/menu")
@owner_required
def admin_menu():
    items = Items.query.filter_by(restaurant_id=session["owner_id"]).all()
    return render_template("admin/menu.html", items=items)

@app.route("/admin/orders")
@owner_required
def admin_orders():
    return render_template("admin/orders.html")

@app.route("/admin/settings", methods=["GET", "POST"])
@owner_required
def admin_settings():
    if request.method == "POST":
        restaurant = Restaurant.query.filter_by(owner_id=session["owner_id"]).first()
        restaurant.name = request.form.get("restaurant_name")
        session["restaurant_name"] = request.form.get("restaurant_name")
        return redirect(url_for("admin_settings"))
    return render_template("admin/settings.html")

@app.route("/admin/change-restaurant-name", methods=["POST"])
@owner_required
def change_restaurant_name():
    # Ensure restaurant are not blank
    restaurant_name = request.form.get("restaurant_name")
    if restaurant_name == "":
        return abort(405)
    
    # Changeing restaurant name in database and session
    restaurant = Restaurant.query.filter_by(owner_id=session["owner_id"]).first()
    restaurant.name = restaurant_name
    session["restaurant_name"] = request.form.get("restaurant_name")
    db.session.commit()
    return redirect(url_for("admin_settings"))

@app.route("/admin/change-password", methods=["POST"])
@owner_required
def change_password():
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if sign_in(session["owner_email"], current_password, "owner") and new_password == confirm_password:
        owner = Owner.query.filter_by(email=session["owner_email"]).first()
        owner.password = generate_password_hash(new_password)
        db.session.commit()
        return redirect(url_for("admin_settings")) 
    
@app.route("/admin/add-item", methods=["POST"])
@owner_required
def add_item():
    name = request.form.get("item_name")
    price = request.form.get("price")
    category = request.form.get("category")
    restaurant_id = session["owner_id"]

    # Ensure all informations are given
    if not all([name, price, category]):
        return abort(405)
    
    item = Items(name=name, price=price, category=category, restaurant_id=restaurant_id)
    db.session.add(item)
    db.session.commit()
    return redirect(url_for("admin_menu"))

@app.route("/admin/edit-item", methods=["POST"])
@owner_required
def edit_item():
    item_id = request.form.get("item_id")
    name = request.form.get("item_name")
    price = request.form.get("price")
    category = request.form.get("category")

    item = Items.query.filter_by(id=item_id).first()
    item.name = name
    item.price = price
    item.category = category
    db.session.commit()
    return redirect(url_for("admin_menu"))

@app.route("/admin/delete-item", methods=["POST"])
@owner_required
def delete_item():
    item_id = request.form.get("item_id")
    item = Items.query.filter_by(id=item_id).first()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("admin_menu"))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/admin/update-photo", methods=["POST"])
@owner_required
def update_photo():
    # check if the post request has the file part
    if 'file' not in request.files:
        print("No file part")
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Add photo to the database
        restaurant = Restaurant.query.filter_by(owner_id=session["owner_id"]).first()
        restaurant.photo = "/static/uploads/" + filename
        db.session.commit()
        return redirect(url_for("admin_settings"))
    return redirect(url_for("admin_settings"))