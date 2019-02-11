import os, sys

ps = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ps)
from components.utils import ApiLogging
from vendor.peewee_moves import DatabaseManager
from core.database import Database
from components.migrator import Migrate
import os
from models.module import ModuleModel
from peewee import IntegrityError


class Update(object):
    # default value data for module
    default_modules = [
        {
            'code': 101,
            'alias': 'bing_search',
            'inout': {1: {1: {'output': [1], 'sub_type': 0}, 2: {'output': [1], 'sub_type': 0},
                          3: {'output': [1], 'sub_type': 0}, 4: {'output': [1], 'sub_type': 0},
                          5: {'output': [1], 'sub_type': 0}, 8: {'output': [1], 'sub_type': 0},
                          11: {'output': [1], 'sub_type': 0}, 12: {'output': [1], 'sub_type': 0},
                          0: {'output': [1], 'sub_type': 0}}},
            'category': 'MQueue',
            'max': 0,
            'active': False
        },
        {
            'code': 102,
            'alias': 'bing_api',
            'inout': {1: {1: {'output': [1], 'sub_type': 0}, 2: {'output': [1], 'sub_type': 0},
                          3: {'output': [1], 'sub_type': 0}, 4: {'output': [1], 'sub_type': 0},
                          5: {'output': [1], 'sub_type': 0}, 8: {'output': [1], 'sub_type': 0},
                          11: {'output': [1], 'sub_type': 0}, 12: {'output': [1], 'sub_type': 0}}},
            'category': 'LQueue',
            'max': 0,
            'active': True
        },
        {
            'code': 105,
            'alias': 'google_search',
            'inout': {1: {1: {'output': [1], 'sub_type': 0}, 2: {'output': [1], 'sub_type': 0},
                          3: {'output': [1], 'sub_type': 0}, 4: {'output': [1], 'sub_type': 0},
                          5: {'output': [1], 'sub_type': 0}, 8: {'output': [1], 'sub_type': 0},
                          11: {'output': [1], 'sub_type': 0}, 12: {'output': [1], 'sub_type': 0},
                          0: {'output': [1], 'sub_type': 0}}},
            'category': 'MQueue',
            'max': 0,
            'active': False
        },
        {
            'code': 106,
            'alias': 'google_api',
            'inout': {1: {1: {'output': [1], 'sub_type': 0}, 2: {'output': [1], 'sub_type': 0},
                          3: {'output': [1], 'sub_type': 0}, 4: {'output': [1], 'sub_type': 0},
                          5: {'output': [1], 'sub_type': 0}, 8: {'output': [1], 'sub_type': 0},
                          11: {'output': [1], 'sub_type': 0}, 12: {'output': [1], 'sub_type': 0}}},
            'category': 'LQueue',
            'max': 0
        },
        {
            'code': 108,
            'alias': 'similar_domain',
            'inout': {1: {12: {'output': [12], 'sub_type': 0}}},
            'category': 'LQueue',
            'max': 0
        },
        {
            'code': 109,
            'alias': 'whois',
            'inout': {0: {0: {'output': [15], 'sub_type': 1}},
                      1: {2: {'output': [12], 'sub_type': 0}}, 2: {11: {'output': [12], 'sub_type': 0}},
                      3: {12: {'output': [0, 2, 4, 8, 11], 'sub_type': 0}},
                      4: {12: {'output': [2, 4, 8, 11, 12], 'sub_type': 0}},
                      5: {3: {'output': [12], 'sub_type': 0}}},
            'category': 'LQueue',
            'max': 3
        },
        {
            'code': 110,
            'alias': 'parser',
            'inout': {1: {0: {'output': [1, 2, 3, 4, 5], 'sub_type': 0}},
                      2: {9: {'output': [1, 2, 3, 4, 5], 'sub_type': 0}}},
            'category': 'LQueue',
            'max': 0
        },
        {
            'code': 111,
            'alias': 'crawler',
            'inout': {1: {1: {'output': [9], 'sub_type': 0}}},
            'category': 'HQueue',
            'max': 0
        },
        {
            'code': 112,
            'alias': 'facebook',
            'inout': {1: {5: {'output': [5], 'sub_type': 1}},
                      2: {5: {'output': [5], 'sub_type': 1}},
                      3: {5: {'output': [5], 'sub_type': 1}},
                      4: {5: {'output': [5], 'sub_type': 1}},
                      5: {2: {'output': [5], 'sub_type': 1}, 4: {'output': [5], 'sub_type': 1},
                          5: {'output': [5], 'sub_type': 1}, 8: {'output': [5], 'sub_type': 1},
                          11: {'output': [5], 'sub_type': 1}, 12: {'output': [5], 'sub_type': 1}}},
            'category': 'MQueue',
            'max': 0,
            'active': True
        },
        {
            'code': 113,
            'alias': 'hash',
            'inout': {1: {6: {'output': [7], 'sub_type': 0}},
                      2: {6: {'output': [7], 'sub_type': 0}}},
            'category': 'LQueue',
            'max': 0,
            'active': True
        },
        {
            'code': 114,
            'alias': 'twitter',
            'inout': {1: {5: {'output': [5], 'sub_type': 2}, 11: {'output': [5], 'sub_type': 2}},
                      2: {5: {'output': [5], 'sub_type': 2}},
                      3: {5: {'output': [5], 'sub_type': 2}},
                      4: {5: {'output': [5], 'sub_type': 2}}},
            'category': 'LQueue',
            'max': 0,
            'active': True
        },
        {
            'code': 115,
            'alias': 'ip2location',
            'inout': {1: {3: {'output': [14], 'sub_type': 0}},
                      2: {3: {'output': [0], 'sub_type': 0}},
                      3: {0: {'output': [15], 'sub_type': 2}},
                       4: {0: {'output': [15], 'sub_type': 3}}},
            'category': 'LQueue',
            'max': 0,
            'active': True
        },
        {
            'code': 116,
            'alias': 'instagram',
            'inout': {1: {5: {'output': [2, 4, 5, 11], 'sub_type': 0}},
                      2: {5: {'output': [5], 'sub_type': 3}},
                      3: {5: {'output': [5], 'sub_type': 3}},
                      4: {4: {'output': [5], 'sub_type': 3}},
                      5: {11: {'output': [5], 'sub_type': 3}}},
            'category': 'LQueue',
            'max': 0,
            'active': True
        },
        {
            'code': 117,
            'alias': 'linkedin',
            'inout': {1: {5: {'output': [5], 'sub_type': 3}},
                      2: {5: {'output': [5], 'sub_type': 3},
                          11: {'output': [5], 'sub_type': 3},
                          8: {'output': [5], 'sub_type': 3}}},
            'category': 'MQueue',
            'max': 0,
            'active': True
        },
        {
            'code': 118,
            'alias': 'truecaller',
            'inout': {1: {4: {'output': [11], 'sub_type': 3}}},
            'category': 'MQueue',
            'max': 0,
            'active': True
        },
        {
            'code': 0,
            'alias': 'module_list',
            'inout': {1: {0: {'output': [0], 'sub_type': 0}}},
            'category': 'action',
            'max': 0,
            'is_action': True
        },
        {
            'code': 1,
            'alias': 'log',
            'inout': {1: {0: {'output': [0], 'sub_type': 0}}},
            'category': 'action',
            'max': 0,
            'is_action': True
        },
        {
            'code': 2,
            'alias': 'download',
            'inout': {1: {0: {'output': [0], 'sub_type': 0}}},
            'category': 'action',
            'max': 0,
            'is_action': True
        },
        {
            'code': 3,
            'alias': 'get_configs',
            'inout': {1: {0: {'output': [0], 'sub_type': 0}}},
            'category': 'action',
            'max': 0,
            'is_action': True
        },
        {
            'code': 4,
            'alias': 'set_configs',
            'inout': {1: {0: {'output': [0], 'sub_type': 0}}},
            'category': 'action',
            'max': 0,
            'is_action': True
        },
        {
            'code': 5,
            'alias': 'system_information',
            'inout': {1: {0: {'output': [0], 'sub_type': 0}}},
            'category': 'action',
            'max': 0,
            'is_action': True
        },
        {
            'code': 6,
            'alias': 'cancel',
            'inout': {1: {0: {'output': [0], 'sub_type': 0}}},
            'category': 'action',
            'max': 0,
            'is_action': True
        },
        {
            'code': 7,
            'alias': 'install_module',
            'inout': {1: {0: {'output': [0], 'sub_type': 0}}},
            'max': 0,
            'category': 'action',
            'is_action': True,
            'active': False
        },
        {
            'code': 8,
            'alias': 'progress',
            'inout': {1: {0: {'output': [0], 'sub_type': 0}}},
            'max': 0,
            'category': 'action',
            'is_action': True,
            'active': True
        },
        {
            'code': 9,
            'alias': 'pause',
            'inout': {1: {0: {'output': [0], 'sub_type': 0}}},
            'max': 0,
            'category': 'action',
            'is_action': True,
            'active': True
        },
        {
            'code': 10,
            'alias': 'resume',
            'inout': {1: {0: {'output': [0], 'sub_type': 0}}},
            'max': 0,
            'category': 'action',
            'is_action': True,
            'active': True
        },
        {
            'code': 11,
            'alias': 'screenshot',
            'inout': {1: {1: {'output': [9], 'sub_type': 0}}},
            'category': 'action',
            'max': 0,
            'is_action': True,
            'active': True
        },
        {
            'code': 12,
            'alias': 'download_by_process_id',
            'inout': {1: {0: {'output': [0], 'sub_type': 0}}},
            'category': 'action',
            'max': 0,
            'is_action': True
        }
    ]

    def __init__(self):
        # define shared operations between upgrade and downgrade
        ApiLogging.info('update to version 1.0')
        # define migration and models dir
        path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        migration_path = path + '/migrations/v_1_0'
        model_path = path + '/models'
        self.manager = DatabaseManager(Database.db, directory=path + '/migrations/v_1_0')
        self.mg = Migrate()
        self.mg.create_migration(self.manager, model_path, migration_path, ignore=['base_model'])

    def upgrade(self):
        # upgrading op
        self.manager.upgrade()
        configs = Update.default_modules
        for module in configs:
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
                    continue
            except Exception as e:
                raise Exception('data base startup failed ' + str(e))

    def downgrade(self):
        # downgrading op
        self.manager.downgrade()
