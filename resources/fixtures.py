from alayatodo import app, connect_db
from alayatodo.models import User
from werkzeug.security import generate_password_hash
from flask import g


def generate_sample_users():
    with app.app_context():
        g.db = connect_db()
        for i in (1, 2, 3):
            s = 'user{}'.format(i)
            User(username=s, password=generate_password_hash(s)).save()


def main():
    generate_sample_users()
