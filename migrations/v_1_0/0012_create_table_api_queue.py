"""
create table api_queue
date created: 2018-08-08 04:55:46.025158
"""


def upgrade(migrator):
    with migrator.create_table('api_queue') as table:
        table.primary_key('id')
        table.text('tag', unique=True)
        table.text('name')
        table.blob('data')
        table.int('priority')


def downgrade(migrator):
    migrator.drop_table('api_queue')
