from aiogram import Router
from .menu import router as menu_router
from .order import router as order_router
from .search import router as search_router

router = Router()
router.include_router(search_router)   # search before menu (catches search_prod before prod:)
router.include_router(menu_router)
router.include_router(order_router)
