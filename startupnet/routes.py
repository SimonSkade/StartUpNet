from startupnet import app, db, bcrypt
from flask import render_template, flash, redirect, url_for, request
from startupnet.models import User, Post, Investor, Founder
from startupnet.forms import RegistrationInvestorForm, RegistrationFounderForm, RegisterChooseForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required

posts = [
{
	"author": "Simon",
	"title": "Post1",
	"content": "first content",
	"date_posted": "aug 20, 2019"
},
{
	"author": "Jan",
	"title": "Post1",
	"content": "second content",
	"date_posted": "aug 20, 2019"
}]

@app.route("/")
@app.route("/home")
def home():
	return render_template("home.html", posts=posts)

@app.route("/about")
def about():
	return render_template("about.html", title="About")


@app.route("/register", methods=["GET", "POST"])
def register():
	form = RegisterChooseForm()
	#if form.validate_on_submit():
	#	return redirect(url_for("register_investor"))
	#	if form.investor:
	#		#flash(f"Register as Investor", "success")
	#		return redirect(url_for(register_investor))
	#	elif form.founder:
	#		return redirect(url_for(register_founder))
	#	return redirect(url_for("home"))
	return render_template("register.html", title="Register", form=form)

@app.route("/register_investor", methods=["GET", "POST"])
def register_investor():
	if current_user.is_authenticated:
		return redirect(url_for("home"))	
	form = RegistrationInvestorForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
		investor = Investor(username=form.username.data, email=form.email.data, password=hashed_password, offers=form.offers.data, interests=form.interests.data)
		db.session.add(investor)
		db.session.commit()
		flash(f"Investor Account created for {form.username.date}!", "success")
		return redirect(url_for("login"))
	return render_template("register_investor.html", title="Register", form=form)

@app.route("/register_founder", methods=["GET", "POST"])
def register_founder():
	if current_user.is_authenticated:
		return redirect(url_for("home"))
	form = RegistrationFounderForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
		founder = Founder(username=form.username.data, email=form.email.data, password=hashed_password, about=form.about.data, skills=form.skills.data)
		db.session.add(founder)
		db.session.commit()
		flash(f"Founder Account created for {form.username.data}!", "success")
		return redirect(url_for("login"))
	return render_template("register_founder.html", title="Register", form=form)



@app.route("/login", methods=["GET", "POST"])
def login():
	if current_user.is_authenticated:
		return redirect(url_for("home"))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get("next")
			flash("You have been logged in!", "success")
			return redirect(url_for("home"))
		else:
			flash("Login failed.")
	return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for("home"))

@app.route("/account")
@login_required
def account():
	return render_template("account.html", title="Account")


