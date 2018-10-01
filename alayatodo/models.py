from orm import Model
from werkzeug.security import check_password_hash


class User(Model):
    table = 'users'
    pk = 'id'
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    
class ToDo(Model):
    table = 'todos'
    pk = 'id'
