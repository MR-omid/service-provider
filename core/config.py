from PyQt5.QtCore import QObject
from peewee import IntegrityError, ProgrammingError
from models.config import ConfigModel
from vendor.custom_exception import DatabaseError


class Setting(QObject):
    def __init__(self):
        super().__init__()

    @staticmethod
    def put(key, value, force=False):
        try:
            model = ConfigModel()
            model.attribute = key
            model.value = value
            model.save()
        except IntegrityError:  # Occurs if primary_key already exists
            if force:
                query=ConfigModel.update(value=value).where(ConfigModel.attribute == key)
                query.execute()
            else:
                raise ValueError('attribute already exists')
        except ProgrammingError:
            raise DatabaseError('can not access api_config table')
        except Exception:
            raise DatabaseError('can not access databases')

    @staticmethod
    def get(key, default=None):
        try:
            result = ConfigModel.get(ConfigModel.attribute == key)
            return result.value
        except:
            return default
        # FIXME: implement cache mechanism

    @staticmethod
    def remove(key):
        try:
            query = ConfigModel.delete().where(ConfigModel.attribute == key)
            query.execute()
            return True
        except:
            return False

    @staticmethod
    def get_keys():
        try:
            query = ConfigModel.select(ConfigModel.attribute)
            return [row._data for row in query]
        except Exception:
            return None
