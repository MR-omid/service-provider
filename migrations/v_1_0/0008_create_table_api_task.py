"""
create table api_task
date created: 2018-07-03 15:37:14.193624
"""


def upgrade(migrator):
    with migrator.create_table('api_task') as table:
        table.primary_key('id')
        table.text('route')
        table.text('process_id')
        table.text('status')
        table.text('token')
        table.text('module_version')
        table.blob('data')
        table.blob('progress')
        table.text('call_back')
        table.int('max_retry')
        table.datetime('create_date')
        table.text('details')
        table.text('delivery')
        table.text('queue_name')


def downgrade(migrator):
    migrator.drop_table('api_task')
