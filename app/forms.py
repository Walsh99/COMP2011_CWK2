from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional

## form for registering an account
class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')
    
## form for logging in to an account
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

## form for editing an account
class AccountUpdateForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    old_password = PasswordField('Old Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[
        Optional(), Length(min=8, max=128), EqualTo('confirm_new_password', message='Passwords must match')])
    confirm_new_password = PasswordField('Confirm New Password', validators=[Optional()])
    submit = SubmitField('Update Account')

class CheckoutForm(FlaskForm):
    address = TextAreaField('Address', validators=[DataRequired()])
    submit = SubmitField('Confirm Checkout')
