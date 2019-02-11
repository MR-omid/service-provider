import os
from PyQt5.QtCore import QObject

from models.base_model import ComplexField


class Migrate(QObject):
    def __init__(self):
        super().__init__()
        self.migration_list = list()
        self.mode_list = list()
        self.diff_list = list()
        from vendor.peewee_moves import PEEWEE_TO_FIELD
        PEEWEE_TO_FIELD.update({ComplexField().__class__: 'blob'})

    def get_models(self, model_path):
        """
        this function get list of models from model directory
        """
        for file in os.listdir(model_path):
            self.mode_list.append(file.split(".")[0])

        for m in self.mode_list.copy():
            if m[:2] == '__':
                self.mode_list.remove(m)
        return self.mode_list

    # *********************************
    def get_module_models(self, module):
        """
        this function get list of module modles from model directory
        """
        m_mode_list = []
        path = 'modules/%s/models' % module
        if os.path.exists(path):
            for file in os.listdir(path):
                m_mode_list.append(file.split(".")[0])
            for m in m_mode_list.copy():
                if m[:2] == '__':
                    m_mode_list.remove(m)
            return m_mode_list
        return None

    # **********************************************
    def get_migrations(self, migration_path):
        """
        this function get list of module migration from migration directory
        """
        for file in os.listdir(migration_path):
            self.migration_list.append(file.split(".")[0])
        return self.migration_list

    def get_module_migrations(self, module):
        """
        this function get list of migration from migration directory
        """
        migrate_list = []
        path = 'modules/%s/migrations' % module
        for file in os.listdir(path):
            migrate_list.append(file.split(".")[0])
        return migrate_list

    def get_diff(self, model_path, migration_path):
        """
        this function compare list of models with list of migration
        """
        names = list()
        migration_list = self.get_migrations(migration_path)
        mode_list = self.get_models(model_path)
        for mig in migration_list:
            names.extend(mig.split("_"))
        for element in mode_list:
            if element.lower() not in names:
                self.diff_list.append(element)
        return self.diff_list

    # ***************************
    def get_module_diff(self, module):
        """
        this function compare list of models with list of migration in one module
        """
        names = list()
        m_diff_list = list()
        module_list = self.get_module_models(module)
        if module_list:
            migration_list = self.get_module_migrations(module)
            for mig in migration_list:
                names.extend(mig.split("_"))
            for element in module_list:
                if element.lower() not in names:
                    m_diff_list.append(element)
            return m_diff_list
        return None

    # **************************************

    def create_migration(self, manager, model_path, migration_path, ignore=[]):
        """
        this function create migartion of models which does not exist
        """

        dif_list = self.get_diff(model_path, migration_path)
        if dif_list is not None:
            for modl in dif_list:
                if modl in ignore:
                    continue
                else:
                    manager.create('models.{}'.format(modl))

    # ********************

    def create_module_migration(self, manager, module):
        """
        this function create migartion of modules models  which does not exist
        """
        dif_list = self.get_module_diff(module)

        if dif_list is not None:
            for modl in dif_list:
                manager.create('modules.{0}.models.{1}'.format(module, modl))

    def apply_migration(self, manager, ):
        """
        this function upgrade new migrations
        """
        manager.upgrade()
