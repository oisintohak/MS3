import os
import requests
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import Form, StringField, IntegerField, PasswordField, SelectField, FormField, FieldList, validators
from wtforms.fields.html5 import EmailField
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")
app.config["RECAPTCHA_PUBLIC_KEY"] = os.environ.get("RECAPTCHA_PUBLIC_KEY")
app.config["RECAPTCHA_PRIVATE_KEY"] = os.environ.get("RECAPTCHA_PRIVATE_KEY")

mongo = PyMongo(app)


class LoginForm(FlaskForm):
    email = EmailField('email', validators=[
        validators.InputRequired('Email is required')])
    password = PasswordField('password', validators=[validators.InputRequired('Password is required'), validators.Length(
        min=3, max=30, message='Password must be between 3 and 30 characters.')])
    recaptcha = RecaptchaField()


class RegistrationForm(LoginForm):
    name = StringField('name', validators=[validators.InputRequired('Name is required'), validators.Length(
        min=3, max=50, message='Name must be between 3 and 50 characters.')])


class IngredientForm(Form):
    quantity = StringField('quantity')
    ingredient = StringField('ingredient')


class AddRecipeForm(FlaskForm):
    name = StringField('name', validators=[validators.InputRequired('Name is required'), validators.Length(
        min=3, max=50, message='Name must be between 3 and 50 characters.')])
    ingredients = FieldList(FormField(IngredientForm),
                            min_entries=2, max_entries=30)
    servings = IntegerField('servings', validators=[validators.InputRequired('Servings is required')])


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if request.method == "POST":
        # check if email has already been used
        email_used = mongo.db.users.find_one(
            {"email": (form.email.data).lower()})
        if email_used:
            flash("That email has already been used.")
            return redirect(url_for("register"))

        if form.validate_on_submit():
            new_user = {
                "name": form.name.data,
                "email": (form.email.data).lower(),
                "password": generate_password_hash(form.password.data)
            }
            mongo.db.users.insert_one(new_user)

            # put the new user into session cookie
            session["user"] = (form.email.data).lower()
            flash("Registration Successful.")
            return redirect(url_for("profile", user=session["user"]))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        # check if email has been registered
        email_registered = mongo.db.users.find_one(
            {"email": (form.email.data).lower()}
        )

        if email_registered:
            # compare hashed password to user input
            if check_password_hash(email_registered["password"], form.password.data):
                if form.validate_on_submit():
                    session["user"] = (form.email.data).lower()
                    flash("Login successful")
                    return redirect(url_for("profile", user=session["user"]))

            else:
                flash("Wrong email/password")
                return redirect(url_for("login"))

        else:
            flash("Wrong email/password")
            return redirect(url_for("login"))

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("index"))


@app.route("/profile/<user>")
def profile(user):
    user = mongo.db.users.find_one(
        {"email": user})
    return render_template("profile.html", user=user)


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    form = AddRecipeForm()
    if request.method == "POST":
        if form.validate_on_submit():
            return render_template("display_recipe.html", recipe=form)

    return render_template("add_recipe.html", form=form)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
