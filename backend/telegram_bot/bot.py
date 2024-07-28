import logging
import os
import django
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler
from django.utils import timezone
from datetime import datetime, timedelta

from datacenter.models import Client, Salon, Service, Appointment, Order
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_salon.settings')
django.setup()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

CHOOSE_DATE, CHOOSE_TIME, CONFIRM_ORDER = range(3)

def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    if not Client.objects.filter(id_tg=chat_id).exists():
        Client.objects.create(id_tg=chat_id, full_name="Unknown", phone_number=None)
    update.message.reply_text('Привет! Пожалуйста, выберите салон или услугу.', reply_markup=main_menu_keyboard())
    return ConversationHandler.END

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton('Список салонов', callback_data='list_salons')],
        [InlineKeyboardButton('Список процедур', callback_data='list_services')],
        [InlineKeyboardButton('Связаться с админом', callback_data='contact_admin')]
    ]
    return InlineKeyboardMarkup(keyboard)

def list_salons(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    salons = Salon.objects.all()
    keyboard = [[InlineKeyboardButton(f"{salon.title} - {salon.address}", callback_data=f'salon_{salon.id}') for salon in salons]]
    keyboard.append([InlineKeyboardButton('Назад', callback_data='main_menu')])
    query.edit_message_text(text="Выберите салон:", reply_markup=InlineKeyboardMarkup(keyboard))

def list_services(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    services = Service.objects.all()
    keyboard = [[InlineKeyboardButton(f"{service.title} - {service.price} руб.", callback_data=f'service_{service.id}') for service in services]]
    keyboard.append([InlineKeyboardButton('Назад', callback_data='main_menu')])
    query.edit_message_text(text="Выберите услугу:", reply_markup=InlineKeyboardMarkup(keyboard))

def service_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    service_id = query.data.split('_')[1]
    context.user_data['service_id'] = service_id
    salons = Salon.objects.all()
    keyboard = [[InlineKeyboardButton(f"{salon.title} - {salon.address}", callback_data=f'salon_{salon.id}') for salon in salons]]
    keyboard.append([InlineKeyboardButton('Назад', callback_data='list_services')])
    query.edit_message_text(text="Выберите салон:", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_DATE

def salon_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    salon_id = query.data.split('_')[1]
    context.user_data['salon_id'] = salon_id
    query.edit_message_text(text="Выберите дату:", reply_markup=date_keyboard())
    return CHOOSE_DATE

def contact_admin(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    admin_contact_info = "Связь с администратором по телефону: +7 123 456 78 90 или по email: admin@example.com"
    query.edit_message_text(text=admin_contact_info, reply_markup=back_to_main_menu_keyboard())

def back_to_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton('Назад', callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def date_keyboard():
    keyboard = []
    today = datetime.today()
    for i in range(7):
        day = today + timedelta(days=i)
        keyboard.append([InlineKeyboardButton(day.strftime('%d-%m-%Y'), callback_data=f'date_{day.strftime("%Y-%m-%d")}')])
    keyboard.append([InlineKeyboardButton('Назад', callback_data='service_back')])
    return InlineKeyboardMarkup(keyboard)

def choose_date(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    selected_date = query.data.split('_')[1]
    context.user_data['selected_date'] = selected_date
    query.edit_message_text(text="Выберите время:", reply_markup=time_keyboard())
    return CHOOSE_TIME

def time_keyboard():
    keyboard = []
    base_time = datetime.strptime("09:00", "%H:%M").time()
    for i in range(18):  # 18 слотов по 30 минут с 9:00 до 18:00
        time_slot = (datetime.combine(datetime.today(), base_time) + timedelta(minutes=30 * i)).time()
        keyboard.append([InlineKeyboardButton(time_slot.strftime('%H:%M'), callback_data=f'time_{time_slot.strftime("%H:%M")}')])
    keyboard.append([InlineKeyboardButton('Назад', callback_data='date_back')])
    return InlineKeyboardMarkup(keyboard)

def choose_time(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    selected_time = query.data.split('_')[1]
    context.user_data['selected_time'] = selected_time
    selected_datetime = datetime.strptime(f"{context.user_data['selected_date']} {selected_time}", "%Y-%m-%d %H:%M")
    context.user_data['selected_datetime'] = selected_datetime

    # Check if the selected time is available
    salon_id = context.user_data['salon_id']
    service_id = context.user_data['service_id']
    appointments = Appointment.objects.filter(salon_id=salon_id, service_id=service_id, date=selected_datetime.date(), start_at=selected_datetime.time())

    if appointments.exists():
        query.edit_message_text(f'Выбранное время {selected_time} занято. Пожалуйста, выберите другое время.', reply_markup=time_keyboard())
        return CHOOSE_TIME

    query.edit_message_text(f'Вы выбрали время с {selected_time}. Подтвердите заказ:', reply_markup=confirm_order_keyboard())
    return CONFIRM_ORDER

def confirm_order_keyboard():
    keyboard = [
        [InlineKeyboardButton('Оформить заказ', callback_data='confirm_order')],
        [InlineKeyboardButton('Назад', callback_data='time_back')]
    ]
    return InlineKeyboardMarkup(keyboard)

def confirm_order(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    client = Client.objects.get(id_tg=query.message.chat.id)
    service_id = context.user_data.get('service_id')
    salon_id = context.user_data.get('salon_id')
    selected_datetime = context.user_data.get('selected_datetime')

    try:
        order = Order.objects.create(client=client, status='waiting')
        Appointment.objects.create(
            client=client, service_id=service_id,
            salon_id=salon_id, status='access',
            date=selected_datetime.date(), start_at=selected_datetime.time(), order=order
        )
        query.edit_message_text(f'Записано на {selected_datetime}')
    except Exception as e:
        query.edit_message_text(f'Ошибка при оформлении заказа: {str(e)}. Попробуй еще раз.')
        return ConversationHandler.END

    return ConversationHandler.END

def back_to_main_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Главное меню', reply_markup=main_menu_keyboard())

def back_to_service(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    services = Service.objects.all()
    keyboard = [[InlineKeyboardButton(f"{service.title} - {service.price} руб.", callback_data=f'service_{service.id}') for service in services]]
    keyboard.append([InlineKeyboardButton('Назад', callback_data='list_salons')])
    query.edit_message_text(text='Выберите услугу:', reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_DATE

def back_to_date(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выбери дату:', reply_markup=date_keyboard())
    return CHOOSE_DATE

def back_to_time(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выбери время:', reply_markup=time_keyboard())
    return CHOOSE_TIME

def send_notifications():
    bot = Bot(token=settings.BOT_TOKEN)
    hundred_days_ago = timezone.now() - timedelta(days=100)
    clients_to_notify = Client.objects.filter(created_at__lte=hundred_days_ago)
    for client in clients_to_notify:
        bot.send_message(chat_id=client.id_tg, text='100 дней прошло, давай опять в салон')

def main():
    updater = Updater(settings.BOT_TOKEN, use_context=True)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSE_DATE: [CallbackQueryHandler(choose_date, pattern='^date_')],
            CHOOSE_TIME: [CallbackQueryHandler(choose_time, pattern='^time_')],
            CONFIRM_ORDER: [CallbackQueryHandler(confirm_order, pattern='^confirm_order$')]},
            fallbacks=[CommandHandler('start', start)]
            )
    
    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(CallbackQueryHandler(list_salons, pattern='^list_salons$'))
    updater.dispatcher.add_handler(CallbackQueryHandler(list_services, pattern='^list_services$'))
    updater.dispatcher.add_handler(CallbackQueryHandler(service_handler, pattern='^service_'))
    updater.dispatcher.add_handler(CallbackQueryHandler(salon_handler, pattern='^salon_'))
    updater.dispatcher.add_handler(CallbackQueryHandler(back_to_main_menu, pattern='^main_menu$'))
    updater.dispatcher.add_handler(CallbackQueryHandler(back_to_service, pattern='^service_back$'))
    updater.dispatcher.add_handler(CallbackQueryHandler(back_to_date, pattern='^date_back$'))
    updater.dispatcher.add_handler(CallbackQueryHandler(back_to_time, pattern='^time_back$'))
    updater.dispatcher.add_handler(CallbackQueryHandler(contact_admin, pattern='^contact_admin$'))

    updater.start_polling()
    updater.idle()


if __name__=='__main__':
    main()