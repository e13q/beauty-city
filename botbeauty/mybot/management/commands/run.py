from django.core.management.base import BaseCommand
from mybot.bot import main


class Command(BaseCommand):
    help_text = 'Запуск бота'
    
    def handle(self, *args, **kwargs):
        main()