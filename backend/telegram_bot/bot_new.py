import datetime as dt
import logging

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
from django.utils import timezone
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Updater,
)

from .common import get_salons_and_times

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
            "Привет! Пожалуйста, выберите услугу, салон или мастера",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        update.message.reply_text(
            "Привет! Пожалуйста, выберите услугу, салон или мастера",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


def list_services(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    services = Service.objects.all()
    keyboard = [
        [
            InlineKeyboardButton(
                f"{service.title} - {service.price} руб.",
                callback_data=f"service_{service.id}",
            )
            for service in services
        ]
    ]
    keyboard.append([InlineKeyboardButton("Назад", callback_data="start")])
    query.edit_message_text(
        text="Выберите услугу:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


def service_handler(update, context):
    query = update.callback_query
    query.answer()
    service_id = query.data.split("_")[-1]
    context.user_data["service_id"] = service_id
    if context.user_data.get("specialist_id"):
        list_salons_free_time_slots(update, context)


def list_salons(update, context):
    query = update.callback_query
    query.answer()
    salons = Salon.objects.all()
    keyboard = [
        [
            InlineKeyboardButton(
                f"{salon.title} - {salon.address}",
                callback_data=f"salon_{salon.id}",
            )
            for salon in salons
        ]
    ]
    keyboard.append([InlineKeyboardButton("Назад", callback_data="start")])
    query.edit_message_text(
        text="Выберите салон:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


def salon_handler(update, context):
    query = update.callback_query
    query.answer()
    salon_id = query.data.split("_")[-1]
    context.user_data["salon_id"] = salon_id
    list_services(update, context)


def list_specialists(update, context):
    query = update.callback_query
    query.answer()
    specialists = Specialist.objects.all()
    keyboard = [
        [
            InlineKeyboardButton(
                f"{specialist.full_name}",
                callback_data=f"specialist_{specialist.id}",
            )
            for specialist in specialists
        ]
    ]
    keyboard.append([InlineKeyboardButton("Назад", callback_data="start")])
    query.edit_message_text(
        text=f"Выберите мастера:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def specialists_handler(update, context):
    query = update.callback_query
    query.answer()
    specialist_id = query.data.split("_")[-1]
    context.user_data["specialist_id"] = specialist_id
    list_services(update, context)


def list_salons_free_time_slots(update, context):
    query = update.callback_query
    query.answer()
    chat_id = update.chat.id
    specialist_id = int(context.user_data["specialist_id"])
    specialist = Specialist.objects.get(pk=specialist_id)
    service_id = int(context.user_data["service_id"])
    service = Service.objects.get(pk=service_id)
    date = dt.date.today()
    salons_and_times = get_salons_and_times(specialist, service, date)
    for salon_times in salons_and_times:
        work_date = salon_times["date"]
        salon_title = salon_times["salon_title"]
        salon_address = salon_times["salon_address"]
        time_slots = salon_times["free_times"]
        keyboard = [
            [
                InlineKeyboardButton(
                    time_slot, callback_data=f"time_slot_{time_slot}"
                )
                for time_slot in time_slots
            ]
        ]
        keyboard.append([InlineKeyboardButton("Назад", callback_data="start")])
        context.bot.send_message(chat_id,
            text=f"{work_date}\n{salon_title}\n{salon_address}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


def main():
    updater = Updater(settings.BOT_TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(
        CallbackQueryHandler(start, pattern="^start$")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(list_services, pattern="^list_services$")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(service_handler, pattern="^service_")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(list_salons, pattern="^list_salons$")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(salon_handler, pattern="^salon_")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(list_specialists, pattern="^list_specialists$")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(specialists_handler, pattern="^specialist_")
    )

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
