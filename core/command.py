import ast
import base64
import importlib
import json
import os
import shutil
import signal
import uuid
from os.path import isdir
import shutil
from shutil import make_archive
from core.queue import PGQ
import psutil
from peewee import DoesNotExist
import base64, io, zipfile
import os
from core.constants import BASE_APP_PATH
from components.LogHandler import LogHandler
from components.utils import find_pid, ApiLogging, to_json
from core import constants
from extensions.hrobot.v_1_0.Hrobot import Hrobot
from models.action import ActionModel
from models.module import ModuleModel
from models.task import TaskModel
from vendor.custom_exception import InvalidInputError, DatabaseError, CancelExecutionError


class Command(object):

    def __init__(self):
        pass

    @staticmethod
    def is_action(route_code):
        try:
            result = ModuleModel.get(ModuleModel.code == route_code, ModuleModel.active == True,
                                     ModuleModel.is_action == True)
            return True
        except Exception:
            return None

    @staticmethod
    def send_signal(process_names):
        try:
            for name in process_names:
                pids = []
                for process_name in constants.APP_PROCESSES:
                    if process_name.get('name') == name:
                        pids = find_pid(process_name.get('token'))
                if len(pids) > 1:
                    ApiLogging.warning('Too many ' + str(name) + ' process running')
                elif len(pids) == 1:
                    p = psutil.Process(pids[0])
                    ApiLogging.info('process name: ' + str(pids[0]))
                    p.send_signal(signal.SIGUSR1)
        except Exception as e:
            ApiLogging.critical('broadcast signal exception: ' + str(e))

    @staticmethod
    def __get_data(data):
        try:
            if isinstance(data, (bytes, bytearray)):
                data = data.decode()
            return json.loads(data)['data']
        except Exception:
            return None

    @staticmethod
    def log(data):
        """
        :param bytearray data: contain log query parameters
        :return: list of application log
        :rtype: dict
        """
        try:
            log = LogHandler.get_log(data)
            return {'data': log, 'status': constants.STATUS_SUCCESS}
        except Exception as e:
            return {'data': e.__str__(), 'status': constants.STATUS_ERROR}

    @staticmethod
    def module_list(data=None):
        try:
            modules = ModuleModel.select().where((ModuleModel.is_action == False) & (ModuleModel.active == True))
            module_list = {}
            for module in modules:
                module_list.update({module.code: module.inout})
            return {'data': module_list, 'status': constants.STATUS_SUCCESS}
        except Exception as e:
            return {'data': e.__str__(), 'status': constants.STATUS_ERROR}

    @staticmethod
    def get_module_config():
        """
        :return: module_config and status
        :rtype: dict
        """
        try:
            modules = ModuleModel.select().where((ModuleModel.is_action == False) & (ModuleModel.active == True))
            module_list = []
            for module in modules:
                module_dic = (
                    {'code': module.code, 'alias': module.alias, 'inout': module.inout, 'category': module.category,
                     'max': module.max, 'is_action': module.is_action, 'active': module.active})
                module_list.append(module_dic)
            return {'data': module_list, 'status': constants.STATUS_SUCCESS}
        except Exception as e:
            return {'data': e.__str__(), 'status': constants.STATUS_ERROR}

    @staticmethod
    def set_module_config(data):
        """
        :param  data: dictionary that contain data keyword, and value of that, is list of module_config
        like : {data:{[{module_1_config},{module_2_config}, ...]}}
        :return: status and message
        :rtype: dict
        """

        try:
            module_list = data['data']
            for module in module_list:
                # updating module category and active
                try:  # catch error if code does not exist
                    query = ModuleModel.select().where(ModuleModel.code == module['code'])
                except DoesNotExist:
                    raise InvalidInputError(' can not find ' + str(module['code']))
                try:  # try updating
                    query = ModuleModel.update(category=module['category'],
                                               active=module['active']).where(ModuleModel.code == module['code'])
                    query.execute()
                except Exception:
                    raise DatabaseError(' can not access database')

            # return status of operation
            return {'data': 'module_config update successfully', 'status': constants.STATUS_SUCCESS}
        except KeyError as e:  # Occurs if one of config keyword missing in input
            return {'data': e, 'status': constants.STATUS_ERROR}

    @staticmethod
    def install_module(ecode_date):
        decode = base64.b64decode(ecode_date)
        with zipfile.ZipFile(io.BytesIO(decode)) as zf:
            # save zip file in vendor/install_module
            (zf.extractall(path=BASE_APP_PATH + '/.temp_install_module'))
        # iteration on dir that exist in vendor/install_module -> module dir
        for module_name in os.listdir(BASE_APP_PATH + '/.temp_install_module'):
            # iteration on dir that exist in vendor/install_module/module_name -> version dir and patch file
            for file in os.listdir(BASE_APP_PATH + '/.temp_install_module/' + module_name):
                # checking if the file in install_module/module_name is version dir
                if os.path.isdir(
                        BASE_APP_PATH + '/.temp_install_module/' + module_name + '/' + file) and file.startswith('v_'):
                    version = file

                    # checking if this version exist in module, if it is True, remove and replace new version,else copy
                    if os.path.isdir(BASE_APP_PATH + '/modules/' + module_name + '/' + version):
                        shutil.rmtree(BASE_APP_PATH + '/modules/' + module_name + '/' + version)
                    shutil.copytree(BASE_APP_PATH + '/.temp_install_module/' + module_name + '/' + version,
                                    BASE_APP_PATH + '/modules/' + module_name + '/' + version)
                # checking if the file in install_module/module_name is patch file
                if (os.path.isfile(
                        BASE_APP_PATH + '/.temp_install_module/' + module_name + '/' + file) and file.startswith(
                    'patch')):
                    # copy patch in module_name dir
                    shutil.copyfile(BASE_APP_PATH + '/.temp_install_module/' + module_name + '/' + file,
                                    BASE_APP_PATH + '/modules/' + module_name + '/' + file)
                    # import patch
                    file_name = file.replace('.py', '')
                    importlib.import_module('modules.' + module_name + '.' + file_name)
                    # remove patch file
                    # os.remove(BASE_APP_PATH + '/modules/' + module_name + '/' + file)
        # remove temp_install dir
        shutil.rmtree(BASE_APP_PATH + '/.temp_install_module')

    @staticmethod
    def cancel(data):
        params = Command.__get_data(data)
        if params:
            if params.get('process_id'):

                tag = params.get('process_id')
                try:  # check if this process_id is running
                    task_exist = TaskModel.get(TaskModel.process_id == tag)
                except Exception:
                    task_exist = False
                queue_exist = PGQ.preview(tag)
                # check if this process_id is on queue or running
                if queue_exist or task_exist:
                    try:  # check if any other command submitted
                        action = ActionModel.get(ActionModel.process_id == tag)
                    except:
                        action = ActionModel()
                        action.process_id = params.get('process_id')
                    action.action = constants.STATUS_CANCEL
                    if queue_exist:
                        action.status = constants.STATUS_SUCCESS
                    action.save()

                    if queue_exist:
                        item = PGQ.get_by_tag(tag)  # get from queue and remove item, and save in task_model
                        task_model = TaskModel()
                        # route, call_back, token, process_id, data, module_version
                        error = {'code': CancelExecutionError.get_code(), 'message': 'task canceled by user!'}
                        task_model.route = item.data.route
                        task_model.process_id = item.data.process_id
                        task_model.status = constants.STATUS_FAILED
                        task_model.token = item.data.token
                        task_model.module_version = item.data.module_version
                        task_model.data = item.data.data
                        task_model.call_back = item.data.call_back
                        task_model.delivery = constants.STATUS_NEW
                        task_model.queue_name = item.name
                        task_model.response_data = {
                            'data': to_json({}),
                            'error': to_json(error),
                            'status': constants.STATUS_ERROR,
                            'token': item.data.token,
                            'process_id': item.data.process_id
                        }
                        try:
                            task_model.save()
                        except Exception:
                            raise DatabaseError('can not access database')
                    Command.send_signal(['process_h.py', 'process_m.py', 'process_l.py'])
                    return {'data': 'cancel request received!', 'status': constants.STATUS_PENDING}
                else:
                    return {'data': 'process_id not found', 'status': constants.STATUS_ERROR}
            else:
                return {'data': 'process_id keyword not found', 'status': constants.STATUS_ERROR}
        return {'data': 'format or process id is wrong', 'status': constants.STATUS_ERROR}

    @staticmethod
    def pause(data):
        params = Command.__get_data(data)
        if params:
            if params.get('process_id'):
                tag = params.get('process_id')
                try:
                    task_exist = TaskModel.get(TaskModel.process_id == tag)
                except Exception:
                    task_exist = False
                queue_exist = PGQ.preview(tag)
                if queue_exist or task_exist:
                    try:
                        action = ActionModel.get(ActionModel.process_id == tag)
                    except:
                        action = ActionModel()
                        action.process_id = params.get('process_id')
                    action.action = constants.STATUS_PAUSE
                    if params.get('timeout'):
                        action.timeout = params.get('timeout')
                    else:
                        return {'data': 'timeout keyword not found', 'status': constants.STATUS_ERROR}
                    try:
                        action.save()
                    except Exception:
                        raise DatabaseError('can not access database')
                    Command.send_signal(['process_h.py', 'process_m.py', 'process_l.py'])
                    return {'data': 'pause request received!', 'status': constants.STATUS_PENDING}
                else:
                    return {'data': 'process_id not found', 'status': constants.STATUS_ERROR}
            else:
                return {'data': 'process_id keyword not found', 'status': constants.STATUS_ERROR}
        return {'data': 'format or process id is wrong', 'status': constants.STATUS_ERROR}

    @staticmethod
    def resume(data):
        params = Command.__get_data(data)
        if params:
            if params.get('process_id'):
                tag = params.get('process_id')
                try:
                    task_exist = TaskModel.get(TaskModel.process_id == tag)
                except Exception:
                    task_exist = False
                if PGQ.preview(tag) or task_exist:
                    try:
                        action = ActionModel.get(ActionModel.process_id == tag)
                    except:
                        action = ActionModel()
                        action.process_id = params.get('process_id')
                    action.action = constants.STATUS_RESUME
                    try:
                        action.save()
                    except Exception:
                        raise DatabaseError(' can not access database')
                    Command.send_signal(['process_h.py', 'process_m.py', 'process_l.py'])
                    return {'data': 'resume request applied!', 'status': constants.STATUS_SUCCESS}
                else:
                    return {'data': 'process_id not found', 'status': constants.STATUS_ERROR}

            else:
                return {'data': 'process_id keyword not found', 'status': constants.STATUS_ERROR}
        return {'data': 'format or process id is wrong', 'status': constants.STATUS_ERROR}

    @staticmethod
    def progress(data):
        params = Command.__get_data(data)
        if params:
            try:
                # check if process is in task_model
                result = TaskModel.get(TaskModel.process_id == params.get('process_id'))
                if result.status == constants.STATUS_RUNNING:
                    return {'data': result.progress, 'status': constants.STATUS_SUCCESS}
                else:
                    res = result.response_data
                    for k, r in res.items():
                        try:
                            res.update({k: json.loads(r)})
                        except Exception:
                            pass
                    return {'data': res, 'status': constants.STATUS_SUCCESS}
            except Exception:  # exception happen when process not exist in task_model, so check queue
                if PGQ.preview(params.get('process_id')):
                    return {'data': {'status': constants.STATUS_QUEUE,
                                     'process_id': params.get('process_id'),
                                     'message': 'process still is in the queue'}, 'status': constants.STATUS_SUCCESS}
                else:  # task not exist in queue neither
                    return {'data': 'process_id not found', 'status': constants.STATUS_ERROR}
        return {'data': 'format or process id is wrong', 'status': constants.STATUS_ERROR}

    @staticmethod
    def download(data):
        """
        :param bytearray data: contain file path
        :return: file content if exists
        :rtype: dict
        """
        params = Command.__get_data(data)
        if params:
            try:
                bp = os.path.realpath('.')
                path = bp + '/' + params
                ApiLogging.info("download path: " + str(path))
                is_exists = os.path.exists(path)
                if is_exists:
                    file = open(path, 'r')
                    raw_data = file.read()
                    file.close()
                else:
                    return {'data': 'File Not Found', 'status': 'error'}
                return {'data': raw_data, 'status': 'success'}
            except:
                return {'data': 'internal exception', 'status': constants.STATUS_ERROR}
        return {'data': 'path format is wrong', 'status': constants.STATUS_ERROR}

    @staticmethod
    def download_by_process_id(data):
        params = Command.__get_data(data)
        base_data_path = BASE_APP_PATH + '/modules/storage'
        if params:
            try:
                full_data_path = base_data_path + '/' + params['process_id']
                ApiLogging.info("download path: " + str(full_data_path))
                if not isdir(full_data_path):
                    return {'data': 'process_id Not Found', 'status': 'error'}
                shutil.make_archive(full_data_path, 'zip', full_data_path)
                with open(base_data_path + '/' + params['process_id']+'.zip', "rb") as f:
                    bytes = f.read()
                    encoded = base64.b64encode(bytes)
                return {'data': encoded, 'status': 'success'}
            except Exception as e:
                print(e)
                return {'data': 'internal exception', 'status': constants.STATUS_ERROR}
        return {'data': 'process_id format is wrong', 'status': constants.STATUS_ERROR}

    @staticmethod
    def system_information(data=None):
        """
        :param bytearray data: not used in this method, only for compatibility
        :return: system information (disk,ram,cpu)
        :rtype: dict
        """
        return {'data': {'CPU': round(psutil.cpu_percent()), 'RAM': round(psutil.virtual_memory().percent),
                         'DISK': round(psutil.disk_usage(os.path.dirname(__file__)).percent),
                         'STATE': 'Not available yet!'}, 'status': 'success'}

    @staticmethod
    def screenshot(data):
        params = Command.__get_data(data)
        if params:
            try:
                robot = Hrobot()
                robot.go_to(params.get('url'))
                name = uuid.uuid4().hex + '.png'
                robot.save_as_png(name)
                f = open(name, "rb")
                file_data = f.read()
                f.close()
                file_data = base64.b64encode(file_data)
                os.remove(name)
                return {'data': file_data.decode(), 'status': constants.STATUS_SUCCESS}
            except Exception as e:
                return {'data': 'url not found', 'status': constants.STATUS_ERROR}
        return {'data': 'format or url is wrong', 'status': constants.STATUS_ERROR}
