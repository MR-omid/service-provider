import os
from models.module import ModuleModel
from peewee import IntegrityError


class Update(object):

    def __init__(self):
        pass

    def upgrade(self):
        new_modules = [{
            'code': 11,
            'alias': 'screenshot',
            'inout': {1: [9]},
            'category': 'action',
            'max': 0,
            'is_action': True,
            'active': True
        },
        {
            'code': 105,
            'alias': 'google_search',
            'inout': {1: [1], 2: [1], 3: [1], 4: [1], 5: [1], 8: [1], 11: [1], 12: [1], 0: [1]},
            'category': 'MQueue',
            'max': 0,
            'active': False
        },
        {
            'code': 101,
            'alias': 'bing_search',
            'inout': {1: [1], 2: [1], 3: [1], 4: [1], 5: [1], 8: [1], 11: [1], 12: [1], 0: [1]},
            'category': 'MQueue',
            'max': 0,
            'active': False
        },
        {
            'code': 112,
            'alias': 'facebook',
            'inout': {1: [0], 2: [0], 3: [0], 4: [0], 5: [0], 8: [0], 11: [0], 12: [0]},
            'category': 'MQueue',
            'max': 0,
            'active': True
        },
        {
            'code': 113,
            'alias': 'hash',
            'inout': {6: [7]},
            'category': 'LQueue',
            'max': 0,
            'active': True
        }
        ]

        drop_modules = [113, 101, 105, 112]
        for module in drop_modules:
            try:
                q = ModuleModel.delete().where(ModuleModel.code == module)
                q.execute()
            except Exception:
                pass

        for module in new_modules:
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
