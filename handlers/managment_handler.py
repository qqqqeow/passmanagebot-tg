from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.client.session.base import BaseSession
from keyboards.menu_kb import get_menu_kb
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.menu_kb import get_back_kb, get_menu_kb, get_confirm_delete_kb, get_export_database_kb
from database.api import FolderManager, PasswordManager, import_db
from config import BOT_TOKEN
import os


router = Router()

class CreateFolderStates(StatesGroup):
    get_data = State()

class CreatePasswordStates(StatesGroup):
    get_data = State()

@router.callback_query(F.data.startswith("create_folder"))
async def create_folder(call: CallbackQuery, state: FSMContext):
    await state.clear()
    
    call_data = call.data.split("|")
    folder_id = int(call_data[1])
    parent_folder_id = int(call_data[2])
    page = int(call_data[3])
    
    await state.set_state(CreateFolderStates.get_data)
    msg_obj = await call.message.edit_text(text="Введите имя для новой папки: ", 
                                           reply_markup=await get_back_kb(parent_folder_id=parent_folder_id))
    await state.update_data(
        msg_obj = msg_obj,
        folder_id = int(folder_id),
        parent_folder_id = int(parent_folder_id),
        page = int(page)
    )

@router.message(CreateFolderStates.get_data)
async def create_folder_final(msg: Message, state: FSMContext):
    state_data = await state.get_data()
    new_folder_name = msg.text
    
    folder_is_exist = await FolderManager.folder_is_exist(folder_name=new_folder_name,
                                             parent_folder_id=state_data["folder_id"])
    await msg.delete()
    
    if folder_is_exist:
        await state_data["msg_obj"].edit_text(text="Папка с данным именем уже существует, введите другое имя:",
                                              reply_markup=await get_back_kb(parent_folder_id=state_data["parent_folder_id"]))
        await state.set_state(CreateFolderStates.get_data)
    else:
        
        await FolderManager.create_folder(folder_name=new_folder_name, parent_folder_id=state_data["folder_id"])
        
        await state_data["msg_obj"].edit_text(text=f"Папка '{new_folder_name}' успешно созданна",
                                              reply_markup=await get_menu_kb(folder_id=state_data["folder_id"],
                                                                             parent_folder_id=state_data["parent_folder_id"],
                                                                             page=1000))
        await state.clear()
        
        
@router.callback_query(F.data.startswith("create_password"))
async def create_password(call: CallbackQuery, state: FSMContext):
    await state.clear()
    
    call_data = call.data.split("|")
    folder_id = int(call_data[1])
    parent_folder_id = int(call_data[2])
    page = int(call_data[3])
    
    await state.set_state(CreatePasswordStates.get_data)
    msg_obj = await call.message.edit_text(text="Введите данные пароля в таком формате:\n\nНазвание пароля|URL|USERNAME|PASSWORD ", 
                                           reply_markup=await get_back_kb(parent_folder_id=parent_folder_id))
    await state.update_data(
        msg_obj = msg_obj,
        folder_id = folder_id,
        parent_folder_id = parent_folder_id,
        page = page
    )

@router.message(CreatePasswordStates.get_data)
async def create_password_final(msg: Message, state: FSMContext):
    state_data = await state.get_data()
    password_data = msg.text.split("|")

    await msg.delete()
    
    if len(password_data) != 4:
        await state_data["msg_obj"].edit_text(text="Вы ввели данные в не верном формате, попробуйте ввести ещё раз в таком формате:\n\nНазвание пароля|URL|USERNAME|PASSWORD",
                                              reply_markup=await get_back_kb(parent_folder_id=state_data["parent_folder_id"]))
        await state.set_state(CreatePasswordStates.get_data)
    else:
        await PasswordManager.create_password(folder_id=state_data["folder_id"],
                                        password_name=password_data[0],
                                        url=password_data[1],
                                        username=password_data[2],
                                        password=password_data[3])
        await state_data["msg_obj"].edit_text(text=f"Пароль '{password_data[0]}' успешно записан",
                                              reply_markup=await get_menu_kb(folder_id=state_data["folder_id"],
                                                                             parent_folder_id=state_data["parent_folder_id"],
                                                                             page=1000))
        await state.clear()
        

