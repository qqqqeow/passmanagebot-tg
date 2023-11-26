from aiogram import Router, F
from aiogram.types import Message
from keyboards.menu_kb import get_menu_kb

router = Router()

@router.message(F.text == "/start")
async def start_msg(msg: Message):
    await msg.answer("<b>Менеджер паролей by @x1x</b>", reply_markup=await get_menu_kb(folder_id=0, 
                                                             parent_folder_id=0, 
                                                             page=1))