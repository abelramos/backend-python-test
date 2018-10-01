from flask import g


class ObjectManager(object):
    def __init__(self, model):
        self._model = model
        self._columns = []
        self._filters = []
        self._order_by = None
        self._offset = None
        self._limit = None
        
    def where(self, **filters):
        self._filters.append(filters)
        return self
    
    def limit(self, limit):
        self._limit = int(limit)
        return self
    
    def offset(self, offset):
        self._offset = int(offset)
        return self
    
    def _to_sql(self):
        sql = "SELECT {} FROM {}".format(
            ",".join(self._columns) if self._columns else "*"   ,
            self._model.table
        )
        if self._filters:
            sql += " WHERE "
            sql += " AND ".join("{} = ?".format(k)
                for f in self._filters for k in f)
        if self._limit:
            sql += " LIMIT {}".format(self._limit)
        if self._offset:
            sql += " OFFSET {}".format(self._offset)
        return sql
    
    def _to_model(self, obj):
        return self._model(**dict(obj))
    
    def _values(self):
        if not self._filters:
            return ()
        return tuple(v for f in self._filters for v in f.values())
    
    def first(self):
        cur = g.db.execute(self._to_sql(), self._values())
        obj = cur.fetchone()
        if obj:
            return self._to_model(obj)
        return None
    
    def all(self):
        cur = g.db.execute(self._to_sql(), self._values())
        objects = cur.fetchall()
        return (self._to_model(obj) for obj in objects)
    
    def count(self):
        self._columns = ["COUNT(*)"]
        cur = g.db.execute(self._to_sql(), self._values())
        return int(cur.fetchone()[0])


class MetaModel(type):
    def __init__(cls, name, bases, dct):
        if name != 'Model':
            for key in ('table', 'pk'):
                if not hasattr(cls, key):
                    msg = "Model '{}' must define property '{}'".format(
                        name, key)
                    raise Exception(msg)
        super(MetaModel, cls).__init__(name, bases, dct)
        
    def __getattr__(cls, name):
        if name == 'objects':
            objects = ObjectManager(cls)
            return objects
        raise AttributeError(name)


class Model(object):
    __metaclass__ = MetaModel
    
    def __init__(self, **data):
        super(Model, self).__setattr__('_data', data)
    
    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(name)
    
    def __setattr__(self, name, value):
        if name == self.pk:
            raise Exception('primary key is inmutable')
        if name in self._data:
            self._data[name] = value
        else:
            super(Model, self).__setattr__(name, value)
    
    def __iter__(self):
        for (k, v) in self._data.items():
            yield (k, v)
    
    def _stored(self):
        return self.pk in self._data
    
    def save(self, commit=True):
        if self._stored():
            self._update(commit)
        else:
            self._save(commit)
    
    def _save(self, commit=True):
        sql = "INSERT INTO {} ({}) VALUES ({})".format(
            self.table,
            ",".join(map(str, self._data.keys())),
            ",".join("?" * len(self._data.values()))
        )
        g.db.execute(sql, self._data.values())
        if commit:
            g.db.commit()
        
    def _update(self, commit=True):
        pk = self.pk
        sql = "UPDATE {} SET {} WHERE {}={}".format(
            self.table,
            ", ".join("{}=?".format(k) for k in self._data if k != pk),
            self.pk,
            self._data[self.pk]
        )
        values = tuple(v for (k, v) in self._data.items() if k != pk)
        g.db.execute(sql, values)
        if commit:
            g.db.commit()
    
    def delete(self, commit=True):
        sql = "DELETE FROM {} WHERE {}={}".format(
            self.table,
            self.pk,
            self._data[self.pk]
        )
        g.db.execute(sql)
        if commit:
            g.db.commit()

