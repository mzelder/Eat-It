from flask import Flask, render_template, request, abort, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from .models import db, User, Owner, Restaurant, Items, RestaurantAddress, DeliveryAddress, Order, OrderItem
from flask_mail import Mail, Message
from functools import wraps
import os
import re
import string
import random
import datetime


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

db.init_app(app)
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
        email = request.form.get("email_create_account")
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

    # Increasing the quantity and update the total price
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

    # Total price of all items in the shopping cart
    total_price = 0.0
    for cart_item in session['shopping_cart']:
        total_price += cart_item['total_price']
    
    # Update the total price in the session
    session['total_price'] = total_price

    session.modified = True
    return redirect(url_for('menu', restaurant_name=session.get("last_restaurant")))

@app.route("/decrease-quantity/<int:id>", methods=["POST"])
def decrease_quantity(id):
    # Query the item by ID
    item = Items.query.get_or_404(id)

    # Decrease the quantity and update the total price
    for cart_item in session['shopping_cart']:
        if cart_item['id'] == item.id:
            cart_item['quantity'] -= 1
            cart_item['total_price'] = cart_item["price"] * cart_item["quantity"]
            if cart_item['quantity'] == 0:
                session['shopping_cart'].remove(cart_item)
            break

    # Total price of all items in the shopping cart
    total_price = 0.0
    for cart_item in session['shopping_cart']:
        total_price += cart_item['total_price']
    
    # Update the total price in the session
    session['total_price'] = total_price
        
    session.modified = True
    return redirect(url_for('menu', restaurant_name=session.get("last_restaurant")))

@app.route("/checkout/<restaurant_name>", methods=["POST"])
def checkout(restaurant_name):
    restaurant = Restaurant.query.filter_by(name=restaurant_name).first()
    return render_template("/user/checkout.html", restaurant=restaurant, user=check_status())

