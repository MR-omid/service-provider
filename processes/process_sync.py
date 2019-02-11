import signal
import sys,os
from time import sleep
ps = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ps)


from PyQt5.QtCore import QCoreApplication, QObject, QTimer, Qt, QRunnable, QThreadPool

from components.Qhttp import  Qhttp
from components.utils import to_json, ApiLogging
from core import constants
from models.task import TaskModel


class ProcessSync(QObject):

    def __init__(self):
        super().__init__()
        self.pool = QThreadPool(self)
        self.pool.setMaxThreadCount(5000)
        self.lock = False
        sync_resource = QTimer(self)
        sync_resource.timeout.connect(self.sync, Qt.DirectConnection)
        sync_resource.start(5 * 1000 * 60)
        signal.signal(signal.SIGUSR1, self.__signal_handler)
        # FIXME: release all locked task
        locked_tasks = TaskModel.select().where(TaskModel.delivery == constants.STATUS_LOCKED)
        for t_locked in locked_tasks:
            t_locked.delivery = constants.STATUS_PENDING
            t_locked.save()
        self.keep_alive()

    def sync(self, is_new=False):
        if self.lock is False:
            self.lock = True
            try:
                if is_new:
                    tasks = TaskModel.select().where(
                        (TaskModel.delivery == constants.STATUS_NEW) &
                        (TaskModel.status != constants.STATUS_RUNNING))
                else:
                    ApiLogging.info('process sync in interval')
                    tasks = TaskModel.select().where(
                        ((TaskModel.delivery == constants.STATUS_NEW) |
                         (TaskModel.delivery == constants.STATUS_PENDING)) &
                        (TaskModel.status != constants.STATUS_RUNNING))
                for task in tasks:
                    task.delivery = constants.STATUS_LOCKED
                    task.save()
                    sync_task = SyncTask(task)
                    sync_task.setAutoDelete(True)
                    self.pool.start(sync_task)
                # print('sync interval')
            except Exception as e:
                # print('sync exception: ', e)
                pass
            finally:
                self.lock = False

    def __signal_handler(self, signal, frame):
        ApiLogging.info('process sync signal received')
        self.sync(True)

    def keep_alive(self):
        while True:
            QCoreApplication.processEvents()
            sleep(5)


class SyncTask(QRunnable):

    def __init__(self, task):
        super().__init__()
        self.task = task

    def run(self):
        try:
            http_result = Qhttp.post(self.task.call_back, self.task.response_data)
            # print('call_back result: ', http_result.content)
            if http_result.status_code == 200 and http_result.content == b'ok':
                self.task.delivery = constants.STATUS_SUCCESS
                self.task.save()
            else:
                self.task.details = to_json(http_result.content.decode())
                self.task.delivery = constants.STATUS_PENDING
                self.task.max_retry -= 1
                if self.task.max_retry < 1:
                    self.task.delivery = constants.STATUS_FAILED
                self.task.save()
        except Exception:
            self.task.details = "Connection refused"
            self.task.delivery = constants.STATUS_PENDING
            self.task.max_retry -= 1
            if self.task.max_retry < 1:
                self.task.delivery = constants.STATUS_FAILED
            self.task.save()


if __name__ == "__main__":
    if sys.argv.pop(-1) != "0X105050":
        ApiLogging.info(type(sys.argv.pop(-1)))
        ApiLogging.critical('missing token parameter')
        sys.exit(0)
    app = QCoreApplication(sys.argv)
    p = ProcessSync()
    sys.exit(app.exec_())
