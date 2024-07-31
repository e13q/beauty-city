from telegram.ext import (
    CallbackContext
)
import datetime as dt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
# import start_from_salons
from .start_from_service import list_salons_by_service
from .start_from_salons import (
    list_services_by_salon,
    list_salon_free_time_slots
)
from .db_querrys import (
    create_client,
    check_and_add_phone_number,
    get_client,
    get_salon_by_title,
    create_appointment,
    create_order,
    get_appointments_by_filter,
    get_specialist_duties,
    is_time_slot_busy
)
from .start_from_specialists import list_salons_free_time_slots
from .start_from_specialists import list_services_by_specialist
import pdb

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


def get_phone_number(update: Update, context: CallbackContext):
    if context.user_data.get('get_number_in_progress'):
        user = update.message.contact
        if update.message.contact:
            ReplyKeyboardRemove(True)
            context.user_data['get_number_in_progress'] = False
            if user.user_id != context.user_data['client_id']:
                create_client(user.user_id, user.first_name, user.last_name)
                context.user_data['client_id'] = user.user_id    
            check_and_add_phone_number(user.user_id, user.phone_number)
            make_appointment(update, context)
            #check_and_create_appointment(update, context)


def time_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    time_str = query.data.split("_")[-1]
    context.user_data["time_str"] = time_str
    context.user_data['get_number_in_progress'] = True
    keyboard = [
        [
            KeyboardButton(
                "Поделиться номером", request_contact=True,
            )
        ]
    ]
    query.edit_message_text(
        """Вы почти записались!""",
        reply_markup=None
    )
    update.callback_query.message.reply_text(
        """Укажите Ваш номер телефона с помощью нажатия на кнопку снизу,
    либо предоставьте контакт клиента""", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True))
    
    #check_appointment(
    #    context.user_data["curr_salon"],
    #    context.user_data["curr_date"],
    #    context.user_data["time_str"],
    #    context.user_data["service"],
    #    context.user_data.get("specialist")
    #)
   # get_phone_number(update, context)

def make_appointment(update: Update, context: CallbackContext):
    client_id = context.user_data["client_id"]
    client = get_client(client_id)
    chosen_date = context.user_data["curr_date"]
    date = dt.datetime.strptime(chosen_date, "%Y-%m-%d").date()

    salon_id = context.user_data["salon_id"]
    curr_salon = context.user_data["curr_salon"]
    if salon_id:
        salon = context.user_data["salon"]
    else:
        salon = get_salon_by_title(curr_salon)

    chosen_time = context.user_data["time_str"] 
    start_at = dt.datetime.strptime(chosen_time, "%H:%M").time()
    service = context.user_data["service"]
    service_duration = dt.timedelta(minutes=service.duration)
    service_time = dt.datetime.combine(date, start_at)
    specialist_id = context.user_data["specialist_id"]
    if specialist_id:
        specialist = context.user_data["specialist"]
    else:
        specialist_duties = get_specialist_duties(service, date, salon)
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

    appointments = get_appointments_by_filter(
        specialist,
        service,
        date,
        salon)
    if is_time_slot_busy(service_time, appointments, service_duration):
        keyboard = [[InlineKeyboardButton("Главное меню", callback_data="start")]]
        update.message.reply_text(
            text="К сожалению, это время уже занято",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    order = create_order(client)
    appointment = create_appointment(
        date=date,
        salon=salon,
        client=client,
        specialist=specialist,
        service=service,
        start_at=start_at,
        order=order,
    )
    keyboard = [[InlineKeyboardButton("Главное меню", callback_data="start")]]
    update.message.reply_text(
        text="Вы записаны",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )