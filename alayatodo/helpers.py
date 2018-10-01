# Borrowed from http://flask.pocoo.org/snippets/44/

from alayatodo import app
from flask import request, url_for


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page
