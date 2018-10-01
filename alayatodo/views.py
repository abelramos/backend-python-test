from alayatodo import app
import alayatodo.helpers as helpers
from alayatodo.pagination import Pagination
from alayatodo.models import User, ToDo
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
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.objects.where(
        username=username, password=password).first()
    if user:
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
def todo(id):
    todo = ToDo.objects.where(id=int(id)).first()
    return render_template('todo.html', todo=todo)


@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    todo = ToDo.objects.where(id=int(id)).first()
    return jsonify(dict(todo))


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    page = int(request.args.get('page', 1))
    per_page = 3
    total = ToDo.objects.count()
    pagination = Pagination(page, per_page, total)
    if page > pagination.pages:
        return redirect('/todo/')
    offset = per_page*(page-1)
    todos = ToDo.objects.offset(offset).limit(per_page).all()
    return render_template('todos.html', 
        todos=todos, pagination=pagination)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')
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
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    ToDo.objects.where(id=int(id)).first().delete()
    flash('TODO successfully deleted')
    return redirect('/todo')


@app.route('/todo/mark/<id>', methods=['POST'])
def todo_mark(id):
    if not session.get('logged_in'):
        return redirect('/login')
    todo = ToDo.objects.where(id=int(id)).first()
    if todo:
        todo.completed = not todo.completed
        todo.save()
    return redirect(request.referrer)
