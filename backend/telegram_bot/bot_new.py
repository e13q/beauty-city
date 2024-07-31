import datetime as dt
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from datacenter.models import (
    Appointment,
)
from django.conf import settings
from telegram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

from .common_handler_functions import (
    salon_handler,
    service_handler,
    specialists_handler,
    time_handler,
    get_phone_number
)
from .db_querrys import check_client, create_client
from .start_from_salons import handlers_register as st_salons_handlers
from .start_from_service import handlers_register as st_service_handlers
from .start_from_specialists import (
    handlers_register as st_specialists_handlers,
)
from .common_handler_functions import (
    service_handler, salon_handler, specialists_handler, get_phone_number, time_handler)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


URL_AGREEMENT = "https://disk.yandex.ru/i/8a4x4M9KB8A3qw"


def reg_user(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user = context.user_data["user_initial"]
    if not check_client(user["id"]):
        create_client(
            user["id"],
            user["first_name"],
            user["last_name"],
            user["username"],
        )
    context.user_data["client_id"] = user["id"]
    start(update, context)


def reg_user_request(update: Update, context: CallbackContext):
    context.user_data["user_initial"] = update.message.from_user
    if not check_client(context.user_data["user_initial"]["id"]):
        keyboard = [
            [InlineKeyboardButton("Согласен", callback_data="register_user")]
        ]
        update.message.reply_text(
            f"""
    Добро пожаловать в бота сети салонов Beauty City\\!
    Для продолжения работы с ботом нам потребуется Ваше согласие на обработку персональных данных\\.
    С документом Вы можете ознакомиться [по ссылке]({URL_AGREEMENT})\\.
    Нажимая "Согласен" \\- Вы даёте своё согласие и можете продолжать пользоваться ботом\\.
    """,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        start()


def start(update: Update, context: CallbackContext):
    context.user_data["client_id"] = update.effective_chat.id
    if not check_client(context.user_data["client_id"]):
        reg_user_request(update, context)
        return
    keyboard = [
        [
            InlineKeyboardButton(
                "Список процедур", callback_data="list_services"
            )
        ],
        [InlineKeyboardButton("Список салонов", callback_data="list_salons")],
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
            "Выберите услугу, салон или мастера",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        update.message.reply_text(
            "Здравствуйте! Выберите услугу, салон или мастера",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


def schedule_notifications():
    bot = Bot(token=settings.BOT_TOKEN)
    hundred_days_ago = dt.date.today() - dt.timedelta(days=100)
    apts_1000_days_past = Appointment.objects.filter(
        date__exact=hundred_days_ago
    )
    for apt in apts_1000_days_past:
        client = apt.client
        bot.send_message(
            chat_id=client.id_tg, text="100 дней прошло, давай опять в салон"
        )


def main():
    updater = Updater(settings.BOT_TOKEN, use_context=True)
    scheduler = BackgroundScheduler()
    scheduler.add_job(schedule_notifications, "cron", hour=12)
    scheduler.start()
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(
        CallbackQueryHandler(start, pattern="^start$")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(reg_user, pattern="^register_user$")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(service_handler, pattern="^service_id_")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(salon_handler, pattern="^salon_id_")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(specialists_handler, pattern="^specialist_id_")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(time_handler, pattern="^time_slot_")
    )
    updater.dispatcher = st_service_handlers(updater)
    updater.dispatcher = st_salons_handlers(updater)
    updater.dispatcher = st_specialists_handlers(updater)    
    updater.dispatcher.add_handler(MessageHandler(Filters.contact & ~Filters.command, get_phone_number))
    updater.start_polling()
    updater.idle()
