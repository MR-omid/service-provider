from core.database import Database
from components.migrator import Migrate
from vendor.peewee_moves import DatabaseManager
import os

# it is IMPORTANT: all model imports must be after database connection ready
""" prepare and initialize database and configs needed before start server """
# set directory for address migration name for create and apply
project_root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
manager = DatabaseManager(Database.db, directory=project_root_path + '/migrations')
mg = Migrate()
migration_path = project_root_path + '/migrations'
model_path = project_root_path + '/models'
mg.create_migration(manager, model_path, migration_path, ignore=['base_model'])
mg.apply_migration(manager)
