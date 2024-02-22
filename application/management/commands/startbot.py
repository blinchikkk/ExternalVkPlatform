from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Start VkBot'

    def handle(self, *args, **options):
        current_bot = ...