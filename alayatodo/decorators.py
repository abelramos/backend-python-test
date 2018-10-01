from functools import wraps
from flask import session, redirect


def login_required(view):
    @wraps(view)
    def _wrapped(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return view(*args, **kwargs)
    return _wrapped
