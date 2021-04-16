import os
import requests
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, validators
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
    password = PasswordField('password', validators=[
                             validators.InputRequired('Password is required')])
    recaptcha = RecaptchaField()


class RegistrationForm(LoginForm):
    name = StringField('name', validators=[validators.InputRequired('Name is required'), validators.Length(
        min=3, max=50, message='Name must be between 3 and 50 characters.')])


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
            session["user"] = form.email.data
            flash("Registration Successful.")
            return redirect(url_for("Profile", name=form.name.data))

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
                session["user"] = (form.email.data).lower()
                flash("Login successful")
                return redirect(url_for("index"))

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


@app.route("/profile")
def profile():
    return render_template("profile.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
