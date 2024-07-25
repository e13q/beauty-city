from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from .models import Saloon, Procedure, Master
from .token import BOT_TOKEN


def start(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("Процедуры", callback_data='procedures'),
        ],
        [
            InlineKeyboardButton("Салоны", callback_data='salons')
        ],
        [
            InlineKeyboardButton("Мастера", callback_data='masters'),
        ],
        [
            InlineKeyboardButton("О нас", callback_data='about'),
            InlineKeyboardButton("Связаться с менеджером", callback_data='contact')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data.startswith('procedure_'):
        procedure_id = int(query.data.split('_')[1])
        procedure = Procedure.objects.get(id=procedure_id)
        query.edit_message_text(
            text=f"Процедура: {procedure.name}\nОписание: {procedure.description}\nЦена: {procedure.price}"
            )

    elif query.data.startswith('salon_'):
        salon_id = int(query.data.split('_')[1])
        salon = Saloon.objects.get(id=salon_id)
        query.edit_message_text(
            text=f"Салон: {salon.name}\nАдрес: {salon.adress}\nТелефон: {salon.phone}"
            )

    elif query.data.startswith('master_'):
        master_id = int(query.data.split('_')[1])
        master = Master.objects.get(id=master_id)
        procedures = master.procedures.all()
        procedures_list = "\n".join([proc.name for proc in procedures])
        query.edit_message_text(
            text=f"Мастер: {master.name}\nПроцедуры:\n{procedures_list}"
            )

    elif query.data == 'procedures':
        keyboard = [
            [
                InlineKeyboardButton(name, callback_data=f'procedure_{id}')
                for id, name in procedure_list()
                ]
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Выберите процедуру:", reply_markup=reply_markup
            )

    elif query.data == 'salons':
        keyboard = [
            [
                InlineKeyboardButton(name, callback_data=f'salon_{id}')
                for id, name in salon_list()
                ]
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Выберите салон:", reply_markup=reply_markup
            )

    elif query.data == 'masters':
        keyboard = [
            [
                InlineKeyboardButton(name, callback_data=f'master_{id}')
                for id, name in master_list()
                ]
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Выберите мастера:", reply_markup=reply_markup
            )

    else:
        query.edit_message_text(text=f"Вы выбрали: {query.data}")


def salon_list():
    salons = Saloon.objects.all()
    return [(salon.id, salon.name) for salon in salons]


def procedure_list():
    procedures = Procedure.objects.all()
    return [(procedure.id, procedure.name) for procedure in procedures]


def master_list():
    masters = Master.objects.all()
    return [(master.id, master.name) for master in masters]


def main():
    updater = Updater(BOT_TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()