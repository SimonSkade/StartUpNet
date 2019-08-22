from startupnet import app, db, bcrypt
from flask import render_template, flash, redirect, url_for, request
from startupnet.models import User, Post, Investor, Founder
from startupnet.forms import RegistrationInvestorForm, RegistrationFounderForm, RegisterChooseForm, LoginForm, UpdateAccountForm, PostForm
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image


@app.route("/")
@app.route("/home")
def home():
	page = request.args.get("page", 1, type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
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
		user = User.query.filter_by(email=form.email.data).first()
		login_user(user)
		flash(f"Investor Account created for {form.username.data}!", "success")
		flash("You were logged in automatically", "success")
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
		user = User.query.filter_by(email=form.email.data).first()
		login_user(user)
		flash(f"Founder Account created for {form.username.data}!", "success")
		flash("You were logged in automatically", "success")
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

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, "static/profile_pics", picture_fn)
	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash("your account has been updated", "success")
		return redirect(url_for("account"))
	elif request.method == "GET":
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for("static", filename="profile_pics/" + current_user.image_file)
	return render_template("account.html", title="Account", image_file=image_file, form=form)


@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title=form.title.data, content=form.content.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash("Your post has been posted", "success")
		return redirect(url_for("home"))
	return render_template("create_post.html", title="New Post", form=form, legend="New Post")

@app.route("/post/<int:post_id>")
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template("post.html", title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash("Your post has been updated", "success")
		return redirect(url_for("post", post_id=post_id))
	elif request.method == "GET":
		form.title.data = post.title
		form.content.data = post.content
	return render_template("create_post.html", title="Update Post", form=form, legend="Update Post")

@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash("Your post has been deleted!", "success")
	return redirect(url_for("home"))



@app.route("/user/<string:username>")
def user_posts(username):
	page = request.args.get("page", 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
	return render_template("user_posts.html", user=user, posts=posts)


