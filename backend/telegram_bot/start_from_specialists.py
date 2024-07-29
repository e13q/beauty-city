import datetime as dt
from datacenter.models import (
    Service
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext
)

from .db_querrys import (
    get_all_specialists, get_specialist, get_salons_and_times)


# ----------------------Старт третьей линии действий----------------------
def list_specialists(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    specialists = get_all_specialists()
    keyboard = [
        [
            InlineKeyboardButton(
                f"{specialist.full_name}",
                callback_data=f"specialist_id_{specialist.id}",
            )
        ] for specialist in specialists
    ]
    keyboard.append([InlineKeyboardButton("Назад", callback_data="start")])
    query.edit_message_text(
        text="Выберите мастера:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def list_salons_free_time_slots(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    chat_id = update.chat.id
    specialist_id = int(context.user_data["specialist_id"])
    specialist = get_specialist(specialist_id)
    service_id = int(context.user_data["service_id"])
    service = Service.objects.get(pk=service_id)
    date = dt.date.today()
    salons_and_times = get_salons_and_times(
        specialist, service, date
    )
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
            ] for time_slot in time_slots
        ]
        keyboard.append([InlineKeyboardButton("Назад", callback_data="start")])
        context.bot.send_message(
            chat_id,
            text=f"{work_date}\n{salon_title}\n{salon_address}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
