"""
create table api_action
date created: 2018-07-03 15:37:14.194780
"""


def upgrade(migrator):
    with migrator.create_table('api_action') as table:
        table.primary_key('id')
        table.text('process_id')
        table.text('action')
        table.int('timeout')
        table.text('status')


def downgrade(migrator):
    migrator.drop_table('api_action')
