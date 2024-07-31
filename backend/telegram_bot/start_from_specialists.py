from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    Updater
)

from .db_querrys import (
    get_all_specialists,
    get_salons_and_times,
    get_services_by_specialist,
    get_service,
    get_specialist
)


# ----------------------Старт третьей линии действий----------------------
def list_specialists(update: Update, context: CallbackContext):
    context.user_data["salon_id"] = None
    context.user_data["specialist_id"] = None
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


def show_cant_add(update):
    keyboard = [[InlineKeyboardButton("Назад", callback_data="start")]]
    update.callback_query.edit_message_text(
        text="К сожалению, запись невозможна",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def list_services_by_specialist(update: Update, context: CallbackContext):
    query = update.callback_query
    if not context.user_data.get("specialist_id"):
        show_cant_add(update, context)
        return None
    specialist_id = int(context.user_data["specialist_id"])
    context.user_data["specialist"] = get_specialist(specialist_id)
    context.user_data["services"] = get_services_by_specialist(specialist_id)
    if not context.user_data["services"]:
        show_cant_add(update, context)
        return None
    context.user_data["services"]
    keyboard = [
        [
            InlineKeyboardButton(
                f"{service.get('title')} - {service.get('price')} руб.",
                callback_data=f"service_id_{service.get('id')}",
            )
        ] for service in context.user_data["services"]
    ]
    keyboard.append(
        [InlineKeyboardButton("Назад", callback_data="list_specialists")])
    query.edit_message_text(
        text="Выберите процедуру:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


def list_salons_free_time_slots(update: Update, context: CallbackContext):
    service_id = int(context.user_data["service_id"])
    service = get_service(service_id)
    context.user_data["service"] = service
    (
        context.user_data["salons_dates_times"],
        context.user_data["salons_address"],
    ) = get_salons_and_times(service=service)
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
    list_salons_by_service_time_by_time(update, context)
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
    list_salons_by_service_time_by_time(update, context)


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
    list_salons_by_service_time_by_time(update, context)


def service_update_salon_up(update: Update, context: CallbackContext):
    context.user_data["curr_salon_index"] += 1
    refresh_context_salon_change(update, context)


def service_update_salon_down(update: Update, context: CallbackContext):
    context.user_data["curr_salon_index"] -= 1
    refresh_context_salon_change(update, context)


def list_salons_by_service_time_by_time(
        update: Update, context: CallbackContext):
    service = context.user_data["service"]
    work_date = context.user_data["curr_date"]
    salon_title = context.user_data["curr_salon"]
    salon_address = context.user_data["salons_address"][salon_title]
    time_slots = context.user_data[
        "salons_dates_times"][salon_title][work_date]
    keyboard = [[InlineKeyboardButton(
        time_slot, callback_data=f"time_slot_{time_slot}",
    )] for time_slot in time_slots]
    key_next_date = InlineKeyboardButton(
        "Следующая дата", callback_data="date_sp_up_")
    key_prev_date = InlineKeyboardButton(
        "Прошлая дата", callback_data="date_sp_down_")
    key_next_salon = InlineKeyboardButton(
        "Следующий адрес", callback_data="salon_sp_up_")
    key_prev_salon = InlineKeyboardButton(
        "Прошлый адрес", callback_data="salon_sp_down_")
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
        "Назад", callback_data="list_services_by_specialist")])
    all_salons = ''.join([salon for salon in context.user_data["all_salons"]])
    all_dates_for_salon = ''.join(
        [date for date in context.user_data["all_dates_for_salon"]])
    update.callback_query.edit_message_text(
        text=f"""Для выбранной услуги '{service}' у
{context.user_data["specialist"].full_name}
Вы можете выбрать свободный день, салон и время:
Дни для записи в салон '{salon_title}':
{all_dates_for_salon}
Запись для данной процедуры доступна в следующих салонах:
{all_salons}\n
Текущий выбор:
\n{work_date}\n{salon_title}\n{salon_address}\n""",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def handlers_register(updater: Updater):
    updater.dispatcher.add_handler(
        CallbackQueryHandler(list_specialists, pattern="^list_specialists$")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            list_services_by_specialist,
            pattern="^list_services_by_specialist$"
        )
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            service_update_date_up,
            pattern="^date_sp_up_"
        )
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            service_update_date_down,
            pattern="^date_sp_down_"
        )
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            service_update_salon_up,
            pattern="^salon_sp_up_"
        )
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            service_update_salon_down,
            pattern="^salon_sp_down_"
        )
    )
    return updater.dispatcher
