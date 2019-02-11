import os, sys
import subprocess

from components.utils import ApiLogging

ps = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ps)
from core import constants

ApiLogging.info('base path', constants.BASE_APP_PATH)
ApiLogging.info('path: ',os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
full_command = "./receive.py"
subprocess.Popen(['/usr/bin/python3',full_command], close_fds=True)
