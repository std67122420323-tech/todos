from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from todo.models import User
from todo.extensions import db, bcrypt
from todo.forms import UpdateAccountForm, LoginForm, RegisterForm
import os, secrets
from PIL import Image

user_bp = Blueprint('user', __name__, template_folder='templates', static_folder='static')

@user_bp.route('/')
def index():
  return render_template('user/index.html', title='User Page')

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
  form = RegisterForm()
  if form.validate_on_submit():
    username = form.username.data
    email = form.email.data
    password = form.password.data
    hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, email=email, password=hash_password)

    db.session.add(user)
    db.session.commit()
    flash('Register successful!', 'success')
    return redirect(url_for('user.login'))
  
  return render_template('user/register.html', title='Register Page', form=form)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    remember = form.remember.data

    user = db.session.scalar(db.select(User).where(User.username==username))

    if user and bcrypt.check_password_hash(user.password, password):
      login_user(user=user, remember=remember)
      return redirect(url_for('user.index'))
  return render_template('user/login.html', title='Login Page', form=form)

@user_bp.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('user.login'))

def save_avatar(form_avatar):
  random_hex = secrets.token_hex(8)
  _, ext = os.path.splitext(form_avatar.filename)
  avatar_fn = random_hex + ext

  avatar_path = os.path.join(user_bp.root_path, 'static/img', avatar_fn)
  # print(user_bp.root_path)
  img_size = (256, 256)
  img = Image.open(form_avatar)
  img.thumbnail(img_size)
  img.save(avatar_path)

  return avatar_fn

@user_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
  form = UpdateAccountForm()
  if request.method == 'GET':
    form.username.data = current_user.username
    form.email.data = current_user.email
    form.fullname.data = current_user.fullname
  elif form.validate_on_submit():
    if form.avatar.data:
      avatar = save_avatar(form.avatar.data)
      current_user.avatar = avatar
    current_user.fullname = form.fullname.data
    db.session.commit()
    flash('Update account successful!', 'success')

    return redirect(url_for('user.account'))
  avatar_pic = current_user.avatar

  return render_template('user/account.html', title='Account Info Page', form=form, avatar_pic=avatar_pic)
