from alayatodo import app
import alayatodo.helpers as helpers
from alayatodo.pagination import Pagination
from alayatodo.models import User, ToDo
from alayatodo.decorators import login_required
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    jsonify,
    flash
    )


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    if session.get('logged_in'):
        return redirect('/')
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    if session.get('logged_in'):
        return redirect('/')
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.objects.where(username=username).first()
    if user and user.check_password(password):
        session['user'] = dict(user)
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
@login_required
def todo(id):
    user_id = session['user']['id']
    todo = ToDo.objects.where(id=int(id), user_id=user_id).first()
    return render_template('todo.html', todo=todo)


@app.route('/todo/<id>/json', methods=['GET'])
@login_required
def todo_json(id):
    user_id = session['user']['id']
    todo = ToDo.objects.where(id=int(id), user_id=user_id).first()
    return jsonify(dict(todo))


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
@login_required
def todos():
    user_id = session['user']['id']
    page = int(request.args.get('page', 1))
    per_page = 3
    total = ToDo.objects.where(user_id=user_id).count()
    pagination = Pagination(page, per_page, total)
    if page > 1 and page > pagination.pages:
        return redirect('/todo/')
    offset = per_page*(page-1)
    todos = ToDo.objects.where(user_id=user_id)
    todos = todos.offset(offset).limit(per_page).all()
    return render_template('todos.html', 
        todos=todos, pagination=pagination)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
@login_required
def todos_POST():
    if not request.form.get('description', ''):
        return redirect('/todo')
    todo = ToDo(
        user_id=session['user']['id'],
        description=request.form.get('description', '')
    )
    todo.save()
    flash('TODO successfully created')
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
@login_required
def todo_delete(id):
    user_id = session['user']['id']
    todo = ToDo.objects.where(id=int(id), user_id=user_id).first()
    if todo:
        todo.delete()
        flash('TODO successfully deleted')
    else:
        flash('Nothing was deleted')
    return redirect('/todo')


@app.route('/todo/mark/<id>', methods=['POST'])
@login_required
def todo_mark(id):
    user_id = session['user']['id']
    todo = ToDo.objects.where(id=int(id), user_id=user_id).first()
    if todo:
        todo.completed = not todo.completed
        todo.save()
    return redirect(request.referrer)