@router.callback_query(F.data.startswith("delete_folder"))
async def delete_folder(call: CallbackQuery):
    call_data = call.data.split("|")
    
    folder_data = await FolderManager.get_folder(folder_id=call_data[1])
    
    await call.message.edit_text(text=f"<b>Вы действительно хотите удалить папку '{folder_data.folder_name}' всесте с паролями?</b>", 
                                 reply_markup=await get_confirm_delete_kb(folder_id=call_data[1], parent_folder_id=call_data[2], page=call_data[3]))

@router.callback_query(F.data.startswith("delete1_folder"))
async def delete_folder1(call: CallbackQuery):
    call_data = call.data.split("|")
    
    folder_id = int(call_data[1])
    await FolderManager.delete_folder(folder_id=folder_id)
    
    
    new_folder_id = int(call_data[2])
    if new_folder_id != 0:
        folder_data = await FolderManager.get_folder(folder_id=new_folder_id)
        parent_folder_id = folder_data.parent_folder_id
    else:
        parent_folder_id = 0
    
    page = int(call_data[3])
    
    if new_folder_id == 0:
        folder_name = "<b>Менеджер паролей 🐻</b>"
    else:
        folder_data = await FolderManager.get_folder(folder_id=folder_id)
        folder_name = folder_data.folder_name
    
    await call.message.edit_text(text=f"<b>🗂 {folder_name}</b>", reply_markup=await get_menu_kb(folder_id=new_folder_id,
                                                                                                 parent_folder_id=parent_folder_id,
                                                                                                 page=page))

@router.callback_query(F.data.startswith("delete_password"))
async def delete_password(call: CallbackQuery):
    password_id = call.data.split("|")[1]
    page = call.data.split("|")[2]
    password_data = await PasswordManager.get_password(password_id=int(password_id))
    
    folder_id = password_data.folder_id
    
    if folder_id != 0:
        folder_data = await FolderManager.get_folder(folder_id=folder_id)
        parent_folder_id = folder_data.parent_folder_id
        folder_name = folder_data.folder_name
    else:
        parent_folder_id = 0
        folder_name = "<b>Менеджер паролей by @x1x</b>"
    
    
    
    await PasswordManager.delete_password(password_id=password_id)
    
    await call.message.edit_text(text=f"<b>🗂 {folder_name}</b>", reply_markup=await get_menu_kb(folder_id=folder_id,
                                                                                                 parent_folder_id=parent_folder_id,
                                                                                                 page=int(page)))
    
class ImportDatabaseStates(StatesGroup):
    get_database = State()
    
@router.callback_query(F.data == "import_database")
async def import_database_call(call:CallbackQuery, state:FSMContext):
    msg_obj = await call.message.edit_text(text="Отправьте файл базы данных:", reply_markup=await get_back_kb(0, 0))
    await state.set_state(ImportDatabaseStates.get_database)
    await state.update_data(msg_obj=msg_obj)
    
@router.message(ImportDatabaseStates.get_database)
async def import_database_message(msg:Message, state:FSMContext, bot:Bot):
    state_data = await state.get_data()
    
    if msg.document == None:
        await msg.delete()
        await state_data["msg_obj"].message.edit_text(text="Вы не отправили файл, отправьте файл базы данных либо отмените операцию:", 
                                                      reply_markup=await get_back_kb(0, 0))
        await state.set_state(ImportDatabaseStates.get_database)
        return
    else:
        file = await bot.get_file(msg.document.file_id)
        file_path = file.file_path
        await bot.download_file(file_path, "storage.db")
        await msg.delete()
        msg_obj = await msg.answer("Обработка БД...")
        import_folders_counter, import_passwords_counter = await import_db("storage.db")
        os.remove("storage.db")
        await msg_obj.delete()
        await state_data["msg_obj"].edit_text(text=f"Было импортированно:\n    Папок - {import_folders_counter}\n    Паролей - {import_passwords_counter}", 
                                                      reply_markup=await get_back_kb(0, 0))
        await state.clear()
        
@router.callback_query(F.data == "export_database")
async def export_database(call: CallbackQuery):
    await call.answer()
    await call.message.answer_document(document=FSInputFile("database\\storage.db"), reply_markup=await get_export_database_kb())
    
@router.callback_query(F.data == "delete_msg")
async def delete_message_call(call: CallbackQuery):
    await call.message.delete()
