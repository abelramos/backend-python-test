import os


class Config(object):
    DATABASE = os.environ.get('DATABASE') or '/tmp/alayatodo.db'
    DEBUG = os.environ['DEBUG'] if 'DEBUG' in os.environ else True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'development key'
    # what are these for?
    USERNAME = 'admin'
    PASSWORD = 'default'
