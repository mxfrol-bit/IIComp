import asyncio
import logging
import os

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.handlers import admin, billing, factory, start
from app.web import app as web_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


async def run_bot() -> None:
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=None),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        start.router,
        admin.router,
        factory.router,
        billing.router,
    )

    log.info("AI Content Factory v8 starting. Image model: %s; video model: %s; prompt provider: %s", settings.fal_model, settings.video_model_i2v, settings.prompt_provider)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def run_web() -> None:
    port = int(os.getenv("PORT", "8080"))
    config = uvicorn.Config(web_app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    log.info("Web admin/Mini App starting on port %s", port)
    await server.serve()


async def main() -> None:
    tasks = [asyncio.create_task(run_bot())]
    if settings.web_enabled:
        tasks.append(asyncio.create_task(run_web()))
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
