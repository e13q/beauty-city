import logging
from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Updater,
    CallbackContext
)

from .start_from_service import handlers_register as st_service_handlers
from .start_from_salons import handlers_register as st_salons_handlers
from .start_from_specialists import handlers_register as st_specialists_handlers
from .common_handler_functions import (
    service_handler, salon_handler, specialists_handler)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton(
                "Список процедур", callback_data="list_services"
            )
        ],
        [
            InlineKeyboardButton(
                "Список салонов", callback_data="list_salons"
            )
        ],
        [
            InlineKeyboardButton(
                "Записаться к мастеру", callback_data="list_specialists"
            )
        ],
    ]
    query = update.callback_query
    if query:
        query.answer()
        query.edit_message_text(
            "Привет! Пожалуйста, выберите услугу, салон или мастера",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        update.message.reply_text(
            "Привет! Пожалуйста, выберите услугу, салон или мастера",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


def main():
    updater = Updater(settings.BOT_TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(
        CallbackQueryHandler(start, pattern="^start$")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            service_handler,
            pattern="^service_id_"
        )
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            salon_handler,
            pattern="^salon_id_"
        )
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            specialists_handler,
            pattern="^specialist_id_"
        )
    )
    updater.dispatcher = st_service_handlers(updater)
    updater.dispatcher = st_salons_handlers(updater)
    updater.dispatcher = st_specialists_handlers(updater)
    updater.start_polling()
    updater.idle()
