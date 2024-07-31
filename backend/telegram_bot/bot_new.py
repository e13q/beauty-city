import datetime as dt
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from datacenter.models import (
    Appointment,
    Client,
    Order,
    Salon,
    Service,
    Specialist,
    SpecialistWorkDayInSalon,
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
)
from .db_querrys import check_client, create_client, is_time_slot_busy
from .start_from_salons import handlers_register as st_salons_handlers
from .start_from_service import handlers_register as st_service_handlers
from .start_from_specialists import (
    handlers_register as st_specialists_handlers,
)

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


def make_appointment(update, context):
    query = update.callback_query
    query.answer()
    client_id = context.user_data["client_id"]
    client = Client.objects.get(id_tg__exact=client_id)
    chosen_date = context.user_data["curr_date"]
    date = dt.datetime.strptime(chosen_date, "%Y-%m-%d").date()

    salon_id = context.user_data["salon_id"]
    curr_salon = context.user_data["curr_salon"]
    if salon_id:
        salon = context.user_data["salon"]
    else:
        salon = Salon.objects.get(title__exact=curr_salon)

    chosen_time = query.data.split("_")[-1]
    start_at = dt.datetime.strptime(chosen_time, "%H:%M").time()
    service = context.user_data["service"]
    service_duration = dt.timedelta(minutes=service.duration)
    service_time = dt.datetime.combine(date, start_at)
    specialist_id = context.user_data["specialist_id"]
    if specialist_id:
        specialist = context.user_data["specialist"]
    else:
        specialist_duties = SpecialistWorkDayInSalon.objects.filter(
            services=service, workday=date, salon=salon
        )
        for duty in specialist_duties:
            duty_start_time = dt.datetime.combine(duty.workday, duty.start_at)
            duty_end_time = dt.datetime.combine(duty.workday, duty.end_at)
            if (
                duty_start_time
                <= service_time
                <= duty_end_time - service_duration
            ):
                specialist = duty.specialist
                break

    appointments = Appointment.objects.filter(
        specialist=specialist,
        service=service,
        date=date,
        salon=salon
    ).exclude(status__in=["discard", "ended"])
    if is_time_slot_busy(service_time, appointments, service_duration):
        keyboard = [[InlineKeyboardButton("Главное меню", callback_data="start")]]
        update.callback_query.edit_message_text(
            text="К сожалению, это время уже занято",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    order = Order.objects.create(client=client, status="waiting")
    appointment = Appointment.objects.create(
        status="access",
        date=date,
        salon=salon,
        client=client,
        specialist=specialist,
        service=service,
        start_at=start_at,
        order=order,
    )

    keyboard = [[InlineKeyboardButton("Главное меню", callback_data="start")]]
    update.callback_query.edit_message_text(
        text="Вы записаны",
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
        CallbackQueryHandler(make_appointment, pattern="^time_slot_")
    )
    updater.dispatcher = st_service_handlers(updater)
    updater.dispatcher = st_salons_handlers(updater)
    updater.dispatcher = st_specialists_handlers(updater)
    updater.start_polling()
    updater.idle()
