from peewee_aio import AIOModel, fields, Manager
from database.manager import manager

@manager.register
class Folders(AIOModel):
    folder_id = fields.IntegerField(unique=True)
    parent_folder_id = fields.IntegerField()
    folder_name = fields.TextField()


@manager.register
class Passwords(AIOModel):
    password_id = fields.IntegerField(unique=True)
    password_name = fields.TextField()
    folder_id = fields.IntegerField()
    url = fields.TextField()
    username = fields.TextField()
    password = fields.TextField()



