import os
import sys
from time import sleep
import psutil
from PyQt5.QtCore import QObject, QCoreApplication, QTimer, Qt

from core import constants
from core.config import Setting
from models.task import TaskModel


class LoadBalancer(QObject):

    def __init__(self):
        super().__init__()
        self.safety_value = round(((psutil.virtual_memory().available / 1048576) * 10) / 100)  # %10 of memory
        self.group_average = {'LQueue': 10, 'MQueue': 40, 'HQueue': 300}
        self.min_value = (self.group_average.get('HQueue') * len(self.group_average))
        self.min_group_limitation = self.init_limitation()
        for name, value in self.min_group_limitation.items():
            Setting.put(name, value, force=True)
        sync_resource = QTimer(self)
        sync_resource.timeout.connect(self.interval, Qt.DirectConnection)
        sync_resource.start(3 * 1000 * 60)

    def init_limitation(self):
        height_ratio = 1
        medium_ratio = round((self.group_average.get('HQueue') / self.group_average.get('MQueue')))
        low_ratio = round((self.group_average.get('HQueue') / self.group_average.get('LQueue')))
        return {'LQueue': low_ratio, 'MQueue': medium_ratio, 'HQueue': height_ratio}

    def interval(self):
        actions = self.calculate_ratio()
        self.apply_action(actions)

    def apply_action(self, actions):
        for key, action in actions.items():
            if action['up']:
                Setting.put(key, Setting.get(key) + self.min_group_limitation.get(key))
            if action['down']:
                down = Setting.get(key) - (self.min_group_limitation.get(key) * action['down_ratio'])
                if down >= self.min_group_limitation.get(key):
                    Setting.put(key, down)

    @staticmethod
    def get_running_services():
        running_services = TaskModel.select().where(TaskModel.status == constants.STATUS_RUNNING)
        l, m, h = 0, 0, 0
        for service in running_services:
            if service.queue_name == 'LQueue':
                l += 1
            elif service.queue_name == 'MQueue':
                m += 1
            elif service.queue_name == 'HQueue':
                h += 1
        return {'LQueue': l, 'MQueue': m, 'HQueue': h}

    def available_resource(self):
        mem = round((psutil.virtual_memory().available / 1048576) - self.safety_value - self.min_value)
        return int(mem)

    def calculate_ratio(self):
        tmpl = {'up': None, 'down': None, 'down_ratio': 0}
        actions = {'LQueue': tmpl.copy(), 'MQueue': tmpl.copy(), 'HQueue': tmpl.copy()}
        running_services = self.get_running_services()
        _max = 0
        for group_k, group_v in self.min_group_limitation.items():
            if self.available_resource() > self.min_value:
                r = running_services.get(group_k)
                l = Setting.get(group_k)
                m = group_v
                if r < l:
                    rt = (l - r)
                    if rt > m:
                        rt = round((rt - m) / m+.5)
                        actions[group_k]['down'] = True
                        actions[group_k]['down_ratio'] = rt
                elif r >= l:
                    actions[group_k]['up'] = True
            else:
                l = Setting.get(group_k)
                rt = (l / group_v)
                if rt > _max:
                    _max = rt
                    actions.clear()
                    actions.update({group_k: {'up': False, 'down': True, 'down_ratio': 1}})

        return actions


if __name__ == "__main__":
    if sys.argv.pop(-1) != "0X105060":
        # print('missing token parameter')
        sys.exit(0)
    app = QCoreApplication(sys.argv)
    p = LoadBalancer()
    sys.exit(app.exec_())
