from aiogram import Router
from handlers.start_handler import router as start_router
from handlers.managment_handler import router as managment_router
from handlers.view_handler import router as view_router

router = Router()
router.include_routers(start_router, 
                       managment_router, 
                       view_router)