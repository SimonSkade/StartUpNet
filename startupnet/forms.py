from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from startupnet.models import User, Founder, Investor

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField("Email", validators=[DataRequired(), Email()])
	password = PasswordField("Password", validators=[DataRequired()])
	confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField("Sign up")

class RegistrationInvestorForm(RegistrationForm):
	offers = StringField("My Offers")
	interests = StringField("My Interests")

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError("The username is taken. Please choose another one.")

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError("The email is taken. Please choose another one.")


class RegistrationFounderForm(RegistrationForm):
	about = StringField("About Me")
	skills = StringField("My Skills")

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError("The username is taken. Please choose another one.")

	def validate_email(self, email):
		user = Investor.query.filter_by(email=email.data).first()
		if not user:
			user = Founder.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError("The email is taken. Please choose another one.")


class RegisterChooseForm(FlaskForm):
	investor = "Investor"
	founder = "Founder"

class LoginForm(FlaskForm):
	email = StringField("Email", validators=[DataRequired(), Email()])
	password = PasswordField("Password", validators=[DataRequired()])
	remember = BooleanField("Remember Me")
	submit = SubmitField("Log in")



