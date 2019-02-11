import signal, os, sys
from time import sleep


ps = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ps)
import psutil
from PyQt5.QtCore import QObject, QThreadPool, pyqtSlot, QCoreApplication
from peewee import OperationalError
from components.utils import find_pid, ApiLogging
from core.api import RequestObject
from core import constants
from core.queue import PGQ
from core.task import Task
from core.config import Setting
from models.action import ActionModel
from models.task import TaskModel
from vendor.custom_exception import NetworkError


class BaseProcess(QObject):

    def __init__(self, queue_name, default_limit):
        super().__init__()
        self.running_tasks = {}
        self.done_tasks = []
        self.default_limit = default_limit
        self.queue = PGQ(queue_name)
        self.queue_name = queue_name
        self.pool = QThreadPool(self)
        self.pool.setMaxThreadCount(5000)
        signal.signal(signal.SIGUSR1, self.__signal_handler)
        self.items = []
        try:
            __items = TaskModel.select().where((TaskModel.status == constants.STATUS_RUNNING) & (TaskModel.queue_name == self.queue_name))
            for __item in __items:
                self.items.append(__item)
        except OperationalError:
            raise NetworkError('Network is unreachable')

    def run(self):
        while 1:
            # sleep for decrease cpu usage
            sleep(0.01)
            QCoreApplication.processEvents()
            from_db = False
            if self.running_tasks.__len__() >= self.limit():
                continue
            try:
                if self.items:
                    from_db = True
                    item = self.items.pop()
                else:
                    item = self.queue.get()  # type: RequestObject
                if item:
                    if not from_db:
                        task_model = TaskModel()
                        task_model.route = item.route
                        task_model.process_id = item.process_id
                        task_model.status = constants.STATUS_RUNNING
                        task_model.data = item.data
                        task_model.call_back = item.call_back
                        task_model.token = item.token
                        task_model.module_version = item.module_version
                        task_model.queue_name = self.queue_name
                        task_model.save()
                    else:
                        task_model = item

                    task = Task(task_model)
                    if task.instance_module:
                        task.instance_module.task_finished.connect(self.__task_finished)
                        task.setAutoDelete(True)
                        self.running_tasks.update({item.process_id: task})
                        # check cancel or pause request before start
                        self.apply_action_by_pid(task, item.process_id)
                        self.pool.start(task)
                    else:
                        # TODO: set error alarm
                        ApiLogging.error('problem running task')
            except Exception as e:
                ApiLogging.error('process exception' + str(e))
                # TODO: set error alarm
                continue

    def limit(self):
        try:
            limit = Setting.get(self.queue_name)
            if limit:
                return int(limit)
        except Exception:
            # use default limit if exception or not present
            pass
        return self.default_limit

    @pyqtSlot(str, name='task_finished')
    def __task_finished(self, task_id):
        ApiLogging.info('task finished')
        del self.running_tasks[task_id]

        self.done_tasks.append(task_id)
        self.send_signal()

    @staticmethod
    def send_signal():
        pids = []
        for process_name in constants.APP_PROCESSES:
            if process_name.get('name') == 'process_sync.py':
                pids = find_pid(process_name.get('token'))
        if len(pids) > 1:
            ApiLogging.warning('Too many sync process running')
        elif len(pids) == 1:
            p = psutil.Process(pids[0])
            p.send_signal(signal.SIGUSR1)

    def __signal_handler(self, signal, frame):
        ApiLogging.info('base process signal received')
        # TODO: update limit
        self.check_pending_actions()

    def apply_action_by_pid(self, task, pid):
        actions = ActionModel.select().where(ActionModel.process_id == pid)
        for action in actions:
            if action.action == constants.STATUS_PAUSE:
                task.instance_module.pause_request = action.timeout
            elif action.action == constants.STATUS_CANCEL:
                task.instance_module.cancel_request = True
            elif action.action == constants.STATUS_RESUME:
                task.instance_module.resume_request = True

            action.status = constants.STATUS_SUCCESS
            action.save()

    def check_pending_actions(self):
        actions = ActionModel.select().where(ActionModel.status == constants.STATUS_PENDING)
        for action in actions:
            if action.process_id in self.running_tasks:
                task = self.running_tasks.get(action.process_id)
                if task:
                    if action.action == constants.STATUS_PAUSE:
                        task.instance_module.pause_request = action.timeout
                    elif action.action == constants.STATUS_CANCEL:
                        task.instance_module.cancel_request = True
                    elif action.action == constants.STATUS_RESUME:
                        task.instance_module.resume_request = True

                action.status = constants.STATUS_SUCCESS
                action.save()
            elif action.process_id in self.done_tasks:
                action.status = constants.STATUS_SUCCESS
                action.save()
