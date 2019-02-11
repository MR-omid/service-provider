"""
create table api_module
date created: 2018-06-27 12:06:36.274918
"""


def upgrade(migrator):
    migrator.drop_column('api_module', 'input', cascade=True)
    migrator.drop_column('api_module', 'output', cascade=True)
    migrator.add_column('api_module', 'inout', 'blob', default='')


def downgrade(migrator):
    pass
