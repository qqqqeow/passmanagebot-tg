from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.api import FolderManager, PasswordManager
from config import MAX_ITEMS_IN_PAGE

def split_list(input_list, chunk_size, page):
    chunks_list = [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]
    max_page = len(chunks_list)
    
    if page > max_page: page = max_page
    
    if max_page != 0:
        return chunks_list[page-1], max_page
    return [], 1


async def get_menu_kb(folder_id:int, parent_folder_id:int, page:int=1):
    
    folders = await FolderManager.get_folders_by_parent_folder(parent_folder_id=folder_id)
    passwords = await PasswordManager.get_passwords_by_folder(folder_id=folder_id)

    
    kb = list()
    
    if folders:
        for folder in folders:
            kb.append([InlineKeyboardButton(text=f"🗂 {folder.folder_name}", callback_data=f"view_folder|{folder.folder_id}|{folder_id}")])
            
    if passwords:
        for password in passwords:
            pass
            kb.append([InlineKeyboardButton(text=f"🔑 {password.password_name}", callback_data=f"view_password|{password.password_id}|{folder_id}|{page}")])
    
    page_kb, max_page = split_list(input_list=kb, chunk_size=MAX_ITEMS_IN_PAGE, page=page)
    if page > max_page: page = max_page

    navigate_kb = list()
    
    if page > 1:
        navigate_kb.append(InlineKeyboardButton(text="◀️", callback_data=f"view_folder|{folder_id}|{parent_folder_id}|{page-1}"))
    
    navigate_kb.append(InlineKeyboardButton(text=f"{page} / {max_page}", callback_data="none"))    
    
    if page < max_page:
        navigate_kb.append(InlineKeyboardButton(text="▶️", callback_data=f"view_folder|{folder_id}|{parent_folder_id}|{page+1}"))
    
    create_kb = [InlineKeyboardButton(text="Создать 🗂", callback_data=f"create_folder|{folder_id}|{parent_folder_id}|{page}"),
                 InlineKeyboardButton(text="Добавить 🔑", callback_data=f"create_password|{folder_id}|{parent_folder_id}|{page}")]


    page_kb_len = len(page_kb)
    if page_kb_len == 0:
        page_kb = [[InlineKeyboardButton(text="Нет папок и паролей :(", callback_data="none")]]


    page_kb.append([InlineKeyboardButton(text="➖➖➖➖➖➖➖➖➖➖➖", callback_data="none")])
    page_kb.append(navigate_kb)
    page_kb.append(create_kb)
    
    if folder_id != 0:
        page_kb.append([InlineKeyboardButton(text="🗑 Удалить данную папку", callback_data=f"delete_folder|{folder_id}|{parent_folder_id}|{page}")])
    else:
        if page == 1:
            page_kb.append([InlineKeyboardButton(text="🗄 Импорт БД", callback_data="import_database"), InlineKeyboardButton(text="🗄 Экспорт БД", callback_data="export_database")])
    
    if folder_id != 0:
        if parent_folder_id != 0:
            folder_data = await FolderManager.get_folder(folder_id=parent_folder_id)
            new_folder_id = parent_folder_id
            new_folder_parent_id = folder_data.parent_folder_id
        else:
            new_folder_id = 0
            new_folder_parent_id = 0
        page_kb.append([InlineKeyboardButton(text="⏪ Назад", callback_data=f"view_folder|{new_folder_id}|{new_folder_parent_id}|1")])
        
    return InlineKeyboardMarkup(inline_keyboard=page_kb)


async def get_back_kb(parent_folder_id:int, page:int=None):
    
    kb = list()
    
    if parent_folder_id != 0:
        folder_data = await FolderManager.get_folder(folder_id=parent_folder_id)
        new_folder_id = parent_folder_id
        new_folder_parent_id = folder_data.parent_folder_id if folder_data.parent_folder_id is not None else 0
    else:
        new_folder_id = 0
        new_folder_parent_id = 0

    
    if not page:
        page = 1
    
    kb.append([InlineKeyboardButton(text="⏪ Назад", callback_data=f"view_folder|{new_folder_id}|{new_folder_parent_id}|{page}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


async def get_password_kb(password_id:int, folder_id:int, page:int):
    kb = [
        [InlineKeyboardButton(text="🗑 Удалить пароль", callback_data=f"delete_password|{password_id}|{page}")]
    ]
    
    if folder_id != 0:
        folder_data = await FolderManager.get_folder(folder_id=folder_id)
        new_folder_id = folder_id
        new_folder_parent_id = folder_data.parent_folder_id
    else:
        new_folder_id = 0
        new_folder_parent_id = 0
    
    if not page:
        page = 1
        
    kb.append([InlineKeyboardButton(text="⏪ Назад", callback_data=f"view_folder|{new_folder_id}|{new_folder_parent_id}|{page}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


async def get_confirm_delete_kb(folder_id:int, parent_folder_id:int, page:int):
    kb = [[
        InlineKeyboardButton(text="🗑 ДА", callback_data=f"delete1_folder|{folder_id}|{parent_folder_id}|{page}"),
        InlineKeyboardButton(text="❌ НЕТ", callback_data=f"view_folder|{folder_id}|{parent_folder_id}|{page}"),
    ]]
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def get_export_database_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Скрыть", callback_data="delete_msg")]])