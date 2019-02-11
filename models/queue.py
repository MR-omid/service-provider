from models.base_model import BaseModel, ComplexField
from peewee import TextField, IntegerField


class QueueModel(BaseModel):
    tag = TextField(unique=True)
    name = TextField()
    data = ComplexField()
    priority = IntegerField(default=1)

    class Meta:
        db_table = 'api_queue'
