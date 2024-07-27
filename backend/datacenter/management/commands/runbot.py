from django.core.management.base import BaseCommand
from telegram_bot import bot


class Command(BaseCommand):
    help_text = 'Запуск бота'

    def handle(self, *args, **kwargs):
        bot.main()
