"""
create table api_config
date created: 2018-07-03 15:37:14.191520
"""


def upgrade(migrator):
    with migrator.create_table('api_config') as table:
        table.primary_key('id')
        table.char('attribute', max_length=255, unique=True)
        table.blob('value')


def downgrade(migrator):
    migrator.drop_table('api_config')
