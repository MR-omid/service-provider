import dill
from peewee import Field, Model
from core.database import Database


class BaseModel(Model):
    def __init__(self):
        super().__init__()

    class Meta:
        database = Database.db


class ComplexField(Field):
    """ custom field for binary python object(s) """
    db_field = 'blob'

    def __init__(self, default=None):
        super().__init__(default=default)

    def db_value(self, value):
        return dill.dumps(value)

    def python_value(self, value):
        return dill.loads(value)
