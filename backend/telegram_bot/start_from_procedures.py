import datetime as dt
from datacenter.models import (
    Service
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
)
from .common import get_salons_and_times


# ----------------------Старт первой линии действий----------------------
def list_services(update: Update, context: CallbackContext):
    # Отображаем список процедур
    query = update.callback_query
    query.answer()
    services = Service.objects.all()
    keyboard = [
        [
            InlineKeyboardButton(
                f"{service.title} - {service.price} руб.",
                callback_data=f"service_{service.id}",
            )
        ] for service in services
    ]
    keyboard.append([InlineKeyboardButton("Назад", callback_data="start")])
    query.edit_message_text(
        text="Выберите услугу:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


def show_cant_add(update):
    keyboard = [[InlineKeyboardButton("Назад", callback_data="start")]]
    update.callback_query.edit_message_text(
        text="К сожалению, запись невозможна",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def list_salons_by_procedure(update: Update, context: CallbackContext):
    service_id = int(context.user_data["service_id"])
    service = Service.objects.get(pk=service_id)
    context.user_data["service"] = service
    date = dt.date.today()
    (
        context.user_data["salons_dates_times"],
        context.user_data["salons_address"],
    ) = get_salons_and_times(service=service, date=date)
    if not context.user_data["salons_dates_times"]:
        show_cant_add(update)
        return None
    salons_dates_times = context.user_data["salons_dates_times"]

    context.user_data["all_salons"] = [
        key for key in salons_dates_times.keys()
    ]
    all_salons = context.user_data["all_salons"]
    context.user_data["curr_salon_index"] = 0
    context.user_data["curr_salon"] = all_salons[
        context.user_data["curr_salon_index"]
    ]
    curr_salon_index = context.user_data["curr_salon_index"]
    context.user_data["all_dates_for_salon"] = [
        key for key in salons_dates_times[all_salons[curr_salon_index]].keys()
    ]
    context.user_data["all_dates_for_salon"].sort()
    context.user_data["curr_date_index"] = 0

    context.user_data["curr_date"] = context.user_data["all_dates_for_salon"][
        context.user_data["curr_date_index"]
    ]
    list_salons_by_procedure_time_by_time(update, context)
    # context.user_data["all_specs"] = [key for key in SAT_by_spec.keys()]


def service_update_date_up(update: Update, context: CallbackContext):
    context.user_data["curr_date_index"] += 1
    refresh_context_date_change(update, context)


def service_update_date_down(update: Update, context: CallbackContext):
    context.user_data["curr_date_index"] -= 1
    refresh_context_date_change(update, context)


def refresh_context_date_change(update: Update, context: CallbackContext):
    context.user_data["curr_date"] = context.user_data["all_dates_for_salon"][
        context.user_data["curr_date_index"]
    ]
    list_salons_by_procedure_time_by_time(update, context)


def refresh_context_salon_change(update: Update, context: CallbackContext):
    context.user_data["curr_salon"] = context.user_data["all_salons"][
        context.user_data["curr_salon_index"]
    ]
    salons_dates_times = context.user_data["salons_dates_times"]
    all_salons = context.user_data["all_salons"]
    curr_salon_index = context.user_data["curr_salon_index"]
    context.user_data["all_dates_for_salon"] = [
        key for key in salons_dates_times[all_salons[curr_salon_index]].keys()
    ]
    context.user_data["all_dates_for_salon"].sort()
    context.user_data["curr_date_index"] = 0

    context.user_data["curr_date"] = context.user_data["all_dates_for_salon"][
        context.user_data["curr_date_index"]
    ]
    list_salons_by_procedure_time_by_time(update, context)


def service_update_salon_up(update: Update, context: CallbackContext):
    context.user_data["curr_salon_index"] += 1
    refresh_context_salon_change(update, context)


def service_update_salon_down(update: Update, context: CallbackContext):
    context.user_data["curr_salon_index"] -= 1
    refresh_context_salon_change(update, context)


def list_salons_by_procedure_time_by_time(
        update: Update, context: CallbackContext):
    service = context.user_data["service"]
    work_date = context.user_data["curr_date"]
    salon_title = context.user_data["curr_salon"]
    salon_address = context.user_data["salons_address"][salon_title]
    time_slots = context.user_data[
        "salons_dates_times"][salon_title][work_date]
    keyboard = [
        [InlineKeyboardButton(
                time_slot, callback_data=f"time_slot_{time_slot}"
        ) for time_slot in time_slots]
    ]
    key_next_date = InlineKeyboardButton(
        "Следующая дата", callback_data="date_up_")
    key_prev_date = InlineKeyboardButton(
        "Прошлая дата", callback_data="date_down_")
    key_next_salon = InlineKeyboardButton(
        "Следующий адрес", callback_data="salon_up_")
    key_prev_salon = InlineKeyboardButton(
        "Прошлый адрес", callback_data="salon_down_")
    if len(context.user_data["all_dates_for_salon"]) == 1:
        None
    elif context.user_data["curr_date_index"] == 0:
        keyboard.append([
            key_next_date
        ])
    elif context.user_data["curr_date_index"] == len(
            context.user_data["all_dates_for_salon"]) - 1:
        keyboard.append([
            key_prev_date
        ])
    else:
        keyboard.append([
            key_prev_date,
            key_next_date
        ])
    if len(context.user_data["all_salons"]) == 1:
        None
    elif context.user_data["curr_salon_index"] == 0:
        keyboard.append([
            key_next_salon,
        ])
    elif context.user_data["curr_salon_index"] == len(
            context.user_data["all_salons"]) - 1:
        keyboard.append([
            key_prev_salon,
        ])
    else:
        keyboard.append([
            key_prev_salon,
            key_next_salon
        ])
    keyboard.append([InlineKeyboardButton(
        "Назад", callback_data="back_to_serv_")])
    all_salons = ''.join([salon for salon in context.user_data["all_salons"]])
    all_dates_for_salon = ''.join(
        [date for date in context.user_data["all_dates_for_salon"]])
    update.callback_query.edit_message_text(
        text=f"""Для выбранной услуги '{service}' у нас
Вы можете выбрать свободный день, салон и время:
Дни для записи в салон '{salon_title}':
{all_dates_for_salon}
Запись для данной процедуры доступна в следующих салонах:
{all_salons}\n
Текущий выбор:
\n{work_date}\n{salon_title}\n{salon_address}\n""",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
