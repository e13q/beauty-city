from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    Updater
)
from .db_querrys import (
    get_all_salons,
    get_salon,
    get_services_by_salon,
    get_service,
    get_salons_and_times
)


# ----------------------Старт второй линии действий----------------------
def list_salons(update: Update, context: CallbackContext):
    context.user_data["salon_id"] = None
    context.user_data["specialist_id"] = None
    query = update.callback_query
    query.answer()
    salons = get_all_salons()
    keyboard = [
        [
            InlineKeyboardButton(
                f"{salon.title} - {salon.address}",
                callback_data=f"salon_id_{salon.id}",
            )
        ] for salon in salons
    ]
    keyboard.append([InlineKeyboardButton("Назад", callback_data="start")])
    query.edit_message_text(
        text="Выберите салон:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


def show_cant_add(update, context):
    context.user_data["salon_id"] = None
    context.user_data["specialist_id"] = None
    keyboard = [[InlineKeyboardButton("Назад", callback_data="start")]]
    update.callback_query.edit_message_text(
        text="К сожалению, запись невозможна",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def list_services_by_salon(update: Update, context: CallbackContext):
    query = update.callback_query
    if not context.user_data.get("salon_id"):
        show_cant_add(update, context)
        return None
    salon_id = int(context.user_data["salon_id"])
    salon = get_salon(salon_id)
    context.user_data["salon"] = salon
    context.user_data["services"] = get_services_by_salon(salon_id)
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
        [InlineKeyboardButton("Назад", callback_data="list_salons")])
    query.edit_message_text(
        text="Выберите процедуру:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


def list_salon_free_time_slots(update: Update, context: CallbackContext):
    service_id = int(context.user_data["service_id"])
    service = get_service(service_id)
    salon = context.user_data["salon"]
    context.user_data["service"] = service
    context.user_data["salon_dates_times"], _ = get_salons_and_times(
        service=service, salon=salon
    )
    if not context.user_data["salon_dates_times"]:
        show_cant_add(update, context)
        return None
    salon_dates_times = context.user_data["salon_dates_times"]
    context.user_data["all_dates_for_salon"] = [
        key for key in salon_dates_times[salon.title].keys()
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


def list_salons_by_service_time_by_time(
        update: Update, context: CallbackContext):
    service = context.user_data["service"]
    work_date = context.user_data["curr_date"]
    salon_title = context.user_data["salon"].title
    salon_address = context.user_data["salon"].address
    time_slots = context.user_data[
        "salon_dates_times"][salon_title][work_date]
    keyboard = [
        [InlineKeyboardButton(
                time_slot, callback_data=f"time_slot_{time_slot}"
        ) for time_slot in time_slots]
    ]
    key_next_date = InlineKeyboardButton(
        "Следующая дата", callback_data="date_sa_up_")
    key_prev_date = InlineKeyboardButton(
        "Прошлая дата", callback_data="date_sa_down_")
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
    keyboard.append([InlineKeyboardButton(
        "Назад", callback_data="list_services_by_salon")])
    all_dates_for_salon = ''.join(
        [date for date in context.user_data["all_dates_for_salon"]])
    update.callback_query.edit_message_text(
        text=f"""Для выбранной услуги '{service}' у нас
Вы можете выбрать свободный день и время:
Дни для записи в салон '{salon_title}':
{all_dates_for_salon}
Текущий выбор:
\n{work_date}\n{salon_title}\n{salon_address}\n""",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def handlers_register(updater: Updater):
    updater.dispatcher.add_handler(
        CallbackQueryHandler(list_salons, pattern="^list_salons$")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            list_services_by_salon, pattern="^list_services_by_salon$")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            service_update_date_up,
            pattern="^date_sa_up_"
        )
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            service_update_date_down,
            pattern="^date_sa_down_"
        )
    )
    return updater.dispatcher
