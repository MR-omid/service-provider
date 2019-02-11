import os
import sys
ps = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ps)
try:
    from components.mode import debug_mode
except ImportError:
    debug_mode = True

if debug_mode:
    database = {
        'name': 'test',
        'host': '127.0.0.1',
        'port': '5432',
        'username': 'postgres',
        'password': 'dpe'
    }
    version = '1.0'
else:
    database = {
        'name': 'pro',
        'host': '127.0.0.1',
        'port': '5432',
        'username': 'postgres',
        'password': 'dpe'
    }
    version = '1.0'

STATUS_NEW = 'new'
STATUS_PENDING = 'pending'
STATUS_RUNNING = 'running'
STATUS_SUCCESS = 'success'
STATUS_FAILED = 'failed'
STATUS_ERROR = 'error'
STATUS_PAUSE = 'pause'
STATUS_CANCEL = 'cancel'
STATUS_RESUME = 'resume'
STATUS_LOCKED = 'locked'
STATUS_QUEUE = 'queue'
BASE_APP_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
APP_PROCESSES = [
    {'path': '.', 'name': 'dev.py', 'token': '0X105010', 'log': 'logs/dev.log'},
    {'path': 'processes', 'name': 'process_h.py', 'token': '0X105020', 'log': 'logs/process_h.log'},
    {'path': 'processes', 'name': 'process_m.py', 'token': '0X105030', 'log': 'logs/process_m.log'},
    {'path': 'processes', 'name': 'process_l.py', 'token': '0X105040', 'log': 'logs/process_l.log'},
    {'path': 'processes', 'name': 'process_sync.py', 'token': '0X105050', 'log': 'logs/process_sync.log'},
    {'path': 'processes', 'name': 'load_balancer.py', 'token': '0X105060', 'log': 'logs/load_balancer.log'},
    {'path': 'processes', 'name': 'process_log.py', 'token': '0X105070', 'log': 'logs/process_log.log'}

]

DEFAULT_SIZE_LOG = 15000  # kilo bytes
REMOVE_LINES_LOG = 10000  # line numbers
