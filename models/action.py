from datetime import datetime

from peewee import TextField, BooleanField, IntegerField, CharField, DateTimeField

from core import constants
from models.base_model import ComplexField
from models.base_model import BaseModel


class ActionModel(BaseModel):
    process_id = TextField()
    action = TextField()
    timeout = IntegerField(default=30)
    status = TextField(default=constants.STATUS_PENDING)

    class Meta:
        db_table = 'api_action'

