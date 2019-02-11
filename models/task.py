from datetime import datetime

from peewee import TextField, BooleanField, IntegerField, CharField, DateTimeField

from core import constants
from models.base_model import ComplexField
from models.base_model import BaseModel


class TaskModel(BaseModel):
    route = TextField()
    process_id = TextField()
    status = TextField()
    token = TextField()
    module_version = TextField()
    data = ComplexField(default={})
    progress = ComplexField(default={'state': 'preparing...', 'percent': 0})
    call_back = TextField()
    max_retry = IntegerField(default=1)
    create_date = DateTimeField(default=datetime.now)
    details = TextField(default='ok')
    delivery = TextField(default=constants.STATUS_NEW)
    queue_name = TextField()
    response_data = ComplexField(default={})

    class Meta:
        db_table = 'api_task'

