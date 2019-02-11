from playhouse.signals import Model
from peewee import PostgresqlDatabase
from core import constants


class DatabaseProperties(type):

    @property
    def db(cls):
        if cls._db:
            return cls._db  # type: PostgresqlDatabase
        else:
            cls._db = PostgresqlDatabase(
                constants.database.get('name'),
                user=constants.database.get('username'),
                password=constants.database.get('password'),
                host=constants.database.get('host'),
                port=constants.database.get('port'),
                autorollback=True
            )
            # cls._db = SqliteDatabase(constants.BASE_APP_PATH+'/debug.db')
            return cls._db  # type: PostgresqlDatabase

    # @property
    # def model(cls):
    #     if cls._model:
    #         return cls._model  # type: Model
    #     else:
    #         class BaseModel(Model):
    #             class Meta:
    #                 database = cls.db
    #         cls._model = BaseModel  # type: Model
    #         return cls._model


class Database(object, metaclass=DatabaseProperties):
    _db = None
