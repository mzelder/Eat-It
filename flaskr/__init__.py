import os
import re
from flask import Flask, render_template, request


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


    
    def validate_password(password):
        # Ensure password length is at least 8 characters
        if len(password) < 8:
            return False
        
        # Ensure password contains at least one uppercase letter
        if not re.search(r"[A-Z]", password):
            return False

        # Ensure password contains at least one digit
        if not re.search(r"\d", password):
            return False

        # Ensure password contains at least one special symbol
        if not re.search(r"[!@#$%^&*()_+{}|:<>?~]", password):
            return False

        return True


    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            # Ensure email is correct (should contain @)
            
            
            # Ensure password have at least 8 characters, one upppercase, number and symbol
            validate_password(password)
            
            # Ensure passwords are exacly the same
            # if password != confirm_password:
            #     return False

        return render_template("index.html")

    
    @app.route("/delivery")
    def delivery():
        # query = request.args.get("search", "")
        # restaurants = db.get_restaurants(query)
        return render_template("delivery.html") #restaurants=restaurants)


    return app