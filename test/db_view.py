import os, sys
from time import sleep

from core.config import Setting
from models.config import ConfigModel
from models.module import ModuleModel

ps = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ps)
from models.task import TaskModel

# models = TaskModel.select().where(TaskModel.id == 1268)
models = ModuleModel.select()
# code = IntegerField(unique=True)
# alias = CharField(unique=True)
# inout = ComplexField()
# category = CharField()
# max = IntegerField(default=0)  # maximum concurrent execution
# is_action = BooleanField(default=False)
# active = BooleanField(default=True)
for model in models:
    print('code: ', model.code)
    print('alias: ', model.alias)
    print('category: ', model.category)
    print('is_action: ', model.is_action)
    # print('data: ', model.data)
    # print("response: ",model.response_data)
    pass
# import subprocess
# import resource
# f = open('oout.txt','a')
#
# def set_limit():
#     resource.setrlimit(resource.RLIMIT_NOFILE, (99999, 99999))
# process = subprocess.Popen(['python3', 'limit.py'],stdout=f, preexec_fn=set_limit)
# # proc_stdout = process.communicate()
# # print(proc_stdout)
# #
# print(resource.getrlimit(resource.RLIMIT_NOFILE))
#
# models = ConfigModel.select()
#
# for model in models:
#     print('id: ', model.id)
#     print("attribute: ", model.attribute)
#     print("value: ",model.value)
for name in ['LQueue', 'MQueue', 'HQueue']:
    # print(name, Setting.get(name))
    pass

#
# def t():
#     try:
#         print('try')
#         raise Exception
#     finally:
#         i = 2
#         print('finaly')
#         if i == 2:
#             raise NotADirectoryError
#         return None
#
# t()
