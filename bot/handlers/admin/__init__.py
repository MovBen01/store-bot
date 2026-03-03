from aiogram import Router
from .panel import router as panel_router

router = Router()
router.include_router(panel_router)
