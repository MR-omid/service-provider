"""
create table api_module
date created: 2018-06-27 12:06:36.274918
"""


def upgrade(migrator):
    with migrator.create_table('api_module') as table:
        table.primary_key('id')
        table.int('code', unique=True)
        table.char('alias', unique=True)
        table.blob('input')
        table.blob('output')
        table.char('category', max_length=255)
        table.int('max')
        table.bool('is_action')
        table.bool('active')


def downgrade(migrator):
    migrator.drop_table('api_module')
