import os, sys
import importlib

# import shutil
ps = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ps)
from components.utils import ApiLogging
from components import mode
mode.debug_mode = False
from core.constants import BASE_APP_PATH, version
from core.config import Setting
from vendor.peewee_moves import Migrator
from core.database import Database

# get updates dir, current system version and database version
update_path = BASE_APP_PATH + '/updates'
current_version = version
if version == '1.0' and mode.debug_mode:
    # drop all tables here, if app_version is 1.0
    mg = Migrator(Database.db)
    table_list = Database.db.get_tables()
    for table in table_list:
        try:
            mg.drop_table(table)
        except Exception:
            continue


database_version = Setting.get('api_version')
if database_version is None:
    database_version = 0.0

try:
    num = sys.argv.pop(-1)
    patch = sys.argv.pop(-1)
except:
    patch = None

# if database version is lower than system current version, make update list from needed update file then apply the list
if float(database_version) < float(current_version):
    updates = []
    # convert database file name to
    current_version = 'v_' + str(database_version).replace('.', '_')
    for dirc in os.listdir(update_path):
        if dirc > current_version:
            updates.append(dirc)
    updates = sorted(updates)
    for update in updates:
        # create object from Update class and run upgrade
        import_file = importlib.import_module('updates.' + update + '.update')
        up = import_file.Update()
        temp_version = update.replace('v_', '')
        # convert dir name format to database record format
        database_new_version = temp_version.replace('_', '.')
        up.upgrade()
        Setting.put('api_version', database_new_version, force=True)


elif float(database_version) > float(current_version):
    # Todo: downgrade
    pass

else:  # database version is equal to system current version
    ApiLogging.info('system is updated', True)

if patch:
    try:
        import_file = importlib.import_module('updates.patch.patch_' + num)
        up = import_file.Update()
        up.upgrade()
        ApiLogging.info('patch ' + str(num) + ' applied!', True)
    except Exception as e:
        ApiLogging.error("patch exception: " + str(e), True)
