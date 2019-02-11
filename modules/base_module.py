from time import sleep
import os, sys
ps = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ps)
from PyQt5.QtCore import QObject, pyqtSignal

from components.Qhttp import Qhttp
from components.utils import to_json, ApiLogging
from core import constants
from models.task import TaskModel
from vendor.custom_exception import InvalidInputError, CancelExecutionError
import json


class BaseModule(QObject):
    task_finished = pyqtSignal(str, name='task_finished')

    def __init__(self, task_model):
        """
        define and initialize object variables

        :param bytearray data: required module data
        """
        super().__init__()
        self.params = None  # type: dict
        self.__task_model = task_model  # type: TaskModel
        self.pause_request = None
        self.cancel_request = None
        self.resume_request = None
        self.__result = None

    def prepare(self):
        """
        convert json to dict and assign value to self.params

        :raise InternalModuleError: when data is not a valid json
        """
        try:
            # ApiLogging.info(str(self.__task_model.data) + str(type(self.__task_model.data)))
            self.params = json.loads(self.__task_model.data.decode())
        except Exception:  # JSONDecodeError
            raise InvalidInputError('Invalid input format')

    @property
    def progress(self):
        return None

    @progress.setter
    def progress(self, value):
        try:
            value.update({"token": self.__task_model.token, 'process_id': self.__task_model.process_id})
            self.__task_model.progress = value
            self.__task_model.save()
            try:
                http_result = Qhttp.post(self.__task_model.call_back, value)
            except:
                pass
        except Exception as e:
            raise ValueError(e)

    @property
    def result(self):
        return self.__result

    @result.setter
    def result(self, value):
        if not value:
            value = 0
        self.__result = value
        self.__task_model.response_data = {
                                    'data': to_json(value),
                                    'error': False,
                                    'status': constants.STATUS_SUCCESS,
                                    'token':  self.__task_model.token,
                                    'process_id': self.__task_model.process_id
                                }
        self.__task_model.save()

    def pause(self, timeout):
        try:
            http_result = Qhttp.post(self.__task_model.call_back,
                                     {
                                        'data': 'pause request applied!',
                                        'status': constants.STATUS_SUCCESS,
                                        'process_id': self.__task_model.process_id,
                                        'token': self.__task_model.token,
                                        'action': 'pause'
                                      })
        except:
            pass
        elapsed = 0
        while not self.resume_request:
            if elapsed > timeout:
                return
            sleep(1)
            elapsed += 1

    def cancel(self):
        try:
            http_result = Qhttp.post(self.__task_model.call_back,
                                     {
                                        'data': 'cancel request applied!',
                                        'status': constants.STATUS_SUCCESS,
                                        'process_id': self.__task_model.process_id,
                                        'token': self.__task_model.token,
                                        'action': 'cancel'
                                      })
        except:
            pass
        raise CancelExecutionError('task canceled by user!')

    def check_point(self):
        if self.pause_request:
            self.pause_request = False
            if isinstance(self.pause_request, str):
                self.pause_request = int(self.pause_request)
            self.pause(self.pause_request)
        if self.cancel_request:
            self.cancel_request = False
            self.cancel()
