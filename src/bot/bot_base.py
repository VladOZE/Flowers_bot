import asyncio
import sys
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from src.config.bot_config import settings
from handlers import router_handler
from functions import set_commands
from callbacks import router_callback


dp = Dispatcher()
bot = Bot(settings.GET_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def start_bot() -> None:
    dp.include_routers(router_handler, router_callback)
    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(start_bot())