"""
create table api_task
date created: 2018-06-27 12:06:36.274918
"""


def upgrade(migrator):
    migrator.add_column('api_task', 'response_data', 'blob', default='')


def downgrade(migrator):
    pass