@app.route("/thank-you", methods=["GET" ,"POST"])
def order_confirm():
    if request.method == "GET":
        return render_template("/user/thankyou.html")
    #required
    street_name = request.form.get("street_name")
    city = request.form.get("city")
    house_number = request.form.get("house_number")
    first, last = request.form.get("first_last_name").split()
    phone_number = request.form.get("phone_number")
    email = request.form.get("email_checkout")
    postal_code = request.form.get("postcode")

    # optional
    nip = request.form.get("nip")
    floor = request.form.get("floor")
    company_name = request.form.get("company_name")
    access_code = request.form.get("access_code")
    flat_number = request.form.get("flat_number")
    add_note = request.form.get("add_note")

    delivery_time = request.form.get("deliveryTimeInput")
    payment_method = request.form.get("paymentMethodInput")
    
    # Ensure first, last, email, phone number and postal code are valid
    if not re.match("^\w+ \w+$", first + " " + last):
        return abort(403)
    if not re.match(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$$", email):
        return abort(403)
    if not re.match(r"^\+\d{2} \d{3} \d{3} \d{3}$", phone_number):
        return abort(403)
    if not re.match(r"^\d{2}-\d{3}$", postal_code):
        return abort(403)
    
    # Ensure all required informations are given
    if not all([street_name, city, house_number, first, last, phone_number, email, postal_code]):
        return abort(403)

    # Add delivery address and personail details to the database
    delivery_address = DeliveryAddress(
        first_name = first,
        last_name = last,
        phone_number = phone_number,
        email = email,
        street = street_name,
        house_number = house_number,
        city = city,
        postal_code = postal_code,
        nip = nip,
        floor = floor,
        company_name = company_name,
        access_code = access_code,
        flat_number = flat_number,
        note = add_note
    )
    db.session.add(delivery_address)
    
    # Add order to the database
    order = Order(
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        set_time = delivery_time,
        payment = payment_method,
        total_price = session["total_price"], # prob bug here
        restaurant_id = Restaurant.query.filter_by(name=session.get("last_restaurant")).first().id
    )
    db.session.add(order)
    db.session.commit()
    
    # Add items from the shopping cart to the database
    if "shopping_cart" in session:
        for item in session["shopping_cart"]:
            order_item = OrderItem(
                order_id = order.id,
                item_id = item["id"],
                quantity = item["quantity"]
            )
            db.session.add(order_item)
    else:
        return abort(403)
    
    db.session.commit()

    return render_template("/user/thankyou.html")

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
            return abort(203)

        # Ensure email, phone number and postal code are valid
        if not re.match(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$$", email):
            return abort(203)
        if not re.match(r"^\+\d{2} \d{3} \d{3} \d{3}$", phone_number):
            return abort(203)
        if not re.match(r"^\d{2}-\d{3}$", postal_code):
            return abort(203)

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
        address = RestaurantAddress(
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
    return render_template("admin/settings.html")

@app.route("/admin/change-restaurant-name", methods=["POST"])
@owner_required
def change_restaurant_name():
    # Ensure restaurant are not blank
    restaurant_name = request.form.get("restaurant_name")
    if restaurant_name == "":
        flash("Restaurant name cannot be blank", "danger")
        return redirect(url_for("admin_settings"))
    
    # Changeing restaurant name in database and session
    restaurant = Restaurant.query.filter_by(owner_id=session["owner_id"]).first()
    restaurant.name = restaurant_name
    session["restaurant_name"] = request.form.get("restaurant_name")
    db.session.commit()
    flash("Restaurant name has been changed", "success")
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
        flash("Your password has been successfully changed.", "success")
    else:
        flash("Failed to change password. Please make sure your current password is correct and the new passwords match.", "danger")
    return redirect(url_for("admin_settings"))
    
@app.route("/admin/add-item", methods=["POST"])
@owner_required
def add_item():
    name = request.form.get("item_name")
    price = request.form.get("price")
    category = request.form.get("category")
    description = request.form.get("description")
    restaurant_id = session["owner_id"]

    #Ensure price meet regex pattern
    if not re.match(r"^(?!0\d)\d+\.\d{2}$", price):
        return abort(403)

    # Ensure all informations are given
    if not all([name, price, category, description]):
        return abort(403)

    item = Items(name=name, price=price, category=category, description=description, restaurant_id=restaurant_id)

    # Ensure image is given
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an empty file without a filename.
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Add photo to the database
        item.image_path = "/static/uploads/" + filename

    db.session.add(item)
    db.session.commit()
    return redirect(url_for("admin_menu"))

@app.route("/admin/edit-item", methods=["POST"])
@owner_required
def edit_item():
    item_id = request.form.get("item_id")
    name = request.form.get("item_name", None)
    price = request.form.get("price", None)
    description = request.form.get("description", None)
    category = request.form.get("category", None)

    #Ensure price meet regex pattern
    if price and not re.match(r"^(?!0\d)\d+\.\d{2}$", price):
        return abort(403)

    item = Items.query.filter_by(id=item_id).first()

    # Check for file upload without making it mandatory
    file = request.files.get('file', None)
    if file and file.filename:
        if not allowed_file(file.filename):
            return abort(400)  # Unsupported file type
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        item.image_path = "/static/uploads/" + filename

    # Only update fields if they are provided
    if name != "":
        item.name = name
    if price != "":
        item.price = price
    if description != "":
        item.description = description
    if category != "":
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

@app.route("/admin/update-image/<image_type>", methods=["POST"])
@owner_required
def update_image(image_type):
    # Check if the post request has the file part
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an empty file without a filename.
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Add photo to the database
        restaurant = Restaurant.query.filter_by(owner_id=session["owner_id"]).first()
        if image_type == "background":
            restaurant.background_image = "/static/uploads/" + filename
        elif image_type == "logo":
            restaurant.icon_image = "/static/uploads/" + filename
        else:
            flash("Invalid image type.", "danger")
            return redirect(request.url)
        db.session.commit()
        flash(f"Your {image_type} image has been successfully changed.", "success")
    return redirect(url_for("admin_settings"))