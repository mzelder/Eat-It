from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), unique=False, nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)

class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), unique=False, nullable=False) 
    restaurant = db.relationship('Restaurant', backref='owner', uselist=False)

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False) 
    background_image = db.Column(db.String(80), unique=False, nullable=True)
    icon_image = db.Column(db.String(80), unique=False, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), unique=True)
    foods = db.relationship('Items', backref='restaurant', lazy=True)
    orders = db.relationship('Order', backref='restaurant', lazy=True)

class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    price = db.Column(db.Integer, unique=False, nullable=False)
    category = db.Column(db.String(80), unique=False, nullable=False)
    description = db.Column(db.String(80), unique=False, nullable=True)
    image_path = db.Column(db.String(80), unique=False, nullable=True) 
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    orders = db.relationship('OrderItem', back_populates='item')

class RestaurantAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(80), unique=False, nullable=False)
    street = db.Column(db.String(80), unique=False, nullable=False)
    street_number = db.Column(db.String(80), unique=False, nullable=False)
    postal_code = db.Column(db.String(80), unique=False, nullable=False)
    phone_number = db.Column(db.String(80), unique=False, nullable=False)

class DeliveryAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(80), unique=False, nullable=False)
    house_number = db.Column(db.String(80), unique=False, nullable=False)
    nip = db.Column(db.String(80), unique=False, nullable=True)
    access_code = db.Column(db.String(80), unique=False, nullable=True)
    city = db.Column(db.String(80), unique=False, nullable=False)
    flat_number = db.Column(db.String(80), unique=False, nullable=True)
    floor = db.Column(db.String(80), unique=False, nullable=True)
    postal_code = db.Column(db.String(80), unique=False, nullable=False)
    company_name = db.Column(db.String(80), unique=False, nullable=True)
    note = db.Column(db.String(80), unique=False, nullable=True)
    first_name = db.Column(db.String(80), unique=False, nullable=False)
    last_name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(80), unique=False, nullable=False)
    phone_number = db.Column(db.String(80), unique=False, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    date = db.Column(db.String(80), unique=False, nullable=False)
    set_time = db.Column(db.String(80), unique=False, nullable=False)
    payment = db.Column(db.String(80), unique=False, nullable=False)
    total_price = db.Column(db.Integer, unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    items = db.relationship('OrderItem', back_populates='order')

class OrderItem(db.Model):
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    order = db.relationship("Order", back_populates="items")
    item = db.relationship("Items", back_populates="orders")