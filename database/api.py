from database.models import (
    Passwords as Password,
    Folders as Folder,
    manager
)

import aiosqlite
from functools import wraps
from typing import Union
import random



def manager_connection(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with manager.connection():
            return await func(*args, **kwargs)
    return wrapper


@manager_connection
async def create_tables():
    await Folder.create_table()
    await Password.create_table()


class FolderManager:
    """ FOLDERS MANAGER """
    @staticmethod
    @manager_connection
    async def folder_is_exist(folder_name:str, parent_folder_id:int):
        folders = await Folder.select().where(Folder.parent_folder_id == parent_folder_id).where(Folder.folder_name == folder_name)
        if folders != []:
            return True
        return False
    
    @staticmethod
    @manager_connection
    async def create_folder(folder_name:str, parent_folder_id:int):
        folder_id = random.randint(11111111, 99999999)
        await Folder.create(folder_id=folder_id, 
                                parent_folder_id=parent_folder_id,
                                folder_name=folder_name)

    
    @staticmethod
    @manager_connection
    async def delete_folder(folder_id:int):
        await PasswordManager.delete_password_by_folder_id(folder_id=folder_id)
        await Folder.delete().where(Folder.folder_id == folder_id)
    
    @staticmethod
    @manager_connection
    async def get_folders():
        folders = await Folder.select()
        return folders
    
    @staticmethod
    @manager_connection
    async def get_folder(folder_id):
        folders = await Folder.select().where(Folder.folder_id == folder_id)
        return folders[0]
        
    @staticmethod
    @manager_connection
    async def get_folders_by_parent_folder(parent_folder_id):
        folders = await Folder.select().where(Folder.parent_folder_id == parent_folder_id)
        return folders


class PasswordManager:
    """PASSWORD MANAGER"""
    @staticmethod
    @manager_connection
    async def create_password(folder_id:int, password_name:str, url:str, username:str, password:str):
        async with manager.connection():
            password_id = random.randint(11111111, 99999999)
            await Password.create(password_id=password_id,
                                  password_name=password_name,
                                  folder_id=folder_id,
                                  url=url,
                                  username=username,
                                  password=password)
    @staticmethod
    @manager_connection
    async def delete_password(password_id:int):
        await Password.delete().where(Password.password_id == password_id)
    
    @staticmethod
    @manager_connection
    async def delete_password_by_folder_id(folder_id:int):
        await Password.delete().where(Password.folder_id == folder_id)
    
    @staticmethod
    @manager_connection
    async def get_password(password_id:int):
        passwords = await Password.select().where(Password.password_id == password_id)
        return passwords[0]
    
    @staticmethod
    @manager_connection
    async def get_passwords_by_folder(folder_id:int):
        passwords = await Password.select().where(Password.folder_id == folder_id)
        return passwords
    

async def import_db(db_path):
    destination_path = "database/storage.db"

    source_conn = await aiosqlite.connect(db_path)
    source_cursor = await source_conn.cursor()

    await source_cursor.execute("SELECT * FROM Folders")
    folders_data = await source_cursor.fetchall()

    await source_cursor.execute("SELECT * FROM Passwords")
    passwords_data = await source_cursor.fetchall()


    destination_conn = await aiosqlite.connect(destination_path)
    destination_cursor = await destination_conn.cursor()

    await destination_cursor.execute("SELECT MAX(id) FROM Folders")
    last_folder_id = await destination_cursor.fetchone()
    last_folder_id = last_folder_id[0] if last_folder_id[0] else 0

    await destination_cursor.execute("SELECT MAX(id) FROM Passwords")
    last_password_id = await destination_cursor.fetchone()
    last_password_id = last_password_id[0] if last_password_id[0] else 0

    await destination_cursor.execute("""
        CREATE TABLE IF NOT EXISTS Folders (
            id INTEGER,
            folder_id INTEGER,
            parent_folder_id INTEGER,
            folder_name TEXT
        )
    """)


    await destination_cursor.execute("""
        CREATE TABLE IF NOT EXISTS Passwords (
            id INTEGER,
            password_id INTEGER,
            password_name TEXT,
            folder_id INTEGER,
            url TEXT,
            username TEXT,
            password TEXT
        )
    """)


    folders_counter = 0
    for folder in folders_data:
        last_folder_id += 1
        try:
            await destination_cursor.execute("INSERT INTO Folders VALUES (?, ?, ?, ?)", (last_folder_id,) + folder[1:])
            folders_counter += 1
        except:
            pass

    passwords_counter = 0
    for password in passwords_data:
        last_password_id += 1
        try:
            await destination_cursor.execute("INSERT INTO Passwords VALUES (?, ?, ?, ?, ?, ?, ?)", (last_password_id,) + password[1:])
            passwords_counter += 1
        except:
            pass
        
    # Сохраняем изменения и закрываем соединения
    await destination_conn.commit()
    await source_conn.close()
    await destination_conn.close()

    return folders_counter, passwords_counter