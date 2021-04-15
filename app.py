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


class RegistrationForm(FlaskForm):
    name = StringField('name', validators=[validators.InputRequired('Name is required'), validators.Length(
        min=3, max=50, message='Name must be between 3 and 50 characters.')])
    email = EmailField('email', validators=[
                       validators.InputRequired('Email is required')])
    password = PasswordField('password', validators=[
                             validators.InputRequired('Password is required')])
    recaptcha = RecaptchaField()


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
            session["user"] = form.name.data
            flash("Registration Successful.")
            return redirect(url_for("results", name=session["user"]))

    return render_template("register.html", form=form)


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("index"))


@app.route("/results")
def results():
    return render_template("results.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
