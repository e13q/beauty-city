import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from datacenter.models import Salon, Service, Specialist, SpecialistWorkDayInSalon


ADMIN_PHONE_NUMBER = "+7(902)9000111"
DESCRIPTION = "Тут будет описание"


BOT_TOKEN = os.environ.get('BOT_TOKEN')
PAYMENT_PROVIDER_TOKEN = os.environ.get('PAYMENT_PROVIDER_TOKEN')


def start(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("Процедуры", callback_data='services'),
        ],
        [
            InlineKeyboardButton("Салоны", callback_data='salons')
        ],
        [
            InlineKeyboardButton("Мастера", callback_data='specialists'),
        ],
        [
            InlineKeyboardButton("О нас", callback_data='about'),
            InlineKeyboardButton("Связаться с менеджером", callback_data='contact')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)


def pay(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    title = "Тестовая оплата"
    description = "Оплата услуг салона Beauty-City"
    payload = "Стрижка машинкой"
    currency = "RUB"
    prices = [LabeledPrice("Тестовая оплата", 10000)]

    provide_token = context.bot_data['provide_token']# Цена в копейках

    context.bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token=provide_token,
        currency=currency,
        prices=prices,
        start_parameter="test-payment",
        need_name=True,
        need_phone_number=True,
    )


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data.startswith('service_'):
        service_id = int(query.data.split('_')[1])
        service = Service.objects.get(id=service_id)
        query.edit_message_text(
            text=f"Процедура: {service.title}\nОписание: {DESCRIPTION}\nЦена: {service.price}"
            )

    elif query.data.startswith('salon_'):
        salon_id = int(query.data.split('_')[1])
        salon = Salon.objects.get(id=salon_id)
        query.edit_message_text(
            text=f"Салон: {salon.title}\nАдрес: {salon.address}\nТелефон: {ADMIN_PHONE_NUMBER}"
            )

    elif query.data.startswith('master_'):
        master_id = int(query.data.split('_')[1])
        master = Specialist.objects.get(id=master_id)
        workdays = SpecialistWorkDayInSalon.objects.filter(
            id=master_id
        )
        if not workdays:
            query.edit_message_text(
                text="Нет доступных процедур"
            )
        #!!!
        services_list = []
        for workday in workdays:
            [services_list.append(proc.title) for proc in workday.services.all()]        
        services_dict = list(dict.fromkeys(services_list))
        services_str = "\n".join([proc for proc in services_dict])
        query.edit_message_text(
            text=f"Мастер: {master.full_name}\nПроцедуры:\n{services_str}"
            )

    elif query.data == 'services':
        keyboard = [
            [
                InlineKeyboardButton(name, callback_data=f'service_{id}')
                for id, name in service_list()
                ]
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Выберите процедуру:", reply_markup=reply_markup
            )

    elif query.data == 'salons':
        keyboard = [
            [
                InlineKeyboardButton(title, callback_data=f'salon_{id}')
                for id, title in salon_list()
                ]
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Выберите салон:", reply_markup=reply_markup
            )

    elif query.data == 'specialists':
        keyboard = [
            [
                InlineKeyboardButton(full_name, callback_data=f'master_{id}')
                for id, full_name in master_list()
                ]
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Выберите мастера:", reply_markup=reply_markup
            )

    else:
        query.edit_message_text(text=f"Вы выбрали: {query.data}")


def salon_list():
    salons = Salon.objects.all()
    return [(salon.id, salon.title) for salon in salons]


def service_list():
    services = Service.objects.all()
    return [(service.id, service.title) for service in services]


def master_list():
    specialists = Specialist.objects.all()
    return [(specialist.id, specialist.full_name) for specialist in specialists]


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    updater.dispatcher.bot_data['provide_token'] = PAYMENT_PROVIDER_TOKEN
    updater.dispatcher.add_handler(CommandHandler('start', start))
    #updater.dispatcher.add_handler(CommandHandler('pay', pay))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
