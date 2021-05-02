import os
import requests
from bson.objectid import ObjectId
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for, abort)
from flask_pymongo import PyMongo
from gridfs import GridFS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from forms import (LoginForm, RegistrationForm, SearchForm,
                   EditProfileForm, IngredientForm, AddRecipeForm)

if os.path.exists('env.py'):
    import env

app = Flask(__name__)

# Only allow files under 2MB to be uploaded
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

app.secret_key = os.environ.get('SECRET_KEY')
app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.config['RECAPTCHA_PUBLIC_KEY'] = os.environ.get('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get('RECAPTCHA_PRIVATE_KEY')
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

mongo = PyMongo(app)


@app.route('/')
def index():
    """Render the home page template"""

    search_form = SearchForm()
    return render_template('index.html', search_form=search_form)


@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    Take a text query from the search_form and return any matching
    results from the database.
    """

    search_form = SearchForm()
    if request.method == 'POST':
        query = search_form.search.data
        recipes = list(mongo.db.recipes.find({'$text': {'$search': query}}))
        return render_template(
            'search.html',
            search_form=search_form,
            recipes=recipes
        )


@app.route('/display_recipe/<recipe_id>')
def display_recipe(recipe_id):
    """
    Retrieve the specified recipe from the database and render
    the display_recipe template.
    """

    recipe = mongo.db.recipes.find_one_or_404({'_id': ObjectId(recipe_id)})
    search_form = SearchForm()
    return render_template(
        'display_recipe.html',
        recipe=recipe,
        search_form=search_form
        )


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Render a registration form. After verifying that
    the email has not been previously registered, add the
    user to the session variable and redirect to the profile page.
    """

    search_form = SearchForm()
    form = RegistrationForm()
    if request.method == 'POST':
        email_used = mongo.db.users.find_one(
            {'email': (form.email.data).lower()})
        if email_used:
            flash('That email has already been used.')
            return redirect(url_for('register'))

        if form.validate_on_submit():
            new_user = {
                'name': form.name.data,
                'email': (form.email.data).lower(),
                'password': generate_password_hash(form.password.data)
            }
            mongo.db.users.insert_one(new_user)

            session['user'] = (form.email.data).lower()
            flash('Registration Successful.')
            return redirect(url_for('profile', user=session['user']))

    return render_template(
        'register.html',
        form=form,
        search_form=search_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Render a login form. After verifying that the email has been
    registered and the password is correct, add the user to
    the session variable and redirect to the profile page.
    """

    search_form = SearchForm()
    form = LoginForm()
    if request.method == 'POST':
        # check if email has been registered
        email_registered = mongo.db.users.find_one(
            {'email': (form.email.data).lower()}
        )

        if email_registered:
            # compare hashed password to user input
            if check_password_hash(email_registered['password'],
                                   form.password.data):
                if form.validate_on_submit():
                    session['user'] = (form.email.data).lower()
                    flash('Login successful')
                    return redirect(
                        url_for('profile', user=session['user'])
                    )

            else:
                flash('Wrong email/password')
                return redirect(url_for('login'))

        else:
            flash('Wrong email/password')
            return redirect(url_for('login'))

    return render_template('login.html', form=form, search_form=search_form)


@app.route('/logout')
def logout():
    """
    Remove the user from the session variable and redirect to
    the home page.
    """

    if session.get('user'):
        session.pop('user')
        flash('You have been logged out')

    return redirect(url_for('index'))


@app.route('/profile/<user>')
def profile(user):
    """
    Retrieve the data for a user and their recipes from the
    database and render the profile template.
    """

    user = mongo.db.users.find_one_or_404(
        {'email': user})
    recipes = list(mongo.db.recipes.find({
        'added_by': user['email']
    }))
    search_form = SearchForm()
    return render_template(
        'profile.html',
        user=user,
        recipes=recipes,
        search_form=search_form
    )


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    """
    After verifying that a user is logged in, render a form to
    edit the user's profile. If an image is selected to upload,
    save a reference to the old image for deletion from GridFS.
    Update the relevant fields in the user document in mongoDB.
    """

    if 'user' not in session:
        redirect(url_for('login'))

    search_form = SearchForm()
    user = mongo.db.users.find_one_or_404(
        {'email': session.get('user')})
    form = EditProfileForm(data=user)
    if request.method == 'POST':
        if form.validate_on_submit():
            update_profile = {'$set': {
                'name': form.name.data,
                'description': form.description.data,
            }}
            if form.image.data:
                try:
                    profile_picture = request.files['image']
                    secured_filename = secure_filename(
                        profile_picture.filename)
                    mongo.save_file(secured_filename, profile_picture)
                    update_profile['$set']['profile_picture'] = secured_filename
                    update_profile['$set']['profile_picture_url'] = url_for(
                        'file', filename=secured_filename
                    )
                except RequestEntityTooLarge as e:
                    # Handle error for upload size limit.
                    abort(413)
                    return redirect(url_for('index'))

            if user.get('profile_picture'):
                old_profile_picture = user['profile_picture']
                image = mongo.db.fs.files.find_one(
                    {'filename': old_profile_picture})
                image_ID = ObjectId(image['_id'])
                GridFS(mongo.db).delete(image_ID)

            mongo.db.users.update_one(
                {'_id': ObjectId(user['_id'])}, update_profile)
            flash('Profile Updated')
            return redirect(url_for('profile', user=session['user']))

    return render_template(
        'edit_profile.html',
        user=user,
        form=form,
        search_form=search_form
    )


@app.route('/delete_profile', methods=['GET', 'POST'])
def delete_profile():
    """
    After verifying that a user is logged in, save a reference
    to any existing profile picture for deletion from gridFS and
    remove the user document from mongoDB. Render the home page
    template.
    """

    if not session.get('user'):
        flash('You need to log in to delete your profile.')
        return redirect(url_for('login'))

    user = mongo.db.users.find_one_or_404({'email': session.get('user')})

    if user.get('profile_picture'):
        image_filename = user['profile_picture']
        image = mongo.db.fs.files.find_one({'filename': image_filename})
        image_ID = ObjectId(image['_id'])
        GridFS(mongo.db).delete(image_ID)

    mongo.db.users.remove({'_id': ObjectId(user['_id'])})
    session.pop('user')
    flash('Profile Deleted')
    return redirect(url_for('index'))


@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    """
    After verifying that a user is logged in, render a form to
    add a new recipe. When submitted, validate the user input and
    any image upload. Secure the image filename and insert the
    document into mongoDB.
    """

    search_form = SearchForm()
    if 'user' not in session:
        flash('You need to log in to add a recipe.')
        return redirect(url_for('login'))

    form = AddRecipeForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_recipe = {
                'name': form.name.data,
                'ingredients': form.ingredients.data,
                'instructions': form.instructions.data,
                'servings': form.servings.data,
                'time_required': form.time_required.data,
                'added_by': session['user'],
                'added_by_name': mongo.db.users.find_one(
                    {'email': session['user']}
                )['name']
            }
            if form.image.data:
                recipe_image = request.files['image']
                secured_filename = secure_filename(recipe_image.filename)
                mongo.save_file(secured_filename, recipe_image)
                new_recipe['recipe_image'] = recipe_image.filename
                new_recipe['recipe_image_url'] = url_for(
                    'file', filename=recipe_image.filename)

            mongo.db.recipes.insert_one(new_recipe)
            return redirect(url_for('profile', user=session['user']))

    return render_template('add_recipe.html',
                           form=form,
                           search_form=search_form)


@app.route('/edit_recipe/<recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    """
    Verify that a user is logged in and they created the recipe.
    Render a form to edit the recipe. Validate the user input when
    submitted and any image upload. Secure the filename and update
    the relevant fields in the mongoDB document.
    """

    if not session.get('user'):
        flash('You need to log in to edit a recipe.')
        return redirect(url_for('login'))

    search_form = SearchForm()
    recipe = mongo.db.recipes.find_one_or_404({'_id': ObjectId(recipe_id)})

    if recipe['added_by'] != session['user']:
        flash('You can only edit your own recipes.')
        return redirect(url_for('profile', user=session['user']))

    form = AddRecipeForm(data=recipe)

    if request.method == 'POST':
        if form.validate_on_submit():
            update_recipe = {'$set': {
                'name': form.name.data,
                'ingredients': form.ingredients.data,
                'instructions': form.instructions.data,
                'servings': form.servings.data,
                'time_required': form.time_required.data,
            }}

            if form.image.data:
                recipe_image = request.files['image']
                secured_filename = secure_filename(recipe_image.filename)
                mongo.save_file(secured_filename, recipe_image)
                update_recipe['$set']['recipe_image'] = recipe_image.filename
                update_recipe['$set']['recipe_image_url'] = url_for(
                    'file', filename=recipe_image.filename
                )
                if recipe.get('recipe_image'):
                    # save reference to old image:
                    old_image = recipe['recipe_image']
                    image = mongo.db.fs.files.find_one(
                        {'filename': old_image}
                    )
                    image_ID = ObjectId(image['_id'])
                    GridFS(mongo.db).delete(image_ID)

            mongo.db.recipes.update_one(
                {'_id': ObjectId(recipe_id)}, update_recipe)
            flash('Recipe Updated')
            return redirect(url_for('profile', user=session['user']))

    return render_template(
        'edit_recipe.html',
        recipe=recipe,
        form=form,
        search_form=search_form
    )


@app.route('/delete_recipe/<recipe_id>', methods=['GET', 'POST'])
def delete_recipe(recipe_id):
    """
    Verify that a user is logged in, they created the recipe and
    the recipe exists. Delete any recipe image and remove the
    document from mongoDB.
    """

    if not session.get('user'):
        flash('You need to log in to delete a recipe.')
        return redirect(url_for('login'))

    recipe = mongo.db.recipes.find_one_or_404({'_id': ObjectId(recipe_id)})
    if recipe['added_by'] != session['user']:
        flash('You can only delete your own recipes.')
        return redirect(url_for('profile', user=session['user']))

    if recipe.get('recipe_image'):
        # save reference to old image:
        image_filename = recipe['recipe_image']
        image = mongo.db.fs.files.find_one({'filename': image_filename})
        image_ID = ObjectId(image['_id'])
        GridFS(mongo.db).delete(image_ID)

    mongo.db.recipes.remove({'_id': ObjectId(recipe_id)})
    flash('Recipe Deleted')
    return redirect(url_for('profile', user=session['user']))


@app.route('/file/<filename>')
def file(filename):
    """Return the specified file from mongoDB GridFS"""
    return mongo.send_file(filename)


@app.errorhandler(404)
def error404(e):
    flash('404 - Page not found')
    return render_template('index.html'), 404


@app.errorhandler(413)
def error413(e):
    flash('Image cannot exceed 2MB.')
    return render_template('index.html')


@app.errorhandler(503)
def error503(e):
    flash('Server Error 503.')
    return render_template('index.html'), 503


@app.errorhandler(500)
def error500(e):
    flash('Server Error 500.')
    return render_template('index.html'), 500


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=os.environ.get('DEBUGGING'))
