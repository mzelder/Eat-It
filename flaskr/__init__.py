import os
import re
from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, abort



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, template_folder="templates")
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)


    @app.route("/", methods=["GET", "POST"])
    def index():
        message = None
        database = db.get_db()
        
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            # Ensure email match regex
            if not re.match(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$", email):
                return abort(400, description="Invalid input")
            
            # Ensure password is not blank
            if not password:
                return abort(400, description="Invalid input")
            
            # Ensure password have at least 8 characters where at least 1 uppercase letter, one number, one symbol
            if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password):
                return abort(400, description="Invalid input")

            # Ensure password and confirm_password are equal
            if password != confirm_password:
                return abort(400, description="Invalid input")

            # Ensure user dont exist
            cursor = database.cursor()
            cursor.execute("SELECT * FROM customer WHERE email = ?", (email,)) 
            user = cursor.fetchone()
            print(user)
            if user is not None:
                message = False
            else:
                # Hash the password
                bcrypt = Bcrypt(app)
                pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")

                # Adding user to the database
                database.execute("INSERT INTO customer (email, password) VALUES (?, ?)", (email, pw_hash))
                database.commit()
                message = True

        return render_template("index.html", message=message)

    
    @app.route("/delivery")
    def delivery():
        # query = request.args.get("search", "")
        # restaurants = db.get_restaurants(query)
        return render_template("delivery.html") #restaurants=restaurants)


    return app