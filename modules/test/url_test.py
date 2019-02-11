# # # import os, sys
# # # import importlib
# import logging
# # import os
# # from core.constants import BASE_APP_PATH
#
# # # ps = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# # # # print(ps)
# # # sys.path.append(ps)
# # # from core.constants import version, BASE_APP_PATH
# # # from core.config import Setting
# # #
# # # # get updates dir, current system version and database version
# # # update_path = BASE_APP_PATH + '/updates'
# # # current_version = version
# # # try:
# # #     database_version = Setting.get('api_version')
# # # except:
# # #     database_version = 0.0
# # #
# # # try:
# # #     num = sys.argv.pop(-1)
# # #     patch = sys.argv.pop(-1)
# # # except:
# # #     patch = None
# # #
# # #
# # # # if database version is lower than system current version, make update list from needed update file then apply the list
# # # if float(database_version) < float(current_version):
# # #     updates = []
# # #     # convert database file name to
# # #     current_version = 'v_' + str(database_version).replace('.', '_')
# # #     for dirc in os.listdir(update_path):
# # #         if dirc > current_version:
# # #             updates.append(dirc)
# # #     updates = sorted(updates)
# # #     for update in updates:
# # #         # create object from Update class and run upgrade
# # #         import_file = importlib.import_module('updates.' + update + '.update')
# # #         a=(update.replace('_','.'))
# # #         a= a.replace('v.','')
# # #         up = import_file.Update()
# # #         up.upgrade()
# # #         Setting.put('api_version',a,True)
# # #
# # #
# # #
# # #
# # # def api_log(message, level='log'):
# # #     debug_mode = Setting.get('debug_mode')
# # #     if debug_mode:
# # #         if level == 'debug':
# # #             logging.debug(message)
# # #         if level == 'info':
# # #             logging.info(message)
# # #         if level == 'warning':
# # #             logging.warning(message)
# # #         if level == 'error':
# # #             logging.error(message)
# # #         if level == 'critical':
# # #             pass+
# # # logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
# # # logging.addLevelName( logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
# # # logging.addLevelName( logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
# # from core.config import Setting
# from colorlog import ColoredFormatter
# #
# #
# # class log():
# #     log_level = logging.DEBUG
# #     log_format = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
# #
# #     logging.root.setLevel(log_level)
# #     formatter = ColoredFormatter(log_format)
# #     stream = logging.StreamHandler()
# #     stream.setLevel(log_level)
# #     stream.setFormatter(formatter)
# #     log = logging.getLogger('pythonConfig')
# #     log.setLevel(log_level)
# #     log.addHandler(stream)
# #     # debug_mode = Setting.get('debug_mode')
# #     debug_mode = True
# #
# #
# #     @staticmethod
# #     def info_log(message):
# #         if log.debug_mode:
# #             log.log.info(message)
# #
# #     @staticmethod
# #     def error_log(message):
# #         if log.debug_mode:
# #             log.log.error(message)
# #
# #     @staticmethod
# #     def warning_log(message):
# #         if log.debug_mode:
# #             log.log.warning(message)
# #
# #     @staticmethod
# #     def critical_log(message):
# #         if log.debug_mode:
# #             log.log.critical(message)
# #     #
# #     # try:
# #     #
# #     # except Exception:
# #     #     # set True by default if can not access database
# #     #     debug_mode = True
# #     # if debug_mode:
# #     #     if level == 'debug':
# #     #         log.debug(message)
# #     #     if level == 'info':
# #     #         log.info(message)
# #     #     if level == 'warning':
# #     #         log.warning(message)
# #     #     if level == 'error':
# #     #         log.error(message)
# #     #     if level == 'critical':
# #     #         log.critical(message)
# #
# #
# # # log.info_log('info_log')
# # # log.warning_log('warning_log')
# # # log.critical_log('critical_log')
# # # log.error_log('error_log')
# # path = BASE_APP_PATH + '/components'
# # file_name = 'mode.py'
# # file_adress = os.path.join(path,file_name)
# # f = open(file_adress, "w+")
# # f.write('debug_mode = ' + str(True))
#
# # cl
#
# from core.config import Setting
# query = Setting.get_keys()
