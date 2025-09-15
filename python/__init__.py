"""
Python версия бота Clash of Clans.

Основной модуль, содержащий всю необходимую функциональность
для работы бота, портированную с Java версии.

Быстрый старт:
    from python.bot import setup_handlers
    
    # В main.py
    application = Application.builder().token(TOKEN).build()
    handlers = setup_handlers(application, bot_instance, message_generator)
    application.run_polling()
"""

from .bot import (
    BotHandlers,
    MessageHandler,
    CallbackHandler,
    setup_handlers,
    validate_clan_tag,
    validate_player_tag,
    process_tag,
    UserState,
    WarSort,
    Keyboards
)

__version__ = "1.0.0"
__author__ = "ClashBot Development Team"

__all__ = [
    'BotHandlers',
    'MessageHandler',
    'CallbackHandler',
    'setup_handlers', 
    'validate_clan_tag',
    'validate_player_tag',
    'process_tag',
    'UserState',
    'WarSort',
    'Keyboards'
]