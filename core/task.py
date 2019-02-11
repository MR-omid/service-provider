import importlib
import sys

from PyQt5.QtCore import QRunnable

from components.LogHandler import LogHandler
from components.utils import to_json, ApiLogging
from core import constants
from models.task import TaskModel
from vendor.custom_exception import ResultNotSetError


class Task(QRunnable):
    """ load and run module depend on route and version"""

    def __init__(self, task_model):
        super().__init__()
        self.task_model = task_model   # type: TaskModel
        self.instance_module = self.__load_module()

    def __load_module(self):
        """
        load module if not loaded

        :return: module instance
        :rtype: BaseModule
        """
        module_path = "modules." + self.task_model.route + '.' + self.task_model.module_version + ".module"
        try:
            ApiLogging.info("import")
            app_module = importlib.import_module(module_path)
            return app_module.Module(self.task_model)
        except Exception as e:
            # TODO: save exception same as run method exception part
            ApiLogging.error("import exception " + str(e))
            return None

    def run(self):
        try:
            """ run module and save result in database """
            ApiLogging.info("module " + str(self.task_model.route))
            self.instance_module.prepare()
            self.instance_module.run()
            self.task_model.status = constants.STATUS_SUCCESS
            if not self.instance_module.result:
                error = {'code': ResultNotSetError.get_code(), 'message': 'module not set any result before return!'}
                self.task_model.response_data = {
                    'data': to_json(self.instance_module.result),
                    'error': to_json(error),
                    'status': constants.STATUS_ERROR,
                    'token': self.task_model.token,
                    'process_id': self.task_model.process_id
                }
        except Exception as e:
            LogHandler.save(sys.exc_info(), process_id=self.task_model.process_id)
            ApiLogging.error('result exception ' + str(e))
            self.task_model.status = constants.STATUS_FAILED
            old_exception = e.__str__()
            try:
                error = {'code': e.get_code(), 'message': e.args[0]}
            except Exception as e:
                error = {'code': 0, 'message': old_exception}

            self.task_model.response_data = {
                'data': to_json(self.instance_module.result),
                'error': to_json(error),
                'status': constants.STATUS_ERROR,
                'token': self.task_model.token,
                'process_id': self.task_model.process_id
            }

        finally:
            self.task_model.save()
            ApiLogging.info('emit finish signal')
            self.instance_module.task_finished.emit(self.task_model.process_id)
