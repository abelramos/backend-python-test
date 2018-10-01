from orm import Model


class User(Model):
    table = 'users'
    pk = 'id'
    
    
class ToDo(Model):
    table = 'todos'
    pk = 'id'
