from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FloatField, IntegerField, SelectField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange
from wtforms.validators import ValidationError
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class StoreForm(FlaskForm):
    name = StringField('Store Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    address = StringField('Address', validators=[Optional(), Length(max=200)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email()])
    website = StringField('Website', validators=[Optional(), Length(max=200)])
    theme = SelectField('Theme', choices=[
        ('default', 'Default'),
        ('modern', 'Modern'),
        ('classic', 'Classic'),
        ('minimal', 'Minimal')
    ])
    logo = FileField('Logo')
    banner = FileField('Banner')
    submit = SubmitField('Save Store')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    compare_price = FloatField('Compare Price', validators=[Optional(), NumberRange(min=0)])
    stock_quantity = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0)])
    is_featured = BooleanField('Featured Product')
    image = FileField('Product Image')
    submit = SubmitField('Save Product')

class OrderForm(FlaskForm):
    shipping_address = TextAreaField('Shipping Address', validators=[DataRequired()])
    notes = TextAreaField('Order Notes')
    payment_method = SelectField('Payment Method', choices=[
        ('stripe', 'Credit Card (Stripe)'),
        ('paypal', 'PayPal'),
        ('evc_plus', 'EVC Plus'),
        ('golis_saad', 'Golis Saad Service'),
        ('edahab', 'Edahab'),
        ('cod', 'Cash on Delivery')
    ], validators=[DataRequired()])
    submit = SubmitField('Place Order')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message') 