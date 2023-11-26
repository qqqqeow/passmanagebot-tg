from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.menu_kb import get_menu_kb, get_password_kb

from aiogram.fsm.context import FSMContext
from database.api import FolderManager, PasswordManager

router = Router()

@router.callback_query(F.data.startswith("view_folder"))
async def view_folder_call(call: CallbackQuery, state: FSMContext):
    await state.clear()
    
    call_data = call.data.split("|")
    
    folder_id = int(call_data[1])
    parent_folder_id = int(call_data[2])
    
    if folder_id == 0:
        folder_name = "<b>Менеджер паролей by @x1x</b>"
    else:
        folder_data = await FolderManager.get_folder(folder_id=folder_id)
        folder_name = folder_data.folder_name
    
    await call.message.edit_text(text=f"<b>🗂 {folder_name}</b>", reply_markup=await get_menu_kb(folder_id=folder_id,
                                                                                                 parent_folder_id=parent_folder_id,
                                                                                                 page=1))
    
@router.callback_query(F.data.startswith("view_password"))
async def view_password_call(call: CallbackQuery, state:FSMContext):
    await state.clear()
    
    call_data = call.data.split("|")
    password_id = int(call_data[1])
    folder_id = int(call_data[2])
    page = int(call_data[3])
    
    password_data = await PasswordManager.get_password(password_id=password_id)
    
    text = f"""<b>
Имя: <code>{password_data.password_name}</code>

URL: <code>{password_data.url}</code>
USERNAME: <code>{password_data.username}</code>
PASSWORD: <code>{password_data.password}</code></b>
"""

    await call.message.edit_text(text=text, reply_markup=await get_password_kb(password_id=password_id, folder_id=folder_id, page=page))