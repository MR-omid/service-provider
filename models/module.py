from peewee import TextField, BooleanField, IntegerField, CharField
from models.base_model import ComplexField
from models.base_model import BaseModel


class ModuleModel(BaseModel):
    code = IntegerField(unique=True)
    alias = CharField(unique=True)
    inout = ComplexField()
    category = CharField()
    max = IntegerField(default=0)  # maximum concurrent execution
    is_action = BooleanField(default=False)
    active = BooleanField(default=True)

    class Meta:
        db_table = 'api_module'

