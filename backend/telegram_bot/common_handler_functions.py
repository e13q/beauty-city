from telegram.ext import (
    CallbackContext
)
from telegram import Update
# import start_from_salons
from .start_from_service import list_salons_by_service
from .start_from_salons import (
    list_services_by_salon,
    list_salon_free_time_slots
)
from .start_from_specialists import list_salons_free_time_slots
from .start_from_specialists import list_services_by_specialist


def service_handler(update: Update, context: CallbackContext):
    # По выбранной процедуре предоставляем выбор салонов
    query = update.callback_query
    query.answer()
    service_id = query.data.split("_")[-1]
    context.user_data["service_id"] = service_id
    if context.user_data.get("specialist_id"):
        list_salons_free_time_slots(update, context)
    elif context.user_data.get("salon_id"):
        list_salon_free_time_slots(update, context)
    elif context:
        list_salons_by_service(update, context)


def salon_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    salon_id = query.data.split("_")[-1]
    context.user_data["salon_id"] = salon_id
    list_services_by_salon(update, context)
    # list_services(update, context)


def specialists_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    specialist_id = query.data.split("_")[-1]
    context.user_data["specialist_id"] = specialist_id
    list_services_by_specialist(update, context)


def time_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    time_str = query.data.split("_")[-1]
    context.user_data["time_str"] = time_str
    #check_appointment(
    #    context.user_data["curr_salon"],
    #    context.user_data["curr_date"],
    #    context.user_data["time_str"],
    #    context.user_data["service"],
    #    context.user_data.get("specialist")
    #)
    #get_phone_number(update, context)