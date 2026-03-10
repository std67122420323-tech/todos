from flask import Flask
from todo.extensions import db, bcrypt, login_manager
from todo.core.routes import core_bp
from todo.todo.routes import todo_bp
from todo.user.routes import user_bp

import os
from todo.models import User, Todo, Task

def create_app():
  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
  app.secret_key = os.environ.get('SECRET_KEY')

  db.init_app(app)
  bcrypt.init_app(app)
  login_manager.init_app(app)
  login_manager.login_view = 'user.login'
  login_manager.login_message = 'Please login before access this page!'
  login_manager.login_message_category = 'warning'

  app.register_blueprint(core_bp, url_prefix='/')
  app.register_blueprint(user_bp, url_prefix='/user' )
  app.register_blueprint(todo_bp, url_prefix='/todo')

  return app

