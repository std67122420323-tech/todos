from flask import Blueprint, render_template, redirect, url_for, request, flash
from todo.models import Todo, Task, User
from flask_login import current_user, login_required
from todo.forms import TaskForm
from todo.extensions import db, bcrypt
from datetime import date

todo_bp = Blueprint('todo', __name__, template_folder='templates')

@todo_bp.route('/todo_today', methods=['GET', 'POST'])
@login_required
def todo_today():
  form = TaskForm()
  todo = db.session.scalar(db.select(Todo).where(Todo.created_at==date.today(), Todo.user==current_user))
  if todo:
    tasks = db.session.scalars(db.select(Task).where(Task.todo==todo)).all()
    if form.validate_on_submit():
      task = form.task.data
      tk = Task(task=task, todo=todo)
      db.session.add(tk)
      db.session.commit()
      return redirect(url_for('todo.todo_today'))
  else:
    tasks = None
  
  return render_template('todo/todos.html', title='Todo Today Page', form=form, todo=todo, tasks=tasks)

@todo_bp.route('/new_todo', methods=['GET', 'POST'])
@login_required
def new_todo():
  todo = Todo(user=current_user)
  db.session.add(todo)
  db.session.commit()

  return redirect(url_for('todo.todo_today'))

@todo_bp.route('/<int:id>/task_completed')
@login_required
def task_completed(id):
  task = db.session.get(Task, id)
  task.completed = True
  db.session.commit()

  return redirect(url_for('todo.todo_today'))

@todo_bp.route('/all_todos')
@login_required
def all_todos():
  tasks = db.session.scalars(db.select(Task).where(Task.todo_id==Todo.id, Todo.user==current_user).order_by(Todo.created_at.desc())).all()
  return render_template('todo/all_todos.html', title='Show All Todos', tasks=tasks)

@todo_bp.route('/completed_todos')
@login_required
def completed_todos():
  tasks = db.session.scalars(db.select(Task).where(Task.todo_id==Todo.id, Todo.user==current_user, Task.completed==True).order_by(Todo.created_at.desc())).all()
  return render_template('todo/all_todos.html',
                         title='Show Completed Tasks',
                         tasks=tasks)

@todo_bp.route('/uncompleted_todos')
@login_required
def uncompleted_todos():
  tasks = db.session.scalars(db.select(Task).where(Task.todo_id==Todo.id, Todo.user==current_user, Task.completed==False).order_by(Todo.created_at.desc())).all()
  return render_template('todo/all_todos.html',
                         title='Show Uncompleted Tasks',
                         tasks=tasks)