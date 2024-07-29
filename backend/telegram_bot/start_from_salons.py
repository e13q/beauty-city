from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext
)
from .db_querrys import get_all_salons


# ----------------------Старт второй линии действий----------------------
def list_salons(update: Update, context: CallbackContext):
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
