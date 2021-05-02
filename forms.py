from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (Form, StringField, IntegerField, PasswordField,
                     TextAreaField, FormField, FieldList, validators)
from wtforms.fields.html5 import EmailField

image_extensions = {'png', 'jpg', 'jpeg'}


class SearchForm(FlaskForm):
    """Search form with 1 text input."""

    search = StringField('Search for recipes', validators=[validators.Length(
        min=1, max=30, message='Search text must be between 1 and 30 characters.')])


class LoginForm(FlaskForm):
    """Login form with email and password inputs."""

    email = EmailField('Email', validators=[
        validators.InputRequired('Email is required')])
    password = PasswordField('Password', validators=[validators.InputRequired('Password is required'), validators.Length(
        min=3, max=30, message='Password must be between 3 and 30 characters.')])


class RegistrationForm(LoginForm):
    """Registration form that extends
    the login form, adding a name input.
    """

    name = StringField('Name', validators=[validators.InputRequired('Name is required'), validators.Length(
        min=3, max=50, message='Name must be between 3 and 50 characters.')])
    # recaptcha = RecaptchaField()


class EditProfileForm(FlaskForm):
    """Form to edit a user profile with name, description
    and image inputs.
    """

    name = StringField('Name', validators=[validators.InputRequired('Name is required'), validators.Length(
        min=3, max=50, message='Name must be between 3 and 50 characters.')])
    description = TextAreaField('Description', validators=[validators.InputRequired('Enter a description.'), validators.length(
        min=10, max=2000, message='Description must be between 10 and 2000 characters.')])
    image = FileField('Profile Picture', validators=[
        FileAllowed(image_extensions, message='Only image files are allowed')
    ])


class IngredientForm(Form):
    """An ingredient subform that is used in a parent recipe form.
    Contains 2 fields; quantity and ingredient.
    """

    quantity = StringField('Quantity', validators=[validators.InputRequired('Quantity is required'), validators.Length(
        min=0, max=30, message='Quantity must be between 0 and 30 characters.')])
    ingredient = StringField('Ingredient', validators=[validators.InputRequired('Ingredient is required'), validators.Length(
        min=1, max=40, message='Ingredient must be between 1 and 40 characters.')])


class AddRecipeForm(FlaskForm):
    """A form to add a new recipe. Contains name, instructions,
    servings, time_required and image inputs. Also contains an ingredient
    subform with 2 inputs.
    """

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
