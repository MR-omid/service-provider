"""
drop old tables
date created: 2018-02-17 08:10:45.911179
"""


def upgrade(migrator):
    try:
        migrator.drop_table('core_request', True)
        migrator.drop_table('F_Config', True)
        migrator.drop_table('core_config', True)
        migrator.drop_table('core_module', True)
    except:
        pass


def downgrade(migrator):
    pass
