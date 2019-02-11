import os
from models.module import ModuleModel
from peewee import IntegrityError


class Update(object):

    def __init__(self):
        pass

    def upgrade(self):
        module = {
            'code': 10,
            'alias': 'resume',
            'inout': {0: [0]},
            'max': 0,
            'category': 'action',
            'is_action': True,
            'active': True
        }
        try:
            model = ModuleModel()
            model.code = module.get('code')
            model.alias = module.get('alias')
            model.inout = module.get('inout')
            model.category = module.get('category')
            model.max = module.get('max', 0)
            model.is_action = module.get('is_action', False)
            model.active = module.get('active', True)
            try:
                model.save()
            except IntegrityError:
                pass
        except Exception as e:
            raise Exception('data base startup failed ' + str(e))

    def downgrade(self):
        pass
