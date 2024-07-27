from django.core.management.base import BaseCommand
from telegram_bot.bot import main


class Command(BaseCommand):
    help = 'Запуск бота для управления салоном красоты'

    def handle(self, *args, **kwargs):
        self.stdout.write("Запуск бота...")
        main()
