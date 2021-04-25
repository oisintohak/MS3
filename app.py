import os
import requests
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from gridfs import GridFS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (Form, StringField, IntegerField, PasswordField,
                     TextAreaField, FormField, FieldList, validators)
from wtforms.fields.html5 import EmailField

if os.path.exists("env.py"):
    import env


app = Flask(__name__)

# only allow files under 2MB to be uploaded
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

app.secret_key = os.environ.get("SECRET_KEY")
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["RECAPTCHA_PUBLIC_KEY"] = os.environ.get("RECAPTCHA_PUBLIC_KEY")
app.config["RECAPTCHA_PRIVATE_KEY"] = os.environ.get("RECAPTCHA_PRIVATE_KEY")
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

mongo = PyMongo(app)

image_extensions = {'png', 'jpg', 'jpeg'}


class LoginForm(FlaskForm):
    email = EmailField('email', validators=[
        validators.InputRequired('Email is required')])
    password = PasswordField('password', validators=[validators.InputRequired('Password is required'), validators.Length(
        min=3, max=30, message='Password must be between 3 and 30 characters.')])
    # recaptcha = RecaptchaField()


class RegistrationForm(LoginForm):
    name = StringField('name', validators=[validators.InputRequired('Name is required'), validators.Length(
        min=3, max=50, message='Name must be between 3 and 50 characters.')])


class IngredientForm(Form):
    quantity = StringField('Quantity', validators=[validators.InputRequired('Quantity is required'), validators.Length(
        min=0, max=30, message='Quantity must be between 0 and 30 characters.')])
    ingredient = StringField('Ingredient', validators=[validators.InputRequired('Ingredient is required'), validators.Length(
        min=1, max=40, message='Ingredient must be between 1 and 40 characters.')])


class AddRecipeForm(FlaskForm):
    name = StringField('Name', validators=[validators.InputRequired('Name is required'), validators.Length(
        min=3, max=50, message='Name must be between 3 and 50 characters.')])
    ingredients = FieldList(FormField(IngredientForm),
                            min_entries=2, max_entries=30)
    instructions = TextAreaField('Instructions', validators=[validators.InputRequired('Enter instructions for the recipe.'), validators.length(
        min=10, max=2000, message='Instructions must be between 10 and 2000 characters.')])
    servings = IntegerField('Servings', validators=[
                            validators.InputRequired('Servings is required'), validators.NumberRange(min=1, max=100, message='Servings must be between 1 and 100.')])
    time_required = IntegerField('Time required (minutes)', validators=[
                                 validators.InputRequired(
                                     'Enter a value for time required (in minutes).'),
                                 validators.NumberRange(
                                     min=1, max=1000, message='Time required must be between 1 and 1000 (minutes).')
                                 ])
    image = FileField('Recipe Image', validators=[
        FileAllowed(image_extensions, message='Only image files are allowed')
    ])


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
    recipes = list(mongo.db.recipes.find({
        "added_by": user
    }))
    user = mongo.db.users.find_one(
        {"email": user})
    return render_template("profile.html", user=user, recipes=recipes)


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if "user" not in session:
        flash("You need to log in to add a recipe.")
        return redirect(url_for("login"))
    form = AddRecipeForm()
    if request.method == "POST":
        if form.validate_on_submit():
            new_recipe = {
                "name": form.name.data,
                "ingredients": form.ingredients.data,
                "instructions": form.instructions.data,
                "servings": form.servings.data,
                "time_required": form.time_required.data,
                "added_by": session["user"],
                "added_by_name": mongo.db.users.find_one(
                    {"email": session["user"]}
                )["name"]
            }
            if form.image.data:
                recipe_image = request.files['image']
                secured_filename = secure_filename(recipe_image.filename)
                mongo.save_file(secured_filename, recipe_image)
                new_recipe["recipe_image"] = recipe_image.filename
                new_recipe["recipe_image_url"] = url_for(
                    'file', filename=recipe_image.filename)

            mongo.db.recipes.insert_one(new_recipe)
            return redirect(url_for("profile", user=session["user"]))

    return render_template("add_recipe.html", form=form)


@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    if "user" not in session:
        flash("You need to log in to edit a recipe.")
        return redirect(url_for("login"))

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    if recipe["added_by"] != session["user"]:
        flash("You can only edit your own recipes.")
        return redirect(url_for("profile", user=session["user"]))

    form = AddRecipeForm(data=recipe)

    if not recipe:
        flash("Recipe not found.")

    if request.method == "POST":
        if form.validate_on_submit():
            # use $set to only change the specified fields
            update_recipe = {"$set": {
                "name": form.name.data,
                "ingredients": form.ingredients.data,
                "instructions": form.instructions.data,
                "servings": form.servings.data,
                "time_required": form.time_required.data,
            }}
            if recipe["recipe_image"]:
                # save reference to old image:
                old_image = recipe["recipe_image"]

            if form.image.data:
                recipe_image = request.files['image']
                secured_filename = secure_filename(recipe_image.filename)
                mongo.save_file(secured_filename, recipe_image)
                update_recipe["recipe_image"] = recipe_image.filename
                update_recipe["recipe_image_url"] = url_for(
                    'file', filename=recipe_image.filename)

            mongo.db.recipes.update_one(
                {"_id": ObjectId(recipe_id)}, update_recipe)
            image = mongo.db.fs.files.find_one({"filename": old_image})
            if image:
                image_ID = ObjectId(image["_id"])
                GridFS(mongo.db).delete(image_ID)
            flash("Recipe Updated")
            return redirect(url_for("profile", user=session["user"]))

    return render_template("edit_recipe.html", recipe=recipe, form=form)


@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)


@app.errorhandler(404)
def error404(e):
    flash("404 - Page not found")
    return render_template('index.html'), 404


@app.errorhandler(413)
def error413(e):
    flash("Image cannot exceed 2MB.")
    return redirect(request.url), 413


@app.errorhandler(503)
def error503(e):
    flash("Server Error 503.")
    return render_template('index.html'), 503


@app.errorhandler(500)
def error500(e):
    flash("Server Error 500.")
    return render_template('index.html'), 500

# if __name__ == "__main__":
#     app.run(host=os.environ.get("IP"),
#             port=int(os.environ.get("PORT")),
#             debug=False)
