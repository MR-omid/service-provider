import os, sys
import resource
import signal
import subprocess
from time import sleep

import psutil

ps = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ps)
from core.constants import BASE_APP_PATH
from components.utils import find_pid, ApiLogging
from core import constants
import argparse

debug_mode = True


arg = argparse.ArgumentParser()
arg.add_argument("-a", "--action", required=True,
                 help="name of action you want to execution, available actions (status, start [-p], stop [-p], restart)")
arg.add_argument("-p", "--process_name", required=False,
                 help="[optional] process name to start or stop specific process,"
                      " if not precent, mean start or stop all process")


def check_requirements():
    error_message = []
    postgres = find_pid('postgresql')
    if not postgres:
        error_message.append('postgresql service required, but not running!')
    return True if not error_message else error_message


def status():
    for process in constants.APP_PROCESSES:
        pids = find_pid(process.get('token'))
        if not pids:
            ApiLogging.error([process.get('name'), pids], True)
        else:
            ApiLogging.info([process.get('name'), pids], True)


def start(process_name=None):
    requirements = check_requirements()
    if requirements is not True:
        for requirement in requirements:
            ApiLogging.critical(requirement, True)
        return
    if process_name and __get_process(process_name) is not None:
        process = __get_process(process_name)
        pids = find_pid(process.get('token'))
        if pids:
            ApiLogging.warning(str(len(pids)) + ' instance(s) of this process already running!', True)
        else:
            __run(process_name, 'start')
    else:
        for process in constants.APP_PROCESSES:
            if find_pid(process.get('token')):
                ApiLogging.warning(process.get('name') + ' is already running!', True)
            else:
                __run(process.get('name'), 'start')


def stop(process_name=None):
    if process_name and __get_process(process_name) is not None:
        process = __get_process(process_name)
        pids = find_pid(process.get('token'))
        if not pids:
            ApiLogging.warning(process_name + ' is not running!', True)
        else:
            for pid in pids:
                ApiLogging.info(process_name + ' stopped successful!', True)
                proc = psutil.Process(pid)
                if proc.is_running():
                    proc.kill()
    else:
        for process in constants.APP_PROCESSES:
            pids = find_pid(process.get('token'))
            if not pids:
                ApiLogging.warning(process.get('name') + ' is not running!', True)
            else:
                for pid in pids:
                    ApiLogging.info(process.get('name') + ' stopped successful!', True)
                    proc = psutil.Process(pid)
                    if proc.is_running():
                        proc.kill()
    try:
        __cleanup()
    except Exception as e:
        # print("cleanup exception: ", e)
        pass


def __get_process(process_name):
    for process in constants.APP_PROCESSES:
        if process.get('name') == process_name:
            return process
    return None


def __set_limit():
    resource.setrlimit(resource.RLIMIT_NOFILE, (99999, 99999))


def __run(process_name, action_name):
    process = __get_process(process_name)
    if process:
        ApiLogging.info(process.get('name') + ' running successful!', True)
        with open(process.get('log'), 'a+') as err:
            subprocess.Popen(['python3', process.get('path') + '/' + process.get('name'), process.get('token')],
                             close_fds=True, stderr=err,bufsize=1, preexec_fn=__set_limit)


def __cleanup():
    # terminate all xvfb process
    pids = find_pid('Xvfb')
    for pid in pids:
        proc = psutil.Process(pid)
        if proc.is_running():
            proc.kill()


def set_mode(debug_mode):
    path = BASE_APP_PATH + '/components'
    file_name = 'mode.py'
    file_adress = os.path.join(path, file_name)
    f = open(file_adress, "w+")
    f.write('debug_mode = ' + str(debug_mode))


if not os.path.exists(BASE_APP_PATH + '/logs'):
    os.mkdir(BASE_APP_PATH + '/logs')
args = vars(arg.parse_args())

action = args.get('action')
p = args.get('process_name', None)
set_mode(debug_mode)

if action == 'status':
    status()
elif action == 'start':
    if p:
        start(p)
    else:
        start()
elif action == 'stop':
    if p:
        stop(p)
    else:
        stop()
elif action == 'restart':
    stop()
    ApiLogging.critical('Start all process after one second...')
    sleep(3)
    start()
else:
    # print('action is not found!')
    pass
