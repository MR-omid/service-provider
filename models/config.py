from models.base_model import BaseModel, ComplexField
from peewee import CharField


class ConfigModel(BaseModel):
    attribute = CharField(unique=True)
    value = ComplexField()

    class Meta:
        db_table = 'api_config'
